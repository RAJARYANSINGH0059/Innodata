"""Deterministic, evidence-anchored feature-candidate discovery (Python adapter, EXPERIMENTAL).

No model is involved. Each candidate points at real code (file, line, symbol, snippet) and names the *kind* of
extension point it represents. A later (model-assisted or human) step turns a candidate into a requirement; this
module only finds and ranks grounded opportunities. It cannot judge whether a candidate is a good task — validity is
established afterwards by the executable gates.
"""
from __future__ import annotations

import ast
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

# Calls that consume attacker/caller-controlled data without a bound.
UNBOUNDED = {"zlib.decompress": "decompression", "gzip.decompress": "decompression", "bz2.decompress": "decompression",
             "lzma.decompress": "decompression", "json.loads": "parsing", "pickle.loads": "deserialisation"}
_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "build", "dist", ".tox"}
KINDS = {
    "tolerance-or-rule-parameter": "A hard-coded validation rule guards a raise; expose it as an optional, validated parameter.",
    "resource-limit-guard": "An unbounded call on external data; add an optional bound with defined failure semantics.",
    "option-threading": "A keyword option is forwarded through call sites; add a sibling option through the same path.",
    "documented-todo": "The maintainers left a TODO/FIXME/XXX at this point.",
    "untested-public-api": "A public function/method is not referenced by any test.",
}


def _py_files(root: Path, tests: bool) -> list[Path]:
    out = []
    for p in sorted(root.rglob("*.py")):
        if any(part in _SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        is_test = any(x.startswith("test") or x == "tests" for x in p.relative_to(root).parts)
        if is_test == tests:
            out.append(p)
    return out


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Attribute):
        return f"{_dotted(node.value)}.{node.attr}"
    return node.id if isinstance(node, ast.Name) else ""


class _Visitor(ast.NodeVisitor):
    def __init__(self, rel: str, lines: list[str]):
        self.rel, self.lines, self.stack, self.found = rel, lines, [], []

    def _sym(self) -> str:
        return ".".join(self.stack) or "<module>"

    def _snippet(self, node: ast.AST) -> str:
        return self.lines[node.lineno - 1].strip()[:140]

    def _emit(self, kind: str, node: ast.AST, why: str, weight: float):
        self.found.append({"kind": kind, "file": self.rel, "line": node.lineno, "symbol": self._sym(),
                           "snippet": self._snippet(node), "why": why, "weight": weight})

    def visit_ClassDef(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node):
        self.stack.append(node.name)
        public = not any(p.startswith("_") for p in self.stack)
        self.public_defs = getattr(self, "public_defs", [])
        if public:
            self.public_defs.append((self._sym(), node.lineno, node.name))
        self.generic_visit(node)
        self.stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_If(self, node):
        if any(isinstance(n, ast.Raise) for b in node.body for n in ast.walk(b)) and isinstance(node.test, ast.Compare):
            names = {n.id for n in ast.walk(node.test) if isinstance(n, ast.Name)}
            consts = [n.value for n in ast.walk(node.test) if isinstance(n, ast.Constant)]
            # comparison of a computed value against a hard-coded literal (e.g. `age < 0`) is a rule point
            if names and any(isinstance(c, (int, float)) and not isinstance(c, bool) for c in consts):
                self._emit("tolerance-or-rule-parameter", node,
                           "comparison against a hard-coded numeric literal guards a raise", 3.0)
        self.generic_visit(node)

    def visit_Call(self, node):
        name = _dotted(node.func)
        if name in UNBOUNDED and not any(k.arg in {"max_length", "wbits", "bufsize"} for k in node.keywords):
            self._emit("resource-limit-guard", node, f"`{name}` ({UNBOUNDED[name]}) has no size bound", 3.0)
        kw = [k.arg for k in node.keywords if k.arg and isinstance(k.value, ast.Name) and k.value.id == k.arg]
        for k in kw:
            self._emit("option-threading", node, f"option `{k}` is forwarded unchanged at this call site", 1.0)
        self.generic_visit(node)


def discover(repo: str | Path, top_per_kind: int = 5) -> dict[str, Any]:
    root = Path(repo).resolve()
    test_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in _py_files(root, True))
    found: list[dict[str, Any]] = []
    for p in _py_files(root, False):
        rel = p.relative_to(root).as_posix()
        src = p.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        v = _Visitor(rel, src.splitlines())
        v.visit(tree)
        found += v.found
        for sym, line, name in getattr(v, "public_defs", []):
            if not re.search(rf"\b{re.escape(name)}\b", test_text):
                found.append({"kind": "untested-public-api", "file": rel, "line": line, "symbol": sym,
                              "snippet": f"def {name}", "why": "name never appears in the test suite", "weight": 1.5})
        for i, text in enumerate(src.splitlines(), 1):
            if re.search(r"#\s*(TODO|FIXME|XXX)\b", text):
                found.append({"kind": "documented-todo", "file": rel, "line": i, "symbol": "<comment>",
                              "snippet": text.strip()[:140], "why": "maintainer-flagged work", "weight": 2.0})
    # merge option-threading per (file, symbol, option): one candidate with all call sites
    merged: dict[tuple, dict[str, Any]] = {}
    for c in found:
        key = (c["kind"], c["file"], c["symbol"], c["why"] if c["kind"] == "option-threading" else c["line"])
        if key in merged:
            merged[key]["weight"] += 0.5
            merged[key].setdefault("also_lines", []).append(c["line"])
        else:
            merged[key] = dict(c)
    cands = sorted(merged.values(), key=lambda c: (-c["weight"], c["file"], c["line"]))
    by_kind: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in cands:
        by_kind[c["kind"]].append(c)
    selected = []
    for kind in KINDS:  # diversity: best few from each kind, not top-N of one kind
        selected += by_kind.get(kind, [])[:top_per_kind]
    for i, c in enumerate(selected, 1):
        c["candidate_id"] = f"C{i:03d}"
        c["intent"] = KINDS[c["kind"]]
    return {"repo": str(root), "language_adapter": "python (EXPERIMENTAL)", "files_scanned": len(_py_files(root, False)),
            "total_candidates": len(cands), "counts_by_kind": {k: len(v) for k, v in by_kind.items()},
            "selected": selected,
            "limitations": ["heuristic, Python only", "ranking is a weak prior, not a quality judgement",
                            "does not check feasibility, testability or contamination"]}


def render_markdown(rep: dict[str, Any]) -> str:
    out = [f"# Feature candidates ({rep['language_adapter']})", "",
           f"Scanned {rep['files_scanned']} source files; {rep['total_candidates']} raw candidates; counts: {rep['counts_by_kind']}", "",
           "| id | kind | location | symbol | evidence |", "|---|---|---|---|---|"]
    for c in rep["selected"]:
        out.append(f"| {c['candidate_id']} | {c['kind']} | {c['file']}:{c['line']} | {c['symbol']} | `{c['snippet'].replace('|', '/')}` |")
    return "\n".join(out) + "\n"


def write_report(repo: str | Path, out_dir: str | Path, top_per_kind: int = 5) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rep = discover(repo, top_per_kind)
    (out / "candidates.json").write_text(json.dumps(rep, indent=2, sort_keys=True), encoding="utf-8")
    (out / "candidates.md").write_text(render_markdown(rep), encoding="utf-8")
    return rep

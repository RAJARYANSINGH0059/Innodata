from __future__ import annotations

import itertools
import json
import re
import tomllib
from pathlib import Path
from typing import Any

from .patching import validate_patch_text

_STOP = set("the and with that this when must should from into have has not are for any all its can does only than then also been will which where while there their they them".split())
_WEIGHTS = {"files": 0.2, "symbols": 0.2, "entrypoints": 0.2, "criteria_tokens": 0.2, "test_tokens": 0.2}
DISTINCT_BELOW = 0.25
REVIEW_ABOVE = 0.5


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z0-9]{3,}", text.lower()) if w not in _STOP}


def signature(task_dir: str | Path) -> dict[str, Any]:
    root = Path(task_dir)
    meta = tomllib.loads((root / "task.toml").read_text(encoding="utf-8"))
    patch = (root / meta["solution"]["patch"]).read_text(encoding="utf-8")
    instr = (root / "instruction.md").read_text(encoding="utf-8")
    files = set(validate_patch_text(patch))
    symbols: set[str] = set()
    for line in patch.splitlines():
        m = re.match(r"@@ .*? @@ (?:async )?(?:def|class) (\w+)", line)
        if m:
            symbols.add(m.group(1))
        m = re.match(r"\+\s*(?:async )?(?:def|class) (\w+)", line)
        if m:
            symbols.add(m.group(1))
        m = re.match(r"\+\s{4}(\w+)\s*:\s*[^=]+=", line)  # added class attribute
        if m:
            symbols.add(m.group(1))
    # entry points / API names the requirement talks about (backticked identifiers)
    entry = {x.split("(")[0] for x in re.findall(r"`([A-Za-z_][\w.]*[^`]*?)`", instr) if re.match(r"[A-Za-z_]", x)}
    entry = {e for e in entry if re.fullmatch(r"[A-Za-z_][\w.]*", e) and len(e) > 3}
    crit = instr.split("## Acceptance criteria", 1)[-1].split("## Non-goals", 1)[0]
    test_text = " ".join(p.read_text(encoding="utf-8") for p in sorted((root / meta["tests"]["feature"]).rglob("test_*.py")))
    tests = set(re.findall(r"def (test_\w+)", test_text))
    return {
        "task_id": meta["task"]["id"],
        "files": sorted(files), "symbols": sorted(symbols), "entrypoints": sorted(entry),
        "criteria_tokens": sorted(_tokens(crit)),
        "test_tokens": sorted(_tokens(" ".join(t.replace("_", " ") for t in tests))),
        "feature_test_count": len(tests),
        "declared_dimensions": meta.get("variation", {}).get("dimensions", []),
        "declared_summary": meta.get("variation", {}).get("summary", ""),
    }


def _jaccard(a: list[str], b: list[str]) -> float:
    A, B = set(a), set(b)
    return 1.0 if not (A | B) else len(A & B) / len(A | B)


def compare(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    parts = {k: round(_jaccard(a[k], b[k]), 3) for k in _WEIGHTS}
    composite = round(sum(parts[k] * w for k, w in _WEIGHTS.items()), 3)
    dims_a, dims_b = set(a["declared_dimensions"]), set(b["declared_dimensions"])
    verdict = ("DISTINCT" if composite < DISTINCT_BELOW else
               "NEEDS_MANUAL_REVIEW" if composite < REVIEW_ABOVE else "TOO_SIMILAR")
    return {"a": a["task_id"], "b": b["task_id"], "similarity": parts, "composite": composite,
            "shared_declared_dimensions": sorted(dims_a & dims_b),
            "shared_files": sorted(set(a["files"]) & set(b["files"])), "verdict": verdict}


def variation_report(task_dirs: list[str | Path]) -> dict[str, Any]:
    sigs = [signature(d) for d in task_dirs]
    pairs = [compare(x, y) for x, y in itertools.combinations(sigs, 2)]
    return {"method": "weighted Jaccard over files/symbols/entrypoints/criteria/test tokens "
                      f"(weights {_WEIGHTS}); DISTINCT<{DISTINCT_BELOW}, REVIEW<{REVIEW_ABOVE}, else TOO_SIMILAR. "
                      "Heuristic only: embeddings not used; every verdict needs manual adjudication.",
            "signatures": sigs, "pairs": pairs}


def render_markdown(report: dict[str, Any]) -> str:
    out = ["# Variation report", "", report["method"], ""]
    for s in report["signatures"]:
        out += [f"## {s['task_id']}", f"- files: {', '.join(s['files'])}", f"- symbols: {', '.join(s['symbols'])}",
                f"- feature tests: {s['feature_test_count']}", f"- declared dimensions: {', '.join(s['declared_dimensions'])}",
                f"- summary: {s['declared_summary']}", ""]
    out += ["## Pairwise", "", "| A | B | composite | files | symbols | entrypoints | criteria | tests | verdict |", "|---|---|---|---|---|---|---|---|---|"]
    for p in report["pairs"]:
        sm = p["similarity"]
        out.append(f"| {p['a']} | {p['b']} | {p['composite']} | {sm['files']} | {sm['symbols']} | {sm['entrypoints']} | {sm['criteria_tokens']} | {sm['test_tokens']} | {p['verdict']} |")
    return "\n".join(out) + "\n"


def write_report(task_dirs: list[str | Path], out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rep = variation_report(task_dirs)
    (out / "variation_report.json").write_text(json.dumps(rep, indent=2, sort_keys=True), encoding="utf-8")
    (out / "variation_report.md").write_text(render_markdown(rep), encoding="utf-8")
    return rep

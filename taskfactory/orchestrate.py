from __future__ import annotations

import hashlib
import os
import json
import sys
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .models import (
    CheckStatus, CommandResult, CommandSpec, GateCheck, StateObservation,
    TaskKind, ThreeStateReport, _jsonable,
)
from .patching import PatchError, apply_patch, install_files, make_workspace
from .repository import inspect_repository
from .runner import run_command
from .test_adapters import annotate_command_result
from .validation import evaluate_three_state

_SEVERITY = [CheckStatus.PASS, CheckStatus.NOT_APPLICABLE, CheckStatus.PASS_WITH_LIMITATIONS,
             CheckStatus.NEEDS_MORE_EVIDENCE, CheckStatus.NOT_YET_AVAILABLE, CheckStatus.FAILED]


@dataclass
class TaskSpec:
    task_id: str
    kind: TaskKind
    commit: str
    patch: Path
    feature_tests: Path
    regression_tests: Path | None
    inject_dir: str = "tests"
    baseline_targets: list[str] = field(default_factory=lambda: ["tests"])
    pythonpath: list[str] = field(default_factory=lambda: ["."])
    import_probe: str = ""
    timeout: int = 300
    repeats: int = 1
    root: Path = Path(".")


def load_task(task_dir: str | Path) -> TaskSpec:
    root = Path(task_dir).resolve()
    data = tomllib.loads((root / "task.toml").read_text(encoding="utf-8"))
    t, r, s, ts, run = (data.get(k, {}) for k in ("task", "repo", "solution", "tests", "run"))
    reg = root / ts["regression"] if ts.get("regression") and (root / ts["regression"]).is_dir() else None
    return TaskSpec(
        task_id=t["id"], kind=TaskKind(t.get("kind", "feature")), commit=r["commit"],
        patch=root / s["patch"], feature_tests=root / ts["feature"], regression_tests=reg,
        inject_dir=ts.get("inject_dir", "tests"),
        baseline_targets=run.get("baseline_targets", ["tests"]),
        pythonpath=run.get("pythonpath", ["."]), import_probe=run.get("import_probe", ""),
        timeout=int(run.get("timeout", 300)), repeats=int(run.get("repeats", 1)), root=root,
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _failing(evidence: dict[str, Any]) -> dict[str, str]:
    j = evidence.get("junit", {})
    out = {}
    for item in j.get("failures", []) + j.get("errors", []):
        out[item["test"]] = (item["message"] or item["detail"]).strip().splitlines()[0][:160] if (item["message"] or item["detail"]) else ""
    return out


def _run_pytest(spec: TaskSpec, ws: Path, out: Path, label: str, target: str) -> tuple[CommandResult, dict[str, Any]]:
    junit = out / f"{label}.xml"
    env = {
        "PYTHONPATH": os.pathsep.join(str((ws / p).resolve()) for p in spec.pythonpath),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    cmd = CommandSpec(
        name=label, timeout_seconds=spec.timeout, env=env,
        argv=[sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
              f"--junitxml={junit}", target],
    )
    res, ev = annotate_command_result(run_command(cmd, ws), junit)
    (out / f"{label}.log").write_text(res.stdout + "\n--- stderr ---\n" + res.stderr, encoding="utf-8")
    return res, ev


def _import_origin(spec: TaskSpec, ws: Path) -> GateCheck | None:
    if not spec.import_probe:
        return None
    env = {"PYTHONPATH": os.pathsep.join(str((ws / p).resolve()) for p in spec.pythonpath),
           "PYTHONDONTWRITEBYTECODE": "1"}
    res = run_command(CommandSpec(
        name="import_probe", env=env, timeout_seconds=60,
        argv=[sys.executable, "-c", f"import {spec.import_probe} as m; print(m.__file__)"]), ws)
    origin = res.stdout.strip()
    ok = res.exit_code == 0 and Path(origin).resolve().is_relative_to(ws.resolve())
    return GateCheck("import_origin", CheckStatus.PASS if ok else CheckStatus.FAILED,
                     f"`{spec.import_probe}` imports from the state workspace",
                     f"origin={origin or res.stderr.strip()[:200]}")


def _build_state(spec: TaskSpec, repo: Path, tmp: Path, out: Path, state: str):
    ws = tmp / state
    head = make_workspace(repo, spec.commit, ws)
    notes: list[str] = []
    if state in ("reference", "removed"):
        notes += apply_patch(ws, spec.patch)
    if state == "removed":
        apply_patch(ws, spec.patch, reverse=True)
    digest = inspect_repository(ws).working_tree_digest  # before test injection
    install_files(ws, spec.feature_tests, f"{spec.inject_dir}/task_feature")
    if spec.regression_tests:
        install_files(ws, spec.regression_tests, f"{spec.inject_dir}/task_regression")

    runs = []
    for rep in range(spec.repeats):
        base, base_ev, task, task_ev = [], [], [], []
        targets = list(spec.baseline_targets)
        if spec.regression_tests:
            targets.append(f"{spec.inject_dir}/task_regression")
        for i, tgt in enumerate(targets):
            r, e = _run_pytest(spec, ws, out, f"{state}_baseline{i}_r{rep}", tgt)
            base.append(r); base_ev.append(e)
        r, e = _run_pytest(spec, ws, out, f"{state}_feature_r{rep}", f"{spec.inject_dir}/task_feature")
        task.append(r); task_ev.append(e)
        runs.append((base, base_ev, task, task_ev))
    return ws, head, digest, notes, runs


def validate_task(task_dir: str | Path, repo: str | Path, out_dir: str | Path) -> dict[str, Any]:
    spec = load_task(task_dir)
    repo, out = Path(repo).resolve(), Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    extra: list[GateCheck] = []
    observations: dict[str, StateObservation] = {}
    digests: dict[str, str] = {}
    failing: dict[str, dict[str, str]] = {}
    flake: dict[str, Any] = {}
    head = None

    with tempfile.TemporaryDirectory(prefix="tf_") as td:
        tmp = Path(td)
        for state in ("original", "reference", "removed"):
            try:
                ws, head, digest, _notes, runs = _build_state(spec, repo, tmp, out, state)
            except PatchError as exc:
                extra.append(GateCheck(f"{state}_workspace", CheckStatus.FAILED, "workspace builds", str(exc)))
                rep = ThreeStateReport(spec.kind, CheckStatus.FAILED, extra, f"{state} state could not be built.")
                result = {"report": rep.to_dict(), "task_id": spec.task_id}
                (out / "validation_report.json").write_text(json.dumps(result, indent=2, sort_keys=True))
                return result
            digests[state] = digest
            probe = _import_origin(spec, ws)
            if probe:
                extra.append(GateCheck(f"{state}_import_origin", probe.status, probe.expected, probe.actual))
            base, base_ev, task, task_ev = runs[0]
            observations[state] = StateObservation(state, base, task)
            failing[state] = _failing(task_ev[0])
            vectors = [[(r.exit_code, r.outcome_class) for r in b + t] for b, _, t, _ in runs]
            fsets = [sorted(_failing(te[0])) for _, _, _, te in runs]
            stable = all(v == vectors[0] for v in vectors) and all(f == fsets[0] for f in fsets)
            flake[state] = {"repeats": len(runs), "stable": stable}
            extra.append(GateCheck(f"{state}_repeat_stability",
                                   CheckStatus.PASS if stable else CheckStatus.FAILED,
                                   f"{len(runs)} identical runs", f"vectors={vectors}"))

    base_report = evaluate_three_state(spec.kind, observations["original"], observations["reference"], observations["removed"])
    extra.append(GateCheck("removed_tree_equals_original_tree",
                           CheckStatus.PASS if digests["original"] == digests["removed"] else CheckStatus.FAILED,
                           "reverting the reference patch restores the exact original source tree",
                           f"original={digests['original'][:16]} removed={digests['removed'][:16]}"))
    extra.append(GateCheck("reference_tree_differs",
                           CheckStatus.PASS if digests["reference"] != digests["original"] else CheckStatus.FAILED,
                           "reference patch changes the source tree", f"reference={digests['reference'][:16]}"))
    same_fail = failing["original"] == failing["removed"] and bool(failing["original"])
    extra.append(GateCheck("failing_tests_consistent_A_vs_C",
                           CheckStatus.PASS if same_fail else CheckStatus.FAILED,
                           "same feature tests fail, for the same reason, in State A and State C",
                           f"A={sorted(failing['original'])[:3]}.. ({len(failing['original'])}) C=({len(failing['removed'])})",
                           evidence={"A": failing["original"], "C": failing["removed"]}))
    checks = base_report.checks + extra
    final = max((c.status for c in checks), key=_SEVERITY.index)
    report = ThreeStateReport(spec.kind, final, checks,
                              base_report.summary if final == base_report.status else
                              f"Overall {final.value}: see failing checks.")
    result = {
        "task_id": spec.task_id, "commit": head, "state_tree_digests": digests,
        "failing_feature_tests": failing, "repeatability": flake,
        "artifact_sha256": {"patch": _sha256(spec.patch)},
        "python": sys.version.split()[0], "report": report.to_dict(),
    }
    (out / "validation_report.json").write_text(json.dumps(_jsonable(result), indent=2, sort_keys=True), encoding="utf-8")
    return result

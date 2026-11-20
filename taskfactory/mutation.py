from __future__ import annotations

import json
import tempfile
from pathlib import Path

from .orchestrate import _run_pytest, load_task
from .patching import apply_patch, install_files, make_workspace


def run_mutants(task_dir: str | Path, repo: str | Path, mutants_file: str | Path, out_dir: str | Path) -> dict:
    """Apply each hand-written variant on top of the reference solution and run the task tests.

    kind="wrong"     -> variant is incorrect; tests MUST fail (killed). Survivors are oracle gaps.
    kind="alt_valid" -> variant is a different correct implementation; tests MUST pass.
    kind="equivalent"-> behaviour-preserving; reported separately, never counted as survivor.
    """
    spec = load_task(task_dir)
    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    mutants = json.loads(Path(mutants_file).read_text(encoding="utf-8"))
    results = []
    for m in mutants:
        with tempfile.TemporaryDirectory(prefix="mut_") as td:
            ws = Path(td) / "ws"
            make_workspace(repo, spec.commit, ws)
            apply_patch(ws, spec.patch)
            target = ws / m["file"]
            text = target.read_text(encoding="utf-8")
            if text.count(m["old"]) != 1:
                results.append({"id": m["id"], "kind": m["kind"], "outcome": "INVALID",
                                "detail": f"pattern matched {text.count(m['old'])} times"})
                continue
            target.write_text(text.replace(m["old"], m["new"]), encoding="utf-8")
            install_files(ws, spec.feature_tests, f"{spec.inject_dir}/task_feature")
            if spec.regression_tests:
                install_files(ws, spec.regression_tests, f"{spec.inject_dir}/task_regression")
            feat, fev = _run_pytest(spec, ws, out, f"{m['id']}_feature", f"{spec.inject_dir}/task_feature")
            if spec.regression_tests:
                reg, _ = _run_pytest(spec, ws, out, f"{m['id']}_regression", f"{spec.inject_dir}/task_regression")
                suite, _ = _run_pytest(spec, ws, out, f"{m['id']}_suite", spec.baseline_targets[0])
                caught = not (feat.passed and reg.passed and suite.passed)
            else:
                caught = not feat.passed
            if feat.timed_out:
                outcome = "TIMEOUT"
            elif m["kind"] == "wrong":
                outcome = "KILLED" if caught else "SURVIVED"
            elif m["kind"] == "alt_valid":
                outcome = "ACCEPTED" if not caught else "REJECTED_VALID_ALTERNATIVE"
            else:  # kind == "equivalent": claimed behaviour-preserving, so tests must NOT catch it
                outcome = "MISLABELLED_EQUIVALENT" if caught else "EQUIVALENT"
            results.append({"id": m["id"], "kind": m["kind"], "outcome": outcome,
                            "description": m.get("description", ""),
                            "failed_tests": sorted(_f for _f in fev.get("junit", {}).get("failures", []) and
                                                   [x["test"].split("::")[-1] for x in fev["junit"]["failures"]])})
    summary = {k: sum(1 for r in results if r["outcome"] == k)
               for k in ("KILLED", "SURVIVED", "INVALID", "TIMEOUT", "ACCEPTED", "REJECTED_VALID_ALTERNATIVE", "EQUIVALENT", "MISLABELLED_EQUIVALENT")}
    report = {"task_id": spec.task_id, "summary": summary, "results": results}
    (out / "mutation_report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .models import _jsonable
from .repository import inspect_repository


def main() -> None:
    parser = argparse.ArgumentParser(prog="taskfactory", description="Phase 1 Coding Task Factory foundation")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect", help="Fingerprint a local repository without modifying it")
    inspect.add_argument("repository", type=Path)
    inspect.add_argument("--out", type=Path, help="Write snapshot JSON to this path")
    val = sub.add_parser("validate", help="Run the three-state validation for a task directory")
    val.add_argument("task_dir", type=Path)
    val.add_argument("--repo", type=Path, required=True, help="Local git repository containing the pinned commit")
    val.add_argument("--out", type=Path, required=True)
    mut = sub.add_parser("mutate", help="Run hand-written wrong/alternative implementations against task tests")
    mut.add_argument("task_dir", type=Path)
    mut.add_argument("--repo", type=Path, required=True)
    mut.add_argument("--mutants", type=Path, required=True)
    mut.add_argument("--out", type=Path, required=True)
    var = sub.add_parser("variation", help="Behavioural-signature overlap report for task directories")
    var.add_argument("task_dirs", type=Path, nargs="+")
    var.add_argument("--out", type=Path, required=True)
    rec = sub.add_parser("reconstruct", help="Verify manifest and re-run validation from scratch; compare to recorded evidence")
    rec.add_argument("task_dir", type=Path)
    rec.add_argument("--repo", type=Path, required=True)
    rec.add_argument("--recorded", type=Path, required=True, help="earlier validation_report.json")
    rec.add_argument("--out", type=Path, required=True)
    man = sub.add_parser("manifest", help="Write MANIFEST.sha256 for a task directory")
    man.add_argument("task_dir", type=Path)
    args = parser.parse_args()

    if args.command == "inspect":
        snapshot = inspect_repository(args.repository)
        payload = json.dumps(_jsonable(asdict(snapshot)), indent=2, sort_keys=True)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(payload + "\n", encoding="utf-8")
        print(payload)
    elif args.command == "validate":
        from .orchestrate import validate_task
        result = validate_task(args.task_dir, args.repo, args.out)
        status = result["report"]["status"]
        print(f"{result['task_id']}: {status}")
        for c in result["report"]["checks"]:
            print(f"  [{c['status']}] {c['check_id']}")
        raise SystemExit(0 if status in ("PASS", "PASS_WITH_LIMITATIONS") else 1)
    elif args.command == "variation":
        from .variation import write_report
        rep = write_report(args.task_dirs, args.out)
        for p in rep["pairs"]:
            print(f"{p['a']} vs {p['b']}: composite={p['composite']} {p['verdict']}")
    elif args.command == "manifest":
        from .reconstruct import write_manifest
        print(f"{len(write_manifest(args.task_dir))} files hashed")
    elif args.command == "reconstruct":
        from .reconstruct import reconstruct
        res = reconstruct(args.task_dir, args.repo, args.recorded, args.out)
        print(json.dumps(res, indent=2))
        raise SystemExit(0 if res["status"] == "PASS" else 1)
    elif args.command == "mutate":
        from .mutation import run_mutants
        rep = run_mutants(args.task_dir, args.repo, args.mutants, args.out)
        print(json.dumps(rep["summary"]))
        for r in rep["results"]:
            print(f"  {r['outcome']:<28} {r['id']}")
        raise SystemExit(1 if rep["summary"]["SURVIVED"] or rep["summary"]["REJECTED_VALID_ALTERNATIVE"] or rep["summary"]["MISLABELLED_EQUIVALENT"] or rep["summary"]["INVALID"] else 0)


if __name__ == "__main__":
    main()

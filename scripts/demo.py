#!/usr/bin/env python3
"""One-command reproducible demo: validates every task in tasks/ against pinned upstream source.

    python scripts/demo.py [--workdir DIR] [--out DIR]

Needs: Python >=3.11, git, network access to github.com, `pip install pytest freezegun`;
node >=22.7 + npm for the TypeScript task (reported NOT_RUN if absent).
Exit code 0 only if every task passes validation, mutation, reconstruction and the variation gate.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([sys.executable, "-m", "taskfactory.cli", *map(str, args)], cwd=ROOT, env=env,
                          text=True, capture_output=True, check=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", type=Path, default=ROOT / ".demo_work")
    ap.add_argument("--out", type=Path, default=ROOT / "demo_out")
    a = ap.parse_args()
    try:
        import freezegun  # noqa: F401
        import pytest  # noqa: F401
    except ImportError:
        print("Missing test dependencies. Run: pip install pytest freezegun")
        return 2

    a.workdir.mkdir(parents=True, exist_ok=True)
    tasks = sorted(p.parent for p in (ROOT / "tasks").glob("*/task.toml"))
    rows, ok, ran, repos = [], True, [], {}
    for t in tasks:
        meta = tomllib.loads((t / "task.toml").read_text(encoding="utf-8"))
        commit, url = meta["repo"]["commit"], meta["repo"]["url"]
        runner = meta.get("run", {}).get("runner", "pytest")
        if runner == "node-test" and not (shutil.which("node") and shutil.which("npm")):
            rows.append({"task": t.name, "three_state": "NOT_RUN", "mutants": "node/npm missing",
                         "alt_valid": "-", "reconstruct": "NOT_RUN"})
            continue
        if url not in repos:
            repo = a.workdir / url.rstrip("/").rsplit("/", 1)[-1]
            if not repo.exists():
                print(f"cloning {url} ...")
                r = subprocess.run(["git", "-c", "core.autocrlf=false", "clone", "-q", url, str(repo)], text=True, capture_output=True)
                if r.returncode:
                    print(r.stderr)
                    return 2
            repos[url] = repo
        repo = repos[url]
        if subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{commit}^{{commit}}"]).returncode:
            print(f"pinned commit {commit} not in clone")
            return 2
        deps: list[str] = []
        if runner == "node-test":
            subprocess.run(["git", "-C", str(repo), "checkout", "-q", "--detach", commit], check=True)
            if not (repo / "node_modules").exists():
                print(f"npm install in {repo.name} (no upstream lockfile; versions may differ from the recorded run) ...")
                r = subprocess.run(["npm", "install", "--no-audit", "--no-fund", "--ignore-scripts"], cwd=repo,
                                   text=True, capture_output=True, shell=(os.name == "nt"))
                if r.returncode:
                    print(r.stderr[-2000:])
                    return 2
            deps = ["--deps-dir", str(repo / "node_modules")]
        out = a.out / t.name
        v = cli("validate", t, "--repo", repo, "--out", out, *deps)
        m = cli("mutate", t, "--repo", repo, "--mutants", t / "mutants.json", "--out", out / "mutation", *deps)
        rc = cli("reconstruct", t, "--repo", repo, "--recorded", out / "validation_report.json", "--out", out / "reconstruction", *deps)
        mut = json.loads((out / "mutation" / "mutation_report.json").read_text())["summary"]
        row = {"task": t.name, "three_state": "PASS" if v.returncode == 0 else "FAIL",
               "mutants": f"{mut['KILLED']} killed / {mut['SURVIVED']} survived / {mut['EQUIVALENT']} equiv",
               "alt_valid": f"{mut['ACCEPTED']} accepted / {mut['REJECTED_VALID_ALTERNATIVE']} rejected",
               "reconstruct": "PASS" if rc.returncode == 0 else "FAIL"}
        ok &= v.returncode == 0 and m.returncode == 0 and rc.returncode == 0
        rows.append(row)
        ran.append(t)
    var = cli("variation", *ran, "--out", a.out / "variation")
    ok &= var.returncode == 0 and "TOO_SIMILAR" not in var.stdout
    print(f"\n{'task':<36}{'3-state':<9}{'mutants':<40}{'alt-valid':<26}reconstruct")
    for r in rows:
        print(f"{r['task']:<36}{r['three_state']:<9}{r['mutants']:<40}{r['alt_valid']:<26}{r['reconstruct']}")
    print("\nvariation:\n" + var.stdout.strip())
    print(f"\nOVERALL: {'PASS' if ok else 'FAIL'}   evidence in {a.out}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

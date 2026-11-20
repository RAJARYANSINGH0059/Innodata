from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

MANIFEST = "MANIFEST.sha256"


def _files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*")
                  if p.is_file() and p.name != MANIFEST and "__pycache__" not in p.parts and not p.is_symlink())


def write_manifest(task_dir: str | Path) -> list[str]:
    root = Path(task_dir)
    lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}" for p in _files(root)]
    (root / MANIFEST).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return lines


def verify_manifest(task_dir: str | Path) -> list[str]:
    """Return a list of problems (empty = intact): changed, missing and unlisted files."""
    root = Path(task_dir)
    mf = root / MANIFEST
    if not mf.is_file():
        return ["manifest missing"]
    listed = {}
    for line in mf.read_text(encoding="utf-8").splitlines():
        digest, _, rel = line.partition("  ")
        listed[rel] = digest
    problems = []
    for rel, digest in listed.items():
        p = root / rel
        if not p.is_file():
            problems.append(f"missing: {rel}")
        elif hashlib.sha256(p.read_bytes()).hexdigest() != digest:
            problems.append(f"modified: {rel}")
    on_disk = {p.relative_to(root).as_posix() for p in _files(root)}
    problems += [f"unlisted: {rel}" for rel in sorted(on_disk - set(listed))]
    return problems


def reconstruct(task_dir: str | Path, repo: str | Path, recorded_report: str | Path, out_dir: str | Path) -> dict[str, Any]:
    """Copy the task to a fresh directory, verify its manifest, re-run validation from a fresh clone and compare
    the outcome, tree digests and patch hash to previously recorded evidence."""
    from .orchestrate import validate_task

    problems = verify_manifest(task_dir)
    result: dict[str, Any] = {"manifest_problems": problems}
    if problems:
        result["status"] = "FAILED"
        result["reason"] = "task directory does not match its manifest"
        return result
    recorded = json.loads(Path(recorded_report).read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="recon_") as td:
        fresh = Path(td) / "task"
        shutil.copytree(task_dir, fresh)
        redo = validate_task(fresh, repo, out_dir)
    same = {
        "status": redo["report"]["status"] == recorded["report"]["status"] == "PASS",
        "commit": redo["commit"] == recorded["commit"],
        "state_tree_digests": redo["state_tree_digests"] == recorded["state_tree_digests"],
        "patch_sha256": redo["artifact_sha256"] == recorded["artifact_sha256"],
        "failing_feature_tests": redo["failing_feature_tests"] == recorded["failing_feature_tests"],
    }
    result.update(comparison=same, status="PASS" if all(same.values()) else "FAILED")
    return result

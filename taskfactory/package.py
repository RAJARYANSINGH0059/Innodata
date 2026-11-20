from __future__ import annotations

import hashlib
import json
import re
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

_RELEASE_KINDS = {"feature", "feature_extension"}
_REQUIRED_METADATA = {
    "task_id", "kind", "title", "repository_url", "license", "base_commit",
    "working_tree_digest",
}
_TASK_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,79}$")
_GIT_SHA = re.compile(r"^[a-fA-F0-9]{7,64}$")
_SHA256 = re.compile(r"^[a-fA-F0-9]{64}$")


def _safe_relative_path(raw: str) -> PurePosixPath:
    path = PurePosixPath(raw)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"Unsafe package-relative path: {raw!r}")
    if "\\" in raw:
        raise ValueError(f"Use POSIX separators in package paths: {raw!r}")
    return path


def _toml_scalar(value: Any) -> str:
    # JSON string escaping is a valid subset of TOML basic-string escaping.
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, list) and all(isinstance(item, (str, int, float, bool)) for item in value):
        return "[" + ", ".join(_toml_scalar(item) for item in value) + "]"
    raise TypeError(f"Unsupported TOML metadata value: {type(value).__name__}")


def _write_bytes(root: Path, relative: str, content: bytes) -> None:
    safe = _safe_relative_path(relative)
    target = root.joinpath(*safe.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)


def build_task_package(
    output_dir: str | Path,
    metadata: Mapping[str, Any],
    instructions: str,
    solution_patch: str,
    feature_tests: Mapping[str, str],
    regression_tests: Mapping[str, str],
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a provisional, checksummed task package.

    This serializer is intentionally internal and must be adapted to the final
    organiser schema when provided. It does not validate whether a task's
    requirements, patch or tests are semantically correct.
    """
    missing = sorted(_REQUIRED_METADATA - set(metadata))
    if missing:
        raise ValueError(f"Missing required metadata: {', '.join(missing)}")
    task_id = str(metadata["task_id"])
    if not _TASK_ID.fullmatch(task_id):
        raise ValueError("task_id must be 3-80 safe filename characters")
    kind = str(metadata["kind"])
    if kind not in _RELEASE_KINDS:
        raise ValueError(f"Task kind {kind!r} is outside the confirmed Phase 1 release scope")
    if not str(metadata["title"]).strip() or not str(metadata["license"]).strip():
        raise ValueError("Task title and repository license must not be empty")
    if not _GIT_SHA.fullmatch(str(metadata["base_commit"])):
        raise ValueError("base_commit must be a 7-64 character hexadecimal Git object ID")
    if not _SHA256.fullmatch(str(metadata["working_tree_digest"])):
        raise ValueError("working_tree_digest must be a 64-character SHA-256 digest")
    if not instructions.strip() or not solution_patch.strip():
        raise ValueError("Instructions and reference patch must not be empty")
    if not feature_tests or not regression_tests:
        raise ValueError("At least one feature test and one regression test are required")

    root = Path(output_dir).resolve()
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(f"Refusing to overwrite non-empty package directory: {root}")
    root.mkdir(parents=True, exist_ok=True)

    toml_lines = []
    for key in sorted(metadata):
        if not re.fullmatch(r"[A-Za-z0-9_-]+", key):
            raise ValueError(f"Invalid TOML metadata key: {key!r}")
        toml_lines.append(f"{key} = {_toml_scalar(metadata[key])}")
    _write_bytes(root, "task.toml", ("\n".join(toml_lines) + "\n").encode("utf-8"))
    _write_bytes(root, "instructions.md", instructions.rstrip().encode("utf-8") + b"\n")
    _write_bytes(root, "solution/solution.patch", solution_patch.rstrip().encode("utf-8") + b"\n")

    for group, files in (("tests/feature", feature_tests), ("tests/regression", regression_tests)):
        for relative, content in sorted(files.items()):
            safe = _safe_relative_path(relative)
            if len(safe.parts) != 1:
                raise ValueError(f"Test files must be direct children of their test group: {relative!r}")
            if not isinstance(content, str) or not content.strip():
                raise ValueError(f"Test file {relative!r} is empty or not text")
            _write_bytes(root, f"{group}/{relative}", content.rstrip().encode("utf-8") + b"\n")

    for relative, payload in sorted(evidence.items()):
        safe = _safe_relative_path(relative)
        if safe.suffix.lower() != ".json":
            raise ValueError(f"Evidence must be JSON: {relative!r}")
        _write_bytes(root, f"evidence/{safe.as_posix()}", (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))

    files = sorted(p for p in root.rglob("*") if p.is_file())
    manifest = {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in files
    }
    _write_bytes(root, "manifest.sha256", (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return verify_task_package(root)


def verify_task_package(package_dir: str | Path) -> dict[str, Any]:
    """Verify package structure, TOML syntax and exact artifact hashes."""
    root = Path(package_dir).resolve()
    manifest_path = root / "manifest.sha256"
    if not manifest_path.is_file():
        return {"valid": False, "errors": ["manifest.sha256 is missing"]}
    errors: list[str] = []
    try:
        expected = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"valid": False, "errors": [f"manifest is invalid: {exc}"]}
    if not isinstance(expected, dict):
        return {"valid": False, "errors": ["manifest must be a JSON object"]}

    actual_files = {
        p.relative_to(root).as_posix(): p
        for p in root.rglob("*") if p.is_file() and p.name != "manifest.sha256"
    }
    for relative in sorted(set(expected) - set(actual_files)):
        errors.append(f"missing artifact: {relative}")
    for relative in sorted(set(actual_files) - set(expected)):
        errors.append(f"unmanifested artifact: {relative}")
    for relative in sorted(set(expected) & set(actual_files)):
        digest = hashlib.sha256(actual_files[relative].read_bytes()).hexdigest()
        if digest != expected[relative]:
            errors.append(f"checksum mismatch: {relative}")

    required = ["task.toml", "instructions.md", "solution/solution.patch"]
    for relative in required:
        if relative not in actual_files:
            errors.append(f"required artifact missing: {relative}")
    if not any(name.startswith("tests/feature/") for name in actual_files):
        errors.append("feature tests are missing")
    if not any(name.startswith("tests/regression/") for name in actual_files):
        errors.append("regression tests are missing")

    metadata: dict[str, Any] = {}
    if "task.toml" in actual_files:
        try:
            metadata = tomllib.loads(actual_files["task.toml"].read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"task.toml is invalid: {exc}")

    return {
        "valid": not errors,
        "errors": errors,
        "task_id": metadata.get("task_id"),
        "artifact_count": len(actual_files),
        "manifest_entries": len(expected),
    }

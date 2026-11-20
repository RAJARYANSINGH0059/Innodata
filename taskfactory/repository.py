from __future__ import annotations

import hashlib
import os
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .models import RepositorySnapshot

_EXCLUDED_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "env", "node_modules",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist",
    "build", "coverage", ".next", ".tox", "target", ".pytest_cache",
}
_EXTENSIONS = {
    ".py": "Python", ".pyi": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".mjs": "JavaScript", ".cjs": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".java": "Java", ".kt": "Kotlin", ".go": "Go", ".rs": "Rust", ".rb": "Ruby",
    ".php": "PHP", ".cs": "C#", ".cpp": "C++", ".cc": "C++", ".c": "C",
    ".h": "C/C++", ".hpp": "C++", ".swift": "Swift", ".scala": "Scala",
    ".sh": "Shell", ".sql": "SQL", ".html": "HTML", ".css": "CSS",
}
_MARKERS = {
    "pyproject.toml": "Python project (pyproject.toml)",
    "setup.py": "Python project (setup.py)",
    "requirements.txt": "Python dependencies (requirements.txt)",
    "Pipfile": "Python project (Pipfile)",
    "package.json": "JavaScript/TypeScript project (package.json)",
    "pnpm-lock.yaml": "pnpm workspace/lockfile",
    "yarn.lock": "Yarn lockfile",
    "package-lock.json": "npm lockfile",
    "Cargo.toml": "Rust project (Cargo.toml)",
    "go.mod": "Go module",
    "pom.xml": "Maven project",
    "build.gradle": "Gradle project",
    "build.gradle.kts": "Gradle Kotlin project",
    "composer.json": "PHP Composer project",
    "Gemfile": "Ruby project (Gemfile)",
    "*.sln": ".NET solution",
    "*.csproj": ".NET project",
    "Makefile": "Make build configuration",
    "Dockerfile": "Docker build configuration",
}


def _git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args], cwd=root, text=True, capture_output=True,
            check=True, timeout=10,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def _iter_files(root: Path):
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in _EXCLUDED_DIRS and not d.endswith((".egg-info", ".dist-info")))
        current_path = Path(current)
        for filename in sorted(files):
            path = current_path / filename
            if path.is_symlink() or not path.is_file():
                continue
            yield path


def _tree_digest(root: Path) -> tuple[str, int, Counter[str]]:
    hasher = hashlib.sha256()
    counts: Counter[str] = Counter()
    file_count = 0
    for path in _iter_files(root):
        rel = path.relative_to(root).as_posix()
        ext = path.suffix.lower()
        if ext in _EXTENSIONS:
            counts[_EXTENSIONS[ext]] += 1
        try:
            data = path.read_bytes()
        except OSError as exc:
            # Fail closed: a partial hash must never be presented as complete.
            raise RuntimeError(f"Unable to hash repository file {rel}: {exc}") from exc
        hasher.update(rel.encode("utf-8", errors="surrogateescape"))
        hasher.update(b"\0")
        hasher.update(str(len(data)).encode("ascii"))
        hasher.update(b"\0")
        hasher.update(data)
        hasher.update(b"\0")
        file_count += 1
    return hasher.hexdigest(), file_count, counts


def _project_markers(root: Path) -> list[str]:
    found: list[str] = []
    for name, label in _MARKERS.items():
        if "*" in name:
            suffix = name.replace("*", "")
            matches = sorted(p.name for p in root.rglob(f"*{suffix}") if p.is_file() and not any(x in _EXCLUDED_DIRS for x in p.parts))
            if matches:
                found.append(f"{label}: {', '.join(matches[:10])}")
        elif (root / name).is_file():
            found.append(label)
    return found


def inspect_repository(path: str | Path) -> RepositorySnapshot:
    root = Path(path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Repository path must be an existing directory: {root}")

    top = _git(root, "rev-parse", "--show-toplevel")
    is_git = top is not None
    git_root = Path(top).resolve() if top else root
    commit = _git(git_root, "rev-parse", "HEAD") if is_git else None
    git_tree = _git(git_root, "rev-parse", "HEAD^{tree}") if is_git else None
    remote = _git(git_root, "remote", "get-url", "origin") if is_git else None
    status = _git(git_root, "status", "--porcelain=v1", "--untracked-files=all") if is_git else None
    digest, count, languages = _tree_digest(root)

    return RepositorySnapshot(
        root=str(root),
        remote_url=remote,
        commit=commit,
        git_tree=git_tree,
        working_tree_digest=digest,
        is_git_repository=is_git,
        is_dirty=bool(status) if is_git else None,
        languages=dict(sorted(languages.items(), key=lambda item: (-item[1], item[0]))),
        project_markers=_project_markers(root),
        file_count=count,
        captured_at_utc=datetime.now(timezone.utc).isoformat(),
    )

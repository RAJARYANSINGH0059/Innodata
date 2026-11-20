from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class PatchError(Exception):
    """Raised when a workspace, patch or file installation is unsafe or fails."""


def _git(args: list[str], cwd: str | Path | None) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k in {"PATH", "HOME", "SYSTEMROOT", "LANG"}}
    env["GIT_TERMINAL_PROMPT"] = "0"
    return subprocess.run(["git", *args], cwd=cwd, env=env, text=True,
                          capture_output=True, check=False, shell=False)


def _safe_rel(path: str) -> bool:
    if not path or path.startswith(("/", "\\")) or "\\" in path or ":" in path.split("/")[0]:
        return False
    parts = path.split("/")
    return ".." not in parts and ".git" not in parts


def validate_patch_text(text: str) -> list[str]:
    """Return the files a unified diff touches; raise PatchError on unsafe content."""
    touched: list[str] = []
    for line in text.splitlines():
        if line.startswith(("--- ", "+++ ")):
            target = line[4:].split("\t")[0].strip()
            if target == "/dev/null":
                continue
            if target.startswith(("a/", "b/")):
                target = target[2:]
            if not _safe_rel(target):
                raise PatchError(f"unsafe path in patch: {target!r}")
            touched.append(target)
        elif line.startswith(("new file mode 120000", "new mode 120000", "old mode 120000")):
            raise PatchError("patch creates or modifies a symlink")
        elif line.startswith(("rename to ", "rename from ", "copy to ", "copy from ")):
            target = line.split(" ", 2)[2]
            if not _safe_rel(target):
                raise PatchError(f"unsafe path in patch: {target!r}")
            touched.append(target)
        elif line.startswith("GIT binary patch"):
            raise PatchError("binary patches are not accepted")
    if not touched:
        raise PatchError("patch touches no files")
    return sorted(set(touched))


def make_workspace(repo: str | Path, commit: str, dest: str | Path) -> str:
    """Create a pristine detached checkout of `commit` in a new directory; return full SHA."""
    dest = Path(dest)
    if dest.exists():
        raise PatchError(f"workspace already exists: {dest}")
    r = _git(["-c", "core.autocrlf=false", "-c", "core.eol=lf", "clone", "-q", "--no-checkout", "--no-hardlinks", str(repo), str(dest)], None)
    if r.returncode:
        raise PatchError(f"clone failed: {r.stderr.strip()}")
    _git(["config", "core.autocrlf", "false"], dest)  # keep LF so patches/hashes are identical on every OS
    r = _git(["checkout", "-q", "--detach", commit], dest)
    if r.returncode:
        raise PatchError(f"checkout {commit} failed: {r.stderr.strip()}")
    head = _git(["rev-parse", "HEAD"], dest).stdout.strip()
    if not head.startswith(commit):
        raise PatchError(f"HEAD {head} does not match requested {commit}")
    if _git(["status", "--porcelain"], dest).stdout.strip():
        raise PatchError("workspace is not clean after checkout")
    return head


def apply_patch(workspace: str | Path, patch: str | Path, reverse: bool = False) -> list[str]:
    """Check then apply (or reverse-apply) a patch. Returns touched files."""
    patch = Path(patch).resolve()
    touched = validate_patch_text(patch.read_text(encoding="utf-8"))
    flags = ["--whitespace=nowarn"] + (["-R"] if reverse else [])
    chk = _git(["apply", "--check", *flags, str(patch)], workspace)
    if chk.returncode:
        raise PatchError(f"patch does not {'reverse-' if reverse else ''}apply: {chk.stderr.strip()}")
    res = _git(["apply", *flags, str(patch)], workspace)
    if res.returncode:
        raise PatchError(f"git apply failed: {res.stderr.strip()}")
    return touched


def install_files(workspace: str | Path, src_dir: str | Path, dest_rel: str) -> list[str]:
    """Copy regular files from src_dir into workspace/dest_rel; symlinks and escapes are rejected."""
    ws = Path(workspace).resolve()
    src = Path(src_dir)
    if not _safe_rel(dest_rel):
        raise PatchError(f"unsafe destination: {dest_rel!r}")
    dest = (ws / dest_rel).resolve()
    if not dest.is_relative_to(ws):
        raise PatchError("destination escapes workspace")
    copied: list[str] = []
    for f in sorted(src.rglob("*")):
        if f.is_symlink():
            raise PatchError(f"symlink in task files: {f}")
        if f.is_file() and "__pycache__" not in f.parts:
            target = dest / f.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, target)
            copied.append(str(target.relative_to(ws)))
    return copied

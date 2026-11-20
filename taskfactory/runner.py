from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from .models import CommandResult, CommandSpec


def run_command(spec: CommandSpec, repository_root: str | Path) -> CommandResult:
    """Run an explicitly configured argv without shell interpolation.

    This is not a sandbox. Execute only trusted commands in a disposable,
    resource-limited environment when handling untrusted repositories.
    """
    root = Path(repository_root).resolve()
    cwd = (root / spec.cwd).resolve()
    if not cwd.is_relative_to(root):
        raise ValueError("Command working directory must remain inside repository root")
    if not spec.argv or any(not isinstance(arg, str) for arg in spec.argv):
        raise ValueError("Command argv must be a non-empty list of strings")
    if spec.timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    if spec.inherit_environment:
        env = os.environ.copy()
    else:
        safe_keys = {"PATH", "SYSTEMROOT", "WINDIR", "LANG", "LC_ALL", "TEMP", "TMP", "TMPDIR"}
        env = {key: value for key, value in os.environ.items() if key in safe_keys}
    env.update(spec.env)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            spec.argv, cwd=cwd, env=env, text=True, capture_output=True,
            timeout=spec.timeout_seconds, check=False, shell=False,
        )
        return CommandResult(
            name=spec.name, argv=spec.argv, cwd=str(cwd),
            exit_code=completed.returncode, timed_out=False,
            duration_seconds=round(time.monotonic() - started, 6),
            stdout=completed.stdout, stderr=completed.stderr,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return CommandResult(
            name=spec.name, argv=spec.argv, cwd=str(cwd),
            exit_code=None, timed_out=True,
            duration_seconds=round(time.monotonic() - started, 6),
            stdout=stdout, stderr=stderr,
        )

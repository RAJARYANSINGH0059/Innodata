# SECURITY

## Threat model (current)
The factory executes **repository code and generated tests** (pytest) on the host. This is the main risk.
- `taskfactory.runner` uses `shell=False`, timeouts, a minimal environment and working-directory confinement. It is **not a sandbox**: executed code can read/write anything the user can, and use the network.
- Run untrusted repositories only in a disposable VM/container, or in GitHub Actions (ephemeral runners, `contents: read`, no secrets).
- Patches are screened before `git apply`: absolute paths, `..`, `.git` paths, symlink creation, binary patches and empty patches are rejected. Task test files are copied only as regular files (symlinks rejected).
- Each state is built in a fresh clone (`git clone --no-hardlinks`) so the upstream checkout is never modified; the demo asserts this (fixture tree stays clean).
- JUnit XML is read with the stdlib parser after a 50 MiB size cap; entity-expansion payloads are rejected by expat (tested).

## Static scan (2026-11-20)
- `bandit -r taskfactory scripts`: 0 high, 0 medium (1 medium XML finding mitigated + annotated), 17 low — all `subprocess` usage that is the product's purpose.
- `ruff --select E9,F`: clean. No secrets found by pattern grep. No third-party runtime dependencies (stdlib only).
- Dependency audit (pip-audit) and CodeQL: NOT RUN.

## Known gaps
No container isolation, no network egress control, no resource limits beyond timeouts, Windows path/line-ending handling untested.

## Reporting
Open a private security advisory on the GitHub repository (once published).

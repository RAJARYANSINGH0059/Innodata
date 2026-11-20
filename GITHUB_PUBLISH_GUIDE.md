# GITHUB_PUBLISH_GUIDE
Status: this session had **no GitHub write access** (`gh` unauthenticated; no write tool). Nothing has been pushed. CI is authored, not executed on GitHub.

## Licence decision (needed before publishing)
No `LICENSE` file exists on purpose. Decide, then add it:
1. Check the hackathon rules/portal for any IP or open-source requirement for submissions.
2. Common choices: **MIT** (simplest) or **Apache-2.0** (patent grant). Tasks derive from BSD-3 itsdangerous — keep `THIRD_PARTY_NOTICES.md`.
3. Update `license` in `pyproject.toml` to match.

## Option A — GitHub web UI (no Git needed)
1. github.com → New repository → name `innodata-coding-task-factory-2026` → **Public** (the portal asks for a public repo) → do not add README/licence → Create.
2. Unzip the checkpoint ZIP locally. On the empty repo page choose "uploading an existing file", drag the *contents* of `innodata-coding-task-factory-2026/` (including the hidden `.github` and `.gitignore` — enable "show hidden files"), commit to `main`.
3. Add the `LICENSE` file (Add file → Create new file → name it LICENSE → "Choose a license template").
4. Open the **Actions** tab → confirm the `ci` workflow ran; fix any failure before announcing results.

## Option B — Git in Windows PowerShell
```powershell
cd path\to\innodata-coding-task-factory-2026
git init -b main
git add -A
git commit -m "Coding Task Factory: validated tasks, evidence, CI"
git remote add origin https://github.com/<YOUR-USER>/innodata-coding-task-factory-2026.git
git push -u origin main
```
(Sign in via the browser prompt / Git Credential Manager. Never paste tokens into chat or files.)

## After the first CI run
- Tag only after CI is green: `git tag v0.2.0 && git push origin v0.2.0`, then create a Release and attach the ZIP + SHA256SUMS.
- Windows: the demo has **not** been run on Windows. If `git apply` fails there, set `git config core.autocrlf false` and re-clone.
- Portal submission also needs: demo video link and the **mandatory organiser PPT template** (not yet received).
`publish.ps1`: intentionally not provided (untestable here).

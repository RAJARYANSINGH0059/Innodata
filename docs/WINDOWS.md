# Running the demo on Windows (PowerShell)

Status: **UNTESTED on Windows by the author.** Line endings are forced to LF in every clone and `.gitattributes` pins LF, and a test simulates Git-for-Windows' `autocrlf=true` — but nobody has run the demo on Windows yet. Please report the outcome (see the last section).

## 1. One-time setup
```powershell
python --version      # needs 3.11 or newer; install from python.org (tick "Add python.exe to PATH") if missing
git --version         # install Git for Windows if missing
```

## 2. Get the code (LF line endings matter — keep the flag)
```powershell
cd $HOME
git clone -c core.autocrlf=false https://github.com/RAJARYANSINGH0059/Innodata.git
cd Innodata
```

## 3. Install and run
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # if blocked: Set-ExecutionPolicy -Scope Process Bypass, then retry
python -m pip install -e ".[dev]"
python -m pytest -q tests             # ~1 min; expect: 50 passed
python scripts/demo.py                # ~4-6 min; clones itsdangerous itself; expect: OVERALL: PASS
```
Expected last lines of the demo:
```
itsdangerous-decompress-limit-002   PASS  8 killed / 0 survived / 5 equiv   2 accepted / 0 rejected   PASS
itsdangerous-leeway-001             PASS  12 killed / 0 survived / 0 equiv  2 accepted / 0 rejected   PASS
itsdangerous-needs-resign-003       PASS  10 killed / 0 survived / 1 equiv  2 accepted / 0 rejected   PASS
OVERALL: PASS   evidence in ...\demo_out
```

## 4. If something fails — send me this
```powershell
python scripts/demo.py *> demo_log.txt
Get-Content demo_log.txt -Tail 40
```
Paste the last 40 lines (no secrets are printed). Likely causes: Python < 3.11; antivirus blocking `git`/`python` subprocesses; a corporate proxy blocking `github.com`; antivirus quarantining test files; long-path limits (`git config --global core.longpaths true`).

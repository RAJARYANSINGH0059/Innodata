# PROJECT_STATE — as of 2026-11-20 (M0 complete)
## Environment (actually probed)
| Capability | Status |
|---|---|
| File read/create, shell (Python 3.13, Node 22, git 2.43) | AVAILABLE |
| pip / PyPI | AVAILABLE |
| git over HTTPS to github.com (clone, ls-remote) | AVAILABLE |
| codeload.github.com zip download | UNAVAILABLE (403 via proxy) |
| GitHub write (push/PR/release) | UNAVAILABLE — `gh` token failed login; no write tool tested. NOT TESTED beyond auth status |
| Docker | NOT TESTED |
## Inputs
- Prototype ZIP sha256 a2ae8479…86aa4c = matches upload manifest. No traversal/abs/symlink members. PASSED (inspect)
- Official explainer .srt: **PRESENT, fully reviewed** (1077 cues, 0:00–47:00; first 2000 lines via Read, remainder via compacted text) → EXPLAINER_EVIDENCE.md, REQUIREMENTS_TRACEABILITY.md. PPT template: **NOT PRESENT**. Organiser handover: **NOT PRESENT**. (No claim made to have read them.)
- Execution record's R-11..R-14 now speaker-confirmed (three-state matrix, task.toml/instruction.md/solution diff/tests, PPT template mandatory, portal fields) — but organiser schema/matrix/repo list still NOT provided.
## Baselines reproduced
- Prototype: `pytest` 24 passed; `unittest discover -s tests` 24 OK. 
- Fixture pallets/itsdangerous @ 672971d66a2ef9f85151e53283113f33d642dabd (tree ef4287f8…): clean tree, BSD-3 LICENSE.txt, 297 passed (needs `freezegun`, a dev dep not in default install). Status: INSPECTED, DOWNLOADED, BASELINE_EXECUTED. TASK_GENERATED/TASK_VALIDATED: not started.
## Prototype scope (unchanged, verified by reading README)
Fingerprinting, safe runner (no sandbox), JUnit parsing, three-state evaluator, package builder. NOT yet: patch apply, discovery, test authoring, mutation, variation, orchestration.
## Defects/risks
- D-001 itsdangerous baseline needs undeclared dev dep `freezegun` → adapter must install/declare test deps explicitly (setup failure ≠ valid failure).
- Runner is not a sandbox; executing generated patches needs isolation (GitHub Actions runner / container).
- Public-repo contamination: itsdangerous is public & likely in model training data.
## Next milestone: M1/M2 bridge — see NEXT_SESSION.md

## Update after SRT
Key deltas: team size 1–4; bug-fix mentioned by speaker (unwritten); 3 organiser repos not yet named/format TBD; security-task policy TBD; deadline 6 Dec. Template still absent.

## M1+M2 status (2026-11-20)
- NEW: taskfactory/patching.py (safe workspace/patch/apply/install), orchestrate.py (State A/B/C + repeat stability + import-origin + A≡C tree check), mutation.py, CLI `validate` and `mutate`; tests/test_orchestrate.py. Factory tests: 35 PASSED.
- NEW task: tasks/itsdangerous-leeway-001 (feature: clock-skew `leeway` for TimestampSigner/TimedSerializer). TASK_GENERATED + TASK_VALIDATED (3-state PASS) for ONE task. Variation (≥2 tasks), reconstruction check, 2nd repo, CI: NOT DONE.
- Task is hand/AI-authored in-session; discovery/requirements generation not automated yet.
- Reproduce: `python -m taskfactory.cli validate tasks/itsdangerous-leeway-001 --repo <itsdangerous clone> --out evidence/x` (needs pytest, freezegun).
- Next: (1) task 2 with different behaviour (e.g. url_safe/serializer-level) for variation; (2) automate discovery+behavioural signature; (3) clean-room reconstruct from task dir + sha manifest; (4) GitHub Actions workflow + publish guide.

## M3 status (2026-11-20)
- NEW modules: variation.py, reconstruct.py (manifest + clean-room re-validation); mutation runner verifies equivalents. CLI: validate, mutate, variation, manifest, reconstruct. Factory tests: 41 PASSED.
- TASKS (both TASK_VALIDATED, reconstruct PASS, manifests written): itsdangerous-leeway-001; itsdangerous-decompress-limit-002. Variation: 0.061 DISTINCT (EXP-002).
- Still NOT done: 2nd repository (M4: sindresorhus/is TS or other), GitHub Actions CI + publish guide (M5), security/licence scan, automated discovery/requirement generation (tasks are hand/AI-authored in-session), model/prompt metadata in packages, organiser schema serializer, bug-fix task type, independent test author/reviewer.
- Discovery module ADDED (taskfactory/discovery.py, CLI `discover`): deterministic, anchored candidates; see V-027/V-028 for limits. Requirement/patch/test generation still manual/AI-in-session.
- Next: M4 portability — run the same orchestrator on a non-Python repo; requires a runner/adapter for JS/TS (node available: v22) and a decision on how `validate` invokes non-pytest runners (JUnit via vitest/jest reporter).

## M5 status (2026-11-20)
- Authored: .github/workflows/ci.yml (actions pinned to SHAs resolved via git ls-remote; least-privilege), scripts/demo.py (RUN: PASS), README, SECURITY, CONTRIBUTING, REPRODUCIBILITY, THIRD_PARTY_NOTICES, GITHUB_PUBLISH_GUIDE, .gitignore, pyproject dev extras. 43 tests pass on py3.11/3.12/3.13.
- PUBLISHED: https://github.com/RAJARYANSINGH0059/Innodata (public) main@d7ea0bd; CI run 44672232036 all green (test 3.11/3.12/3.13 + demo).
- Still on user: licence decision (public repo currently has none); PPT template; demo video; Windows run.
- Next: M4 portability (second repo/stack) OR automate discovery/generation (biggest gap vs 'factory' claim) — recommend generation/discovery first since judges weigh a *factory*.

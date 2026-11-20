# CHANGELOG
- 2026-11-20 M0: added state/ledger files, evidence/baseline_itsdangerous.xml. No source changes to taskfactory/.
- 2026-11-20 SRT review: EXPLAINER_EVIDENCE.md, REQUIREMENTS_TRACEABILITY.md populated; state/ledger updated.
- M1: patching.py, orchestrate.py, mutation.py, CLI validate/mutate, tests/test_orchestrate.py (35 tests). M2: tasks/itsdangerous-leeway-001 + evidence. Fixes D-002, D-003, D-004.
- M3: task 002, variation.py, reconstruct.py, mutation equivalence verification, 41 tests, evidence/ for both tasks, docs/VARIATION_ADJUDICATION.md.
- M5: CI workflow, demo script, docs, security scan fixes (JUnit cap, pathsep), 43 tests, py3.11/3.12 verified.
- Discovery: taskfactory/discovery.py, `discover` CLI, tests/test_discovery.py, evidence/discovery-itsdangerous/. Published to GitHub (44bcdc4), CI green.
- Windows hardening: LF forced in clones, .gitattributes, docs/WINDOWS.md, CRLF regression test.

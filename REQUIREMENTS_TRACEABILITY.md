# REQUIREMENTS_TRACEABILITY (updated after SRT review; evidence IDs → EXPLAINER_EVIDENCE.md)
| ID | Requirement | Source | Engineering consequence | Status |
|---|---|---|---|---|
| R-01 | Reusable factory, not one task | E-06,E-21 | CLI over any repo | M0 foundation; unproven on 2 repos |
| R-02 | Req + reference diff + tests per task | E-07,E-15 | package: task.toml, instruction.md, solution/*.diff, tests/ | schema provisional; builder exists |
| R-03 | Multiple tasks per repo | E-07 | discovery→N tasks | 2 tasks validated on itsdangerous (hand/AI-authored); discovery not automated |
| R-04 | Three-state matrix A/B/C | E-09 | validation.py evaluator | 2 real runs PASS |
| R-05 | Tests prove solvability, shown live | E-08 | reproducible demo script | NOT STARTED |
| R-06 | Meaningful variation (rules/behaviour, not text) | E-13 | behavioural signature + pairwise audit | variation.py + EXP-002 + manual adjudication; 1 pair |
| R-07 | Repeatable; no hard-coding; disclose manual edits | E-12,E-14 | seeds, logs, manual-intervention field | partial |
| R-08 | AI-generated reference OK with proof | E-16 | model metadata + validation proof | NOT STARTED |
| R-09 | Bug-fix tasks | E-05 | support internally; competition-facing only after written confirm | OPEN |
| R-10 | Public GitHub repo, demo video, mandatory PPT template | E-03 | publish guide; template not in hand | BLOCKED (template, GitHub write) |
| R-11 | Security-related tasks | E-19 | avoid until policy given | OPEN |
| R-12 | Team 1–4 | E-02 | — | updated |

# Coding Task Factory — Innodata Frontier AI Hackathon 2026, Track 1

A **reusable pipeline** that turns a software repository + a feature requirement into a **proof-carrying task package** — requirement, reference patch, tests — and *earns* its validity by executing evidence, not by model confidence.

```
python -m pip install -e ".[dev]"
python scripts/demo.py            # ~4 min: clones itsdangerous at a pinned commit, re-validates every task
```

## What the factory proves for each task (all executed, all logged)
| Gate | Question | Evidence |
|---|---|---|
| **Three-state** | Do feature tests FAIL on the original repo, PASS with the reference patch, and FAIL again with it removed — *for assertion reasons, not setup errors*? | `validation_report.json`, JUnit XML + logs per state/repeat |
| **Regression** | Does the upstream suite (297 tests for itsdangerous) stay green in every state? | per-state baseline runs |
| **Repeatability** | Same result across 3 runs per state? | repeat-stability checks |
| **Isolation** | Is the code under test really imported from the state's own checkout? | import-origin probe; A≡C source-tree digest |
| **Oracle quality** | Do the tests reject plausible wrong implementations and accept other correct ones? | `mutation_report.json` (hand-written variants; equivalents verified, not trusted) |
| **Variation** | Are tasks different in behaviour, not just in names/constants? | `variation_report.md` (+ metric validated on a renamed clone) |
| **Reconstruction** | Does a clean copy + fresh clone reproduce the recorded result? | `MANIFEST.sha256`, `taskfactory reconstruct` |

## Tasks in this repository (pinned `pallets/itsdangerous@672971d`)
| Task | Behaviour | Feature tests failing in A/C |
|---|---|---|
| `itsdangerous-leeway-001` | clock-skew tolerance in timestamp verification (business rule, 3 entry points) | 16 |
| `itsdangerous-decompress-limit-002` | bounded streaming decompression (zip-bomb defence, memory bound, unsafe-load path) | 8 |
| `itsdangerous-needs-resign-003` | key-rotation introspection: classify valid tokens by which signer verified them (signature-only, no payload/age) — chosen from discovery candidate C004 | 12 |
Pairwise variation composites 0.049–0.068 → all DISTINCT.

## CLI
`taskfactory discover | validate | mutate | variation | manifest | reconstruct | inspect …` (see `--help`). Task folder layout: `task.toml`, `instruction.md`, `solution/solution.diff`, `tests/feature`, `tests/regression`, `mutants.json`, `MANIFEST.sha256`.

## Honest status
- **Works & tested:** the validation machinery (50 tests on Python 3.11/3.12/3.13) and three validated tasks.
- **Partly automated:** feature *discovery* (`taskfactory discover`: deterministic, evidence-anchored candidates; Python only; noisy). **Not automated yet:** requirement/patch/test *generation* — tasks here were authored interactively with an AI assistant (tests written before the patch, from the requirement only, but by the same author). The factory validates; it does not yet generate.
- **Not done:** second repository / non-Python stack, container sandbox, independent test author, organiser-specific schema (provisional layout follows the explainer's description), GitHub CI run, Windows/macOS runs.
- Full ledger: `VALIDATION_LEDGER.md`; defects found and fixed: `DEFECTS.md`; limits of each claim are listed beside the claim.

## Windows
See `docs/WINDOWS.md` (untested on Windows; LF line endings enforced).

## Safety
Executes repository code on the host — use a disposable VM/container or CI. See `SECURITY.md`. Licence: **not yet assigned** (until one is added, all rights are reserved by default) (see `GITHUB_PUBLISH_GUIDE.md`); upstream notices in `THIRD_PARTY_NOTICES.md`.

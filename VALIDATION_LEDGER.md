# VALIDATION_LEDGER
| ID | Claim | Method | Result | Status |
|---|---|---|---|---|
| V-001 | ZIP safe | python zipfile member scan (abs, `..`, symlink, `:`) | 0 suspicious / 20 members | PASSED |
| V-002 | ZIP checksum | sha256sum vs upload manifest | match | PASSED |
| V-003 | Prototype tests | `python3 -m pytest -q` in extracted dir (pytest 9.1.1, py3.13) | 24 passed, 0.12s | PASSED |
| V-004 | itsdangerous baseline | `pytest -q` @672971d, after `pip install -e . freezegun`; JUnit in evidence/ | 297 passed, 0.66s; first run errored at collection (missing freezegun) | PASSED (after dep fix) |
| V-005 | Explainer SRT reviewed | full read of 1077 cues; timestamped register written | 21 evidence items; speaker statements ≠ written rules | INSPECTED_ONLY |
| V-006 | GitHub write | `gh auth status` failed; nothing else tried | — | BLOCKED |
| V-007 | Three-state on a real task | no task yet | — | NOT_RUN |
| V-003b | README command `python -m unittest discover -s tests` | run from project root | 24 tests OK (note: with `python -I` it fails ImportError because package isn't installed — isolation artifact, not a defect) | PASSED |
| V-008 | Factory unit/integration tests | `pytest -q tests` (py3.13) | 35 passed incl. synthetic-repo 3-state, negative cases (always-pass tests, collection error, failing-on-reference, regression broken by patch, non-applying patch), patch safety (traversal/abs/.git/symlink/binary), mutation runner w/ relative out dir | PASSED |
| V-009 | Task `itsdangerous-leeway-001` State A/B/C | `taskfactory validate` on pinned 672971d; 3 repeats/state; JUnit+logs in evidence/itsdangerous-leeway-001/ | A: 16 feature tests fail (TypeError unexpected kwarg `leeway`), 4 regression pass, 297 baseline pass. B: all pass. C (patch reverse-applied): same 16 fail, tree digest == A. Import origin verified per state. Report PASS | PASSED |
| V-010 | Oracle adequacy (hand-written variants) | `taskfactory mutate`, 14 variants | 12 wrong → 12 KILLED, 0 survived (after adding test for M12); 2 alt-valid → 2 ACCEPTED | PASSED w/ limitations (see L-1..L-4) |
| V-011 | Run 1 of V-009 (before fix) | same | FAILED: reference_implements_requirement — test defect D-002 (kept in evidence/…_run1_FAILED_test_defect) | FAILED→fixed |
| V-012 | Bandit/license/security scan, clean-room reconstruction, 2nd task variation, 2nd repo, GitHub CI | — | — | NOT_RUN |
### Limitations of V-009/V-010
- L-1 Same model authored tests, patch and mutants in one session; tests were written before the patch from instruction.md only, but are NOT independently authored. Mutants were hand-written after seeing the patch.
- L-2 Test set changed after first mutation run (added unconditional-ValueError test after survivor M12); first run of the final set is the one recorded; earlier run kept for audit in git-less form only via this ledger.
- L-3 Variants are hand-crafted (14), not an operator-based mutation tool; no equivalent-mutant analysis needed/performed.
- L-4 State C is the exact reverse of the patch, so C ≡ A by construction (tree digest proves it). The matrix is satisfied but C adds no independent information for single-patch tasks.
- L-5 Feature tests fail in A/C via TypeError (kwarg absent), a signature-level failure, not a deeper behavioural assertion; this is inherent to adding a new parameter.
- L-6 Public repo/contamination: itsdangerous is public; `leeway` may resemble patterns in training data.
## M3 (2026-11-20)
| ID | Claim | Method | Result | Status |
|---|---|---|---|---|
| V-013 | Task 2 `itsdangerous-decompress-limit-002` State A/B/C | `taskfactory validate`, pinned 672971d, 3 repeats/state, JUnit+logs in evidence/itsdangerous-decompress-limit-002/ | PASS: A fails feature tests with real assertion failures (`DID NOT RAISE BadPayload`, wrong `loads_unsafe` result, AttributeError for missing attribute); B passes all; C == A (tree digest equal); 297 baseline pass in all states | PASSED |
| V-014 | Task 2 oracle adequacy | `taskfactory mutate`, 15 variants | 8 wrong KILLED, 0 SURVIVED; 5 EQUIVALENT (verified: tests do not catch them; classification made AFTER observation, justified in mutants.json); 2 alt-valid ACCEPTED (chunked streaming loop; ValueError wrapped to BadPayload); M13 (both redundant checks removed) KILLED | PASSED w/ limitations (L-1,L-3,L-7) |
| V-015 | Task 1 re-recorded on final files | validate+mutate rerun after task.toml gained [variation] | PASS; 12 KILLED, 2 ACCEPTED, 0 SURVIVED | PASSED |
| V-016 | Variation metric | `taskfactory variation`; unit tests incl. superficial clone (rename `leeway`→`skew_tolerance`) | real pair composite 0.061 DISTINCT (0 shared files/symbols/declared dims); renamed clone 0.947 TOO_SIMILAR; identical = 1.0 | PASSED (heuristic; manual adjudication in docs/VARIATION_ADJUDICATION.md) |
| V-017 | Clean-room reconstruction | `taskfactory reconstruct` for both tasks: verify MANIFEST.sha256, copy to fresh dir, fresh clone at pinned commit, re-validate, compare status/commit/tree digests/patch hash/failing tests to recorded evidence | both PASS (all 5 comparisons true); unit test: tampering detected (modified/missing/unlisted) | PASSED |
| V-018 | Factory test suite | `pytest -q tests` | 41 passed | PASSED |
| V-019 | Second repo, GitHub CI, security/licence scan, bug-fix task type, model-assisted generation metadata | — | — | NOT_RUN |
- L-7 Task-2 equivalents were classified post hoc (after seeing survivors). Two of them (M10, M12) are weak mutant designs rather than provably equivalent; M10 truncation could in principle yield valid JSON for exotic payloads — not tested.
- L-8 Both tasks were chosen and authored by the same agent in one session on the same small repo; they share a repository, test style (freezegun/pytest) and author, so "variation" is demonstrated across behaviour classes, not across codebases.

## M5 (2026-11-20)
| ID | Claim | Method | Result | Status |
|---|---|---|---|---|
| V-020 | One-command demo from fresh upstream clone | `python scripts/demo.py` (clone, per task: validate+mutate+reconstruct, then variation) | OVERALL PASS in 1m56s; both tasks PASS | PASSED (Linux/py3.13) |
| V-021 | Python matrix | venvs `pip install -e .[dev]`; ruff + `pytest -q tests` | 3.11: 43 passed; 3.12: 43 passed; 3.13: 43 passed (see V-022) | PASSED local; GitHub Actions NOT_RUN |
| V-022 | Static scan | bandit -r (high/medium gate `-ll`), ruff E9,F, secret grep | bandit: 0 high, 0 medium after fixing JUnit XML (size cap + entity-bomb test), 17 low (subprocess). ruff clean (3 unused imports fixed). No secrets | PASSED; pip-audit/CodeQL NOT_RUN |
| V-023 | Windows/macOS | — | os.pathsep fix applied but never executed | NOT_RUN |
| V-024 | GitHub publish | user created empty repo; session attached with push access; `git push -u origin main` | https://github.com/RAJARYANSINGH0059/Innodata (public), `main` @ d7ea0bd; `git ls-remote` head == local HEAD | PASSED |
| V-025 | GitHub Actions CI | workflow `ci` run 44672232036 on d7ea0bd | test (3.11), test (3.12), test (3.13), demo: all `success` (demo re-validated both tasks from a fresh upstream clone on the runner) | PASSED |
| V-026 | Release / tag | not created | — | NOT_RUN |
## Discovery (2026-11-20)
| ID | Claim | Method | Result | Status |
|---|---|---|---|---|
| V-027 | `taskfactory discover` finds evidence-anchored candidates | AST heuristics (5 kinds) run on pinned itsdangerous@672971d; evidence/discovery-itsdangerous/ | 14 raw / 13 selected. C001 `timed.py:148 if age < 0` and C002 `url_safe.py:46 zlib.decompress` rank first in their kinds = the anchors of tasks 001/002; C007 `validate` option-threading = leeway call site. 5 `untested-public-api` and C003–C006 `option-threading` are weak/noisy | PASSED (unit tests: 5 tests incl. negatives + determinism) |
| V-028 | Discovery quality | — | Heuristics were written AFTER tasks 001/002 were authored; the hit on both is a recall sanity check, NOT an evaluation. Precision judged by the author: ~3 of 13 strong. Only Python; not run on a second repo | INSPECTED_ONLY |
| V-029 | CRLF robustness | test sets HOME/.gitconfig autocrlf=true; red without fix, green with fix | PASSED (simulated) | Real Windows run: NOT_RUN |
| V-030 | CI on discovery commit | run 44672888536 on 02b2be5 | test 3.11/3.12/3.13 + demo: success | PASSED |

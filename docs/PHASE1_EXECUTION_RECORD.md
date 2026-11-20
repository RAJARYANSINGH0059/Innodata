# Phase 1 execution record — Innodata Frontier AI Hackathon 2026, Track 1

**Captured:** 2026-11-19  
**Prototype version:** 0.1.0  
**Operating mode:** Phase 1, as explicitly requested  
**Release status:** NOT READY — foundation only

## 1. Evidence boundary

This record distinguishes official public facts, user-supplied operating assumptions, local execution evidence, and unresolved information. No Stage 2 compatibility is claimed.

### Official public source checks

| Source | Verified information | Status |
|---|---|---|
| Hack2skill event page | Track 1 asks for a reusable pipeline generating feature-development tasks, requirements, reference implementation, feature tests, regression checks, and starting-repository-version tagging | VERIFIED |
| Hack2skill event overview | Build phase 10 Nov–6 Dec 2026; submissions due 6 Dec; Grand Finale 20 Dec in New Delhi; team size 3–4; total prize pool ₹10 lakh | VERIFIED |
| Hack2skill evaluation/FAQ section | Weights: implementation 25%, validity 25%, meaningful variation 20%, originality 15%, practical impact/communication 15%; public FAQ says Claude Code/model API access and target repository/interface material are shared with registered participants | VERIFIED AS CURRENT PUBLIC PAGE TEXT |
| Official explainer subtitle | The prompt refers to an uploaded English auto-generated SRT and gives timestamp ranges. A conversation-file check, title/semantic search, and a complete seven-page recursive Library metadata scan did not surface an Innodata SRT | NOT YET AVAILABLE |
| Mandatory PPT template | Claimed in the user-provided master prompt as a webinar/portal requirement; no template file or authenticated portal resource was accessible in this execution | NOT YET VERIFIED |
| Three target repository choices | Claimed in user-provided master prompt based on explainer/resource handover; not stated in the publicly indexed event page content checked here | NOT YET VERIFIED |
| Final task interface and schema | No organiser handover was attached or made accessible in this Phase 1 execution | NOT YET AVAILABLE |

### Timing/resource discrepancy

The current public FAQ says organisers will share the repository, target models/rules, task interface and submission formats with registered participants. It does not say, in the public text inspected, that this occurs only after selection. This public statement must not override the team's actual resource receipt history; it does mean the exact phase boundary should be verified against team communications and the handover itself.

This project nevertheless remains in Phase 1 mode for this execution because that is the explicit operating instruction. No hidden target repository or task interface is assumed.

## 2. Source-to-requirement traceability — first pass

| ID | Source/evidence | Requirement interpretation | Engineering consequence | Evidence expected | Status |
|---|---|---|---|---|---|
| R-01 | Official Track 1 problem statement | Factory, not one generated task, is the product | CLI/pipeline accepts a repository input and runs repeatably | Same pipeline runs on more than one repository | VERIFIED |
| R-02 | Official Track 1 problem statement | Each task is a feature-development task with clear requirements, reference implementation and tests | Internal task contract separates spec, patch and tests | Packaged tasks and execution logs | VERIFIED |
| R-03 | Official Track 1 problem statement | Feature tests and existing-behaviour regression checks are both required | Separate test suites and baseline recording | Test outcomes across task states | VERIFIED |
| R-04 | Official Track 1 problem statement | Task must be tied to starting repository version | Commit/tree/content digest in metadata | Reconstructed pristine starting snapshot | VERIFIED |
| R-05 | Official scoring: 25% implementation | A repeatable end-to-end implementation is central | Build pipeline before UI/presentation work | Clean repeated runs | VERIFIED |
| R-06 | Official scoring: 25% validity | Reference code and tests must demonstrate solvability and behaviour | Executable validation and independent test audit | Three-state, negative and regression evidence | VERIFIED |
| R-07 | Official scoring: 20% variation | Different tasks must differ in behaviour, rules or interactions | Behavioural signature and pairwise audit | Distinct patches/acceptance criteria/tests | VERIFIED |
| R-08 | Official scoring: 15% originality | Engineering decisions and checkpoints must be defensible | Compare architectures and record design decisions | ADRs and measured trade-offs | VERIFIED |
| R-09 | Official FAQ | Manual fixes are allowed only with transparency | Store generation/correction history; rerun affected checks | Change log plus revalidation | VERIFIED |
| R-10 | Official FAQ | API keys/secrets must not be present in submission | Secret scanning and redacted logs | Clean repository scan | VERIFIED |
| R-11 | User-provided prompt / reported explainer | Three-state original/reference/removed check is expected | Dedicated validation evaluator | State A/B/C results and logs | NEEDS SRT CONFIRMATION |
| R-12 | User-provided prompt / reported explainer | TOML metadata, Markdown instructions, solution patch and tests are a provisional package structure | Internal package serializer must remain adaptable | Provisional serializer plus Stage 2 schema adapter | NEEDS SRT CONFIRMATION |
| R-13 | User-provided prompt / reported explainer | PPT template and video/GitHub links are part of prototype submission | Submission checklist and deck/video prep | Actual portal fields/template | NEEDS PORTAL/SRT CONFIRMATION |
| R-14 | Public FAQ | Organiser resources are distributed to registered participants | Maintain receipt inventory; do not assume absent resources | Resource inventory with file hashes | CHECK TEAM HANDOVER |

## 3. Benchmark research — implications for this factory

### SWE-bench (2023)

The original benchmark introduced 2,294 real GitHub issue-resolution problems from 12 Python repositories. Its value is repository-grounded work that requires coordinated code changes, not isolated completion snippets. However, its issue/PR-derived bug-resolution framing is not identical to Track 1's current written emphasis on generating new feature-development tasks.

Primary paper: https://arxiv.org/abs/2310.06770

### SWE-bench Verified (2024; OpenAI audit, 23 February 2026)

OpenAI reported that in a review of 138 difficult tasks, 59.4% had material test-design and/or task-description problems that made functionally correct solutions fail or made tasks unreasonably difficult. The review also identified training-data contamination and environment dependence. Epoch AI's September 2026 review describes the audited subset as 27.6% of the 500-task set and classifies the benchmark as flawed under its rubric.

Primary audit: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
Independent review: https://epoch.ai/benchmarks/swe-bench-verified/review

### SWE-bench Pro (OpenAI audit, 8 July 2026)

OpenAI's analysis pipeline flagged 200 of 731 public tasks (27.4%); human annotation identified 249 (34.1%). The paper's summary estimates approximately 30% broken tasks. Main categories: overly strict tests, underspecified prompts, low-coverage tests, and misleading prompts.

Primary audit: https://openai.com/index/separating-signal-from-noise-coding-evaluations/

### SWE-bench Pro V2 (22 September 2026)

The refreshed public split contains 642 tasks across 11 repositories. The release dropped 89 tasks found invalid; 69 tasks had instruction/test contradictions whose text was corrected after blind expert solving. The evaluation protocol restricts agent network access, grades patches on pristine images, and applies a two-sided gate: reference patch passes; empty patch fails.

Official release: https://labs.scale.com/blog/swe-bench-pro-v2
Task/leaderboard: https://labs.scale.com/leaderboard/swe_bench_pro_public_v2

**Novelty consequence:** the reference-patch-pass/empty-patch-fail check is a recognised prior practice and cannot honestly be advertised as novel on its own. Our proposed differentiation must be a wider auditable chain: acceptance-criteria traceability, independent test authorship, test-outcome classification, plausible alternate valid implementations, targeted requirement mutations, regression preservation, version/environment integrity, behavioural variation evidence and reproducible task reconstruction.

### LiveCodeBench (2024)

LiveCodeBench continuously collects contest problems by publication date and evaluates several code capabilities (including generation, execution, self-repair and test-output prediction). It informs freshness and contamination controls but does not directly solve repository-level feature-task synthesis.

Paper: https://arxiv.org/abs/2403.07974
Implementation: https://github.com/LiveCodeBench/LiveCodeBench

## 4. Competing architectures

Ratings below are qualitative design hypotheses, not measured benchmark results.

| Architecture | Strength | Principal failure mode | Assessment |
|---|---|---|---|
| A. Prompt-only multi-agent generation | Fast to prototype; can create requirements, patches and tests | Correlated hallucinations; same model family can invent and approve the same defect; weak repository grounding | Reject as core architecture; use models only as components |
| B. Historical issue/PR inversion | Real code context, concrete diffs, existing tests and commit history | Leaks the solution; often reproduces bug-fix tasks rather than novel features; duplicates public history; may inherit historical test defects | Use history as evidence and candidate source, not sole generator |
| C. Static-analysis / AST / dependency-graph synthesis | Deterministic repository grounding; identifies APIs, call paths, extension points and test gaps | Structural facts do not supply business intent or independently valid acceptance criteria | Use as discovery/grounding layer |
| D. Test-oracle-first / mutation-guided generation | Optimises discriminative tests and can reveal weak coverage | Can overfit a narrow test oracle or produce tests for behaviours not required; mutations may be equivalent | Use as an adversarial validation layer, not the only source of tasks |
| E. Specification-first generation with one model producing patch and tests | Clear separation of contract and code; relatively simple | Shared-context coupling: tests can mirror the reference patch's assumptions | Better than prompt-only, but not sufficient alone |
| F. Repository-grounded hybrid with independent evidence gates | Combines deterministic context, explicit contract, separate implementation/test paths and executable gates | More integration work; requires test-framework adapters and controlled execution | **Selected for Phase 1 prototype** |

### Selected design: repository-grounded hybrid, evidence-carrying outputs

1. Deterministic intake: snapshot repository, commit/tree digest, language/framework markers, directory map, tests/build instructions and baseline health.
2. Grounded discovery: combine AST/symbol/dependency/test-coverage facts with selected documentation and history. Candidates must cite concrete extension points and affected modules.
3. Contract-first task drafting: produce a structured requirement with observable acceptance conditions, inputs/outputs, edge cases, error behaviour, invariants, explicit non-goals and repository conventions.
4. Independent requirement review: check contradictions, underspecification, scope and testability before implementation generation.
5. Reference implementation: generated in an isolated worktree from the recorded base commit; patch saved separately.
6. Independent test design: a separate context/agent or deterministic test-template process sees the task contract and repository, but not the reference patch while authoring its initial tests.
7. Evidence gates: baseline, reference, removed-patch, regression, negative/mutation, alternate-valid-implementation and repeatability checks.
8. Behavioural diversity check: use API/interface deltas, rules, state transitions, data relationships, test cases and changed dependency/module graph; embeddings may assist review but cannot decide acceptance alone.
9. Versioned package and evidence manifest: immutable hashes for requirements, patch, tests, logs, environment and generation/correction history.
10. Release policy: reject on critical validity failure; do not average away failed gates with a high composite score.

## 5. Validation design decisions

### Three-state semantics

For feature-development tasks:

- **A — Original:** baseline suite recorded; existing tests should pass subject to disclosed pre-existing failures; task-specific tests should show a classified behavioural failure.
- **B — Reference:** all task-specific tests pass; baseline/regression suite remains stable.
- **C — Removed:** reference patch is removed while task tests remain; task tests again show the expected behavioural failure; baseline results return to A.

A timeout, dependency failure, test-collection error or generic nonzero process exit is not acceptable evidence that a task test detected missing feature behaviour. A test-framework adapter must classify the failure as an assertion/behavioural failure and preserve the relevant test identity and traceback. This is stricter than checking only exit code 1.

For bug-fix tasks, if explicitly authorised later, a defect reproducer fails at A, passes at B, and fails again at C. General baseline tests must be interpreted separately; it is incorrect to demand that every original test pass at A when the reported defect is intentionally reproduced by one dedicated test.

### Independent test oracle

The test authoring path must be separated from reference patch generation. For high-value tasks, require at least one plausible alternate implementation produced without viewing the reference patch. The alternate implementation need not be used as the official gold patch; it is a fairness probe. It should satisfy the contract and pass behaviour-oriented tests. A failed alternate implementation is not automatically proof of an overly strict test; the implementation itself must first be reviewed against the contract.

### Mutation strategy

Use requirement-directed mutants (e.g., boundary off-by-one, skipped validation, wrong state transition, incorrect eligibility predicate, dropped error path) rather than relying only on raw mutation score. Record equivalent mutants and exclude them with reasons. The objective is to show that plausible incorrect behaviours are caught, not to maximise a percentage.

### Variation signature

For each task, record: business rule(s), public interface/API changes, state transitions, inputs/outputs, data model relationships, error cases, module boundaries, affected dependency edges and tests. Pairwise duplicate review should compare these signatures and actual patches; natural-language embeddings are only a candidate-screening feature.

## 6. Provisional package layout — internal only

```text
<task-id>/
  task.toml                  # provisional metadata, not organiser schema
  instructions.md            # contract and acceptance criteria
  solution/solution.patch    # patch relative to exact base commit
  tests/feature/              # task-specific tests
  tests/regression/           # existing or targeted regression suite
  evidence/
    repository.json
    baseline.json
    state-a-original.json
    state-b-reference.json
    state-c-removed.json
    traceability.json
    test-quality.json
    mutation-results.json
    alternate-implementation.json
    variation.json
    reproducibility.json
    manual-corrections.json
  manifest.sha256             # hashes of package artifacts
```

The normalized internal task model is distinct from its serializer. An organiser adapter will translate it to the actual TOML/Markdown/patch/tests format once the official schema is received. The final schema takes precedence.

## 7. Public repository candidates — metadata research only

| Repository | Language/stack | License | Observed default-branch commit | Candidate strengths | Risks / current status |
|---|---|---|---|---|---|
| https://github.com/pallets/itsdangerous | Python; pytest; pyproject/flit; typed package | BSD-3-Clause | `672971d66a2ef9f85151e53283113f33d642dabd` | Established library, clear public API, modules/tests/docs, relatively low runtime dependency burden | Timed tests require `freezegun`; security-sensitive domain; local full clone/test execution blocked by container DNS |
| https://github.com/sindresorhus/is | TypeScript/Node ESM; Node >=22; TypeScript build and Node test runner | MIT | `e9c026c611c1160eaad50da00be4e676b626018f` | Different language and package architecture, extensive type and runtime tests, clean API boundary | Tests require external dev dependencies including jsdom/rxjs/tempy/expect-type/zen-observable/xo; local clone/install blocked by container DNS |

GitHub connector inspection verified the public repository metadata, default branch tree, selected configuration/source/test file contents and licenses. The execution container could not resolve `github.com`, so a full local clone and baseline test run have **not** been completed. These are candidates, not yet accepted experiment repositories. Do not state that the factory has been tested end-to-end on either repository until a real local snapshot is obtained and executed.

## 8. Local prototype evidence (version 0.1.0)

Implemented under `taskfactory/`:

- Repository inspector: detects Git root/commit/tree, dirty status, project markers, language-extension counts and a working-tree content digest.
- Explicit command runner: argv execution with `shell=False`, timeout, working-directory containment check, and no ambient environment inheritance by default.
- Three-state evaluator: validates state order, baseline outcome stability, reference test pass, and original/removed behavioural failures.
- Test failure classification boundary: a nonzero exit is not counted as a behavioural failure unless a framework adapter explicitly marks `outcome_class="test_assertion_failure"`; timeouts, empty suites, skipped suites, mixed infrastructure failures and unclassified errors do not count as successful negative evidence.
- JUnit XML adapter: differentiates assertion failures, setup/collection errors, skipped tests, no tests collected, timeout and process/report mismatch.
- Provisional package builder/verifier: writes TOML metadata, Markdown instructions, a solution patch, separate feature/regression test files, JSON evidence and a SHA-256 manifest; rejects unsafe relative paths, non-empty output directories and bug-fix task packages in the Phase 1 release scope.

**Local unit test result:** 24 tests passed using both `pytest -q` and `python -m unittest discover -s tests -v` (24/24 in each runner during final verification). These are unit tests of the foundation and package-integrity code, not tests of generated tasks or external repositories.

**Local environment/snapshot:** Python 3.13.5; pytest 9.0.2; 19 project files; 13 Python source/test files; not a Git checkout; working-tree digest `54116eed30d36352eae76cc722e7ecc2c2e5277c394f278433941510446a9369`. Snapshot JSON was written outside the project directory to avoid changing the measured tree.

Command:

```bash
cd /mnt/data/innodata_phase1
PYTHONPATH=. python -m unittest discover -s tests -v
```

## 9. Ten-check validation ledger — current state

| # | Check | Method performed | Result |
|---:|---|---|---|
| 1 | Official requirement validation | Live official event page and FAQ checked | PASS for public Track 1 brief/weights; explainer-specific details pending SRT |
| 2 | Source/evidence validation | Primary OpenAI, Scale, GitHub and paper sources inspected | PASS for cited benchmark facts; additional research remains open |
| 3 | Repository compatibility | GitHub metadata/tree/source inspected for two candidate stacks | NEEDS MORE EVIDENCE — not cloned locally |
| 4 | Technical correctness | Unit tests for repository scanner, command runner, gate logic, JUnit classifier and package integrity | PASS for covered behaviours only |
| 5 | Empirical execution | 24 local unit tests executed with pytest and unittest | PASS for foundation; NOT YET AVAILABLE for generated tasks |
| 6 | Feature/regression validation | Gate evaluator has unit-level cases | NEEDS MORE EVIDENCE — no real generated feature patch |
| 7 | Negative/adversarial validation | Tests cover task test passing on original, baseline drift, timeout, mixed infra/assertion outcomes, empty/skipped tests, path traversal, tampering and wrong state order | PASS for these unit cases; not an exhaustive security audit |
| 8 | Test adequacy | No mutation campaign or alternate implementation yet | NOT YET AVAILABLE |
| 9 | Reproducibility | Unit suite run via pytest and unittest in same runtime; no clean-room build yet | NEEDS MORE EVIDENCE — clean-environment reconstruction pending |
| 10 | Independent reconstruction | No second independent implementation/reviewer execution | NOT YET AVAILABLE |

## 10. Open risks

1. The explainer SRT is unavailable in this active execution context; full timestamp/Q&A analysis is incomplete.
2. The official public page currently describes feature-development task generation; permitted inclusion of bug-fix tasks needs confirmation from the webinar or organiser.
3. The final target repository, exact task interface and package schema have not been inspected in this Phase 1 session.
4. Public repository candidates are not yet locally cloned or tested because outbound GitHub DNS resolution failed in the container.
5. The local gate evaluator requires language/test-framework adapters. It does not apply patches, construct worktrees, run a sandbox, or interpret raw framework output itself.
6. No model-generated requirements, reference patches, independent test suites, mutation experiments or variation benchmarks exist yet.
7. No official portal template was downloaded; the mandatory-deck claim remains to be cross-checked.
8. No external publication, GitHub push, submission or video upload has been performed.

## 11. Next execution backlog

### P0 — unblock evidence and repository experiments

- Obtain the exact SRT and build a timestamp-indexed explainer register.
- Inventory all actually received organiser resources and current portal fields.
- Obtain local public repository snapshots (or an approved archive) and record exact commit and license.
- Run pristine baseline builds/tests before generating any feature.

### P1 — convert the foundation into a working factory

- Add Python and TypeScript repository adapters; do not infer broad language support from file extensions alone.
- Add clean worktree creation, patch apply/reverse and immutable state capture.
- Add pytest and Node test-runner result adapters that distinguish assertion failures from collection/dependency/timeouts.
- Implement requirement schema and criteria-to-test traceability.
- Generate one feature task manually/with model assistance and record every intervention.
- Add an independent test authoring path and one reviewed alternate valid patch.
- Add requirement-directed mutants, regression checks and repeat-run verification.

### P2 — evidence and release

- Generate multiple behaviourally distinct task packages.
- Run pairwise behavioural variation audits.
- Harden internal package serializer and checksums; adapt to organiser schema only when received.
- Run at least two repositories with distinct stack characteristics.
- Produce reproducible reports and a demo based on actual execution.
- Check the official portal/template before any final Phase 1 submission.

## 12. Source links

- Official event: https://hack2skill.com/event/innodata/
- Official event criteria/FAQ section: https://hack2skill.com/event/innodata/?sectionid=6aee108b9be15aea67016065
- Innodata event page: https://innodata.com/events/innodata-hackathon-2026/
- SWE-bench paper: https://arxiv.org/abs/2310.06770
- SWE-bench Verified audit: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
- SWE-bench Pro audit: https://openai.com/index/separating-signal-from-noise-coding-evaluations/
- SWE-Bench Pro V2 announcement: https://labs.scale.com/blog/swe-bench-pro-v2
- LiveCodeBench paper: https://arxiv.org/abs/2403.07974
- LiveCodeBench source: https://github.com/LiveCodeBench/LiveCodeBench
- itsdangerous source: https://github.com/pallets/itsdangerous
- sindresorhus/is source: https://github.com/sindresorhus/is

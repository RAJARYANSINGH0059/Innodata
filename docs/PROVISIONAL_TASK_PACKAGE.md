# Provisional internal task package contract (not the organiser schema)

This is a normalized internal model for Phase 1. It is deliberately separated from serialization so the final official format can be adopted without changing the generator's core model.

## Required identity and provenance

- Stable task ID and schema version.
- Task kind (Phase 1 release scope: feature / feature extension; bug-fix is disabled pending confirmation).
- Repository URI, license, base commit, Git tree SHA, clean/dirty state and working-tree digest.
- Runtime, framework, dependency lock hash, execution image digest and supported platform.
- Generation model/API identifier, prompt version, configuration, seed where applicable, and timestamps.

## Requirement contract

- Title and concise user-facing problem statement.
- Context and reason for the change.
- Observable requirements with stable IDs (`REQ-001`, ...).
- Acceptance criteria with stable IDs (`AC-001`, ...), each linked to at least one requirement.
- Inputs, outputs, boundary values, invalid inputs, error conditions and state transitions.
- Public interfaces that may be added or changed.
- Existing behaviour and invariants that must remain unchanged.
- Explicit non-goals and out-of-scope areas.
- Affected modules and code-grounding references (file, symbol, relevant line or AST span).

## Reference and tests

- Reference patch relative to the exact starting commit.
- Separate feature and regression test suites.
- Test-to-acceptance-criterion traceability.
- Independent test authoring provenance, including what artifacts the test author could see.
- Expected test framework and exact invocation.
- Failure-classification adapter version.

## Validation evidence

- State A original, State B reference, State C removed observations.
- Baseline health and pre-existing failure inventory.
- Test outcome classification, test IDs, logs and exit codes.
- Requirement-directed mutation outcomes and equivalent-mutant exclusions.
- Alternate valid implementation review and results, where feasible.
- Regression comparison and repeated-run stability.
- Environment, package-lock and artifact checksums.

## Variation and release decision

- Behavioural taxonomy signature.
- Interface/module/dependency graph deltas.
- Pairwise overlap against tasks already generated for the same repository.
- Human/adversarial audit notes.
- Gate decisions, remediation attempts, final status and disclosed limitations.

## Manual interventions

Record each intervention as an append-only event containing timestamp, actor/tool, artifact hash before and after, exact change summary, reason, and the validations rerun. No silent edits.

from __future__ import annotations


from .models import (
    CheckStatus, GateCheck, StateObservation, TaskKind, ThreeStateReport,
)

_EXPECTED_STATES = ("original", "reference", "removed")


def _exit_vector(results) -> tuple[tuple[int | None, str | None], ...]:
    return tuple((None if r.timed_out else r.exit_code, r.outcome_class) for r in results)


def _all_pass(results) -> bool:
    return bool(results) and all(r.passed for r in results)


def _expected_test_failure(results) -> bool:
    # A nonzero process exit alone is insufficient: dependency and collection
    # failures must not masquerade as evidence of missing feature behaviour.
    allowed = {"test_assertion_failure", "tests_pass"}
    return (
        bool(results)
        and all(
            not r.timed_out
            and r.exit_code is not None
            and r.outcome_class in allowed
            for r in results
        )
        and any(r.outcome_class == "test_assertion_failure" for r in results)
    )


def _ambiguous_test_failure(results) -> bool:
    return any(
        r.exit_code not in (None, 0)
        and not r.timed_out
        and r.outcome_class != "test_assertion_failure"
        for r in results
    ) or any(r.timed_out for r in results)


def evaluate_three_state(
    task_kind: TaskKind,
    original: StateObservation,
    reference: StateObservation,
    removed: StateObservation,
) -> ThreeStateReport:
    """Evaluate the required original/reference/removed evidence pattern.

    Baseline suites must have identical pass/fail vectors across all states.
    A baseline already failing at State A is disclosed as a limitation rather
    than attributed to the generated task.
    """
    observations = (original, reference, removed)
    checks: list[GateCheck] = []

    shape_ok = tuple(o.state for o in observations) == _EXPECTED_STATES
    checks.append(GateCheck(
        check_id="three_state_order",
        status=CheckStatus.PASS if shape_ok else CheckStatus.FAILED,
        expected=str(_EXPECTED_STATES), actual=str(tuple(o.state for o in observations)),
    ))
    if not shape_ok:
        return ThreeStateReport(task_kind, CheckStatus.FAILED, checks,
                                "State observations are missing or incorrectly ordered.")

    baseline_vectors = [_exit_vector(o.baseline) for o in observations]
    baseline_same = baseline_vectors[0] == baseline_vectors[1] == baseline_vectors[2]
    baseline_checks_present = all(bool(o.baseline) for o in observations)
    baseline_all_green = all(_all_pass(o.baseline) for o in observations)
    baseline_has_timeout = any(r.timed_out for o in observations for r in o.baseline)
    baseline_status = CheckStatus.PASS if baseline_same and baseline_all_green else (
        CheckStatus.NEEDS_MORE_EVIDENCE if baseline_same and baseline_checks_present and baseline_has_timeout
        else CheckStatus.PASS_WITH_LIMITATIONS if baseline_same and baseline_checks_present
        else CheckStatus.FAILED
    )
    checks.append(GateCheck(
        check_id="baseline_regression_stability",
        status=baseline_status,
        expected="Baseline test exit-code vector is unchanged across all three states; ideally all pass.",
        actual=f"vectors={baseline_vectors}; all_green={baseline_all_green}",
        evidence={"baseline_vectors": [list(v) for v in baseline_vectors]},
        limitation=("Pre-existing baseline failures exist and remain unchanged. They must be listed in the task evidence."
                    if baseline_same and not baseline_all_green else None),
    ))

    task_tests_present = all(bool(o.task_tests) for o in observations)
    original_fails = _expected_test_failure(original.task_tests)
    reference_passes = _all_pass(reference.task_tests)
    removed_fails = _expected_test_failure(removed.task_tests)
    failure_states = (
        ("original_detects_missing_behaviour", original.task_tests, original_fails,
         "At least one task-specific test is classified as an assertion/behaviour failure on the original repository."),
        ("removed_patch_reveals_missing_behaviour", removed.task_tests, removed_fails,
         "At least one task-specific test is classified as an assertion/behaviour failure after patch removal."),
    )
    for check_id, results, observed, expected in failure_states:
        status = CheckStatus.PASS if observed and task_tests_present else (
            CheckStatus.NEEDS_MORE_EVIDENCE if _ambiguous_test_failure(results) and task_tests_present
            else CheckStatus.FAILED
        )
        checks.append(GateCheck(
            check_id=check_id, status=status, expected=expected,
            actual=f"task_test_outcomes={_exit_vector(results)}",
            limitation=("The test adapter has not established that the nonzero exit came from the expected behavioural assertion."
                        if status == CheckStatus.NEEDS_MORE_EVIDENCE else None),
        ))

    checks.append(GateCheck(
        check_id="reference_implements_requirement",
        status=CheckStatus.PASS if reference_passes and task_tests_present else CheckStatus.FAILED,
        expected="All task-specific tests pass with the reference implementation.",
        actual=f"task_test_outcomes={_exit_vector(reference.task_tests)}",
    ))

    if not task_tests_present:
        checks.append(GateCheck(
            check_id="task_test_presence", status=CheckStatus.FAILED,
            expected="At least one task-specific test command in every state.",
            actual="One or more task-specific test command lists are empty.",
        ))

    statuses = [c.status for c in checks]
    if CheckStatus.FAILED in statuses:
        final = CheckStatus.FAILED
        summary = "Three-state validation failed. Do not release this task package."
    elif CheckStatus.NEEDS_MORE_EVIDENCE in statuses:
        final = CheckStatus.NEEDS_MORE_EVIDENCE
        summary = "Three-state pattern is incomplete: a test outcome is ambiguous or a baseline command timed out."
    elif CheckStatus.PASS_WITH_LIMITATIONS in statuses:
        final = CheckStatus.PASS_WITH_LIMITATIONS
        summary = "Three-state pattern holds, but pre-existing baseline failures must be disclosed."
    else:
        final = CheckStatus.PASS
        summary = "Three-state pattern holds and the baseline remains green in all states."

    # The state semantics are shared by feature and bug-fix reproducer tests;
    # their expected behaviour must be described explicitly in the task contract.
    return ThreeStateReport(task_kind, final, checks, summary)

import unittest

from taskfactory.models import CheckStatus, CommandResult, StateObservation, TaskKind
from taskfactory.validation import evaluate_three_state


def result(name: str, exit_code: int) -> CommandResult:
    return CommandResult(name, ["test"], ".", exit_code, False, 0.01, "", "", "test_assertion_failure" if exit_code else None)


class ThreeStateTests(unittest.TestCase):
    def make_state(self, state, baseline_code=0, task_code=1):
        return StateObservation(state, [result("baseline", baseline_code)], [result("task", task_code)])

    def test_feature_three_state_passes(self):
        report = evaluate_three_state(
            TaskKind.FEATURE,
            self.make_state("original", task_code=1),
            self.make_state("reference", task_code=0),
            self.make_state("removed", task_code=1),
        )
        self.assertEqual(report.status, CheckStatus.PASS)

    def test_task_test_that_passes_on_original_is_rejected(self):
        report = evaluate_three_state(
            TaskKind.FEATURE,
            self.make_state("original", task_code=0),
            self.make_state("reference", task_code=0),
            self.make_state("removed", task_code=1),
        )
        self.assertEqual(report.status, CheckStatus.FAILED)

    def test_patch_that_breaks_baseline_is_rejected(self):
        report = evaluate_three_state(
            TaskKind.FEATURE,
            self.make_state("original", baseline_code=0, task_code=1),
            self.make_state("reference", baseline_code=1, task_code=0),
            self.make_state("removed", baseline_code=0, task_code=1),
        )
        self.assertEqual(report.status, CheckStatus.FAILED)

    def test_preexisting_baseline_failure_is_disclosed(self):
        report = evaluate_three_state(
            TaskKind.BUG_FIX,
            self.make_state("original", baseline_code=1, task_code=1),
            self.make_state("reference", baseline_code=1, task_code=0),
            self.make_state("removed", baseline_code=1, task_code=1),
        )
        self.assertEqual(report.status, CheckStatus.PASS_WITH_LIMITATIONS)

    def test_timeout_is_not_accepted_as_expected_feature_failure(self):
        timeout = CommandResult("task", ["test"], ".", None, True, 120.0, "", "timed out", "timeout")
        report = evaluate_three_state(
            TaskKind.FEATURE,
            StateObservation("original", [result("baseline", 0)], [timeout]),
            self.make_state("reference", task_code=0),
            self.make_state("removed", task_code=1),
        )
        self.assertEqual(report.status, CheckStatus.NEEDS_MORE_EVIDENCE)

    def test_baseline_timeout_requires_more_evidence(self):
        timeout = CommandResult("baseline", ["test"], ".", None, True, 120.0, "", "timed out", "timeout")
        report = evaluate_three_state(
            TaskKind.FEATURE,
            StateObservation("original", [timeout], [result("task", 1)]),
            StateObservation("reference", [timeout], [result("task", 0)]),
            StateObservation("removed", [timeout], [result("task", 1)]),
        )
        self.assertEqual(report.status, CheckStatus.NEEDS_MORE_EVIDENCE)

    def test_unclassified_nonzero_exit_requires_more_evidence(self):
        ambiguous = CommandResult("task", ["test"], ".", 2, False, 0.01, "", "collection error", "collection_error")
        report = evaluate_three_state(
            TaskKind.FEATURE,
            StateObservation("original", [result("baseline", 0)], [ambiguous]),
            self.make_state("reference", task_code=0),
            self.make_state("removed", task_code=1),
        )
        self.assertEqual(report.status, CheckStatus.NEEDS_MORE_EVIDENCE)

    def test_assertion_failure_plus_infrastructure_error_is_ambiguous(self):
        assertion = result("feature", 1)
        infrastructure = CommandResult("setup", ["test"], ".", 2, False, 0.01, "", "missing dependency", "test_error")
        report = evaluate_three_state(
            TaskKind.FEATURE,
            StateObservation("original", [result("baseline", 0)], [assertion, infrastructure]),
            self.make_state("reference", task_code=0),
            self.make_state("removed", task_code=1),
        )
        self.assertEqual(report.status, CheckStatus.NEEDS_MORE_EVIDENCE)

    def test_missing_state_order_fails_closed(self):
        report = evaluate_three_state(
            TaskKind.FEATURE,
            self.make_state("reference"), self.make_state("original"), self.make_state("removed"),
        )
        self.assertEqual(report.status, CheckStatus.FAILED)


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from taskfactory.models import CommandResult
from taskfactory.test_adapters import annotate_command_result, classify_junit_xml


class JUnitAdapterTests(unittest.TestCase):
    def write_report(self, directory, body):
        path = Path(directory) / "junit.xml"
        path.write_text(body, encoding="utf-8")
        return path

    def test_assertion_failure_classified_as_behaviour_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_report(tmp, '<testsuite tests="1" failures="1"><testcase classname="pkg.test" name="test_feature"><failure message="wrong value" type="AssertionError">assert 1 == 2</failure></testcase></testsuite>')
            kind, evidence = classify_junit_xml(path)
            self.assertEqual(kind, "test_assertion_failure")
            self.assertEqual(evidence["failures"][0]["test"], "pkg.test::test_feature")

    def test_collection_or_setup_error_is_not_assertion_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_report(tmp, '<testsuite tests="1" errors="1"><testcase classname="pkg.test" name="test_feature"><error message="missing dependency" type="ImportError">No module named x</error></testcase></testsuite>')
            kind, _ = classify_junit_xml(path)
            self.assertEqual(kind, "test_error")

    def test_empty_and_all_skipped_reports_are_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = self.write_report(tmp, '<testsuite tests="0"/>')
            self.assertEqual(classify_junit_xml(empty)[0], "no_tests_collected")
            skipped = self.write_report(tmp, '<testsuite tests="1" skipped="1"><testcase classname="pkg.test" name="skip"><skipped message="platform"/></testcase></testsuite>')
            self.assertEqual(classify_junit_xml(skipped)[0], "all_tests_skipped")

    def test_annotate_detects_process_report_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_report(tmp, '<testsuite tests="1"><testcase classname="pkg.test" name="ok"/></testsuite>')
            result = CommandResult("pytest", ["pytest"], ".", 1, False, 0.1, "", "")
            annotated, _ = annotate_command_result(result, path)
            self.assertEqual(annotated.outcome_class, "runner_process_error")
            self.assertFalse(annotated.passed)

    def test_zero_exit_with_missing_report_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = CommandResult("pytest", ["pytest"], ".", 0, False, 0.1, "", "")
            annotated, _ = annotate_command_result(result, Path(tmp) / "missing.xml")
            self.assertEqual(annotated.outcome_class, "report_process_mismatch")
            self.assertFalse(annotated.passed)


if __name__ == "__main__":
    unittest.main()

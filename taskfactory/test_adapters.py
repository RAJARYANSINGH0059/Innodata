from __future__ import annotations

from dataclasses import replace
from pathlib import Path
# JUnit reports are size-capped below and expat rejects entity-expansion payloads (see tests).
from xml.etree import ElementTree  # nosec B405

MAX_REPORT_BYTES = 50 * 1024 * 1024

from .models import CommandResult


def classify_junit_xml(path: str | Path) -> tuple[str, dict[str, object]]:
    """Classify a JUnit XML report without treating any nonzero exit as a test failure.

    The adapter deliberately distinguishes test-body failures from test errors,
    empty reports and all-skipped reports. Framework-specific details still
    require review; this is evidence parsing, not proof of requirement validity.
    """
    report = Path(path)
    if not report.is_file():
        return "missing_test_report", {"report_path": str(report)}

    if report.stat().st_size > MAX_REPORT_BYTES:
        return "invalid_test_report", {"report_path": str(report), "error": "report exceeds size cap"}

    try:
        root = ElementTree.parse(report).getroot()  # nosec B314
    except (ElementTree.ParseError, OSError) as exc:
        return "invalid_test_report", {"report_path": str(report), "error": str(exc)}

    cases = list(root.iter("testcase"))
    failures: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    for case in cases:
        identity = "::".join(part for part in (case.attrib.get("classname"), case.attrib.get("name")) if part)
        for element, bucket in (("failure", failures), ("error", errors), ("skipped", skipped)):
            for node in case.findall(element):
                bucket.append({
                    "test": identity,
                    "message": node.attrib.get("message", ""),
                    "type": node.attrib.get("type", ""),
                    "detail": (node.text or "")[:2000],
                })

    total = len(cases)
    executed = total - len(skipped)
    evidence = {
        "report_path": str(report),
        "testcases": total,
        "executed_testcases": executed,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
    }
    # Empty suites and all-skipped suites are distinct: neither establishes
    # that the expected feature behaviour was exercised.
    if total == 0:
        return "no_tests_collected", evidence
    if errors:
        return "test_error", evidence
    if failures:
        return "test_assertion_failure", evidence
    if executed == 0:
        return "all_tests_skipped", evidence
    return "tests_pass", evidence


def annotate_command_result(result: CommandResult, junit_path: str | Path) -> tuple[CommandResult, dict[str, object]]:
    """Attach a conservative framework classification to a captured command result."""
    if result.timed_out:
        return replace(result, outcome_class="timeout"), {"classification": "timeout"}

    classification, evidence = classify_junit_xml(junit_path)
    if result.exit_code == 0 and classification != "tests_pass":
        classification = "report_process_mismatch"
    elif result.exit_code != 0 and classification == "tests_pass":
        classification = "runner_process_error"

    return replace(result, outcome_class=classification), {
        "classification": classification,
        "junit": evidence,
    }

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any


class TaskKind(StrEnum):
    FEATURE = "feature"
    FEATURE_EXTENSION = "feature_extension"
    BUG_FIX = "bug_fix"  # Keep disabled for release until organisers confirm scope.


class CheckStatus(StrEnum):
    PASS = "PASS"
    PASS_WITH_LIMITATIONS = "PASS_WITH_LIMITATIONS"
    NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
    FAILED = "FAILED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_YET_AVAILABLE = "NOT_YET_AVAILABLE"


@dataclass(frozen=True)
class RepositorySnapshot:
    root: str
    remote_url: str | None
    commit: str | None
    git_tree: str | None
    working_tree_digest: str
    is_git_repository: bool
    is_dirty: bool | None
    languages: dict[str, int]
    project_markers: list[str]
    file_count: int
    captured_at_utc: str


@dataclass(frozen=True)
class CommandSpec:
    name: str
    argv: list[str]
    cwd: str = "."
    timeout_seconds: int = 120
    env: dict[str, str] = field(default_factory=dict)
    inherit_environment: bool = False


@dataclass(frozen=True)
class CommandResult:
    name: str
    argv: list[str]
    cwd: str
    exit_code: int | None
    timed_out: bool
    duration_seconds: float
    stdout: str
    stderr: str
    outcome_class: str | None = None

    @property
    def passed(self) -> bool:
        invalid_outcomes = {
            "timeout", "report_process_mismatch", "missing_test_report",
            "invalid_test_report", "no_tests_collected", "test_error",
            "test_assertion_failure", "all_tests_skipped", "runner_process_error",
        }
        return (
            self.exit_code == 0
            and not self.timed_out
            and self.outcome_class not in invalid_outcomes
        )


@dataclass(frozen=True)
class StateObservation:
    state: str
    baseline: list[CommandResult]
    task_tests: list[CommandResult]


@dataclass(frozen=True)
class GateCheck:
    check_id: str
    status: CheckStatus
    expected: str
    actual: str
    evidence: dict[str, Any] = field(default_factory=dict)
    limitation: str | None = None


@dataclass(frozen=True)
class ThreeStateReport:
    task_kind: TaskKind
    status: CheckStatus
    checks: list[GateCheck]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


def _jsonable(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value

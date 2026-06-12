from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum


class FailureCategory(str, Enum):
    """Supported high-level CI failure categories."""

    TEST_FAILURE = "test_failure"
    DEPENDENCY_ERROR = "dependency_error"
    SYNTAX_ERROR = "syntax_error"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    PERMISSION_ERROR = "permission_error"
    DISK_SPACE_ERROR = "disk_space_error"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class LogEntry:
    line_number: int
    text: str
    severity: str = "info"


@dataclass(frozen=True)
class ParsedLog:
    raw: str
    source: str
    entries: list[LogEntry]


@dataclass(frozen=True)
class TriageResult:
    category: FailureCategory
    confidence: float
    summary: str
    evidence: list[str]
    source: str | None = None

    def as_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["category"] = self.category.value
        return data

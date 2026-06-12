from __future__ import annotations

from .models import LogEntry, ParsedLog


_ERROR_MARKERS = (
    "error",
    "failed",
    "failure",
    "traceback",
    "exception",
    "syntaxerror",
    "permission denied",
    "timed out",
    "timeout",
    "no space left",
)
_WARNING_MARKERS = ("warning", "warn")


def parse_log(log: str, source: str = "<memory>") -> ParsedLog:
    """Parse raw CI log text into line-oriented entries.

    The MVP parser intentionally keeps structure simple: every physical line is
    preserved with a line number and a best-effort severity label. Classifiers
    can then use both raw text and line-level evidence.
    """

    entries = [
        LogEntry(line_number=index, text=line, severity=_detect_severity(line))
        for index, line in enumerate(log.splitlines(), start=1)
    ]
    return ParsedLog(raw=log, source=source, entries=entries)


def _detect_severity(line: str) -> str:
    lowered = line.lower()
    if any(marker in lowered for marker in _ERROR_MARKERS):
        return "error"
    if any(marker in lowered for marker in _WARNING_MARKERS):
        return "warning"
    return "info"

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from .models import FailureCategory, ParsedLog, TriageResult
from .parser import parse_log


Rule = tuple[FailureCategory, float, str, tuple[str, ...]]


_RULES: tuple[Rule, ...] = (
    (FailureCategory.DISK_SPACE_ERROR, 0.97, "Disk space exhausted", (r"no space left on device", r"enospc", r"disk quota exceeded")),
    (FailureCategory.PERMISSION_ERROR, 0.95, "Permission or access denied", (r"permission denied", r"access is denied", r"eacces", r"operation not permitted")),
    (FailureCategory.TIMEOUT, 0.93, "Job or command timed out", (r"timed out", r"timeout", r"took longer than", r"deadline exceeded")),
    (FailureCategory.NETWORK_ERROR, 0.91, "Network connectivity failure", (r"could not resolve host", r"connection refused", r"connection reset", r"network is unreachable", r"tls handshake timeout", r"temporary failure in name resolution")),
    (FailureCategory.DEPENDENCY_ERROR, 0.9, "Dependency installation or resolution failure", (r"no matching distribution found", r"could not find a version", r"npm err!.*eresolve", r"module not found", r"cannot find module", r"failed to resolve dependencies")),
    (FailureCategory.SYNTAX_ERROR, 0.94, "Syntax error in source or configuration", (r"syntaxerror", r"invalid syntax", r"yaml.parser.parsererror", r"toml.*parse", r"jsondecodeerror")),
    (FailureCategory.TEST_FAILURE, 0.92, "Automated test failure", (r"\bfailed\b.*tests?[/\\]", r"assertionerror", r"pytest", r"junit.*failures=\"[1-9]", r"test[s]? failed")),
)


def classify(parsed_log: ParsedLog) -> TriageResult:
    """Classify a parsed CI log using transparent regex rules."""

    for category, confidence, summary, patterns in _RULES:
        evidence = _matching_evidence(parsed_log, patterns)
        if evidence:
            return TriageResult(
                category=category,
                confidence=confidence,
                summary=summary,
                evidence=evidence,
                source=parsed_log.source,
            )

    fallback = _first_non_empty_line(parsed_log.raw) or "No recognizable failure signature found"
    return TriageResult(
        category=FailureCategory.UNKNOWN,
        confidence=0.1,
        summary="Unknown CI failure",
        evidence=[fallback],
        source=parsed_log.source,
    )


def triage_log(log: str, source: str = "<memory>") -> TriageResult:
    """Convenience API: parse and classify raw log text."""

    return classify(parse_log(log, source=source))


def summarize_failures(logs: Iterable[str]) -> dict[str, object]:
    results = [triage_log(log) for log in logs]
    counts = Counter(result.category.value for result in results)
    return {
        "total": len(results),
        "by_category": dict(counts),
        "top_category": counts.most_common(1)[0][0] if counts else None,
    }


def _matching_evidence(parsed_log: ParsedLog, patterns: tuple[str, ...]) -> list[str]:
    evidence: list[str] = []
    for entry in parsed_log.entries:
        for pattern in patterns:
            if re.search(pattern, entry.text, re.IGNORECASE):
                evidence.append(entry.text.strip())
                break
        if len(evidence) >= 3:
            break
    return evidence


def _first_non_empty_line(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return None

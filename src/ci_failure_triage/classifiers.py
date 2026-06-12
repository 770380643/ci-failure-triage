from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from .models import FailureCategory, ParsedLog, TriageResult
from .parser import parse_log


Rule = tuple[FailureCategory, float, str, tuple[str, ...]]

_NEXT_STEPS: dict[FailureCategory, list[str]] = {
    FailureCategory.TEST_FAILURE: [
        "Re-run the failed test locally with verbose output.",
        "Inspect the assertion and recent changes around the failing test.",
        "Check related service logs if the test depends on an external system.",
    ],
    FailureCategory.DEPENDENCY_ERROR: [
        "Verify the package name and version constraints.",
        "Check whether the package index or lock file changed recently.",
        "Rebuild the environment from a clean dependency cache.",
    ],
    FailureCategory.SYNTAX_ERROR: [
        "Open the referenced file and line from the error output.",
        "Run the language parser or formatter locally before re-running CI.",
        "Check recent edits to configuration files if the parser error is not from source code.",
    ],
    FailureCategory.TIMEOUT: [
        "Re-run the slow step with timing or verbose logs enabled.",
        "Check for external service waits, deadlocks, or unusually large test data.",
        "Compare runtime with the previous successful CI run.",
    ],
    FailureCategory.NETWORK_ERROR: [
        "Retry the job to rule out a transient network failure.",
        "Check DNS, proxy, firewall, and package registry availability.",
        "Prefer pinned mirrors or cached artifacts for frequently downloaded dependencies.",
    ],
    FailureCategory.PERMISSION_ERROR: [
        "Check file ownership and permissions for the reported path.",
        "Verify the CI user has access to caches, artifacts, and workspace directories.",
        "Avoid running the same workspace with mixed privileged and unprivileged steps.",
    ],
    FailureCategory.DISK_SPACE_ERROR: [
        "Inspect workspace, cache, and container layer disk usage.",
        "Remove stale build artifacts or reduce cache size before retrying.",
        "Consider moving large artifacts to external storage.",
    ],
    FailureCategory.UNKNOWN: [
        "Inspect the first failing command and nearby log lines manually.",
        "Add a sanitized sample log if this is a recurring failure pattern.",
        "Create a new classifier rule once the failure signature is understood.",
    ],
}


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
                next_steps=_NEXT_STEPS[category],
                source=parsed_log.source,
            )

    fallback = _first_non_empty_line(parsed_log.raw) or "No recognizable failure signature found"
    return TriageResult(
        category=FailureCategory.UNKNOWN,
        confidence=0.1,
        summary="Unknown CI failure",
        evidence=[fallback],
        next_steps=_NEXT_STEPS[FailureCategory.UNKNOWN],
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

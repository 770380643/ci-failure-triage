from __future__ import annotations

import json

from .models import TriageResult


def render_json_report(result: TriageResult) -> str:
    """Render a machine-readable JSON report."""

    return json.dumps(result.as_dict(), indent=2, sort_keys=True) + "\n"


def render_markdown_report(result: TriageResult) -> str:
    """Render a human-readable Markdown report."""

    evidence = "\n".join(f"- {item}" for item in result.evidence) or "- No evidence captured"
    source = result.source or "<unknown>"
    return (
        "# CI Failure Triage Report\n\n"
        f"**Source:** {source}\n\n"
        f"**Category:** {result.category.value}\n\n"
        f"**Confidence:** {result.confidence:.2f}\n\n"
        f"**Summary:** {result.summary}\n\n"
        "## Evidence\n\n"
        f"{evidence}\n"
    )


def render_report(result: TriageResult, output_format: str) -> str:
    if output_format == "json":
        return render_json_report(result)
    if output_format == "markdown":
        return render_markdown_report(result)
    raise ValueError(f"Unsupported report format: {output_format}")

from __future__ import annotations

import json

from .models import TriageResult


def render_json_report(result: TriageResult) -> str:
    """Render a machine-readable JSON report."""

    return json.dumps(result.as_dict(), indent=2, sort_keys=True) + "\n"


def render_markdown_report(result: TriageResult) -> str:
    """Render a human-readable Markdown report."""

    evidence = "\n".join(f"- {item}" for item in result.evidence) or "- No evidence captured"
    next_steps = "\n".join(
        f"{index}. {item}" for index, item in enumerate(result.next_steps, start=1)
    ) or "1. Inspect the full CI log manually."
    source = result.source or "<unknown>"
    return (
        "# CI Failure Triage Report\n\n"
        f"**Source:** {source}\n\n"
        f"**Category:** {result.category.value}\n\n"
        f"**Confidence:** {result.confidence:.2f}\n\n"
        f"**Summary:** {result.summary}\n\n"
        "## Evidence\n\n"
        f"{evidence}\n\n"
        "## Suggested Next Steps\n\n"
        f"{next_steps}\n"
    )


def render_report(result: TriageResult, output_format: str) -> str:
    if output_format == "json":
        return render_json_report(result)
    if output_format == "markdown":
        return render_markdown_report(result)
    raise ValueError(f"Unsupported report format: {output_format}")


def render_json_batch_report(results: list[TriageResult]) -> str:
    by_category: dict[str, int] = {}
    for result in results:
        category = result.category.value
        by_category[category] = by_category.get(category, 0) + 1
    payload = {
        "summary": {
            "total": len(results),
            "by_category": by_category,
        },
        "results": [result.as_dict() for result in results],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def render_markdown_batch_report(results: list[TriageResult]) -> str:
    by_category: dict[str, int] = {}
    for result in results:
        category = result.category.value
        by_category[category] = by_category.get(category, 0) + 1

    lines = [
        "# CI Failure Triage Batch Report",
        "",
        f"**Total logs:** {len(results)}",
        "",
        "## Summary",
        "",
    ]
    if by_category:
        lines.extend(f"- {category}: {count}" for category, count in by_category.items())
    else:
        lines.append("- No log files found")

    for result in results:
        source = result.source or "<unknown>"
        title = source.replace("\\", "/").rsplit("/", 1)[-1]
        lines.extend(
            [
                "",
                f"## {title}",
                "",
                f"**Source:** {source}",
                "",
                f"**Category:** {result.category.value}",
                "",
                f"**Confidence:** {result.confidence:.2f}",
                "",
                f"**Summary:** {result.summary}",
                "",
                "### Evidence",
                "",
            ]
        )
        lines.extend(f"- {item}" for item in result.evidence)
        lines.extend(["", "### Suggested Next Steps", ""])
        lines.extend(f"{index}. {item}" for index, item in enumerate(result.next_steps, start=1))

    return "\n".join(lines) + "\n"


def render_batch_report(results: list[TriageResult], output_format: str) -> str:
    if output_format == "json":
        return render_json_batch_report(results)
    if output_format == "markdown":
        return render_markdown_batch_report(results)
    raise ValueError(f"Unsupported report format: {output_format}")

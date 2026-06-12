import json

from ci_failure_triage.models import FailureCategory, TriageResult
from ci_failure_triage.report import (
    render_json_batch_report,
    render_json_report,
    render_markdown_batch_report,
    render_markdown_report,
)


def _result():
    return TriageResult(
        category=FailureCategory.TEST_FAILURE,
        confidence=0.95,
        summary="Pytest assertion failure",
        evidence=["AssertionError: assert 500 == 200"],
        next_steps=["Re-run the failed test locally with verbose output."],
        source="ci.log",
    )


def test_render_json_report_is_machine_readable():
    report = render_json_report(_result())

    data = json.loads(report)
    assert data["category"] == "test_failure"
    assert data["source"] == "ci.log"
    assert data["evidence"] == ["AssertionError: assert 500 == 200"]
    assert data["next_steps"] == ["Re-run the failed test locally with verbose output."]


def test_render_markdown_report_contains_human_summary():
    report = render_markdown_report(_result())

    assert "# CI Failure Triage Report" in report
    assert "**Category:** test_failure" in report
    assert "- AssertionError: assert 500 == 200" in report
    assert "## Suggested Next Steps" in report
    assert "1. Re-run the failed test locally with verbose output." in report


def test_render_json_batch_report_summarizes_categories():
    report = render_json_batch_report([_result()])

    data = json.loads(report)
    assert data["summary"] == {"total": 1, "by_category": {"test_failure": 1}}
    assert data["results"][0]["category"] == "test_failure"


def test_render_markdown_batch_report_contains_sections():
    report = render_markdown_batch_report([_result()])

    assert "# CI Failure Triage Batch Report" in report
    assert "- test_failure: 1" in report
    assert "## ci.log" in report

import json

from typer.testing import CliRunner

from ci_failure_triage.cli import app


runner = CliRunner()


def test_analyze_writes_json_report(tmp_path):
    log_file = tmp_path / "ci.log"
    output = tmp_path / "report.json"
    log_file.write_text("SyntaxError: invalid syntax", encoding="utf-8")

    result = runner.invoke(app, ["analyze", str(log_file), "--format", "json", "--output", str(output)])

    assert result.exit_code == 0, result.output
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["category"] == "syntax_error"


def test_analyze_writes_markdown_report(tmp_path):
    log_file = tmp_path / "ci.log"
    output = tmp_path / "report.md"
    log_file.write_text("ERROR: Job timed out after 30 minutes", encoding="utf-8")

    result = runner.invoke(app, ["analyze", str(log_file), "--format", "markdown", "--output", str(output)])

    assert result.exit_code == 0, result.output
    assert "**Category:** timeout" in output.read_text(encoding="utf-8")


def test_analyze_dir_writes_json_report_for_each_log(tmp_path):
    log_dir = tmp_path / "logs"
    output = tmp_path / "reports.json"
    log_dir.mkdir()
    (log_dir / "test.log").write_text("FAILED tests/test_api.py::test_ok - AssertionError: boom", encoding="utf-8")
    (log_dir / "deps.log").write_text("ERROR: No matching distribution found for nope", encoding="utf-8")

    result = runner.invoke(app, ["analyze-dir", str(log_dir), "--format", "json", "--output", str(output)])

    assert result.exit_code == 0, result.output
    data = json.loads(output.read_text(encoding="utf-8"))
    assert [item["category"] for item in data["results"]] == ["dependency_error", "test_failure"]
    assert data["summary"] == {
        "total": 2,
        "by_category": {"dependency_error": 1, "test_failure": 1},
    }


def test_analyze_dir_prints_markdown_sections(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "timeout.log").write_text("ERROR: Job timed out after 30 minutes", encoding="utf-8")

    result = runner.invoke(app, ["analyze-dir", str(log_dir), "--format", "markdown"])

    assert result.exit_code == 0, result.output
    assert "# CI Failure Triage Batch Report" in result.output
    assert "## timeout.log" in result.output
    assert "**Category:** timeout" in result.output

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

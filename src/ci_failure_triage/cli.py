from __future__ import annotations

import typer
from pathlib import Path
from typing import Optional

from .classifiers import classify
from .parser import parse_log
from .report import render_batch_report, render_report

app = typer.Typer(help="Triage CI failure logs and generate reports.")


@app.callback()
def _main() -> None:
    """Triage CI failure logs and generate reports."""


@app.command()
def analyze(
    log_file: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True, help="CI log file to analyze."),
    output_format: str = typer.Option("markdown", "--format", help="Report format: markdown or json."),
    output: Optional[Path] = typer.Option(None, "--output", help="Write report to this path. Prints to stdout when omitted."),
) -> None:
    """Analyze a CI log file and render a Markdown or JSON report."""

    if output_format not in {"markdown", "json"}:
        raise typer.BadParameter("format must be 'markdown' or 'json'")

    log_text = log_file.read_text(encoding="utf-8", errors="replace")
    parsed = parse_log(log_text, source=str(log_file))
    result = classify(parsed)
    report = render_report(result, output_format)

    if output is None:
        typer.echo(report, nl=False)
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    typer.echo(f"Wrote {output_format} report to {output}")


@app.command("analyze-dir")
def analyze_dir(
    log_dir: Path = typer.Argument(..., exists=True, file_okay=False, readable=True, help="Directory containing .log files to analyze."),
    output_format: str = typer.Option("markdown", "--format", help="Report format: markdown or json."),
    output: Optional[Path] = typer.Option(None, "--output", help="Write report to this path. Prints to stdout when omitted."),
) -> None:
    """Analyze all .log files under a directory and render a batch report."""

    if output_format not in {"markdown", "json"}:
        raise typer.BadParameter("format must be 'markdown' or 'json'")

    results = []
    for log_file in sorted(log_dir.rglob("*.log")):
        log_text = log_file.read_text(encoding="utf-8", errors="replace")
        parsed = parse_log(log_text, source=str(log_file))
        results.append(classify(parsed))

    report = render_batch_report(results, output_format)
    if output is None:
        typer.echo(report, nl=False)
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    typer.echo(f"Wrote {output_format} batch report to {output}")


def main() -> None:
    app()


if __name__ == "__main__":  # pragma: no cover
    main()

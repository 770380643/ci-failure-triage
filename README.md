# ci-failure-triage

`ci-failure-triage` is a small, transparent Python tool for turning noisy CI logs
into actionable failure reports. It is designed for maintainers, QA engineers,
and automation bots that need a dependable first-pass diagnosis before a human
opens the full build log.

## Motivation

CI systems fail for many repeatable reasons: broken tests, missing dependencies,
timeouts, flaky networks, permission mistakes, and full disks. Raw logs often
bury the useful line in thousands of lines of setup output. This project provides
a rules-based MVP that is:

- deterministic and easy to review;
- fast enough for local hooks or CI bots;
- simple to extend with new signatures;
- able to emit both human Markdown and machine JSON reports.

## Supported categories

- `test_failure`
- `dependency_error`
- `syntax_error`
- `timeout`
- `network_error`
- `permission_error`
- `disk_space_error`
- `unknown`

## Installation

From a local checkout:

```bash
python -m pip install -e .
```

For development:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

Repository and issue tracker URLs will be added after the public GitHub
repository is created.

## Usage

Analyze a log and write Markdown:

```bash
ci-triage analyze samples/test_failure.log --format markdown --output report.md
```

Analyze a log and write JSON:

```bash
ci-triage analyze samples/dependency_error.log --format json --output report.json
```

If `--output` is omitted, the report is printed to stdout.

## Sample Markdown output

```markdown
# CI Failure Triage Report

**Source:** samples/test_failure.log

**Category:** test_failure

**Confidence:** 0.92

**Summary:** Automated test failure

## Evidence

- FAILED tests/test_api.py::test_returns_200 - AssertionError: assert 500 == 200
```

## Sample JSON output

```json
{
  "category": "dependency_error",
  "confidence": 0.9,
  "evidence": [
    "ERROR: No matching distribution found for internal-widget==99.0"
  ],
  "source": "samples/dependency_error.log",
  "summary": "Dependency installation or resolution failure"
}
```

## Project layout

- `src/ci_failure_triage/models.py` — dataclasses and category enum
- `src/ci_failure_triage/parser.py` — line-oriented log parser
- `src/ci_failure_triage/classifiers.py` — deterministic category rules
- `src/ci_failure_triage/report.py` — Markdown and JSON renderers
- `src/ci_failure_triage/cli.py` — Typer command-line app
- `samples/` — realistic sample logs for every supported category
- `tests/` — parser, classifier, report, and CLI coverage

## Roadmap

- Add GitHub Actions, GitLab CI, Azure Pipelines, and Jenkins-specific parsers.
- Include remediation hints per category.
- Support batch analysis of directories and artifacts.
- Add SARIF or annotations output for code-hosting integrations.
- Track classifier precision with a curated fixture corpus.

## Contribution guide

Contributions are welcome. Please:

1. Open an issue or TODO note describing the failure signature you want to add.
2. Add or update a sample log in `samples/`.
3. Add tests for parser/classifier/report or CLI behavior.
4. Run `python -m pytest` before submitting changes.
5. Keep rules understandable; prefer explicit evidence over opaque heuristics.

See `CONTRIBUTING.md` for the short local development checklist.

## License

MIT

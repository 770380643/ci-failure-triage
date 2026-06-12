# Roadmap

`ci-failure-triage` starts as a small, test-covered CLI for summarizing CI log
failures. The next milestones keep the project focused on practical CI usage.

## v0.2.0

- Add GitHub Actions annotation output for workflow-native errors and warnings.
- Add a `--fail-on` option so teams can use the tool as a CI quality gate.
- Expand sample logs for common package manager failures.

## Later

- Support JUnit XML input for test-suite-level summaries.
- Add confidence scores for overlapping failure signatures.
- Publish a small guide for using the CLI in GitHub Actions.

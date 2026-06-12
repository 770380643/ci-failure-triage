import pytest

from ci_failure_triage.classifiers import classify
from ci_failure_triage.models import FailureCategory
from ci_failure_triage.parser import parse_log


@pytest.mark.parametrize(
    ("filename", "snippet", "category"),
    [
        ("test_failure.log", "FAILED tests/test_api.py::test_returns_200 - AssertionError: assert 500 == 200", FailureCategory.TEST_FAILURE),
        ("dependency_error.log", "ERROR: No matching distribution found for missing-package", FailureCategory.DEPENDENCY_ERROR),
        ("syntax_error.log", "SyntaxError: invalid syntax", FailureCategory.SYNTAX_ERROR),
        ("timeout.log", "ERROR: Job failed: execution took longer than 30 minutes and timed out", FailureCategory.TIMEOUT),
        ("network_error.log", "curl: (6) Could not resolve host: pypi.org", FailureCategory.NETWORK_ERROR),
        ("permission_error.log", "Permission denied: '/var/cache/pip'", FailureCategory.PERMISSION_ERROR),
        ("disk_space_error.log", "OSError: [Errno 28] No space left on device", FailureCategory.DISK_SPACE_ERROR),
        ("unknown.log", "Process completed with exit code 1", FailureCategory.UNKNOWN),
    ],
)
def test_classify_supported_categories(filename, snippet, category):
    parsed = parse_log(snippet, source=filename)

    result = classify(parsed)

    assert result.category is category
    assert result.confidence > 0
    assert result.summary
    assert result.evidence
    assert result.next_steps


def test_classify_test_failure_includes_actionable_next_steps():
    parsed = parse_log(
        "FAILED tests/test_api.py::test_returns_200 - AssertionError: assert 500 == 200",
        source="pytest.log",
    )

    result = classify(parsed)

    assert "Re-run the failed test locally with verbose output." in result.next_steps

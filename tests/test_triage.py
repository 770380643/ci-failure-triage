from ci_failure_triage import FailureCategory, summarize_failures, triage_log


def test_triage_log_returns_new_mvp_category_names():
    result = triage_log("FAILED tests/test_api.py::test_returns_200 - AssertionError: assert 500 == 200")

    assert result.category is FailureCategory.TEST_FAILURE
    assert result.confidence > 0
    assert result.summary == "Automated test failure"
    assert result.evidence


def test_summarize_failures_ranks_categories_by_frequency():
    logs = [
        "FAILED tests/test_cli.py::test_help - AssertionError: bad help",
        "ERROR: No matching distribution found for nope",
        "FAILED tests/test_unit.py::test_math - AssertionError: broken math",
    ]

    summary = summarize_failures(logs)

    assert summary == {
        "total": 3,
        "by_category": {"test_failure": 2, "dependency_error": 1},
        "top_category": "test_failure",
    }

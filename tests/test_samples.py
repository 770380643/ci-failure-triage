from pathlib import Path

from ci_failure_triage.classifiers import classify
from ci_failure_triage.models import FailureCategory
from ci_failure_triage.parser import parse_log


EXPECTED = {
    "test_failure.log": FailureCategory.TEST_FAILURE,
    "dependency_error.log": FailureCategory.DEPENDENCY_ERROR,
    "syntax_error.log": FailureCategory.SYNTAX_ERROR,
    "timeout.log": FailureCategory.TIMEOUT,
    "network_error.log": FailureCategory.NETWORK_ERROR,
    "permission_error.log": FailureCategory.PERMISSION_ERROR,
    "disk_space_error.log": FailureCategory.DISK_SPACE_ERROR,
    "unknown.log": FailureCategory.UNKNOWN,
}


def test_sample_logs_cover_every_supported_category():
    samples_dir = Path(__file__).parents[1] / "samples"

    for filename, expected_category in EXPECTED.items():
        log_path = samples_dir / filename
        parsed = parse_log(log_path.read_text(encoding="utf-8"), source=str(log_path))

        assert classify(parsed).category is expected_category

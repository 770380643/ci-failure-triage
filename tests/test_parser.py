from ci_failure_triage.models import LogEntry
from ci_failure_triage.parser import parse_log


def test_parse_log_extracts_entries_with_line_numbers_and_severity():
    log = """INFO starting job
ERROR tests/test_api.py::test_ok FAILED
Traceback (most recent call last):
"""

    parsed = parse_log(log, source="ci.log")

    assert parsed.source == "ci.log"
    assert parsed.raw == log
    assert parsed.entries == [
        LogEntry(line_number=1, text="INFO starting job", severity="info"),
        LogEntry(line_number=2, text="ERROR tests/test_api.py::test_ok FAILED", severity="error"),
        LogEntry(line_number=3, text="Traceback (most recent call last):", severity="error"),
    ]

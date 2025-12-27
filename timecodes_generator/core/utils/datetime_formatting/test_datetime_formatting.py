from timecodes_generator.core.utils.datetime_formatting import (
    format_timestamp_from_seconds,
)


def test_format_timestamp_from_seconds():
    assert format_timestamp_from_seconds(0) == "00:00:00"
    assert format_timestamp_from_seconds(1) == "00:00:01"
    assert format_timestamp_from_seconds(10) == "00:00:10"
    assert format_timestamp_from_seconds(65) == "00:01:05"
    assert format_timestamp_from_seconds(3600) == "01:00:00"
    assert format_timestamp_from_seconds(10_000) == "02:46:40"
    assert format_timestamp_from_seconds(100_000) == "27:46:40"

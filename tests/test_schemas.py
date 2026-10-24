"""Tests for the Reading message contract."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from airquality.schemas import Reading

# (loc, type) of one validation error, e.g. (("pm25",), "greater_than_equal").
ErrorKey = tuple[tuple[int | str, ...], str]


def valid_reading(**overrides: Any) -> dict[str, Any]:
    """Return a valid reading payload, with the given fields replaced."""
    data: dict[str, Any] = {
        "device_id": "sensor-01",
        "ts": "2026-10-04T12:00:00Z",  # "Z" = UTC
        "pm25": 12.5,
        "pm10": 20.0,
        "temp": 21.3,
        "humidity": 55.0,
    }
    return data | overrides


def error_set(exc_info: pytest.ExceptionInfo[ValidationError]) -> set[ErrorKey]:
    """Reduce a captured ValidationError to its set of (loc, type) pairs.

    A set makes the comparison independent of order and catches extra errors.
    """
    return {(e["loc"], e["type"]) for e in exc_info.value.errors()}


def test_valid_reading() -> None:
    r = Reading(**valid_reading())
    assert r.device_id == "sensor-01"
    assert r.schema_version == 1  # by default


def test_naive_ts_rejected() -> None:
    with pytest.raises(ValidationError) as exc:
        Reading(**valid_reading(ts="2026-10-04T12:00:00"))
    assert error_set(exc) == {(("ts",), "timezone_aware")}


def test_out_of_range_rejected() -> None:
    with pytest.raises(ValidationError) as exc:
        Reading(**valid_reading(pm25=-1))
    assert error_set(exc) == {(("pm25",), "greater_than_equal")}


def test_extra_field_rejected() -> None:
    with pytest.raises(ValidationError) as exc:
        Reading(**valid_reading(pm2_5=10))
    assert error_set(exc) == {(("pm2_5",), "extra_forbidden")}


def test_ts_converted_to_utc() -> None:
    r = Reading(**valid_reading(ts="2026-10-04T12:00:00+02:00"))
    # Same instant: 12:00 at +02:00 is 10:00 UTC.
    assert r.ts == datetime(2026, 10, 4, 10, 0, tzinfo=UTC)
    # compares instants, not zones; this line checks it is stored in UTC.
    assert r.ts.tzinfo == UTC

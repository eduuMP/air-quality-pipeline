from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from airquality.schemas import Reading


def valid_reading(**overrides):
    data = {
        "device_id": "sensor-01",
        "ts": "2026-10-04T12:00:00Z",  # "Z" = UTC
        "pm25": 12.5,
        "pm10": 20.0,
        "temp": 21.3,
        "humidity": 55.0,
    }
    return data | overrides


def error_set(exc_info):
    return {(e["loc"], e["type"]) for e in exc_info.value.errors()}


def test_valid_reading():
    r = Reading(**valid_reading())
    assert r.device_id == "sensor-01"
    assert r.schema_version == 1  # by default


def test_naive_ts_rejected():
    with pytest.raises(ValidationError) as exc:
        Reading(**valid_reading(ts="2026-10-04T12:00:00"))
    assert error_set(exc) == {(("ts",), "timezone_aware")}


def test_out_of_range_rejected():
    with pytest.raises(ValidationError) as exc:
        Reading(**valid_reading(pm25=-1))
    assert error_set(exc) == {(("pm25",), "greater_than_equal")}


def test_extra_field_rejected():
    with pytest.raises(ValidationError) as exc:
        Reading(**valid_reading(pm2_5=10))
    assert error_set(exc) == {(("pm2_5",), "extra_forbidden")}


def test_ts_converted_to_utc():
    r = Reading(**valid_reading(ts="2026-10-04T12:00:00+02:00"))
    assert r.ts == datetime(2026, 10, 4, 10, 0, tzinfo=timezone.utc)
    assert r.ts.tzinfo == timezone.utc

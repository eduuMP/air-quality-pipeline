"""Message contract shared by every stage of the pipeline.

The simulator builds a Reading and publishes ``model_dump_json()``; the consumer
parses the payload with ``Reading.model_validate_json()``. A message that breaks
the contract raises ValidationError and never reaches the raw storage.
"""

from datetime import UTC, datetime
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator


class Reading(BaseModel):
    """One measurement from one device at one instant."""
    # extra="forbid": unknown keys are an error, not silently dropped.
    # frozen=True: a validated reading cannot be modified afterwards.
    model_config = ConfigDict(extra="forbid", frozen=True)

    device_id: str = Field(
        min_length=1,
        max_length=20,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Device identifier, e.g. 'sensor-01'.",
    )
    ts: AwareDatetime = Field(
        description="Measurement instant. Must include a UTC offset; stored in UTC."
    )
    pm25: float = Field(ge=0, le=1000, description="PM2.5 concentration in µg/m³.")
    pm10: float = Field(ge=0, le=1000, description="PM10 concentration in µg/m³.")
    temp: float = Field(ge=-50, le=90, description="Temperature in °C.")
    humidity: float = Field(ge=0, le=100, description="Relative humidity in %.")
    schema_version: Literal[1] = Field(
        default=1, description="Contract version, bumped on breaking changes."
    )

    @field_validator("ts", mode="after")
    @classmethod
    def ts_to_utc(cls, ts: datetime) -> datetime:
        """Normalize any offset to UTC, keeping the same instant."""
        return ts.astimezone(UTC)

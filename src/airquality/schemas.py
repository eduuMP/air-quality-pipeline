from datetime import datetime, timezone
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator


class Reading(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    device_id: str = Field(min_length=1, max_length=20, pattern=r"^[A-Za-z0-9_-]+$")
    ts: AwareDatetime
    pm25: float = Field(ge=0, le=1000)
    pm10: float = Field(ge=0, le=1000)
    temp: float = Field(ge=-50, le=90)
    humidity: float = Field(ge=0, le=100)
    schema_version: Literal[1] = 1

    @field_validator("ts", mode="after")
    @classmethod
    def ts_to_utc(cls, ts: datetime) -> datetime:
        return ts.astimezone(timezone.utc)

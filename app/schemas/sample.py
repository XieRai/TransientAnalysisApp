"""Sensor sample data contracts."""
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Sample(BaseModel):
    voltage: float = Field(..., description="Voltage in volts")
    current: float = Field(..., description="Current in amperes")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sequence: int | None = None
    device_id: str | None = None


class SampleAccepted(BaseModel):
    accepted: bool
    count: int

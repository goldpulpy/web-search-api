"""Engine models."""

from pydantic import BaseModel, Field


class EngineListResponse(BaseModel):
    """Engine list response."""

    engines: list[str] = Field(description="List of engines")

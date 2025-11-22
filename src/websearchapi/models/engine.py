"""Engine models."""

from pydantic import BaseModel


class EngineListResponse(BaseModel):
    """Engine list response."""

    engines: list[str]

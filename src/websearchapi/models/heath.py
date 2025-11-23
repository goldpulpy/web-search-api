"""Health check models."""

from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="Health status")
    timestamp: int = Field(description="Timestamp")

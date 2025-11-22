"""Health check endpoint."""

from datetime import datetime

from fastapi import APIRouter, status

from websearchapi.models.heath import HealthCheckResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Check the health of the service",
    response_description="Health check response",
    responses={
        200: {
            "description": "Service is healthy",
            "model": HealthCheckResponse,
        },
        429: {"description": "Rate limit exceeded"},
        503: {"description": "Service unavailable"},
    },
)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=int(datetime.now().astimezone().timestamp()),
    )

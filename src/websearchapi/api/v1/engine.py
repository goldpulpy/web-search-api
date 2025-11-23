"""Engine routers."""

from fastapi import APIRouter, HTTPException, status

from websearchapi.core import engines
from websearchapi.models.engine import EngineListResponse

router = APIRouter()


@router.get(
    "/engines",
    status_code=status.HTTP_200_OK,
    summary="Get all engines",
    description="Get all engines",
    response_description="List of engines",
    responses={
        200: {"description": "Success", "model": EngineListResponse},
        491: {"description": "Invalid API key"},
        500: {"description": "Internal server error"},
    },
)
async def engines_list() -> EngineListResponse:
    """Get all engines."""
    try:
        return EngineListResponse(engines=list(engines.keys()))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

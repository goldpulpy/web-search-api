"""Search routers."""

from fastapi import APIRouter, HTTPException, status

from websearchapi.engine import get_engine
from websearchapi.models.search import SearchRequest, SearchResponse

router = APIRouter()


@router.post(
    "/search",
    status_code=status.HTTP_200_OK,
    summary="Search for a query",
    description="Search for a query",
    response_description="Search results",
    responses={
        200: {"description": "Success", "model": SearchRequest},
        404: {"description": "Engine not found"},
        491: {"description": "Invalid API key"},
        500: {"description": "Internal server error"},
    },
)
async def search(request: SearchRequest) -> SearchResponse:
    """Search for a query."""
    try:
        engine = get_engine(request.engine)
        return await engine.search(request.query, request.page)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

"""Search routers."""

from fastapi import APIRouter, HTTPException, status

from websearchapi.core import get_engine
from websearchapi.models.search import SearchRequest, SearchResponse

router = APIRouter(tags=["Search"])


@router.post(
    "/search",
    status_code=status.HTTP_200_OK,
    summary="Search for a query",
    description="Search for a query",
    response_description="Search results",
    responses={
        200: {"description": "Success", "model": SearchRequest},
        401: {"description": "Invalid API key"},
        404: {"description": "Engine not found"},
        500: {"description": "Internal server error"},
    },
)
async def search(request: SearchRequest) -> SearchResponse:
    """Search for a query."""
    try:
        engine = get_engine(request.engine)
        return await engine.search(request)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

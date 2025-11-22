"""Search models."""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Search request."""

    engine: str = Field(min_length=1, description="Engine name")
    query: str = Field(min_length=1, description="Search query")
    page: int = Field(default=1, ge=1, le=10, description="Page number")


class SearchObject(BaseModel):
    """Search object."""

    title: str
    link: str
    snippet: str


class SearchResponse(BaseModel):
    """Search response."""

    engine: str
    result: list[SearchObject]
    page: int

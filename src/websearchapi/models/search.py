"""Search models."""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Search request."""

    engine: str = Field(min_length=1, description="Engine name")
    query: str = Field(min_length=1, description="Search query")
    page: int = Field(default=1, ge=1, le=10, description="Page number")


class SearchObject(BaseModel):
    """Search object."""

    title: str = Field(description="Result title")
    link: str = Field(description="Result link")
    snippet: str = Field(description="Result snippet")


class SearchResponse(BaseModel):
    """Search response."""

    engine: str = Field(description="Engine name")
    result: list[SearchObject] = Field(description="Search results")
    page: int = Field(description="Current page number")
    count: int = Field(description="Number of results")

"""Abstract base class for engines."""

from abc import ABC, abstractmethod

from websearchapi.models.search import SearchRequest, SearchResponse


class Engine(ABC):
    """Abstract base class for engines."""

    NAME: str

    @abstractmethod
    async def search(self, request: SearchRequest) -> SearchResponse:
        """Search for a query."""

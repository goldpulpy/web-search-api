"""Abstract base class for engines."""

from abc import ABC, abstractmethod

from websearchapi.models.search import SearchResponse


class Engine(ABC):
    """Abstract base class for engines."""

    NAME: str

    @abstractmethod
    async def search(self, query: str, page: int = 1) -> SearchResponse:
        """Search for a query."""

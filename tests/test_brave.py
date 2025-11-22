# pylint: disable=redefined-outer-name
"""Tests for Brave search engine."""

from unittest.mock import AsyncMock, patch

import pytest

from websearchapi.engine.brave import Brave
from websearchapi.engine.browser import DefaultConfig
from websearchapi.models.search import SearchObject, SearchResponse


class TestBraveURLBuilding:
    """Test Brave URL building functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.engine = Brave()

    def test_build_search_url_basic(self) -> None:
        """Test building search URL with basic query."""
        query = "test query"
        expected_url = "https://search.brave.com/search?q=test+query&offset=0"
        result = self.engine._build_search_url(query)
        assert result == expected_url

    def test_build_search_url_with_page(self) -> None:
        """Test building search URL with specific page."""
        query = "python programming"
        page = 2
        expected_url = (
            "https://search.brave.com/search?q=python+programming&offset=1"
        )
        result = self.engine._build_search_url(query, page)
        assert result == expected_url

    def test_build_search_url_with_special_chars(self) -> None:
        """Test building search URL with special characters."""
        query = "test@email.com & symbols"
        expected_url = "https://search.brave.com/search?q=test%40email.com+%26+symbols&offset=0"
        result = self.engine._build_search_url(query)
        assert result == expected_url

    def test_build_search_url_page_1(self) -> None:
        """Test building search URL for page 1 (default)."""
        query = "test"
        result = self.engine._build_search_url(query, page=1)
        assert "offset=0" in result

    def test_build_search_url_page_3(self) -> None:
        """Test building search URL for page 3."""
        query = "test"
        result = self.engine._build_search_url(query, page=3)
        assert "offset=2" in result


class TestBravePageParsing:
    """Test Brave page parsing functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.engine = Brave()

    @pytest.mark.asyncio
    async def test_parse_page_empty_results(self) -> None:
        """Test parsing page with no results."""
        mock_page = AsyncMock()
        mock_page.query_selector_all.return_value = []

        results = await self.engine._parse_page(mock_page)

        assert results == []
        mock_page.query_selector_all.assert_called_once_with(
            "div.result-content",
        )

    @pytest.mark.asyncio
    async def test_parse_page_with_results(self) -> None:
        """Test parsing page with search results."""
        # Create mock result items
        mock_item1 = AsyncMock()
        mock_title1 = AsyncMock()
        mock_link1 = AsyncMock()
        mock_snippet1 = AsyncMock()

        mock_title1.inner_text.return_value = "Test Title 1"
        mock_link1.get_attribute.return_value = "https://example1.com"
        mock_snippet1.inner_text.return_value = "Test snippet 1"

        mock_item1.query_selector.side_effect = lambda selector: {
            "div.title": mock_title1,
            "a": mock_link1,
            "div.content": mock_snippet1,
        }.get(selector)

        mock_item2 = AsyncMock()
        mock_title2 = AsyncMock()
        mock_link2 = AsyncMock()
        mock_snippet2 = AsyncMock()

        mock_title2.inner_text.return_value = "Test Title 2"
        mock_link2.get_attribute.return_value = "https://example2.com"
        mock_snippet2.inner_text.return_value = "Test snippet 2"

        mock_item2.query_selector.side_effect = lambda selector: {
            "div.title": mock_title2,
            "a": mock_link2,
            "div.content": mock_snippet2,
        }.get(selector)

        mock_page = AsyncMock()
        mock_page.query_selector_all.return_value = [mock_item1, mock_item2]

        results = await self.engine._parse_page(mock_page)

        assert len(results) == 2
        assert isinstance(results[0], SearchObject)
        assert results[0].title == "Test Title 1"
        assert results[0].link == "https://example1.com"
        assert results[0].snippet == "Test snippet 1"

        assert isinstance(results[1], SearchObject)
        assert results[1].title == "Test Title 2"
        assert results[1].link == "https://example2.com"
        assert results[1].snippet == "Test snippet 2"

    @pytest.mark.asyncio
    async def test_parse_page_missing_elements(self) -> None:
        """Test parsing page with missing title or link elements."""
        mock_item = AsyncMock()
        mock_item.query_selector.return_value = None

        mock_page = AsyncMock()
        mock_page.query_selector_all.return_value = [mock_item]

        results = await self.engine._parse_page(mock_page)

        assert results == []
        mock_item.query_selector.assert_called()

    @pytest.mark.asyncio
    async def test_parse_page_missing_link(self) -> None:
        """Test parsing page with missing link attribute."""
        mock_item = AsyncMock()
        mock_title = AsyncMock()
        mock_link = AsyncMock()
        mock_snippet = AsyncMock()

        mock_title.inner_text.return_value = "Test Title"
        mock_link.get_attribute.return_value = None
        mock_snippet.inner_text.return_value = "Test snippet"

        mock_item.query_selector.side_effect = lambda selector: {
            "div.title": mock_title,
            "a": mock_link,
            "div.content": mock_snippet,
        }.get(selector)

        mock_page = AsyncMock()
        mock_page.query_selector_all.return_value = [mock_item]

        results = await self.engine._parse_page(mock_page)

        assert results == []

    @pytest.mark.asyncio
    async def test_parse_page_missing_snippet(self) -> None:
        """Test parsing page with missing snippet."""
        mock_item = AsyncMock()
        mock_title = AsyncMock()
        mock_link = AsyncMock()

        mock_title.inner_text.return_value = "Test Title"
        mock_link.get_attribute.return_value = "https://example.com"
        mock_snippet = None

        mock_item.query_selector.side_effect = lambda selector: {
            "div.title": mock_title,
            "a": mock_link,
            "div.content": mock_snippet,
        }.get(selector)

        mock_page = AsyncMock()
        mock_page.query_selector_all.return_value = [mock_item]

        results = await self.engine._parse_page(mock_page)

        assert len(results) == 1
        assert results[0].title == "Test Title"
        assert results[0].link == "https://example.com"
        assert results[0].snippet == ""


class TestBraveSearch:
    """Test Brave search functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.engine = Brave()

    @pytest.mark.asyncio
    async def test_search_successful(self) -> None:
        """Test successful search operation."""
        query = "test query"
        page = 1

        with patch(
            "websearchapi.engine.brave.async_playwright",
        ) as mock_playwright:
            mock_p = AsyncMock()
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_p
            mock_p.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page

            mock_page.wait_for_selector.return_value = None

            with patch.object(self.engine, "_parse_page") as mock_parse:
                mock_parse.return_value = [
                    SearchObject(
                        title="Test Result 1",
                        link="https://example1.com",
                        snippet="Test snippet 1",
                    ),
                    SearchObject(
                        title="Test Result 2",
                        link="https://example2.com",
                        snippet="Test snippet 2",
                    ),
                ]

                result = await self.engine.search(query, page)

            assert isinstance(result, SearchResponse)
            assert result.engine == "Brave"
            assert result.page == page
            assert len(result.result) == 2
            assert result.result[0].title == "Test Result 1"
            assert result.result[1].title == "Test Result 2"

            mock_context.close.assert_called_once()
            mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_different_page(self) -> None:
        """Test search with different page number."""
        query = "test query"
        page = 2

        with patch(
            "websearchapi.engine.brave.async_playwright",
        ) as mock_playwright:
            mock_p = AsyncMock()
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_p
            mock_p.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page

            mock_page.wait_for_selector.return_value = None

            with patch.object(self.engine, "_parse_page") as mock_parse:
                mock_parse.return_value = []

                result = await self.engine.search(query, page)

            assert result.page == page
            expected_url = self.engine._build_search_url(query, page)
            mock_page.goto.assert_called_once_with(expected_url)

    @pytest.mark.asyncio
    async def test_search_browser_configuration(self) -> None:
        """Test browser configuration during search."""
        query = "test query"

        with patch(
            "websearchapi.engine.brave.async_playwright",
        ) as mock_playwright:
            mock_p = AsyncMock()
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_p
            mock_p.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page

            mock_page.wait_for_selector.return_value = None

            with patch.object(self.engine, "_parse_page") as mock_parse:
                mock_parse.return_value = []

                await self.engine.search(query)

            mock_p.chromium.launch.assert_called_once_with(
                channel="chrome",
                headless=True,
                args=DefaultConfig.args,
            )

            mock_browser.new_context.assert_called_once_with(
                user_agent=DefaultConfig.user_agent,
                locale=DefaultConfig.locale,
                timezone_id=DefaultConfig.timezone_id,
            )

    @pytest.mark.asyncio
    async def test_search_exception_handling(self) -> None:
        """Test that browser is closed even when exception occurs."""
        query = "test query"

        with patch(
            "websearchapi.engine.brave.async_playwright",
        ) as mock_playwright:
            mock_p = AsyncMock()
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_p
            mock_p.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            mock_page.goto.side_effect = Exception("Navigation failed")

            with pytest.raises(Exception, match="Navigation failed"):
                await self.engine.search(query)

            mock_context.close.assert_called_once()
            mock_browser.close.assert_called_once()

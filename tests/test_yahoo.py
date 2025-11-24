# pylint: disable=redefined-outer-name
"""Tests for Yahoo search engine."""

from unittest.mock import AsyncMock, patch

import pytest

from websearchapi.core.browser import DefaultConfig
from websearchapi.core.engines.yahoo import Yahoo
from websearchapi.models.search import (
    SearchObject,
    SearchRequest,
    SearchResponse,
)


class TestYahooURLBuilding:
    """Test Yahoo URL building functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.engine = Yahoo()

    def test_build_search_url_basic(self) -> None:
        """Test building search URL with basic query."""
        query = "test query"
        expected_url = "https://search.yahoo.com/search?q=test+query&b=1"
        result = self.engine._build_search_url(query)
        assert result == expected_url

    def test_build_search_url_with_page(self) -> None:
        """Test building search URL with specific page."""
        query = "python programming"
        page = 2
        expected_url = (
            "https://search.yahoo.com/search?q=python+programming&b=8"
        )
        result = self.engine._build_search_url(query, page)
        assert result == expected_url

    def test_build_search_url_with_special_chars(self) -> None:
        """Test building search URL with special characters."""
        query = "test@email.com & symbols"
        expected_url = "https://search.yahoo.com/search?q=test%40email.com+%26+symbols&b=1"
        result = self.engine._build_search_url(query)
        assert result == expected_url

    def test_build_search_url_page_1(self) -> None:
        """Test building search URL for page 1 (default)."""
        query = "test"
        result = self.engine._build_search_url(query, page=1)
        assert "b=1" in result

    def test_build_search_url_page_3(self) -> None:
        """Test building search URL for page 3."""
        query = "test"
        result = self.engine._build_search_url(query, page=3)
        assert "b=15" in result

    def test_build_search_url_page_calculation(self) -> None:
        """Test that page calculation follows Yahoo's offset formula."""
        # Yahoo uses: offset = (page - 1) * 7 + 1
        query = "test"

        # Page 1: (1-1)*7 + 1 = 1
        result_page1 = self.engine._build_search_url(query, page=1)
        assert "b=1" in result_page1

        # Page 2: (2-1)*7 + 1 = 8
        result_page2 = self.engine._build_search_url(query, page=2)
        assert "b=8" in result_page2

        # Page 3: (3-1)*7 + 1 = 15
        result_page3 = self.engine._build_search_url(query, page=3)
        assert "b=15" in result_page3


class TestYahooBannerSkipping:
    """Test Yahoo banner skipping functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.engine = Yahoo()

    @pytest.mark.asyncio
    async def test_skip_banner_successful(self) -> None:
        """Test successful banner skipping."""
        mock_page = AsyncMock()
        mock_page.wait_for_selector.return_value = None

        await self.engine._skip_banner(mock_page)

        mock_page.wait_for_selector.assert_called_once_with(
            "button.reject-all",
        )
        mock_page.click.assert_called_once_with("button.reject-all")

    @pytest.mark.asyncio
    async def test_skip_banner_timeout(self) -> None:
        """Test banner skipping when banner doesn't appear."""
        mock_page = AsyncMock()
        mock_page.wait_for_selector.side_effect = Exception("Timeout")

        # Should not raise exception, just log and continue
        await self.engine._skip_banner(mock_page)

        mock_page.wait_for_selector.assert_called_once_with(
            "button.reject-all",
        )
        mock_page.click.assert_not_called()


class TestYahooPageParsing:
    """Test Yahoo page parsing functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.engine = Yahoo()

    @pytest.mark.asyncio
    async def test_parse_page_empty_results(self) -> None:
        """Test parsing page with no results."""
        mock_page = AsyncMock()
        mock_page.query_selector_all.return_value = []

        results = await self.engine._parse_page(mock_page)

        assert results == []
        mock_page.query_selector_all.assert_called_once_with("div.algo")

    @pytest.mark.asyncio
    async def test_parse_page_with_results(self) -> None:
        """Test parsing page with search results."""
        mock_item1 = AsyncMock()
        mock_title1 = AsyncMock()
        mock_link1 = AsyncMock()
        mock_snippet1 = AsyncMock()

        mock_title1.inner_text.return_value = "Test Title 1"
        mock_link1.get_attribute.return_value = "https://example1.com"
        mock_snippet1.inner_text.return_value = "Test snippet 1"

        mock_item1.query_selector.side_effect = lambda selector: {
            "h3": mock_title1,
            "a": mock_link1,
            "div.compText": mock_snippet1,
        }.get(selector)

        mock_item2 = AsyncMock()
        mock_title2 = AsyncMock()
        mock_link2 = AsyncMock()
        mock_snippet2 = AsyncMock()

        mock_title2.inner_text.return_value = "Test Title 2"
        mock_link2.get_attribute.return_value = "https://example2.com"
        mock_snippet2.inner_text.return_value = "Test snippet 2"

        mock_item2.query_selector.side_effect = lambda selector: {
            "h3": mock_title2,
            "a": mock_link2,
            "div.compText": mock_snippet2,
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
            "h3": mock_title,
            "a": mock_link,
            "div.compText": mock_snippet,
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
            "h3": mock_title,
            "a": mock_link,
            "div.compText": mock_snippet,
        }.get(selector)

        mock_page = AsyncMock()
        mock_page.query_selector_all.return_value = [mock_item]

        results = await self.engine._parse_page(mock_page)

        assert len(results) == 1
        assert results[0].title == "Test Title"
        assert results[0].link == "https://example.com"
        assert results[0].snippet == ""

    @pytest.mark.asyncio
    async def test_parse_page_with_whitespace_trimming(self) -> None:
        """Test parsing page with whitespace trimming."""
        mock_item = AsyncMock()
        mock_title = AsyncMock()
        mock_link = AsyncMock()
        mock_snippet = AsyncMock()

        mock_title.inner_text.return_value = "  Test Title with spaces  "
        mock_link.get_attribute.return_value = "https://example.com"
        mock_snippet.inner_text.return_value = "  Test snippet with spaces  "

        mock_item.query_selector.side_effect = lambda selector: {
            "h3": mock_title,
            "a": mock_link,
            "div.compText": mock_snippet,
        }.get(selector)

        mock_page = AsyncMock()
        mock_page.query_selector_all.return_value = [mock_item]

        results = await self.engine._parse_page(mock_page)

        assert len(results) == 1
        assert results[0].title == "Test Title with spaces"
        assert results[0].snippet == "Test snippet with spaces"


class TestYahooSearch:
    """Test Yahoo search functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.engine = Yahoo()

    @pytest.mark.asyncio
    async def test_search_successful(self) -> None:
        """Test successful search operation."""
        request = SearchRequest(
            engine=self.engine.NAME,
            query="test query",
            page=1,
        )

        with patch(
            "websearchapi.core.engines.yahoo.BrowserManager.get_browser",
        ) as mock_get_browser:
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()
            mock_response = AsyncMock()

            mock_get_browser.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page

            mock_page.goto.return_value = mock_response
            mock_response.status = 200

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

                result = await self.engine.search(request)

            assert isinstance(result, SearchResponse)
            assert result.engine == "Yahoo"
            assert result.page == request.page
            assert len(result.result) == 2
            assert result.result[0].title == "Test Result 1"
            assert result.result[1].title == "Test Result 2"

            mock_context.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_different_page(self) -> None:
        """Test search with different page number."""
        request = SearchRequest(
            engine=self.engine.NAME,
            query="test query",
            page=2,
        )

        with patch(
            "websearchapi.core.engines.yahoo.BrowserManager.get_browser",
        ) as mock_get_browser:
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_get_browser.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page

            mock_page.wait_for_selector.return_value = None

            with patch.object(self.engine, "_parse_page") as mock_parse:
                mock_parse.return_value = []

                result = await self.engine.search(request)

            assert result.page == request.page
            expected_url = self.engine._build_search_url(
                request.query,
                request.page,
            )
            mock_page.goto.assert_called_once_with(expected_url)

    @pytest.mark.asyncio
    async def test_search_browser_configuration(self) -> None:
        """Test browser configuration during search."""
        request = SearchRequest(
            engine=self.engine.NAME,
            query="test query",
            page=2,
        )

        with patch(
            "websearchapi.core.engines.yahoo.BrowserManager.get_browser",
        ) as mock_get_browser:
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_get_browser.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page

            mock_page.wait_for_selector.return_value = None

            with patch.object(self.engine, "_parse_page") as mock_parse:
                mock_parse.return_value = []

                await self.engine.search(request)

            mock_browser.new_context.assert_called_once_with(
                user_agent=DefaultConfig.user_agent,
                locale=DefaultConfig.locale,
                timezone_id=DefaultConfig.timezone_id,
            )

    @pytest.mark.asyncio
    async def test_search_exception_handling(self) -> None:
        """Test that browser is closed even when exception occurs."""
        request = SearchRequest(
            engine=self.engine.NAME,
            query="test query",
            page=1,
        )

        with patch(
            "websearchapi.core.engines.yahoo.BrowserManager.get_browser",
        ) as mock_get_browser:
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_get_browser.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            mock_page.goto.side_effect = Exception("Navigation failed")

            with pytest.raises(Exception, match="Navigation failed"):
                await self.engine.search(request)

            mock_context.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_banner_skipping(self) -> None:
        """Test that banner skipping is called during search."""
        request = SearchRequest(
            engine=self.engine.NAME,
            query="test query",
            page=1,
        )

        with patch(
            "websearchapi.core.engines.yahoo.BrowserManager.get_browser",
        ) as mock_get_browser:
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()
            mock_response = AsyncMock()


            mock_get_browser.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page

            mock_page.goto.return_value = mock_response
            mock_response.status = 200

            mock_page.wait_for_selector.return_value = None


            with patch.object(self.engine, "_parse_page") as mock_parse:
                with patch.object(
                    self.engine,
                    "_skip_banner",
                ) as mock_skip_banner:
                    mock_parse.return_value = []

                    await self.engine.search(request)

                    mock_skip_banner.assert_called_once_with(mock_page)

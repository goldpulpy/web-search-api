# pylint: disable=redefined-outer-name
"""Tests for DuckDuckGo search engine."""

from unittest.mock import AsyncMock, patch
from urllib.parse import urlencode

import pytest

from websearchapi.core.browser import DefaultConfig
from websearchapi.core.engines.duckduckgo import DuckDuckGo
from websearchapi.models.search import SearchObject, SearchRequest, SearchResponse


class TestDuckDuckGoURLBuilding:
    """Test DuckDuckGo URL building functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.engine = DuckDuckGo()

    def test_build_search_url_basic(self) -> None:
        """Test building search URL with basic query."""
        query = "test query"
        expected_url = "https://duckduckgo.com/html/?q=test+query&s=0&o=json&dc=1&api=d.js"
        result = self.engine._build_search_url(query)
        assert result == expected_url

    def test_build_search_url_with_page(self) -> None:
        """Test building search URL with specific page."""
        query = "python programming"
        page = 2
        expected_url = "https://duckduckgo.com/html/?q=python+programming&s=10&o=json&dc=11&api=d.js"
        result = self.engine._build_search_url(query, page)
        assert result == expected_url

    def test_build_search_url_with_special_chars(self) -> None:
        """Test building search URL with special characters."""
        query = "test@email.com & symbols"
        expected_url = "https://duckduckgo.com/html/?q=test%40email.com+%26+symbols&s=0&o=json&dc=1&api=d.js"
        result = self.engine._build_search_url(query)
        assert result == expected_url

    def test_build_search_url_page_1(self) -> None:
        """Test building search URL for page 1 (default)."""
        query = "test"
        result = self.engine._build_search_url(query, page=1)
        assert "s=0" in result
        assert "dc=1" in result

    def test_build_search_url_page_3(self) -> None:
        """Test building search URL for page 3."""
        query = "test"
        result = self.engine._build_search_url(query, page=3)
        assert "s=20" in result
        assert "dc=21" in result


class TestDuckDuckGoURLCleaning:
    """Test DuckDuckGo URL cleaning functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.engine = DuckDuckGo()

    def test_clean_duckduckgo_url_empty(self) -> None:
        """Test cleaning empty URL."""
        result = self.engine._clean_duckduckgo_url("")
        assert result == ""

    def test_clean_duckduckgo_url_none(self) -> None:
        """Test cleaning None URL."""
        result = self.engine._clean_duckduckgo_url("")
        assert result == ""

    def test_clean_duckduckgo_url_regular_url(self) -> None:
        """Test cleaning regular URL (no change)."""
        url = "https://example.com/page"
        result = self.engine._clean_duckduckgo_url(url)
        assert result == url

    def test_clean_duckduckgo_url_duckduckgo_redirect(self) -> None:
        """Test cleaning DuckDuckGo redirect URL."""
        original_url = "https://real-website.com/path"
        encoded_url = urlencode({"uddg": original_url})
        duckduckgo_url = f"https://duckduckgo.com/l/?{encoded_url}"

        result = self.engine._clean_duckduckgo_url(duckduckgo_url)
        assert result == original_url

    def test_clean_duckduckgo_url_protocol_relative(self) -> None:
        """Test cleaning protocol-relative DuckDuckGo URL."""
        original_url = "https://example.com"
        encoded_url = urlencode({"uddg": original_url})
        protocol_relative_url = f"//duckduckgo.com/l/?{encoded_url}"

        result = self.engine._clean_duckduckgo_url(protocol_relative_url)
        assert result == original_url

    def test_clean_duckduckgo_url_no_uddg_param(self) -> None:
        """Test cleaning DuckDuckGo URL without uddg parameter."""
        url = "https://duckduckgo.com/l/?other=param"
        result = self.engine._clean_duckduckgo_url(url)
        assert result == url

    def test_clean_duckduckgo_url_encoded_url(self) -> None:
        """Test cleaning URL with encoded characters."""
        original_url = "https://example.com/path with spaces"
        encoded_url = urlencode({"uddg": original_url})
        duckduckgo_url = f"https://duckduckgo.com/l/?{encoded_url}"

        result = self.engine._clean_duckduckgo_url(duckduckgo_url)
        assert result == original_url


class TestDuckDuckGoPageParsing:
    """Test DuckDuckGo page parsing functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.engine = DuckDuckGo()

    @pytest.mark.asyncio
    async def test_parse_page_empty_results(self) -> None:
        """Test parsing page with no results."""
        mock_page = AsyncMock()
        mock_page.query_selector_all.return_value = []

        results = await self.engine._parse_page(mock_page)

        assert results == []
        mock_page.query_selector_all.assert_called_once_with("div.result")

    @pytest.mark.asyncio
    async def test_parse_page_with_results(self) -> None:
        """Test parsing page with search results."""
        # Create mock result items
        mock_item1 = AsyncMock()
        mock_title_link1 = AsyncMock()
        mock_snippet1 = AsyncMock()

        mock_title_link1.inner_text.return_value = "Test Title 1"
        mock_title_link1.get_attribute.return_value = "https://example1.com"
        mock_snippet1.inner_text.return_value = "Test snippet 1"

        mock_item1.query_selector.side_effect = lambda selector: {
            "a.result__a": mock_title_link1,
            "a.result__snippet": mock_snippet1,
        }.get(selector)

        mock_item2 = AsyncMock()
        mock_title_link2 = AsyncMock()
        mock_snippet2 = AsyncMock()

        mock_title_link2.inner_text.return_value = "Test Title 2"
        mock_title_link2.get_attribute.return_value = (
            "https://duckduckgo.com/l/?uddg=https%3A%2F%2Fexample2.com"
        )
        mock_snippet2.inner_text.return_value = "Test snippet 2"

        mock_item2.query_selector.side_effect = lambda selector: {
            "a.result__a": mock_title_link2,
            "a.result__snippet": mock_snippet2,
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
        mock_title_link = AsyncMock()
        mock_snippet = AsyncMock()

        mock_title_link.inner_text.return_value = "Test Title"
        mock_title_link.get_attribute.return_value = None
        mock_snippet.inner_text.return_value = "Test snippet"

        mock_item.query_selector.side_effect = lambda selector: {
            "a.result__a": mock_title_link,
            "a.result__snippet": mock_snippet,
        }.get(selector)

        mock_page = AsyncMock()
        mock_page.query_selector_all.return_value = [mock_item]

        results = await self.engine._parse_page(mock_page)

        assert results == []

    @pytest.mark.asyncio
    async def test_parse_page_missing_snippet(self) -> None:
        """Test parsing page with missing snippet."""
        mock_item = AsyncMock()
        mock_title_link = AsyncMock()
        mock_title_link.inner_text.return_value = "Test Title"
        mock_title_link.get_attribute.return_value = "https://example.com"
        mock_snippet = None

        mock_item.query_selector.side_effect = lambda selector: {
            "a.result__a": mock_title_link,
            "a.result__snippet": mock_snippet,
        }.get(selector)

        mock_page = AsyncMock()
        mock_page.query_selector_all.return_value = [mock_item]

        results = await self.engine._parse_page(mock_page)

        assert len(results) == 1
        assert results[0].title == "Test Title"
        assert results[0].link == "https://example.com"
        assert results[0].snippet == ""


class TestDuckDuckGoSearch:
    """Test DuckDuckGo search functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.engine = DuckDuckGo()

    @pytest.mark.asyncio
    async def test_search_successful(self) -> None:
        """Test successful search operation."""
        request = SearchRequest(engine=self.engine.NAME, query="test query", page=1)

        with patch(
            "websearchapi.core.engines.duckduckgo.BrowserManager.get_browser",
        ) as mock_get_browser:
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_get_browser.return_value = mock_browser
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

                result = await self.engine.search(request)

            assert isinstance(result, SearchResponse)
            assert result.engine == "DuckDuckGo"
            assert result.page == request.page
            assert len(result.result) == 2
            assert result.result[0].title == "Test Result 1"
            assert result.result[1].title == "Test Result 2"

            mock_context.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_different_page(self) -> None:
        """Test search with different page number."""
        request = SearchRequest(engine=self.engine.NAME, query="test query", page=2)

        with patch(
            "websearchapi.core.engines.duckduckgo.BrowserManager.get_browser",
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
            expected_url = self.engine._build_search_url(request.query, request.page)
            mock_page.goto.assert_called_once_with(expected_url, timeout=30000)

    @pytest.mark.asyncio
    async def test_search_browser_configuration(self) -> None:
        """Test browser configuration during search."""
        request = SearchRequest(engine=self.engine.NAME, query="test query")

        with patch(
            "websearchapi.core.engines.duckduckgo.BrowserManager.get_browser",
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
        request = SearchRequest(engine=self.engine.NAME, query="test query", page=1)

        with patch(
            "websearchapi.core.engines.duckduckgo.BrowserManager.get_browser",
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

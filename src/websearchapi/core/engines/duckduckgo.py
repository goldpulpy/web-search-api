"""DuckDuckGo search engine."""

import logging
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

from playwright.async_api import Page

from websearchapi.core.browser import BrowserManager, DefaultConfig
from websearchapi.core.engines.abc import Engine
from websearchapi.models.search import (
    SearchObject,
    SearchResponse,
)

logger = logging.getLogger(__name__)


class DuckDuckGo(Engine):
    """DuckDuckGo search engine."""

    NAME = "DuckDuckGo"
    SEARCH_URL = "https://duckduckgo.com/html/"

    async def search(self, query: str, page: int = 1) -> SearchResponse:
        """Perform search using DuckDuckGo."""
        logger.info("Starting DuckDuckGo search for query: '%s'", query)

        browser = await BrowserManager.get_browser()

        pw_context = await browser.new_context(
            user_agent=DefaultConfig.user_agent,
            locale=DefaultConfig.locale,
            timezone_id=DefaultConfig.timezone_id,
        )

        pw_page = await pw_context.new_page()
        await pw_page.add_init_script(DefaultConfig.init_script)

        try:
            search_url = self._build_search_url(query, page)
            await pw_page.goto(search_url, timeout=30000)

            logger.debug("Waiting for search results to load")
            await pw_page.wait_for_selector("div.results", timeout=10000)

            results = await self._parse_page(pw_page)
            logger.info(
                "Found %s search results for query: '%s'",
                len(results),
                query,
            )

        finally:
            logger.debug("Closing browser context")
            await pw_context.close()

        return SearchResponse(engine=self.NAME, result=results, page=page)

    def _build_search_url(self, query: str, page: int = 1) -> str:
        """Build search URL."""
        offset = (page - 1) * 10
        encoded_query = quote_plus(query)
        return (
            f"{self.SEARCH_URL}?q={encoded_query}"
            f"&s={offset}&o=json&dc={offset + 1}&api=d.js"
        )

    def _clean_duckduckgo_url(self, url: str) -> str:
        """Extract real URL from DuckDuckGo redirect link."""
        if not url:
            logger.debug("Received empty URL, returning empty string")
            return ""

        if url.startswith("//duckduckgo.com/l/"):
            url = "https:" + url

        if "duckduckgo.com/l/" in url:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if "uddg" in params:
                return unquote(params["uddg"][0])

        return url

    async def _parse_page(self, page: Page) -> list[SearchObject]:
        """Parse page and extract search results."""
        logger.debug("Starting page parsing")
        results = []

        search_items = await page.query_selector_all("div.result")
        logger.debug("Found %s search result items", len(search_items))

        for index, item in enumerate(search_items):
            title_elem = await item.query_selector("a.result__a")
            link_elem = await item.query_selector("a.result__a")
            snippet_elem = await item.query_selector("a.result__snippet")

            if title_elem and link_elem:
                title = (await title_elem.inner_text()).strip()
                link = await link_elem.get_attribute("href")
                snippet = (
                    (await snippet_elem.inner_text()).strip()
                    if snippet_elem
                    else ""
                )

                if link:
                    clean_link = self._clean_duckduckgo_url(link)
                    results.append(
                        SearchObject(
                            title=title,
                            link=clean_link,
                            snippet=snippet,
                        ),
                    )
                else:
                    logger.debug(
                        "Skipping result %s: no link found",
                        index + 1,
                    )

            else:
                logger.debug(
                    "Skipping result %s: missing title or link elements",
                    index + 1,
                )

        return results

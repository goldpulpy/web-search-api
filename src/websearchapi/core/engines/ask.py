"""Ask search engine."""

import logging
from urllib.parse import quote_plus

from playwright.async_api import Page

from websearchapi.core.browser import BrowserManager, DefaultConfig
from websearchapi.core.engines.abc import Engine
from websearchapi.models.search import (
    SearchObject,
    SearchRequest,
    SearchResponse,
)

logger = logging.getLogger(__name__)


class Ask(Engine):
    """Brave search engine."""

    NAME = "Ask"
    SEARCH_URL = "https://www.ask.com/"

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Perform search using Ask."""
        logger.info("Starting Ask search for query: '%s'", request.query)

        pw_browser = await BrowserManager.get_browser()

        pw_context = await pw_browser.new_context(
            user_agent=DefaultConfig.user_agent,
            locale=DefaultConfig.locale,
            timezone_id=DefaultConfig.timezone_id,
        )

        pw_page = await pw_context.new_page()
        await pw_page.add_init_script(DefaultConfig.init_script)

        try:
            search_url = self._build_search_url(request.query, request.page)
            await pw_page.goto(search_url)

            logger.debug("Waiting for search results to load")
            await pw_page.wait_for_selector("div.results")

            results = await self._parse_page(pw_page)
            logger.info(
                "Found %s search results for query: '%s'",
                len(results),
                request.query,
            )

        finally:
            logger.debug("Closing browser context and browser")
            await pw_context.close()

        return SearchResponse(
            engine=self.NAME,
            search_url=search_url,
            result=results,
            page=request.page,
            count=len(results),
        )

    def _build_search_url(self, query: str, page: int = 1) -> str:
        """Build search URL."""
        encoded_query = quote_plus(query)
        return f"{self.SEARCH_URL}web?q={encoded_query}&page={page}"

    async def _parse_page(self, page: Page) -> list[SearchObject]:
        """Parse page and extract search results."""
        logger.debug("Starting page parsing")
        results = []

        search_items = await page.query_selector_all("div.result")
        logger.debug("Found %s search result items", len(search_items))

        for index, item in enumerate(search_items):
            title_elem = await item.query_selector("div.result-title")
            link_elem = await item.query_selector("a.result-title-link")
            snippet_elem = await item.query_selector("p.result-abstract")

            if title_elem and link_elem:
                title = (await title_elem.inner_text()).strip()
                link = await link_elem.get_attribute("href")
                snippet = (
                    (await snippet_elem.inner_text()).strip()
                    if snippet_elem
                    else ""
                )

                if link:
                    results.append(
                        SearchObject(
                            title=title,
                            link=link,
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

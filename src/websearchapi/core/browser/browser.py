"""Config for engines."""

import logging
from typing import ClassVar

from playwright.async_api import Browser, async_playwright

logger = logging.getLogger(__name__)


class DefaultConfig:
    """Default config for engines."""

    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
    timezone_id = "America/New_York"
    locale = "en-US"
    args: ClassVar = [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-infobars",
    ]

    init_script = """
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});

Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});

window.chrome = {
    runtime: {}
};

Object.defineProperty(navigator, 'permissions', {
    get: () => ({
        query: () => Promise.resolve({ state: 'prompt' })
    })
});

"""


class BrowserManager:
    """Browser manager."""

    _browser: Browser | None = None
    _playwright = None

    @classmethod
    async def get_browser(cls) -> Browser:
        """Get or create browser instance."""
        if cls._browser is None or not cls._browser.is_connected():
            logger.debug("Initializing browser instance")
            cls._playwright = await async_playwright().start()
            cls._browser = await cls._playwright.chromium.launch(
                channel="chrome",
                headless=True,
                args=DefaultConfig.args,
            )
        return cls._browser

    @classmethod
    async def close(cls) -> None:
        """Close browser and playwright."""
        if cls._browser:
            await cls._browser.close()
            cls._browser = None

        if cls._playwright:
            await cls._playwright.stop()
            cls._playwright = None

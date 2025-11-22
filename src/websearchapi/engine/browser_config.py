"""Config for engines."""

from typing import ClassVar


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

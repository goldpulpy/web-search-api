"""Config for engines."""

from typing import ClassVar


class DefaultConfig:
    """Default config for engines."""

    user_agent = (
        "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Mobile Safari/537.36"
    )
    timezone_id = "America/New_York"
    locale = "en-US"
    args: ClassVar = [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
    ]

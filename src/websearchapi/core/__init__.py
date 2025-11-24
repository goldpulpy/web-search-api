"""Engines."""

from .engines.abc import Engine
from .engines.ask import Ask
from .engines.brave import Brave
from .engines.duckduckgo import DuckDuckGo
from .engines.yahoo import Yahoo

_engine_classes = [DuckDuckGo, Brave, Yahoo, Ask]
engines: dict[str, type[Engine]] = {cls.NAME: cls for cls in _engine_classes}


def get_engine(name: str) -> Engine:
    """Get engine by name."""
    for engine_class in engines.values():
        if engine_class.NAME.lower() == name.lower():
            return engine_class()

    msg = f"Unknown engine: {name}"
    raise ValueError(msg)

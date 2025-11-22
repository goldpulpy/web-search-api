"""Config module."""

from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    """LogLevel enum."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class BaseConfig(BaseSettings):
    """Base config class."""

    model_config = SettingsConfigDict(extra="ignore", frozen=True)


class Config(BaseConfig):
    """APP config class."""

    host: str = "0.0.0.0"  # noqa: S104 # nosec
    port: int = Field(default=5000, ge=1, le=65535)
    log_level: LogLevel = LogLevel.INFO
    api_key: str | None = None
    api_prefix: str = "/api"
    enable_docs: bool = True


config = Config()  # type: ignore[call-arg]

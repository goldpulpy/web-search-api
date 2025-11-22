"""Authentication middleware."""

import logging
import secrets
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from websearchapi.shared import config

logger = logging.getLogger(__name__)
EXCLUDED_PATHS = {"/docs", "/openapi.json", "/health"}


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Authentication middleware with bearer token validation."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Dispatch request with authentication check."""
        if not config.api_key or request.method == "OPTIONS":
            return await call_next(request)

        if request.url.path in EXCLUDED_PATHS:
            logger.debug(
                "Excluded path %s (skipping authentication)",
                request.url.path,
            )
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        ip_addr = request.client.host if request.client else "unknown"

        if not auth_header:
            logger.warning("Invalid API key attempt from %s", ip_addr)
            return self._unauthorized("Missing Authorization header")

        parts = auth_header.split(maxsplit=1)
        if len(parts) != 2 or parts[0].lower() != "bearer":  # noqa: PLR2004
            logger.warning("Invalid API key attempt from %s", ip_addr)
            return self._unauthorized("Invalid Authorization header")

        api_key = parts[1]

        if not secrets.compare_digest(api_key, config.api_key):
            logger.warning("Invalid API key attempt from %s", ip_addr)
            return self._unauthorized("Invalid API key")

        return await call_next(request)

    @staticmethod
    def _unauthorized(reason: str) -> JSONResponse:
        """Return unauthorized response."""
        return JSONResponse(
            status_code=401,
            content={"detail": reason},
        )

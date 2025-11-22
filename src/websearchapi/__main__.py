"""Entry point for the Web Search API (FastAPI)."""

import logging

import uvicorn
from fastapi import FastAPI

from websearchapi import api
from websearchapi.api import docs, health, middlewares
from websearchapi.shared import config

logging.basicConfig(
    level=config.log_level.value,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI(docs_url=None, redoc_url=None)

app.add_middleware(middlewares.AuthenticationMiddleware)
app.include_router(api.router)
app.include_router(health.router)

if config.enable_docs:
    docs.setup_scalar(app)


if __name__ == "__main__":
    logger.info(
        "Starting the application, loglevel=%s",
        config.log_level.value,
    )
    if not config.api_key:
        logger.warning("API key is not set, authentication is disabled")

    if config.enable_docs:
        logger.info(
            "Docs available: http://%s:%s/docs",
            config.host,
            config.port,
        )

    uvicorn.run(app, host=config.host, port=config.port)

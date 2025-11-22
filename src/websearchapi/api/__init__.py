"""API routes."""

from fastapi import APIRouter

from websearchapi.shared import config

from . import v1

router = APIRouter(prefix=config.api_prefix)
router.include_router(v1.router)

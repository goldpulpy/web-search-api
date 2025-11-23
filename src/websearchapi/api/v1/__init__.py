"""v1 API routes."""

from fastapi import APIRouter

from . import engine, search

router = APIRouter(prefix="/v1")
router.include_router(engine.router)
router.include_router(search.router)

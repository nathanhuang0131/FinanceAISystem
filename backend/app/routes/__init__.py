from __future__ import annotations

from fastapi import APIRouter

from backend.app.routes.core import router as core_router
from backend.app.routes.ingest import router as ingest_router

router = APIRouter()
router.include_router(core_router)
router.include_router(ingest_router)

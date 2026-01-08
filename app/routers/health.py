from __future__ import annotations
from fastapi import APIRouter
from app.config import APP_VERSION, CACHE_TTL_SECONDS
from app.utils import envelope

router = APIRouter()

@router.get("/health")
def health():
    return envelope(
        tool="idx_stock_analyzer",
        operation="health",
        data={"status":"ok","version": APP_VERSION, "cache_ttl_sec": CACHE_TTL_SECONDS},
        meta={"version": APP_VERSION},
    )

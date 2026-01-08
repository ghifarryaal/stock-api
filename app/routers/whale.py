from __future__ import annotations
from fastapi import APIRouter, Query
from app.services.whale import whale_alert
from app.utils import envelope
from app.config import APP_VERSION

router = APIRouter(prefix="/v1/whale", tags=["whale"])

@router.get("/{ticker}")
def whale(ticker: str, days: int = Query(5, ge=3, le=30)):
    res = whale_alert(ticker, days=days)
    return envelope(tool="idx_market_intel", operation="whale_alert", data=res, meta={"version": APP_VERSION})

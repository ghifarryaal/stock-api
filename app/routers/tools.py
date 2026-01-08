from __future__ import annotations

from fastapi import APIRouter, Body, HTTPException
from app.models.schemas import ToolExecuteRequest, AnalyzeRequest
from app.services.combined import combine_analysis
from app.services.whale import whale_alert
from app.services.news import veteran_news_analysis, fetch_google_news_rss
from app.utils import envelope
from app.config import APP_VERSION

router = APIRouter(prefix="/v1/tools", tags=["tools"])

@router.post("/execute")
def execute(req: ToolExecuteRequest = Body(...)):
    tool = (req.tool or "").strip()
    op = (req.operation or "").strip()
    payload = req.input or {}

    # Keep backward compatibility with previous "idx_stock_analyzer"
    if tool in ("idx_stock_analyzer", "idx_market_intel", "idx_unified"):
        if op == "health":
            return envelope(tool=tool, operation="health", request_id=req.request_id, data={"status":"ok","version":APP_VERSION}, meta={"version": APP_VERSION})

        if op == "analyze":
            ticker = payload.get("ticker") or payload.get("symbol")
            if not ticker:
                raise HTTPException(status_code=422, detail="input.ticker wajib diisi")
            # Allow injecting news_items and whale as dicts
            news_items = payload.get("news_items")
            whale_in = payload.get("whale")
            res = combine_analysis(
                ticker,
                style=payload.get("style", "ringkas"),
                with_fundamental=payload.get("with_fundamental", True),
                with_technical=payload.get("with_technical", True),
                with_whale=payload.get("with_whale", True),
                with_news=payload.get("with_news", False),
                news_items=news_items,  # pydantic coercion not available here; accept list of dicts
                fetch_news=payload.get("fetch_news", False),
                news_query=payload.get("news_query"),
                period=payload.get("period", "2y"),
                interval=payload.get("interval", "1d"),
                rsi_period=int(payload.get("rsi_period", 14)),
                sma_fast=int(payload.get("sma_fast", 20)),
                sma_slow=int(payload.get("sma_slow", 50)),
                whale_payload=whale_in,
            )
            return envelope(tool=tool, operation="analyze", request_id=req.request_id, data=res, meta={"version": APP_VERSION})

        if op == "whale":
            ticker = payload.get("ticker") or payload.get("symbol")
            if not ticker:
                raise HTTPException(status_code=422, detail="input.ticker wajib diisi")
            res = whale_alert(ticker, days=int(payload.get("days", 5)))
            return envelope(tool=tool, operation="whale", request_id=req.request_id, data=res, meta={"version": APP_VERSION})

        if op == "news_analyze":
            emiten = payload.get("emiten") or payload.get("ticker") or payload.get("symbol")
            items = payload.get("items") or payload.get("news_items") or []
            res = veteran_news_analysis(emiten, items)
            return envelope(tool=tool, operation="news_analyze", request_id=req.request_id, data=res, meta={"version": APP_VERSION})

        if op == "fetch_news":
            q = payload.get("query")
            if not q:
                raise HTTPException(status_code=422, detail="input.query wajib diisi")
            items = fetch_google_news_rss(q, limit=int(payload.get("limit", 10)))
            return envelope(tool=tool, operation="fetch_news", request_id=req.request_id, data={"query": q, "items": [i.model_dump() for i in items]}, meta={"version": APP_VERSION})

    raise HTTPException(status_code=404, detail="tool/operation tidak dikenali")

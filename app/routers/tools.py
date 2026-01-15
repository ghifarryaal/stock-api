from __future__ import annotations

from fastapi import APIRouter, Body, HTTPException
from app.models.schemas import ToolExecuteRequest
from app.services.combined import combine_analysis
from app.services.whale import whale_alert
from app.services.news_engine import run_news_engine
from app.utils import envelope
from app.config import APP_VERSION

router = APIRouter(prefix="/v1/tools", tags=["tools"])


@router.post("/execute")
def execute(req: ToolExecuteRequest = Body(...)):
    tool = (req.tool or "").strip()
    op = (req.operation or "").strip()
    payload = req.input or {}

    if tool in ("idx_stock_analyzer", "idx_market_intel", "idx_unified"):

        # =========================
        # HEALTH
        # =========================
        if op == "health":
            return envelope(
                tool=tool,
                operation="health",
                request_id=req.request_id,
                data={"status": "ok", "version": APP_VERSION},
                meta={"version": APP_VERSION},
            )

        # =========================
        # ANALYZE (COMBINED)
        # =========================
        if op == "analyze":
            ticker = payload.get("ticker") or payload.get("symbol")
            if not ticker:
                raise HTTPException(422, "input.ticker wajib diisi")

            res = combine_analysis(
                ticker,
                style=payload.get("style", "ringkas"),
                with_fundamental=payload.get("with_fundamental", True),
                with_technical=payload.get("with_technical", True),
                with_whale=payload.get("with_whale", True),
                with_news=payload.get("with_news", False),
                with_broker=payload.get("with_broker", True),
                period=payload.get("period", "2y"),
                interval=payload.get("interval", "1d"),
                rsi_period=int(payload.get("rsi_period", 14)),
                sma_fast=int(payload.get("sma_fast", 20)),
                sma_slow=int(payload.get("sma_slow", 50)),
                whale_payload=payload.get("whale"),
            )

            return envelope(
                tool=tool,
                operation="analyze",
                request_id=req.request_id,
                data=res,
                meta={"version": APP_VERSION},
            )

        # =========================
        # WHALE
        # =========================
        if op == "whale":
            ticker = payload.get("ticker") or payload.get("symbol")
            if not ticker:
                raise HTTPException(422, "input.ticker wajib diisi")

            res = whale_alert(ticker, days=int(payload.get("days", 5)))

            return envelope(
                tool=tool,
                operation="whale",
                request_id=req.request_id,
                data=res,
                meta={"version": APP_VERSION},
            )

        # =========================
        # NEWS ENGINE (AUTO)
        # =========================
        if op == "news_engine":
            ticker = payload.get("ticker") or payload.get("symbol")
            if not ticker:
                raise HTTPException(422, "input.ticker wajib diisi")

            days = int(payload.get("days", 7))
            limit = int(payload.get("limit", 8))

            res = run_news_engine(
                ticker=ticker,
                window_days=days,
                limit=limit
            )

            return envelope(
                tool=tool,
                operation="news_engine",
                request_id=req.request_id,
                data=res,
                meta={"version": APP_VERSION},
            )

    raise HTTPException(404, "tool/operation tidak dikenali")

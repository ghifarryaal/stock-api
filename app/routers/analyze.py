from __future__ import annotations

from fastapi import APIRouter, Body, Path
from app.models.schemas import AnalyzeRequest
from app.services.combined import combine_analysis
from app.config import (
    DEFAULT_WITH_FUNDAMENTAL, DEFAULT_WITH_TECHNICAL, DEFAULT_WITH_WHALE, DEFAULT_WITH_NEWS,
    APP_VERSION,
)
from app.utils import envelope

router = APIRouter(prefix="/v1", tags=["analysis"])

@router.post("/analyze/{ticker}")
def analyze_post(ticker: str = Path(..., description="Contoh: BBCA.JK"), req: AnalyzeRequest = Body(default=AnalyzeRequest())):
    with_fundamental = DEFAULT_WITH_FUNDAMENTAL if req.with_fundamental is None else req.with_fundamental
    with_technical = DEFAULT_WITH_TECHNICAL if req.with_technical is None else req.with_technical
    with_whale = DEFAULT_WITH_WHALE if req.with_whale is None else req.with_whale
    with_news = DEFAULT_WITH_NEWS if req.with_news is None else req.with_news

    whale_payload = req.whale.model_dump() if req.whale else None

    res = combine_analysis(
        ticker,
        style=req.style,
        with_fundamental=with_fundamental,
        with_technical=with_technical,
        with_whale=with_whale,
        with_news=with_news,
        news_items=req.news_items,
        fetch_news=req.fetch_news,
        news_query=req.news_query,
        period=req.period,
        interval=req.interval,
        rsi_period=req.rsi_period,
        sma_fast=req.sma_fast,
        sma_slow=req.sma_slow,
        whale_payload=whale_payload,
    )
    return envelope(tool="idx_stock_analyzer", operation="analyze", data=res, meta={"version": APP_VERSION})

@router.get("/analyze/{ticker}")
def analyze_get(ticker: str, style: str = "ringkas"):
    res = combine_analysis(ticker, style=style, with_news=False)
    return envelope(tool="idx_stock_analyzer", operation="analyze", data=res, meta={"version": APP_VERSION})

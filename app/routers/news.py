from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any, Optional
from app.services.news import fetch_google_news_rss, veteran_analyze_news

router = APIRouter(prefix="/v1/news", tags=["News"])

@router.get("/rss-veteran")
def rss_veteran(
    ticker: str = Query(..., description="Kode saham IDX, contoh: BBCA"),
    limit: int = Query(5, ge=1, le=20)
):
    try:
        items = fetch_google_news_rss(ticker, limit=limit)
        enriched = []
        for it in items:
            enriched.append({
                **it,
                "veteran": veteran_analyze_news(it.get("title"), it.get("description"))
            })

        return {
            "tool": "idx_market_intel",
            "operation": "news_rss_veteran",
            "success": True,
            "data": {"ticker": f"{ticker}.JK", "total": len(enriched), "items": enriched},
            "errors": [],
            "meta": {"version": "1.0.0"}
        }

    except Exception as e:
        # supaya kamu langsung tau errornya dari response juga
        raise HTTPException(status_code=502, detail=f"Failed to fetch/analyze RSS: {e}")

from fastapi import APIRouter, Query, HTTPException
from app.services.news_engine import run_news_engine
from app.utils import envelope
from app.config import APP_VERSION

router = APIRouter(prefix="/v1/news", tags=["News"])


@router.get("/sentiment")
def news_sentiment(
    ticker: str = Query(..., description="Kode saham IDX, contoh: BBCA"),
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(8, ge=1, le=20),
):
    try:
        res = run_news_engine(
            ticker=ticker,
            window_days=days,
            limit=limit
        )

        return envelope(
            tool="idx_market_intel",
            operation="news_sentiment_engine",
            data=res,
            meta={"version": APP_VERSION}
        )

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch/analyze news sentiment: {e}"
        )

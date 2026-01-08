from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class NewsItem(BaseModel):
    title: str
    description: Optional[str] = None
    link: Optional[str] = None
    source: Optional[str] = None

class WhaleInput(BaseModel):
    symbol: str
    company: Optional[str] = None
    today_price: Optional[float] = None
    today_turnover: Optional[float] = None
    turnover_formatted: Optional[str] = None
    vol_ratio: Optional[float] = None
    is_whale_detected: Optional[bool] = None
    analysis_note: Optional[str] = None

class AnalyzeRequest(BaseModel):
    # News & Whale can be injected from n8n (recommended)
    news_items: Optional[List[NewsItem]] = Field(default=None, description="List berita dari RSS / scraping (opsional).")
    whale: Optional[WhaleInput] = Field(default=None, description="Payload whale alert dari node n8n (opsional).")

    # Fetch news automatically (Google News RSS) if true AND news_items not provided
    fetch_news: bool = False
    news_query: Optional[str] = None  # default: "{ticker} stock IDX"

    # Technical parameters
    period: str = "2y"
    interval: str = "1d"
    rsi_period: int = 14
    sma_fast: int = 20
    sma_slow: int = 50

    # Output style
    style: str = "ringkas"  # ringkas|detail

    # Include toggles
    with_fundamental: Optional[bool] = None
    with_technical: Optional[bool] = None
    with_whale: Optional[bool] = None
    with_news: Optional[bool] = None

class NewsAnalyzeRequest(BaseModel):
    emiten: str
    items: List[NewsItem]

class ToolExecuteRequest(BaseModel):
    tool: str
    operation: str
    input: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None

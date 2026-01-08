from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import yfinance as yf

def get_fundamental(symbol: str) -> Dict[str, Any]:
    t = yf.Ticker(symbol)
    info = t.fast_info or {}
    # 'info' is heavy and sometimes rate-limited; try fast_info first.
    price = info.get("last_price") or info.get("lastPrice") or info.get("regularMarketPrice")
    # fallback
    if price is None:
        hist = t.history(period="5d", interval="1d")
        if not hist.empty:
            price = float(hist["Close"].dropna().iloc[-1])

    # For ratios we may need info; keep best-effort.
    i = {}
    try:
        i = t.info or {}
    except Exception:
        i = {}

    sector = i.get("sector")
    trailing_pe = i.get("trailingPE")
    price_to_book = i.get("priceToBook")
    debt_to_equity = i.get("debtToEquity")  # often in %
    roe = i.get("returnOnEquity")  # fraction
    div_yield = i.get("dividendYield")  # fraction

    return {
        "available": True,
        "price": float(price) if price is not None else None,
        "sector": sector,
        "ratios": {
            "per": trailing_pe,
            "pbv": price_to_book,
            "der": (float(debt_to_equity) / 100.0) if isinstance(debt_to_equity, (int, float)) else debt_to_equity,
            "roe_pct": (float(roe) * 100.0) if isinstance(roe, (int, float)) else None,
            "div_yield_pct": (float(div_yield) * 100.0) if isinstance(div_yield, (int, float)) else None,
        },
        "cached": False,
    }

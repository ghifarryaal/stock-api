from __future__ import annotations

from typing import Any, Dict, Optional
import yfinance as yf

def whale_alert(symbol: str, *, days: int = 5) -> Dict[str, Any]:
    # Pull last ~days sessions; yfinance may return extra due to non-trading days.
    t = yf.Ticker(symbol)
    df = t.history(period=f"{max(days,5)}d", interval="1d")
    if df is None or df.empty or "Volume" not in df.columns:
        return {"available": False, "reason": "no_volume_data"}

    vol = df["Volume"].dropna().astype(float)
    close = df["Close"].dropna().astype(float)
    if len(vol) < 2 or len(close) < 1:
        return {"available": False, "reason": "insufficient_data"}

    current_vol = float(vol.iloc[-1])
    current_price = float(close.iloc[-1])
    turnover = current_vol * current_price

    prev = vol.iloc[:-1]
    avg_prev = float(prev.mean()) if len(prev) else None
    vol_ratio = (current_vol / avg_prev) if avg_prev and avg_prev > 0 else None

    detected = bool(vol_ratio and vol_ratio > 1.5)

    return {
        "available": True,
        "symbol": symbol,
        "today_price": current_price,
        "today_turnover": turnover,
        "vol_ratio": float(vol_ratio) if vol_ratio is not None else None,
        "is_whale_detected": detected,
        "analysis_note": f"Aktivitas volume {vol_ratio:.2f}x lebih tinggi dari rata-rata {len(prev)} hari terakhir." if vol_ratio is not None else "Volume ratio tidak tersedia.",
    }

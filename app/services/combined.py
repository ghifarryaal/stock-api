from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.services.fundamental import get_fundamental
from app.services.technical import analyze_technical
from app.services.whale import whale_alert
from app.services.news import fetch_google_news_rss, veteran_news_analysis
from app.models.schemas import NewsItem


# ======================================================
# FUNDAMENTAL SCORING
# ======================================================
def score_fundamental(ratios: Dict[str, Any]) -> Dict[str, Any]:
    score = 50.0

    per = ratios.get("per")
    pbv = ratios.get("pbv")
    der = ratios.get("der")
    roe_pct = ratios.get("roe_pct")
    div_yield_pct = ratios.get("div_yield_pct")

    if isinstance(per, (int, float)) and per > 0:
        if per < 10:
            score += 12
        elif per < 18:
            score += 6
        elif per > 30:
            score -= 10

    if isinstance(pbv, (int, float)) and pbv > 0:
        if pbv < 1.5:
            score += 8
        elif pbv > 5:
            score -= 8

    if isinstance(der, (int, float)):
        if der < 1:
            score += 6
        elif der > 3:
            score -= 6

    if isinstance(roe_pct, (int, float)):
        if roe_pct >= 15:
            score += 10
        elif roe_pct < 5:
            score -= 6

    if isinstance(div_yield_pct, (int, float)):
        if div_yield_pct >= 4:
            score += 6
        elif div_yield_pct < 1:
            score -= 3

    score = float(max(0.0, min(100.0, score)))
    action = "CICIL" if score >= 65 else "BUANG" if score <= 35 else "PANTAU"

    return {
        "score": score,
        "action": action,
        "details": {
            "per": per,
            "pbv": pbv,
            "der": der,
            "roe": roe_pct,
            "dividend_yield": div_yield_pct,
        },
    }


# ======================================================
# MAIN COMBINE ANALYSIS (FINAL)
# ======================================================
def combine_analysis(
    symbol: str,
    *,
    style: str = "ringkas",
    with_fundamental: bool = True,
    with_technical: bool = True,
    with_whale: bool = True,
    with_news: bool = False,
    news_items: Optional[List[NewsItem]] = None,
    fetch_news: bool = False,
    news_query: Optional[str] = None,
    period: str = "2y",
    interval: str = "1d",

    # kompatibilitas router
    rsi_period: int = 14,
    sma_fast: int = 20,
    sma_slow: int = 50,

    whale_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    fundamental = None
    technical = None
    whale = None
    news = None

    fundamental_score = None
    technical_score = None
    combined_score = None

    score_details = {
        "fundamental": None,
        "technical": None,
        "news": None,
        "whale": None,
    }

    # =========================
    # FUNDAMENTAL
    # =========================
    if with_fundamental:
        try:
            fundamental = get_fundamental(symbol)
            fscore = score_fundamental(fundamental.get("ratios", {}))
            fundamental_score = fscore["score"]
            score_details["fundamental"] = fscore["details"]
        except Exception as e:
            fundamental = {"available": False, "error": str(e)}

    # =========================
    # TECHNICAL
    # =========================
    if with_technical:
        try:
            technical = analyze_technical(symbol, period=period, interval=interval)
            decision = technical.get("decision", {})
            signal = decision.get("signal")

            if signal == "BUY":
                technical_score = 70.0
            elif signal == "SELL":
                technical_score = 30.0
            else:
                technical_score = 50.0

            score_details["technical"] = {
                "signal": signal,
                "bullish_score": decision.get("bullish_score"),
                "bearish_score": decision.get("bearish_score"),
                "rsi_period": rsi_period,
                "sma_fast": sma_fast,
                "sma_slow": sma_slow,
            }

        except Exception as e:
            technical = {"available": False, "error": str(e)}
            score_details["technical"] = {"error": str(e)}

    # =========================
    # WHALE
    # =========================
    if with_whale:
        try:
            whale = whale_payload if whale_payload else whale_alert(symbol)
            score_details["whale"] = {
                "vol_ratio": whale.get("vol_ratio"),
                "is_whale_detected": whale.get("is_whale_detected"),
            } if whale else None
        except Exception as e:
            whale = {"available": False, "error": str(e)}

    # =========================
    # NEWS (ANTI-NULL)
    # =========================
    if with_news:
        try:
            if news_items is None and fetch_news:
                q = news_query or f"{symbol} saham IDX"
                items = fetch_google_news_rss(q)
            else:
                items = news_items or []

            news = veteran_news_analysis(symbol, items)

            score_details["news"] = {
                "kategori": news.get("kategori"),
                "rating": news.get("rating"),
                "total_items": news.get("total_items"),
            }

        except Exception as e:
            news = {
                "available": False,
                "kategori": "Netral",
                "rating": None,
                "reason": str(e),
            }
            score_details["news"] = {"error": str(e)}
    else:
        # 🔒 PENTING: jangan biarkan null
        news = {
            "available": False,
            "kategori": "Netral",
            "rating": None,
            "reason": "disabled_by_flag",
        }
        score_details["news"] = {"reason": "disabled_by_flag"}

    # =========================
    # COMBINE SCORE
    # =========================
    weights = []
    total = 0.0

    if isinstance(fundamental_score, (int, float)):
        weights.append((0.55, fundamental_score))
        total += 0.55

    if isinstance(technical_score, (int, float)):
        weights.append((0.35, technical_score))
        total += 0.35

    bias = 0.0
    if whale and whale.get("is_whale_detected"):
        bias += 3.0
    if news and news.get("kategori") == "Rumor":
        bias -= 2.0

    if total > 0:
        combined_score = sum(w * s for w, s in weights) / total + bias
        combined_score = float(max(0.0, min(100.0, combined_score)))

    action = (
        "CICIL" if combined_score is not None and combined_score >= 68
        else "BUANG" if combined_score is not None and combined_score <= 32
        else "PANTAU"
    )

    # =========================
    # SUMMARY
    # =========================
    summary_parts = [
        symbol,
        f"Skor: {combined_score:.1f}" if combined_score is not None else None,
        f"Teknikal: {technical.get('decision', {}).get('signal')}" if technical else None,
        f"News: {news.get('kategori')}" if news else None,
    ]
    summary = " | ".join([s for s in summary_parts if s])

    return {
        "ticker": symbol,
        "style": style,
        "scores": {
            "fundamental_score": fundamental_score,
            "technical_score": technical_score,
            "combined_score": combined_score,
            "action": action,
            "details": score_details,
        },
        "fundamental": fundamental,
        "technical": technical,
        "whale": whale,
        "news": news,   # ⬅️ TIDAK PERNAH NULL
        "summary": summary,
    }

import feedparser
from typing import Dict, Any, List
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import urllib.parse

try:
    nltk.data.find("vader_lexicon")
except LookupError:
    nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()

RUMOR_KEYWORDS = [
    "rumor", "isu", "spekulasi", "bocoran",
    "gosip", "katanya", "konon", "diduga"
]


# =========================
# QUERY BUILDER
# =========================
def build_news_query(ticker: str) -> str:
    return f"{ticker} saham OR {ticker} stock OR {ticker} emiten"


# =========================
# FETCH RSS
# =========================
def fetch_news(query: str, days: int = 7, limit: int = 10) -> List[Dict]:
    q = urllib.parse.quote(query)
    url = (
        f"https://news.google.com/rss/search?"
        f"q={q}+when:{days}d&hl=id&gl=ID&ceid=ID:id"
    )

    feed = feedparser.parse(url)

    results = []
    for e in feed.entries[:limit]:
        results.append({
            "title": e.get("title", ""),
            "summary": e.get("summary", ""),
            "link": e.get("link", ""),
            "published": e.get("published", "")
        })
    return results


# =========================
# SENTIMENT CORE
# =========================
def analyze_single(title: str, desc: str) -> Dict[str, Any]:
    text = f"{title} {desc}".lower()

    scores = sia.polarity_scores(text)
    compound = scores["compound"]

    rating = (compound + 1) / 2 * 100

    rumor_hits = [k for k in RUMOR_KEYWORDS if k in text]

    if rumor_hits:
        cat = "Rumor"
        rating = min(rating, 45)
    elif compound >= 0.05:
        cat = "Positif"
    elif compound <= -0.05:
        cat = "Negatif"
    else:
        cat = "Netral"

    return {
        "sentiment": cat,
        "score": round(rating, 2),
        "compound": compound,
        "rumor_hits": rumor_hits
    }


# =========================
# MAIN ENGINE
# =========================
def run_news_engine(
    ticker: str,
    window_days: int = 7,
    limit: int = 10
) -> Dict[str, Any]:

    query = build_news_query(ticker)
    items = fetch_news(query, window_days, limit)

    if not items:
        return {
            "source": "google_news",
            "ticker": ticker,
            "window": f"{window_days}d",
            "available": False
        }

    breakdown = {
        "Positif": 0,
        "Negatif": 0,
        "Netral": 0,
        "Rumor": 0
    }

    scores = []
    enriched = []

    for it in items:
        s = analyze_single(it["title"], it["summary"])

        breakdown[s["sentiment"]] += 1
        scores.append(s["score"])

        enriched.append({
            "title": it["title"],
            "sentiment": s["sentiment"],
            "score": s["score"],
            "published": it["published"],
            "link": it["link"]
        })

    avg_score = sum(scores) / len(scores)

    # Bias label
    if avg_score >= 65:
        bias = "Bullish"
    elif avg_score <= 40:
        bias = "Bearish"
    else:
        bias = "Neutral"

    if breakdown["Rumor"] > 0:
        overall = "Rumor"
    elif breakdown["Positif"] > breakdown["Negatif"]:
        overall = "Positif"
    elif breakdown["Negatif"] > breakdown["Positif"]:
        overall = "Negatif"
    else:
        overall = "Netral"

    return {
        "source": "google_news",
        "ticker": ticker,
        "window": f"{window_days}d",
        "total_news": len(enriched),
        "available": True,
        "overall_sentiment": overall,
        "sentiment_score": round(avg_score, 2),
        "sentiment_bias": bias,
        "breakdown": breakdown,
        "items": enriched
    }

# app/services/news.py
import feedparser
from typing import Any, Dict, List, Optional
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download required VADER lexicon
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

# Keyword lists untuk deteksi rumor (tetap digunakan)
RUMOR_KEYWORDS = ["rumor", "isu", "spekulasi", "bocoran", "gosip", "tidak terkonfirmasi", "katanya", "konon", "diduga"]

def fetch_google_news_rss(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Fetch news from Google News RSS feed."""
    url = f"https://news.google.com/rss/search?q={query}%20when:7d&ceid=ID:id&hl=id"
    feed = feedparser.parse(url)
    
    items = []
    for entry in feed.entries[:limit]:
        items.append({
            "title": entry.get("title", ""),
            "description": entry.get("summary", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
        })
    
    return items

def veteran_analyze_news(title: Optional[str], description: Optional[str] = None) -> Dict[str, Any]:
    """Analyze news sentiment using VADER sentiment analysis."""
    text = f"{title or ''} {description or ''}".strip()
    
    if not text:
        return {
            "available": False,
            "kategori": "Netral",
            "rating": None,
            "reasons": ["judul/summary kosong"]
        }

    # Deteksi rumor
    text_lower = text.lower()
    hits_rumor = [kw for kw in RUMOR_KEYWORDS if kw in text_lower]
    
    # Analisis sentimen menggunakan VADER
    scores = sia.polarity_scores(text)
    compound = scores['compound']  # Nilai -1 (negatif) hingga 1 (positif)
    
    # Konversi compound score ke rating 0-100
    rating = (compound + 1) / 2 * 100
    
    # Tentukan kategori berdasarkan sentimen
    if hits_rumor:
        kategori = "Rumor"
        rating = min(rating, 45)  # Cap rating untuk rumor
    elif compound >= 0.05:
        kategori = "Positif"
    elif compound <= -0.05:
        kategori = "Negatif"
    else:
        kategori = "Netral"

    return {
        "available": True,
        "kategori": kategori,
        "rating": float(round(rating, 2)),
        "sentiment_scores": {
            "positive": float(scores['pos']),
            "negative": float(scores['neg']),
            "neutral": float(scores['neu']),
            "compound": float(scores['compound'])
        },
        "reasons": {
            "rumor": hits_rumor,
        },
    }

def veteran_news_analysis(emiten: str, items: List[Any]) -> Dict[str, Any]:
    """Analyze multiple news items and provide overall sentiment."""
    if not items:
        return {
            "available": False,
            "kategori": "Netral",
            "rating": None,
            "reason": "news_items kosong"
        }

    enriched = []
    ratings: List[float] = []
    kategori_counter = {"Positif": 0, "Negatif": 0, "Netral": 0, "Rumor": 0}

    for raw in items:
        obj = raw.model_dump() if hasattr(raw, "model_dump") else dict(raw)
        vet = veteran_analyze_news(obj.get("title"), obj.get("description"))
        
        if vet.get("rating") is not None:
            ratings.append(vet["rating"])
        
        kategori = vet.get("kategori", "Netral")
        kategori_counter[kategori] = kategori_counter.get(kategori, 0) + 1
        enriched.append({**obj, "veteran": vet})

    # Tentukan sentimen keseluruhan
    if kategori_counter["Rumor"] > 0:
        overall_kategori = "Rumor"
    elif kategori_counter["Positif"] > kategori_counter["Negatif"]:
        overall_kategori = "Positif"
    elif kategori_counter["Negatif"] > kategori_counter["Positif"]:
        overall_kategori = "Negatif"
    else:
        overall_kategori = "Netral"

    avg_rating = float(round(sum(ratings) / len(ratings), 2)) if ratings else None

    return {
        "available": True,
        "emiten": emiten,
        "total_items": len(enriched),
        "kategori": overall_kategori,
        "rating": avg_rating,
        "kategori_breakdown": kategori_counter,
        "items": enriched,
    }
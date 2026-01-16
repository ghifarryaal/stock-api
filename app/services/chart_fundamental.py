import yfinance as yf
import time

# ================= CACHE =================
CACHE = {}
CACHE_TTL = 3600

def get_cache(key):
    if key in CACHE:
        data, exp = CACHE[key]
        if time.time() < exp:
            return data
        del CACHE[key]
    return None

def set_cache(key, value):
    CACHE[key] = (value, time.time() + CACHE_TTL)

# ================= SCORING =================
def scoring(data):
    score = 0
    notes = []

    if data["rev_growth"] > 5:
        score += 30
        notes.append("Revenue bertumbuh")
    else:
        notes.append("Revenue stagnan")

    if data["profit_growth"] > 5:
        score += 40
        notes.append("Laba bertumbuh")
    else:
        notes.append("Laba melemah")

    if data["avg_margin"] > 10:
        score += 20
        notes.append("Margin sehat")
    else:
        notes.append("Margin tipis")

    if data["positive_profit"] >= 3:
        score += 10
        notes.append("Profit konsisten")

    verdict = "BURUK"
    if score >= 70:
        verdict = "SEHAT"
    elif score >= 40:
        verdict = "NETRAL"

    return {
        "score": score,
        "verdict": verdict,
        "notes": notes
    }

# ================= MAIN =================
def get_fundamental_chart(ticker: str):

    cache_key = f"fundamental_{ticker}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    symbol = ticker.upper()
    if not symbol.endswith(".JK"):
        symbol += ".JK"

    stock = yf.Ticker(symbol)
    df = stock.quarterly_financials

    if df.empty:
        return None

    result = []
    margins = []
    profits = []

    prev_rev = None
    prev_profit = None
    rev_growth = 0
    profit_growth = 0

    for col in df.columns[::-1]:

        revenue = df.loc["Total Revenue", col]
        profit = df.loc["Net Income", col]

        margin = round((profit / revenue) * 100, 2)

        margins.append(margin)
        profits.append(profit)

        if prev_rev:
            rev_growth = ((revenue - prev_rev) / prev_rev) * 100
        if prev_profit:
            profit_growth = ((profit - prev_profit) / prev_profit) * 100

        prev_rev = revenue
        prev_profit = profit

        result.append({
            "date": str(col),
            "revenue": int(revenue),
            "net_income": int(profit),
            "net_margin": margin
        })

    analytics = {
        "rev_growth": round(rev_growth, 2),
        "profit_growth": round(profit_growth, 2),
        "avg_margin": round(sum(margins) / len(margins), 2),
        "positive_profit": len([p for p in profits if p > 0])
    }

    score = scoring(analytics)

    response = {
        "ticker": symbol,
        "chart": result,
        "analytics": analytics,
        "score": score
    }

    set_cache(cache_key, response)
    return response

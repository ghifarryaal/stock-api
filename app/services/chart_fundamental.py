import yfinance as yf
import time

# ================= CACHE =================
CACHE = {}
CACHE_TTL = 3600

FX_CACHE = {}
FX_TTL = 3600


def get_cache(key):
    if key in CACHE:
        data, exp = CACHE[key]
        if time.time() < exp:
            return data
        del CACHE[key]
    return None


def set_cache(key, value):
    CACHE[key] = (value, time.time() + CACHE_TTL)


def get_fx_cache(key):
    if key in FX_CACHE:
        rate, exp = FX_CACHE[key]
        if time.time() < exp:
            return rate
        del FX_CACHE[key]
    return None


def set_fx_cache(key, value):
    FX_CACHE[key] = (value, time.time() + FX_TTL)


# ================= FX =================
def get_usd_idr_rate():
    cached = get_fx_cache("USDIDR")
    if cached:
        return cached

    fx = yf.Ticker("USDIDR=X")
    hist = fx.history(period="1d")

    rate = float(hist["Close"].iloc[-1])

    set_fx_cache("USDIDR", rate)
    return rate


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

    # ================= CURRENCY (IMPORTANT FIX) =================
    financial_currency = stock.info.get("financialCurrency", "IDR")

    fx_rate = 1
    converted = False

    if financial_currency == "USD":
        fx_rate = get_usd_idr_rate()
        converted = True

    result = []
    margins = []
    profits = []

    prev_rev = None
    prev_profit = None
    rev_growth = 0
    profit_growth = 0

    for col in df.columns[::-1]:

        revenue_raw = df.loc["Total Revenue", col]
        profit_raw = df.loc["Net Income", col]

        revenue = revenue_raw * fx_rate
        profit = profit_raw * fx_rate

        margin = round((profit_raw / revenue_raw) * 100, 2)

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

        # PRICE currency (IDX = IDR)
        "price_currency": stock.info.get("currency", "IDR"),

        # FINANCIAL currency (important)
        "financial_currency": financial_currency,

        # OUTPUT
        "currency": "IDR",
        "fx_rate": round(fx_rate, 2),
        "converted": converted,

        "chart": result,
        "analytics": analytics,
        "score": score
    }

    set_cache(cache_key, response)
    return response


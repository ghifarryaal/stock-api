import yfinance as yf
import time

# ===== CACHE =====
CACHE = {}
CACHE_TTL = 300  # 5 menit

def get_chart_data(ticker: str):

    now = time.time()

    symbol = ticker.upper()
    if len(symbol) == 4 and not symbol.endswith(".JK"):
        symbol += ".JK"

    # === CACHE HIT ===
    if symbol in CACHE:
        cached = CACHE[symbol]
        if now - cached["time"] < CACHE_TTL:
            print(f"[CACHE HIT] {symbol}")
            return cached["data"]

    print(f"[FETCH YAHOO] {symbol}")

    stock = yf.Ticker(symbol)
    hist = stock.history(
        period="1y",
        interval="1d"
    )

    if hist.empty:
        return None

    hist["EMA20"] = hist["Close"].ewm(span=20).mean()
    hist["EMA50"] = hist["Close"].ewm(span=50).mean()
    hist = hist.dropna()

    data = [
        {
            "date": d.strftime("%Y-%m-%d"),
            "price": round(r["Close"], 2),
            "ema20": round(r["EMA20"], 2),
            "ema50": round(r["EMA50"], 2),
        }
        for d, r in hist.iterrows()
    ]

    result = {
        "ticker": symbol,
        "data": data
    }

    # SAVE CACHE
    CACHE[symbol] = {
        "time": now,
        "data": result
    }

    return result

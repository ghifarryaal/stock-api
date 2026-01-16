import yfinance as yf
from app.core.cache import get_cache, set_cache
from app.core.syariah import SYARIAH_SET


def is_syariah(ticker):
    return ticker.replace(".JK","") in SYARIAH_SET


def is_suspended(hist):
    if hist.empty:
        return True

    last_vol = hist["Volume"].tail(5)
    if (last_vol == 0).all():
        return True

    return False


def get_chart_data(ticker: str):

    symbol = ticker.upper()
    if len(symbol) == 4 and not symbol.endswith(".JK"):
        symbol += ".JK"

    # === CACHE ===
    cached = get_cache(symbol)
    if cached:
        return cached

    stock = yf.Ticker(symbol)
    hist = stock.history(period="1y", interval="1d")

    suspend_status = is_suspended(hist)

    if hist.empty:
        result = {
            "ticker": symbol,
            "syariah": is_syariah(symbol),
            "suspend": True,
            "data": []
        }
        set_cache(symbol, result)
        return result

    hist["EMA20"] = hist["Close"].ewm(span=20).mean()
    hist["EMA50"] = hist["Close"].ewm(span=50).mean()
    hist = hist.dropna()

    data = [
        {
            "date": d.strftime("%Y-%m-%d"),
            "open": round(r["Open"], 2),
            "high": round(r["High"], 2),
            "low": round(r["Low"], 2),
            "close": round(r["Close"], 2),
            "price": round(r["Close"], 2),
            "volume": int(r["Volume"]),
            "ema20": round(r["EMA20"], 2),
            "ema50": round(r["EMA50"], 2),
        }
        for d, r in hist.iterrows()
    ]

    result = {
        "ticker": symbol,
        "syariah": is_syariah(symbol),
        "suspend": suspend_status,
        "data": data
    }

    set_cache(symbol, result)
    return result

import yfinance as yf
import time
from app.services.chart_fundamental import get_usd_idr_rate

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


def pick_row(df, keywords):
    for row in df.index:
        for k in keywords:
            if k.lower() in row.lower():
                return row
    return None


# ================= SCORING =================
def score_balance(latest):
    score = 0
    notes = []

    der = latest["debt_equity_ratio"]

    if der < 1:
        score += 50
        notes.append("DER sehat (<1)")
    elif der < 2:
        score += 30
        notes.append("DER moderat (1-2)")
    else:
        notes.append("DER tinggi (>2)")

    if latest["equity"] > 0:
        score += 30
        notes.append("Ekuitas positif")
    else:
        notes.append("Ekuitas negatif")

    if latest["total_assets"] > latest["total_liabilities"]:
        score += 20
        notes.append("Aset > Liabilitas")

    if score >= 70:
        status = "SEHAT"
    elif score >= 40:
        status = "WASPADA"
    else:
        status = "BAHAYA"

    return {
        "score": score,
        "status": status,
        "notes": notes
    }


# ================= MAIN =================
def get_balance_chart(ticker: str):

    cache_key = f"balance_{ticker}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    symbol = ticker.upper()
    if not symbol.endswith(".JK"):
        symbol += ".JK"

    stock = yf.Ticker(symbol)
    df = stock.quarterly_balance_sheet

    if df.empty:
        return None

    fin_currency = stock.info.get("financialCurrency", "IDR")

    fx_rate = 1
    converted = False
    if fin_currency == "USD":
        fx_rate = get_usd_idr_rate()
        converted = True

    asset_row = pick_row(df, ["total assets"])
    liab_row = pick_row(df, ["total liabilities", "liab"])

    if not asset_row or not liab_row:
        return None

    result = []

    for col in df.columns[::-1]:

        assets = df.loc[asset_row, col] * fx_rate
        liab = df.loc[liab_row, col] * fx_rate

        equity = assets - liab
        der = round(liab / equity, 2) if equity else 99

        result.append({
            "date": str(col),
            "total_assets": int(assets),
            "total_liabilities": int(liab),
            "equity": int(equity),
            "debt_equity_ratio": der
        })

    latest = result[-1]
    score = score_balance(latest)

    response = {
        "ticker": symbol,
        "financial_currency": fin_currency,
        "currency": "IDR",
        "fx_rate": round(fx_rate, 2),
        "converted": converted,
        "chart": result,
        "score": score
    }

    set_cache(cache_key, response)
    return response

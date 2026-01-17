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
def score_cashflow(data):
    score = 0
    notes = []

    last = data[-1]
    prev = data[-2] if len(data) > 1 else None

    # Operating cashflow
    if last["operating"] > 0:
        score += 40
        notes.append("OCF positif")
    else:
        notes.append("OCF negatif")

    # Trend OCF
    if prev and last["operating"] > prev["operating"]:
        score += 20
        notes.append("OCF bertumbuh")

    # Investing
    if last["investing"] < 0:
        score += 20
        notes.append("Investasi ekspansi (CFI negatif)")
    else:
        notes.append("Minim investasi")

    # Financing
    if last["financing"] < 0:
        score += 20
        notes.append("Pelunasan utang/dividen")
    else:
        notes.append("Penambahan utang / right issue")

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
def get_cashflow_chart(ticker: str):

    cache_key = f"cashflow_{ticker}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    symbol = ticker.upper()
    if not symbol.endswith(".JK"):
        symbol += ".JK"

    stock = yf.Ticker(symbol)
    df = stock.quarterly_cashflow

    if df.empty:
        return None

    fin_currency = stock.info.get("financialCurrency", "IDR")

    fx_rate = 1
    converted = False
    if fin_currency == "USD":
        fx_rate = get_usd_idr_rate()
        converted = True

    op_row = pick_row(df, ["operating"])
    inv_row = pick_row(df, ["investing"])
    fin_row = pick_row(df, ["financing"])

    if not op_row or not inv_row or not fin_row:
        return None

    result = []

    for col in df.columns[::-1]:

        operating = df.loc[op_row, col] * fx_rate
        investing = df.loc[inv_row, col] * fx_rate
        financing = df.loc[fin_row, col] * fx_rate

        result.append({
            "date": str(col),
            "operating": int(operating),
            "investing": int(investing),
            "financing": int(financing)
        })

    score = score_cashflow(result)

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

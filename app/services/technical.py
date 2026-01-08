from typing import Dict, Any
import yfinance as yf
import pandas as pd
import numpy as np
from fastapi import FastAPI, Query

# ======================================================
# FASTAPI APP (OPTIONAL – boleh dipakai atau tidak)
# ======================================================
app = FastAPI(
    title="Technical Analysis Service",
    version="1.1.0"
)

# ======================================================
# UTIL
# ======================================================
def safe(v):
    return None if pd.isna(v) else float(v)


# ======================================================
# FETCH DATA
# ======================================================
def fetch_data(symbol: str, period: str, interval: str) -> pd.DataFrame:
    df = yf.Ticker(symbol).history(period=period, interval=interval)
    if df is None or df.empty:
        return pd.DataFrame()
    return df.dropna()


# ======================================================
# INDICATORS (MANUAL – NO pandas_ta)
# ======================================================

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(close: pd.Series):
    ema12 = ema(close, 12)
    ema26 = ema(close, 26)
    macd_line = ema12 - ema26
    signal_line = ema(macd_line, 9)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    mf = tp * df["Volume"]

    positive = mf.where(tp > tp.shift(1), 0)
    negative = mf.where(tp < tp.shift(1), 0)

    pos_sum = positive.rolling(period).sum()
    neg_sum = negative.rolling(period).sum()

    mfr = pos_sum / neg_sum.replace(0, np.nan)
    return 100 - (100 / (1 + mfr))


def stoch_rsi(close: pd.Series, period: int = 14):
    rsi_val = rsi(close, period)
    min_rsi = rsi_val.rolling(period).min()
    max_rsi = rsi_val.rolling(period).max()

    stoch = (rsi_val - min_rsi) / (max_rsi - min_rsi)
    k = stoch.rolling(3).mean() * 100
    d = k.rolling(3).mean()
    return k, d


# ======================================================
# FIBONACCI
# ======================================================
def fibonacci(df: pd.DataFrame, period: int = 60) -> Dict[str, Any]:
    data = df.tail(period)
    high = data["High"].max()
    low = data["Low"].min()
    diff = high - low

    return {
        "swing_high": safe(high),
        "swing_low": safe(low),
        "levels": {
            "0.0": safe(low),
            "0.236": safe(low + diff * 0.236),
            "0.382": safe(low + diff * 0.382),
            "0.5": safe(low + diff * 0.5),
            "0.618": safe(low + diff * 0.618),
            "0.786": safe(low + diff * 0.786),
            "1.0": safe(high),
            "1.272": safe(high + diff * 0.272),
            "1.618": safe(high + diff * 0.618),
            "2.618": safe(high + diff * 1.618),
        }
    }


# ======================================================
# PIVOT POINTS
# ======================================================
def pivot_points(df: pd.DataFrame, period: int = 15) -> Dict[str, Any]:
    data = df.tail(period)
    high = data["High"].max()
    low = data["Low"].min()
    close = data["Close"].iloc[-1]

    p = (high + low + close) / 3

    return {
        "pivot": safe(p),
        "r1": safe((2 * p) - low),
        "s1": safe((2 * p) - high),
        "r2": safe(p + (high - low)),
        "s2": safe(p - (high - low)),
    }


# ======================================================
# SCORING
# ======================================================
def scoring(rsi_sig: str, mfi_sig: str, macd_trend: str, stoch_trend: str) -> Dict[str, Any]:
    bull, bear = 0, 0

    if rsi_sig == "oversold":
        bull += 1
    if rsi_sig == "overbought":
        bear += 1

    if mfi_sig == "oversold":
        bull += 1
    if mfi_sig == "overbought":
        bear += 1

    bull += 1 if macd_trend == "bullish" else 0
    bear += 1 if macd_trend == "bearish" else 0

    bull += 1 if stoch_trend == "bullish" else 0
    bear += 1 if stoch_trend == "bearish" else 0

    if bull >= 3:
        signal = "BUY"
    elif bear >= 3:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "bullish_score": bull,
        "bearish_score": bear,
        "signal": signal
    }


# ======================================================
# CORE SERVICE FUNCTION (INI YANG DICARI combined.py)
# ======================================================
def analyze_technical(
    symbol: str,
    period: str = "2y",
    interval: str = "1d"
) -> Dict[str, Any]:

    df = fetch_data(symbol, period, interval)
    if df.empty:
        return {"status": "error", "message": "No data"}

    close = df["Close"]

    rsi_val = rsi(close).iloc[-1]
    macd_line, signal_line, hist = macd(close)
    mfi_val = mfi(df).iloc[-1]
    k, d = stoch_rsi(close)

    rsi_sig = "oversold" if rsi_val < 30 else "overbought" if rsi_val > 70 else "neutral"
    mfi_sig = "oversold" if mfi_val < 20 else "overbought" if mfi_val > 80 else "neutral"
    macd_trend = "bullish" if macd_line.iloc[-1] > signal_line.iloc[-1] else "bearish"
    stoch_trend = "bullish" if k.iloc[-1] > d.iloc[-1] else "bearish"

    decision = scoring(rsi_sig, mfi_sig, macd_trend, stoch_trend)

    return {
        "symbol": symbol,
        "price": {
            "close": safe(close.iloc[-1]),
            "volume": int(df["Volume"].iloc[-1]),
        },
        "rsi": {"value": safe(rsi_val), "signal": rsi_sig},
        "macd": {
            "macd": safe(macd_line.iloc[-1]),
            "signal": safe(signal_line.iloc[-1]),
            "histogram": safe(hist.iloc[-1]),
            "trend": macd_trend,
        },
        "mfi": {"value": safe(mfi_val), "signal": mfi_sig},
        "stoch_rsi": {
            "k": safe(k.iloc[-1]),
            "d": safe(d.iloc[-1]),
            "trend": stoch_trend,
        },
        "fibonacci": fibonacci(df),
        "pivot": pivot_points(df),
        "decision": decision,
    }


# ======================================================
# OPTIONAL API ENDPOINT
# ======================================================
@app.get("/technical")
def technical_endpoint(
    symbol: str = Query(...),
    period: str = Query("2y"),
    interval: str = Query("1d"),
):
    return {
        "status": "ok",
        "analysis": analyze_technical(symbol, period, interval),
    }

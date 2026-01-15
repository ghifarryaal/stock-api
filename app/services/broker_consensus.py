import yfinance as yf


def analyze_broker_consensus(ticker: str):
    try:
        stock = yf.Ticker(ticker)

        # =========================
        # SUMMARY (INI KUNCINYA)
        # =========================
        summary = stock.recommendations_summary

        if summary is None or summary.empty:
            return {
                "available": False,
                "reason": "no_data"
            }

        row = summary.iloc[0].to_dict()

        # contoh field:
        # strongBuy, buy, hold, sell, strongSell

        strong_buy = int(row.get("strongBuy", 0))
        buy = int(row.get("buy", 0))
        hold = int(row.get("hold", 0))
        sell = int(row.get("sell", 0))
        strong_sell = int(row.get("strongSell", 0))

        total = strong_buy + buy + hold + sell + strong_sell

        if total == 0:
            return {
                "available": False,
                "reason": "no_data"
            }

        # =========================
        # HITUNG AVERAGE RATING
        # =========================
        avg = (
            strong_buy * 1 +
            buy * 2 +
            hold * 3 +
            sell * 4 +
            strong_sell * 5
        ) / total

        avg = round(avg, 2)

        # =========================
        # CONSENSUS
        # =========================
        if avg <= 1.5:
            consensus = "Strong Buy"
        elif avg <= 2.5:
            consensus = "Buy"
        elif avg <= 3.5:
            consensus = "Hold"
        elif avg <= 4.5:
            consensus = "Sell"
        else:
            consensus = "Strong Sell"

        # =========================
        # TARGET PRICE
        # =========================
        info = stock.info

        target_price = info.get("targetMeanPrice")
        current_price = info.get("currentPrice")

        upside = None
        if target_price and current_price:
            upside = round(
                ((target_price - current_price) / current_price) * 100,
                2
            )

        return {
            "available": True,
            "consensus": consensus,
            "average_rating": avg,
            "total_analysts": total,
            "confidence": "High" if total >= 10 else "Low",

            # breakdown (UI butuh ini)
            "breakdown": {
                "strong_buy": strong_buy,
                "buy": buy,
                "hold": hold,
                "sell": sell,
                "strong_sell": strong_sell,
            },

            # target
            "target_price": target_price,
            "current_price": current_price,
            "upside_pct": upside,
        }

    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }

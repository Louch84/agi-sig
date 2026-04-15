#!/usr/bin/env python3
"""
MA Signals Module — Golden Cross / Death Cross detection.
Computes EMA 9, 21, 50, 200 and returns crossover signals.
"""
import yfinance as yf


def compute_ema(prices, period):
    """Compute EMA for a list of prices."""
    k = 2 / (period + 1)
    ema = float(prices[0])
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return ema


def get_ma_signals(ticker: str, price: float) -> dict:
    """
    Get all MA signals for a ticker.
    Returns: {ma_signal, short_signal, ema9, ema21, ema50, ema200, golden_cross_bars, death_cross_bars}
    """
    result = {
        "ticker": ticker,
        "price": price,
        "ma_signal": "NEUTRAL",       # GOLDEN_CROSS, DEATH_CROSS, or NEUTRAL
        "short_signal": "NEUTRAL",     # ABOVE_EMA21, BELOW_EMA21
        "ema9": None,
        "ema21": None,
        "ema50": None,
        "ema200": None,
        "golden_cross_bars": 0,         # Days since golden cross
        "death_cross_bars": 0,          # Days since death cross
        "slope_50": 0,                 # % change in EMA50 over last 5 days
    }

    try:
        t = yf.Ticker(ticker)
        h = t.history(period="6mo", interval="1d")

        if h.empty or len(h) < 60:
            return result

        closes = h["Close"].values

        # Compute EMAs
        ema9 = compute_ema(closes, 9)
        ema21 = compute_ema(closes, 21)
        ema50 = compute_ema(closes, 50) if len(closes) >= 50 else None
        ema200 = compute_ema(closes, 200) if len(closes) >= 200 else None

        result["ema9"] = round(ema9, 2)
        result["ema21"] = round(ema21, 2)
        if ema50:
            result["ema50"] = round(ema50, 2)
        if ema200:
            result["ema200"] = round(ema200, 2)

        # Slope of EMA50 (% change over last 5 days)
        if ema50 and len(closes) >= 55:
            ema50_5d_ago = compute_ema(closes[:-5], 50)
            result["slope_50"] = round(((ema50 - ema50_5d_ago) / ema50_5d_ago) * 100, 2)

        # Short-term signal: price vs EMA21
        result["short_signal"] = "ABOVE_EMA21" if price > ema21 else "BELOW_EMA21"

        # Golden / Death cross — need 50 and 200
        if ema50 and ema200:
            if ema50 > ema200:
                result["ma_signal"] = "GOLDEN_CROSS"  # Bullish
            elif ema50 < ema200:
                result["ma_signal"] = "DEATH_CROSS"   # Bearish

        # Count bars since cross
        # Compute EMA for each historical bar to find the cross point
        golden_cross_bars = 0
        death_cross_bars = 0
        if len(closes) >= 200:
            for i in range(len(closes) - 1, max(50, len(closes) - 60), -1):
                window = closes[:i]
                if len(window) < 50:
                    break
                e50 = compute_ema(window, 50)
                e200 = compute_ema(window, 200)
                next_window = closes[:i+1]
                e50_next = compute_ema(next_window, 50)
                e200_next = compute_ema(next_window, 200)

                # Did 50 cross 200 at this bar?
                if e50 > e200 and e50_next <= e200_next:
                    golden_cross_bars = len(closes) - i
                    break
                elif e50 < e200 and e50_next >= e200_next:
                    death_cross_bars = len(closes) - i
                    break

        result["golden_cross_bars"] = golden_cross_bars
        result["death_cross_bars"] = death_cross_bars

    except Exception as e:
        result["error"] = str(e)

    return result


def ma_confidence_score(ma: dict) -> dict:
    """
    Given MA signals, compute a confidence score for longs and shorts.
    Returns: {bullish_score, bearish_score, recommendation}
    """
    bullish = 0
    bearish = 0

    # Golden cross = bullish
    if ma["ma_signal"] == "GOLDEN_CROSS":
        bullish += 40
        # Recent cross = stronger signal
        if ma["golden_cross_bars"] <= 5:
            bullish += 15
        elif ma["golden_cross_bars"] <= 20:
            bullish += 8
    elif ma["ma_signal"] == "DEATH_CROSS":
        bearish += 40
        if ma["death_cross_bars"] <= 5:
            bearish += 15
        elif ma["death_cross_bars"] <= 20:
            bearish += 8

    # Price vs EMA21
    if ma["short_signal"] == "ABOVE_EMA21":
        bullish += 15
    else:
        bearish += 15

    # EMA50 slope
    slope = ma.get("slope_50", 0)
    if slope > 2:
        bullish += 20
    elif slope > 0.5:
        bullish += 10
    elif slope < -2:
        bearish += 20
    elif slope < -0.5:
        bearish += 10

    # EMA9 vs EMA21
    ema9 = ma.get("ema9")
    ema21 = ma.get("ema21")
    if ema9 and ema21:
        if ema9 > ema21:
            bullish += 10
        else:
            bearish += 10

    total = bullish + bearish
    bullish_pct = round(bullish / total * 100) if total > 0 else 50

    if bullish_pct >= 70:
        rec = "LONG"
    elif bullish_pct >= 55:
        rec = "CAUTIOUS_LONG"
    elif bullish_pct <= 30:
        rec = "SHORT"
    elif bullish_pct <= 45:
        rec = "CAUTIOUS_SHORT"
    else:
        rec = "NEUTRAL"

    return {
        "bullish_score": bullish_pct,
        "bearish_score": 100 - bullish_pct,
        "recommendation": rec,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: ma_signals.py <TICKER>")
        sys.exit(1)

    ticker = sys.argv[1].upper()

    # Get current price
    t = yf.Ticker(ticker)
    price = t.info.get("currentPrice") or t.info.get("regularMarketPrice")
    if not price:
        print(f"Could not get price for {ticker}")
        sys.exit(1)

    ma = get_ma_signals(ticker, price)
    conf = ma_confidence_score(ma)

    print(f"\n{'='*50}")
    print(f"MA SIGNALS: {ticker} @ ${price}")
    print(f"{'='*50}")
    print(f"Signal:     {ma['ma_signal']} ({ma['golden_cross_bars']} bars ago)" if ma['ma_signal'] != 'NEUTRAL' else f"Signal:     NEUTRAL")
    print(f"Short:      {ma['short_signal']}")
    print(f"EMA9:       ${ma['ema9']}")
    print(f"EMA21:      ${ma['ema21']}")
    print(f"EMA50:      ${ma['ema50']} (slope: {ma['slope_50']:+.2f}%)")
    print(f"EMA200:     ${ma['ema200']}")
    print(f"\nConfidence: {conf['recommendation']} ({conf['bullish_score']}% bullish / {conf['bearish_score']}% bearish)")

#!/usr/bin/env python3
"""
Short Squeeze Scanner — Gap Down + Short Interest + Technicals
Finds stocks setup to squeeze and gap fill.
"""
import yfinance as yf
import numpy as np
import json
import os
import sys
from datetime import datetime, timedelta
from urllib.error import URLError

# Universe — curated stocks known for squeeze potential
UNIVERSE = [
    "TSLA", "NVDA", "AMD", "AVGO", "MU", "QQQ",
    "AAPL", "AMZN", "META", "MSFT", "GOOGL", "NFLX",
    "PLTR", "SOFI", "GME", "AMC", "BBBY", "BB", "NOK",
    "RIVN", "LCID", "F", "GM",
    "SPY", "QCOM", "MSTR", "COIN", "HOOD",
    "SMCI", "ASTS", "RKLB", "LUNR",
    "TSM", "ASML", "AMAT", "LRCX",
    "ARM", "SNAP", "PINS", "RBLX",
    "DIRI", "NAAS",  # micro-caps with high SI
]

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "squeeze-scanner.json")


def get_gap_data(ticker, period="5d"):
    """Get gap down data for a ticker."""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period, interval="1d")
        if hist.empty or len(hist) < 3:
            return None

        closes = hist['Close'].values
        volumes = hist['Volume'].values
        opens = hist['Open'].values
        highs = hist['High'].values
        lows = hist['Low'].values

        # Today's data
        today_close = closes[-1]
        today_open = opens[-1]
        today_vol = volumes[-1]
        today_high = highs[-1]
        today_low = lows[-1]

        # Yesterday's close
        yesterday_close = closes[-2]

        # Gap calculation
        gap_pct = ((today_open - yesterday_close) / yesterday_close) * 100

        # Yesterday's range
        yesterday_range = highs[-2] - lows[-2]
        avg_volume_5d = np.mean(volumes[:-1])

        # RSI (14-day)
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else np.mean(gains)
        avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else np.mean(losses)
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))

        # MACD
        ema12 = _ema(closes, 12)
        ema26 = _ema(closes, 26)
        macd = ema12 - ema26
        signal = _ema(np.concatenate([[ema12[-1]], [macd[-1]]]), 9)
        macd_hist = macd[-1] - signal[-1] if len(signal) > 0 else 0

        # Volume ratio
        vol_ratio = today_vol / avg_volume_5d if avg_volume_5d > 0 else 1

        # Distance from VWAP
        vwap = np.mean(hist['High'].values[-20:] + hist['Low'].values[-20:]) / 2
        vwap_dist = ((today_close - vwap) / vwap) * 100

        # 52-week position
        hist52 = t.history(period="1y")
        high52 = hist52['High'].max()
        low52 = hist52['Low'].min()

        return {
            "today_close": round(today_close, 2),
            "today_open": round(today_open, 2),
            "yesterday_close": round(yesterday_close, 2),
            "gap_pct": round(gap_pct, 2),
            "gap_filled_pct": round(((today_close - today_open) / (yesterday_close - today_open)) * 100, 1) if (yesterday_close - today_open) != 0 else 0,
            "today_high": round(today_high, 2),
            "today_low": round(today_low, 2),
            "rsi": round(rsi, 1),
            "macd": round(macd[-1], 3),
            "macd_hist": round(macd_hist, 3),
            "vol_ratio": round(vol_ratio, 2),
            "vwap_dist": round(vwap_dist, 2),
            "52w_high": round(high52, 2),
            "52w_low": round(low52, 2),
            "52w_pct": round(((today_close - low52) / (high52 - low52)) * 100, 1),
            "avg_vol_5d": round(avg_volume_5d, 0),
            "today_vol": round(today_vol, 0),
        }
    except Exception as e:
        return None


def _ema(data, period):
    """Calculate EMA."""
    data = np.array(data)
    ema = np.zeros(len(data))
    ema[0] = data[0]
    multiplier = 2 / (period + 1)
    for i in range(1, len(data)):
        ema[i] = (data[i] - ema[i-1]) * multiplier + ema[i-1]
    return ema


def get_short_data(ticker):
    """Get short interest data (from yfinance info)."""
    try:
        t = yf.Ticker(ticker)
        info = t.info

        si = info.get('shortPercentOfFloat', 0) or 0
        si_shares = info.get('sharesShort', 0) or 0
        short_ratio = info.get('shortRatio', 0) or 0
        price = info.get('currentPrice') or info.get('regularMarketPrice') or 0

        return {
            "short_pct_float": round(si * 100, 2) if si else 0,
            "short_ratio": round(short_ratio, 2) if short_ratio else 0,
            "shares_short": si_shares,
            "price": price,
        }
    except Exception:
        return {"short_pct_float": 0, "short_ratio": 0, "shares_short": 0, "price": 0}


def get_market_cap(ticker):
    """Get market cap and sector."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        mc = info.get('marketCap', 0) or 0
        sector = info.get('sector', '') or ''
        name = info.get('shortName', '') or info.get('longName', '') or ticker
        return mc, sector, name
    except:
        return 0, '', ticker


def score_squeeze(row, short_data):
    """Score squeeze potential 0-100."""
    score = 0

    # Gap down bonus (bigger gap = bigger squeeze potential) — cap at -20%
    gap = row.get('gap_pct', 0)
    if gap < -2:
        score += min(abs(gap) * 4, 40)  # up to 40 pts for gap
    elif gap < -1:
        score += abs(gap) * 3

    # Short interest — the core squeeze catalyst
    si = short_data.get('short_pct_float', 0)
    score += min(si * 3, 35)  # up to 35 pts for high SI

    # Short ratio (days to cover)
    sr = short_data.get('short_ratio', 0)
    score += min(sr * 3, 20)  # up to 20 pts

    # RSI oversold bonus
    rsi = row.get('rsi', 50)
    if rsi < 35:
        score += (35 - rsi) * 0.8  # up to ~28 pts
    elif rsi < 45:
        score += (45 - rsi) * 0.4

    # Volume surge bonus
    vr = row.get('vol_ratio', 1)
    if vr > 2:
        score += min(vr * 3, 15)  # up to 15 pts

    # MACD histogram improvement bonus
    if row.get('macd_hist', 0) > 0:
        score += 5  # bullish macd

    # Gap not yet filled — bigger unfilled gap = more squeeze room
    gf = row.get('gap_filled_pct', 0)
    if gf < 30:
        score += 10  # gap mostly intact
    elif gf < 60:
        score += 5

    return min(round(score, 1), 100)


def scan():
    print(f"Scanning {len(UNIVERSE)} stocks for squeeze setups...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("=" * 60)

    results = []

    for i, ticker in enumerate(UNIVERSE):
        print(f"[{i+1}/{len(UNIVERSE)}] {ticker}...", end=" ", flush=True)

        gap_data = get_gap_data(ticker)
        if not gap_data:
            print("⚠ no data")
            continue

        short_data = get_short_data(ticker)
        mc, sector, name = get_market_cap(ticker)

        gap_pct = gap_data['gap_pct']

        # Filter: must have gapped DOWN today (setup we want)
        if gap_pct >= 0:
            print(f"↑ {gap_pct:+.1f}% (not gapped down)")
            continue

        score = score_squeeze(gap_data, short_data)

        row = {
            "ticker": ticker,
            "name": name,
            "sector": sector,
            "market_cap": mc,
            "score": score,
            "gap_pct": gap_pct,
            "gap_filled_pct": gap_data.get('gap_filled_pct', 0),
            "price": gap_data['today_close'],
            "rsi": gap_data.get('rsi', 0),
            "short_pct_float": short_data.get('short_pct_float', 0),
            "short_ratio": short_data.get('short_ratio', 0),
            "vol_ratio": gap_data.get('vol_ratio', 0),
            "macd": gap_data.get('macd', 0),
            "macd_hist": gap_data.get('macd_hist', 0),
            "vwap_dist": gap_data.get('vwap_dist', 0),
            "52w_pct": gap_data.get('52w_pct', 0),
            "today_high": gap_data.get('today_high', 0),
            "today_low": gap_data.get('today_low', 0),
            "avg_vol_5d": gap_data.get('avg_vol_5d', 0),
        }

        results.append(row)
        print(f"gap {gap_pct:+.1f}% | RSI {gap_data.get('rsi',0):.0f} | SI {short_data.get('short_pct_float',0):.1f}% | score {score}")

    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)

    print("\n" + "=" * 60)
    print(f"TOP SQUEEZE SETUPS (gapped down today):")
    print("=" * 60)

    for i, r in enumerate(results[:15]):
        mc_m = r['market_cap'] / 1e9 if r['market_cap'] > 1e9 else r['market_cap'] / 1e6
        mc_str = f"${mc_m:.1f}B" if r['market_cap'] > 1e9 else f"${mc_m:.0f}M"
        print(f"\n{i+1}. {r['ticker']} — {r['name']}")
        print(f"   Price: ${r['price']} | Gap: {r['gap_pct']:+.1f}% | Gap Filled: {r['gap_filled_pct']:.0f}%")
        print(f"   RSI: {r['rsi']:.0f} | MACD hist: {r['macd_hist']:+.3f} | VWAP dist: {r['vwap_dist']:+.1f}%")
        print(f"   Short %Float: {r['short_pct_float']:.1f}% | Short ratio: {r['short_ratio']:.1f} days")
        print(f"   Vol ratio: {r['vol_ratio']:.1f}x | 52w position: {r['52w_pct']:.0f}%")
        print(f"   SCORE: {r['score']}/100 🎯 | Sector: {r['sector'] or 'N/A'}")

    # Save results
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results[:15]
        }, f, indent=2)

    print(f"\n✅ Saved to {RESULTS_FILE}")
    return results[:10]


if __name__ == "__main__":
    tickers = sys.argv[1:] if len(sys.argv) > 1 else None
    if tickers:
        UNIVERSE[:] = tickers
    scan()

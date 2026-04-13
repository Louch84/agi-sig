#!/usr/bin/env python3
"""
Breakout Scanner — Gap-Up Momentum + Volatility Contraction
Finds stocks UNDER $50 that are coiled to pop or already breaking out.
Designed for options plays with IV expansion potential.
"""
import yfinance as yf
import numpy as np
import json
import os
import sys
from datetime import datetime

# Universe — high-momentum stocks UNDER $50
# Rotates weekly; curated for breakout potential + options liquidity
UNIVERSE = [
    # AI/Tech (sub-$50)
    "SOUN",   # $6 — SoundHound AI, hot sector
    "PLTR",   # $28 — Palantir, AI/data play
    "SMCI",   # $24 — Super Micro, AI infrastructure
    "ASTS",   # $25 — AST SpaceMobile, satellite AI
    "LUNR",   # $23 — Intuitive Machines, space AI
    "RKLB",   # $19 — Rocket Lab, space tech
    "GPRO",   # $3 — GoPro, turnaround play
    "API",    # $18 — AliveCore/pharma AI
    "GRPN",   # $15 — Groupon, micro-cap momentum
    "SOFI",   # $16 — SoFi, fintech
    "RIVN",   # $15 — Rivian, EV momentum
    "LCID",   # $9 — Lucid, EV squeeze candidate
    "NOK",    # $5 — Nokia, turnaround
    "BB",     # $4 — BlackBerry, tech turnaround
    "SNAP",   # $5 — Snap, social media
    "PINS",   # $17 — Pinterest, social
    "RBLX",   # $35 — Roblox, gaming
    "HOOD",   # $70 — Robinhood (over $50, skip)
    "MARA",   # $14 — Marathon Digital, crypto mining
    "COIN",   # $180 — Coinbase (over $50, skip)
    "SMCI",   # $24 — already listed
    "INDI",   # $4 — indie Semiconductor
    "ENVX",   # $6 — Enovix, battery tech
    "SENS",   # $2 — Senseonics, biotech micro-cap
    "MVST",   # $3 — Microvast, battery
    "AIML",   # $4 — Investsmart AI
    "NAAS",   # $2 — MicroCap squeeze
    "DIRI",   # $2 — Direct Digital squeeze
    "TIGO",   # $8 — Tigera SaaS
    "OPK",    # $5 — OPKO Health biotech
    "CTRM",   # $3 — Castor Maritime
    "SRAX",   # $2 — SRAX micro-cap
    "FU",     # $8 — Direxion 3x
    "TNA",    # $45 — Direxion 3x small cap
    "FAS",    # $45 — Direxion 3x financial
    "LABD",   # $25 — Direxion 3x biotech
    "SOXS",   # $15 — Direxion 3x semibear
    "DRIP",   # $12 — 3x oil & gas
    "GUSH",   # $30 — 3x energy
    "NUGT",   # $45 — 3x gold
    "JDST",   # $10 — 3x junior gold
]

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "breakout-scanner.json")


def calculate_atr(high, low, close, period=14):
    """Calculate Average True Range."""
    trs = []
    for i in range(1, len(high)):
        tr = max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
        trs.append(tr)
    return np.mean(trs[-period:]) if len(trs) >= period else np.mean(trs)


def get_breakout_data(ticker, period="30d"):
    """Get breakout readiness data for a ticker."""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period, interval="1d")
        if hist.empty or len(hist) < 20:
            return None

        closes = hist['Close'].values
        highs = hist['High'].values
        lows = hist['Low'].values
        volumes = hist['Volume'].values
        opens = hist['Open'].values

        price = closes[-1]
        if price > 50:
            return None  # Skip stocks over $50

        if price < 0.50:
            return None  # Skip penny stocks (no options liquidity)

        today_close = closes[-1]
        today_open = opens[-1]
        today_high = highs[-1]
        today_low = lows[-1]
        today_vol = volumes[-1]

        yesterday_close = closes[-2]

        # Gap today
        gap_pct = ((today_open - yesterday_close) / yesterday_close) * 100

        # ATR compression: current ATR vs 30d ATR
        atr_14 = calculate_atr(highs, lows, closes, 14)
        atr_30 = calculate_atr(highs, lows, closes, 30)
        atr_ratio = atr_14 / atr_30 if atr_30 > 0 else 1

        # Volume contraction: today's vol vs 50d avg
        vol_50d_avg = np.mean(volumes[-50:]) if len(volumes) >= 50 else np.mean(volumes)
        vol_ratio = today_vol / vol_50d_avg if vol_50d_avg > 0 else 1

        # RSI
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
        macd_slope = macd_hist - (macd[-2] - signal[-2]) if len(macd) > 2 else 0

        # Distance from 52w high
        high52 = float(np.max(highs))
        low52 = float(np.min(lows))
        dist_from_high = ((high52 - price) / high52) * 100 if high52 > 0 else 100
        dist_from_low = ((price - low52) / low52) * 100 if low52 > 0 else 0
        w52_pct = ((price - low52) / (high52 - low52)) * 100 if (high52 - low52) > 0 else 50

        # Bollinger Band position
        ma20 = np.mean(closes[-20:])
        std20 = np.std(closes[-20:])
        bb_upper = ma20 + (2 * std20)
        bb_lower = ma20 - (2 * std20)
        bb_position = ((price - bb_lower) / (bb_upper - bb_lower)) * 100 if (bb_upper - bb_lower) > 0 else 50

        # Price near consolidation high (resistance)
        recent_highs = np.max(highs[-10:])
        dist_from_recent_high = ((recent_highs - price) / recent_highs) * 100 if recent_highs > 0 else 100

        return {
            "price": round(price, 2),
            "gap_pct": round(gap_pct, 2),
            "today_high": round(today_high, 2),
            "today_low": round(today_low, 2),
            "atr_ratio": round(atr_ratio, 3),      # < 0.5 = compressed
            "vol_ratio": round(vol_ratio, 2),
            "vol_50d_avg": round(vol_50d_avg, 0),
            "rsi": round(rsi, 1),
            "macd_hist": round(macd_hist, 3),
            "macd_slope": round(macd_slope, 4),
            "high52": round(high52, 2),
            "dist_from_high": round(dist_from_high, 1),
            "dist_from_low": round(dist_from_low, 1),
            "w52_pct": round(w52_pct, 1),
            "bb_position": round(bb_position, 1),  # > 80 = near upper band = overbought
            "dist_from_recent_high": round(dist_from_recent_high, 1),
            "atr_14": round(atr_14, 3),
            "atr_30": round(atr_30, 3),
        }
    except Exception as e:
        return None  # yfinance error (404, delisted, no data)


def _ema(data, period):
    data = np.array(data)
    ema = np.zeros(len(data))
    ema[0] = data[0]
    multiplier = 2 / (period + 1)
    for i in range(1, len(data)):
        ema[i] = (data[i] - ema[i-1]) * multiplier + ema[i-1]
    return ema


def score_breakout(row):
    """Score breakout readiness 0-100."""
    score = 0

    # === ATR COMPRESSION (tight coil = big move coming) ===
    atr = row.get('atr_ratio', 1)
    if atr < 0.4:
        score += 30  # extremely compressed
    elif atr < 0.5:
        score += 20
    elif atr < 0.6:
        score += 10

    # === DISTANCE FROM 52W HIGH (uptrend, ready to break) ===
    dist = row.get('dist_from_high', 100)
    if dist < 5:
        score += 20  # within 5% of 52w high = breaking out NOW
    elif dist < 10:
        score += 15
    elif dist < 15:
        score += 10
    elif dist < 25:
        score += 5

    # === RSI (sweet spot for pre-breakout) ===
    rsi = row.get('rsi', 50)
    if 50 <= rsi <= 60:
        score += 15  # perfect pre-breakout RSI
    elif 45 <= rsi <= 70:
        score += 8
    elif rsi < 40:
        score += 3  # still coiling

    # === MACD SLOPE (momentum building) ===
    macd_slope = row.get('macd_slope', 0)
    if macd_slope > 0.05:
        score += 15
    elif macd_slope > 0.02:
        score += 10
    elif macd_slope > 0:
        score += 5

    # === GAP UP TODAY (already firing) ===
    gap = row.get('gap_pct', 0)
    if gap > 5:
        score += 25  # big gap = momentum confirmed
    elif gap > 3:
        score += 18
    elif gap > 2:
        score += 12
    elif gap > 1:
        score += 8

    # === VOLUME (confirmation) ===
    vr = row.get('vol_ratio', 1)
    if vr > 3:
        score += 10
    elif vr > 2:
        score += 7
    elif vr > 1.5:
        score += 4

    # === BOLLINGER BAND POSITION ===
    bb = row.get('bb_position', 50)
    if 70 <= bb <= 90:
        score += 8  # near upper band, ready to break through
    elif bb > 90:
        score -= 5  # overextended, risky

    return min(round(score, 1), 100)


def scan():
    print(f"Scanning {len(UNIVERSE)} stocks for breakout setups (under $50)...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("=" * 60)

    results = []

    for i, ticker in enumerate(UNIVERSE):
        print(f"[{i+1}/{len(UNIVERSE)}] {ticker}...", end=" ", flush=True)

        data = get_breakout_data(ticker)
        if not data:
            print("⚠ no data")
            continue

        score = score_breakout(data)

        # Filter: only show if there's a real setup
        # Must have either: gap up, close to 52w high, or compressed ATR
        if score < 20 and data.get('gap_pct', 0) < 2:
            print(f"score {score} — no setup")
            continue

        print(f"gap {data['gap_pct']:+.1f}% | RSI {data['rsi']:.0f} | ATR ratio {data['atr_ratio']:.2f} | score {score}")

        results.append({
            "ticker": ticker,
            "score": score,
            **data
        })

    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)

    print("\n" + "=" * 60)
    print(f"TOP BREAKOUT SETUPS (under $50):")
    print("=" * 60)

    for i, r in enumerate(results[:15]):
        atr_note = "📉 COMPRESSED" if r['atr_ratio'] < 0.5 else ""
        gap_note = f"🚀 GAP +{r['gap_pct']:.1f}%" if r['gap_pct'] > 2 else f"gap {r['gap_pct']:+.1f}%"
        print(f"\n{i+1}. {r['ticker']} — ${r['price']}")
        print(f"   {gap_note} | RSI {r['rsi']:.0f} | ATR ratio {r['atr_ratio']:.2f} {atr_note}")
        print(f"   52w high: ${r['high52']} | Dist from high: {r['dist_from_high']:.1f}%")
        print(f"   MACD hist: {r['macd_hist']:+.3f} | BB position: {r['bb_position']:.0f}%")
        print(f"   Vol ratio: {r['vol_ratio']:.1f}x | SCORE: {r['score']}/100 🎯")

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

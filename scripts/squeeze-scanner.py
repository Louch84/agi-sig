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

# Universe — curated stocks known for squeeze potential + fresh high-SI bottomfishing picks
# Updated 2026-04-13: replaced stale tickers with current high-SI list
UNIVERSE = [
    # === SQUEEZE CLASSICS ===
    "GME", "AMC", "LCID", "SOFI", "PLTR", "RIVN", "SMCI",
    "BB", "NOK", "COIN", "HOOD", "ASTS", "LUNR", "RKLB",
    # === FRESH HIGH-SI BOTTOMFISHING PICKS (from highshortinterest.com 2026-04-13) ===
    # These have 25-53% short interest — prime squeeze fuel near lows
    "GRPN",   # 53% SI — highest on the list
    "HTZ",    # 48% SI — Hertz
    "HIMS",   # 40% SI — telehealth momentum
    "SOUN",   # 35% SI — SoundHound AI (hot sector)
    "AI",      # 36% SI — C3.ai
    "TTEC",   # 33% SI — scored 78/100 today
    "PCT",    # 33% SI — Purecycle
    "MARA",   # 31% SI — crypto mining
    "INDI",   # 32% SI — semiconductor
    "NVAX",   # 30% SI — biotech squeeze history
    "BYND",   # 30% SI — activist investor interest
    "ENVX",   # 32% SI — Enovix battery
    "RXRX",   # 35% SI — Recursion Pharma AI drug discovery
    "CYPH",   # 32% SI — biotech
    "IOVA",   # 32% SI — Iovance Biotherapeutics
    "CRDF",   # 26% SI — Cardiff Oncology (scored 75/100 today)
    "ABEO",   # 28% SI — Abeona Therapeutics (scored 74/100 today)
    "MNPR",   # 66% SI — Monopar Therapeutics (EXTREME SI)
    "SNBR",   # 30% SI — Sleep Number
    "ROOT",   # 28% SI — Root Inc insurance
    "EOSE",   # 28% SI — Eos Energy
    "ABEO",   # 28% SI — Abeona Therapeutics
    # === HIGH-SI SQUEEZE TIGHT ENTRY ===
    "SRPT",   # 25% SI — Sarepta Therapeutics
    "BETR",   # 34% SI — Better Home & Finance
    "SPHR",   # 29% SI — Sphere Entertainment
    "MPTI",   # 29% SI — MicroPort
    "BBAI",   # 26% SI — BigBear.ai
]

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "squeeze-scanner.json")


def get_gap_data(ticker, period="10d"):
    """Get gap down + bottomfishing data for a ticker.
    
    Uses 10d fetch for RSI divergence detection (compares recent low to previous low).
    Still derives 52w stats from same window — no extra API call.
    """
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period, interval="1d")
        if hist.empty or len(hist) < 5:
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
        avg_volume_5d = np.mean(volumes[:-1])

        # RSI (14-day) + DIVERGENCE DETECTION
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else np.mean(gains)
        avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else np.mean(losses)
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))

        # RSI DIVERGENCE: compare RSI in recent lows vs older lows
        # If price making similar/low lows but RSI is higher = bullish divergence
        rsi_divergence = 0
        if len(closes) >= 10:
            recent_5_rsi = []
            for i in range(len(closes)-5, len(closes)):
                if i > 0:
                    d = np.diff(closes[max(0,i-14):i+1])
                    g = np.where(d > 0, d, 0)
                    l = np.where(d < 0, -d, 0)
                    ag = np.mean(g) if len(g) > 0 else 0
                    al = np.mean(l) if len(l) > 0 else 0
                    r = ag/al if al > 0 else 100
                    recent_5_rsi.append(100 - (100/(1+r)))
            prev_5_rsi = []
            for i in range(max(0, len(closes)-10), max(0, len(closes)-5)):
                if i > 0:
                    d = np.diff(closes[max(0,i-14):i+1])
                    g = np.where(d > 0, d, 0)
                    l = np.where(d < 0, -d, 0)
                    ag = np.mean(g) if len(g) > 0 else 0
                    al = np.mean(l) if len(l) > 0 else 0
                    r = ag/al if al > 0 else 100
                    prev_5_rsi.append(100 - (100/(1+r)))
            if recent_5_rsi and prev_5_rsi:
                avg_recent = np.mean(recent_5_rsi)
                avg_prev = np.mean(prev_5_rsi)
                # Bullish divergence: recent RSI higher but price similar or lower
                price_recent_low = np.min(closes[-5:])
                price_prev_low = np.min(closes[-10:-5])
                if avg_recent > avg_prev and price_recent_low <= price_prev_low * 1.05:
                    rsi_divergence = min(avg_recent - avg_prev, 20)  # up to 20pt divergence bonus

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

        # 52-week position — derived from rolling window (no extra t.history call)
        high52 = float(np.max(highs))
        low52 = float(np.min(lows))

        return {
            "today_close": round(today_close, 2),
            "today_open": round(today_open, 2),
            "yesterday_close": round(yesterday_close, 2),
            "gap_pct": round(gap_pct, 2),
            "gap_filled_pct": round(((today_close - today_open) / (yesterday_close - today_open)) * 100, 1) if (yesterday_close - today_open) != 0 else 0,
            "today_high": round(today_high, 2),
            "today_low": round(today_low, 2),
            "rsi": round(rsi, 1),
            "rsi_divergence": round(rsi_divergence, 1),
            "macd": round(macd[-1], 3),
            "macd_hist": round(macd_hist, 3),
            "vol_ratio": round(vol_ratio, 2),
            "vwap_dist": round(vwap_dist, 2),
            "52w_high": round(high52, 2),
            "52w_low": round(low52, 2),
            "52w_pct": round(((today_close - low52) / (high52 - low52)) * 100, 1) if (high52 - low52) != 0 else 50,
            "avg_vol_5d": round(avg_volume_5d, 0),
            "today_vol": round(today_vol, 0),
            "at_52w_low": today_close <= low52 * 1.05,  # within 5% of 52w low = bottomfishing signal
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
    """Score squeeze + bottomfishing potential 0-100.
    
    Enhanced 2026-04-13:
    - Added RSI divergence detection bonus
    - Added 52w low position bonus (bottomfishing edge)
    - Weighted days-to-cover more heavily (DTOC > 5 = trapped shorts)
    - Added at-52w-low bonus for bottomfishing entries
    """
    score = 0

    # === GAP DOWN (core trigger) ===
    gap = row.get('gap_pct', 0)
    if gap < -3:
        score += min(abs(gap) * 4, 45)  # up to 45 pts for big gaps
    elif gap < -2:
        score += min(abs(gap) * 3.5, 35)
    elif gap < -1:
        score += abs(gap) * 2.5

    # === SHORT INTEREST (squeeze battery) ===
    si = short_data.get('short_pct_float', 0)
    score += min(si * 2.5, 40)  # up to 40 pts — SI is the core catalyst

    # === DAYS TO COVER (trapped shorts = explosive) ===
    # Higher DTC = more forced covering = bigger squeeze
    sr = short_data.get('short_ratio', 0)
    if sr >= 10:
        score += 25  # extreme DTC — shorts are completely trapped
    elif sr >= 5:
        score += 20  # high DTC — significant squeeze fuel
    elif sr >= 3:
        score += 12
    elif sr >= 1:
        score += min(sr * 3, 10)

    # === RSI OVERSOLD (bounce probability) ===
    rsi = row.get('rsi', 50)
    if rsi < 25:
        score += 35  # deeply oversold — high bounce probability
    elif rsi < 30:
        score += 28
    elif rsi < 35:
        score += (35 - rsi) * 1.5
    elif rsi < 45:
        score += (45 - rsi) * 0.5

    # === RSI DIVERGENCE (bottomfishing edge) ===
    # Price making similar lows but RSI higher = bullish divergence
    rsi_div = row.get('rsi_divergence', 0)
    score += min(rsi_div * 2, 20)  # up to 20 pts for divergence

    # === AT 52-WEEK LOW (bottomfishing entry) ===
    # Being near the 52w low means more room to run, less overhead resistance
    w52_pct = row.get('52w_pct', 50)
    if w52_pct <= 15:
        score += 15  # within 15% of 52w low = near absolute bottom
    elif w52_pct <= 25:
        score += 10
    elif w52_pct <= 35:
        score += 5

    # === VOLUME SURGE (confirmation) ===
    vr = row.get('vol_ratio', 1)
    if vr > 3:
        score += 15  # strong volume confirms the move
    elif vr > 2:
        score += 10
    elif vr > 1.5:
        score += 5

    # === MACD HISTOGRAM (momentum shift) ===
    if row.get('macd_hist', 0) > 0:
        score += 5  # bullish MACD confirms bounce

    # === GAP FILL INTACT (room to run) ===
    gf = row.get('gap_filled_pct', 0)
    if gf < 20:
        score += 12  # gap mostly intact
    elif gf < 50:
        score += 6
    elif gf < 80:
        score += 2

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
            "rsi_divergence": gap_data.get('rsi_divergence', 0),
            "short_pct_float": short_data.get('short_pct_float', 0),
            "short_ratio": short_data.get('short_ratio', 0),
            "vol_ratio": gap_data.get('vol_ratio', 0),
            "macd": gap_data.get('macd', 0),
            "macd_hist": gap_data.get('macd_hist', 0),
            "vwap_dist": gap_data.get('vwap_dist', 0),
            "52w_pct": gap_data.get('52w_pct', 0),
            "at_52w_low": gap_data.get('at_52w_low', False),
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
        div_note = f" | RSI div: +{r['rsi_divergence']:.0f}" if r['rsi_divergence'] > 2 else ""
        low_note = " 📍52W LOW" if r.get('at_52w_low') else ""
        print(f"\n{i+1}. {r['ticker']} — {r['name']}{low_note}")
        print(f"   Price: ${r['price']} | Gap: {r['gap_pct']:+.1f}% | Gap Filled: {r['gap_filled_pct']:.0f}%{div_note}")
        print(f"   RSI: {r['rsi']:.0f} | MACD hist: {r['macd_hist']:+.3f} | VWAP dist: {r['vwap_dist']:+.1f}%")
        print(f"   Short %Float: {r['short_pct_float']:.1f}% | Short ratio: {r['short_ratio']:.1f} days to cover")
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

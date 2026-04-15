from fundamental_filter import check_fundamentals
"""
Coiled Consolidation Scanner — Tight range compression breakout setups.
Finds stocks coiled up in narrow consolidation (low volatility compressing)
that are ready to explode on a breakout.

Lou's spec: stocks that have compressed into tight ranges, coiling energy
for a breakout. Not a gap play — this is a range-bound squeeze before the pop.
"""
import yfinance as yf
import numpy as np
import json
import os
import sys
import time
from datetime import datetime

# Universe: loaded from data/universe.json if it exists, otherwise falls back to hardcoded list
UNIVERSE_FILE = "/Users/sigbotti/.openclaw/workspace/data/universe.json"

def load_universe():
    if os.path.exists(UNIVERSE_FILE):
        with open(UNIVERSE_FILE) as f:
            data = json.load(f)
            tickers = data.get('tickers', [])
            if tickers:
                print(f"📦 Loaded {len(tickers)} tickers from universe.json")
                return tickers
    return None

_fallback_universe = [
    "GME", "AMC", "LCID", "SOFI", "PLTR", "RIVN", "SMCI",
    "BB", "NOK", "COIN", "HOOD", "ASTS", "LUNR", "RKLB",
    "GRPN", "HTZ", "HIMS", "SOUN", "AI", "TTEC", "PCT", "MARA", "INDI",
    "NVAX", "BYND", "ENVX", "RXRX", "CYPH", "IOVA", "CRDF", "ABEO",
    "MNPR", "SNBR", "ROOT", "EOSE", "SRPT", "BETR", "SPHR", "MPTI", "BBAI",
    "SRAX", "OPK", "CTRM", "NCTY", "TIGO", "SENS", "MVST",
]

_universe = load_universe() or _fallback_universe
# Re-assign UNIVERSE for backward compat
UNIVERSE = _universe

RESULTS_FILE = "/Users/sigbotti/.openclaw/workspace/data/coil-scanner.json"


def _ema(data, period):
    data = np.array(data)
    ema = np.zeros(len(data))
    ema[0] = data[0]
    m = 2 / (period + 1)
    for i in range(1, len(data)):
        ema[i] = (data[i] - ema[i-1]) * m + ema[i-1]
    return ema


def _atr(high, low, close, period=14):
    high = np.array(high)
    low = np.array(low)
    close = np.array(close)
    tr1 = np.abs(high[1:] - low[1:])
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])
    tr = np.maximum(np.maximum(tr1, tr2), tr3)
    atr = np.zeros(len(close))
    atr[period-1] = np.mean(tr[:period])
    for i in range(period, len(close)):
        atr[i] = (atr[i-1] * (period - 1) + tr[i-1]) / period
    return atr


def get_coil_data(ticker, lookback=60):
    """Get coil/compression metrics for a ticker."""
    try:
        t = yf.Ticker(ticker)
        h = None
        for attempt in range(4):
            try:
                h = t.history(period="60d", interval="1d")
                if h is not None and not h.empty and len(h) >= 30:
                    break
            except Exception as e:
                print(f"  [retry {attempt+1}] {e}", end="")
                time.sleep(2 ** attempt)
        if h is None or h.empty or len(h) < 30:
            return None

        closes = h['Close'].values
        highs = h['High'].values
        lows = h['Low'].values
        volumes = h['Volume'].values

        # Current price
        current = closes[-1]
        current_high = highs[-1]
        current_low = lows[-1]

        # ATR + ATR SMA (for squeeze detection)
        atr_vals = _atr(highs, lows, closes, 14)
        current_atr = atr_vals[-1]
        atr_sma_10 = np.mean(atr_vals[-10:])  # 10d ATR SMA
        atr_ratio = current_atr / atr_sma_10 if atr_sma_10 > 0 else 1.0  # < 0.7 = squeeze

        # Bollinger Band width (as % of price — lower = more compressed)
        # sma20 and std20 are same length — compute on full window then slice last value
        sma20_full = _ema(closes, 20)
        std20_full = np.array([np.std(closes[max(0,i-20):i+1]) for i in range(20, len(closes))])
        # Pad std20 to match closes length (first 20 bars have no std)
        std20 = np.concatenate([np.full(20, np.nan), std20_full])
        bb_upper = sma20_full + (std20 * 2)
        bb_lower = sma20_full - (std20 * 2)
        # Use last valid values (index 59)
        valid_idx = 59  # last bar with valid std
        bb_width = (bb_upper[valid_idx] - bb_lower[valid_idx]) / sma20_full[valid_idx] * 100

        # BB width percentile (how compressed vs history)
        bb_widths = []
        for i in range(20, len(closes)):
            s20 = _ema(closes[:i], 20)
            st = np.std(closes[i-20:i])
            bw = ((s20[-1] + st*2) - (s20[-1] - st*2)) / s20[-1] * 100
            bb_widths.append(bw)
        if len(bb_widths) >= 20:
            bw_percentile = (sorted(bb_widths).index(bb_widths[-1]) / len(bb_widths)) * 100
        else:
            bw_percentile = 50

        # Range compression ratio (current range vs 20d avg range)
        current_range = current_high - current_low
        avg_range_20d = np.mean([highs[i] - lows[i] for i in range(-21, -1)])
        range_ratio = current_range / avg_range_20d if avg_range_20d > 0 else 1.0  # < 0.7 = compressed

        # Days in range (count days where range < 50% of ATR)
        atrs = _atr(highs, lows, closes, 14)
        days_in_range = 0
        for i in range(-15, 0):
            day_range = highs[i] - lows[i]
            if day_range < current_atr * 0.5:
                days_in_range += 1

        # Volume trend (declining = accumulation, not distribution)
        vol_5d_avg = np.mean(volumes[-5:])
        vol_20d_avg = np.mean(volumes[-20:])
        vol_trend = vol_5d_avg / vol_20d_avg if vol_20d_avg > 0 else 1.0  # < 0.8 = declining

        # RSI (14d)
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        ag = np.mean(gains[-14:])
        al = np.mean(losses[-14:])
        rs = ag / al if al > 0 else 100
        rsi = 100 - (100 / (1 + rs))

        # Trend: price above EMA 20 = short-term bullish coil
        ema20 = _ema(closes, 20)[-1]
        ema50 = _ema(closes, 50)[-1] if len(closes) >= 50 else None
        ema200 = _ema(closes, 200)[-1] if len(closes) >= 200 else None

        above_ema20 = current > ema20
        ema20_above_ema50 = ema20 > ema50 if ema50 else False
        ema50_above_ema200 = ema50 > ema200 if ema50 and ema200 else False

        # MACD for momentum
        ema12 = _ema(closes, 12)[-1]
        ema26 = _ema(closes, 26)[-1]
        macd = ema12 - ema26
        macd_signal = _ema(np.concatenate([[ema12], [macd]]), 9)[-1]
        macd_hist = macd - macd_signal

        # VWAP distance
        vwap = np.mean(h['High'].values[-20:] + h['Low'].values[-20:]) / 2
        vwap_dist = ((current - vwap) / vwap) * 100

        # 10d high/low position (coiled near lows = better setup)
        window_high = float(np.max(highs[-10:]))
        window_low = float(np.min(lows[-10:]))
        pos_in_range = (current - window_low) / (window_high - window_low) * 100 if window_high != window_low else 50

        # Gap today (coiled stocks shouldn't gap much — < 1% is ideal)
        today_open = h['Open'].iloc[-1]
        prev_close = closes[-2]
        gap_today = ((today_open - prev_close) / prev_close) * 100

        # ── Fundamental check ─────────────────────────────────────────
        fund = check_fundamentals(ticker)
        dilution = fund.get('dilution_risk', False)
        verdict = fund.get('fundamental_verdict', 'UNKNOWN')
        red_flags = fund.get('red_flags', [])

        return {
            "ticker": ticker,
            "price": round(current, 2),
            "open": round(today_open, 2),
            "prev_close": round(prev_close, 2),
            "gap_today": round(gap_today, 2),
            "bb_width": round(bb_width, 2),
            "bb_width_pct": round(bw_percentile, 1),
            "atr_ratio": round(atr_ratio, 3),
            "range_ratio": round(range_ratio, 3),
            "days_in_range": days_in_range,
            "vol_trend": round(vol_trend, 2),
            "rsi": round(rsi, 1),
            "ema20": round(ema20, 2),
            "ema50": round(ema50, 2) if ema50 else None,
            "ema200": round(ema200, 2) if ema200 else None,
            "above_ema20": bool(above_ema20),
            "ema20_above_ema50": bool(ema20_above_ema50),
            "ema50_above_ema200": bool(ema50_above_ema200),
            "macd_hist": round(macd_hist, 3),
            "vwap_dist": round(vwap_dist, 2),
            "pos_in_range": round(pos_in_range, 1),
            "window_high": round(window_high, 2),
            "window_low": round(window_low, 2),
            "10d_range_size": round(window_high - window_low, 2),
            "fundamental_verdict": verdict,
            "dilution_risk": dilution,
            "red_flags": red_flags,
        }
    except Exception as e:
        return None


def score_coil(row):
    """Score 0-100 how coiled + ready to burst."""
    score = 0

    # Dilution penalty
    if row.get('dilution_risk', False):
        score -= 40

    # === ATR SQUEEZE (< 0.7 = significant compression) ===
    atr = row.get('atr_ratio', 1)
    if atr <= 0.5:
        score += 30  # extreme squeeze
    elif atr <= 0.65:
        score += 22
    elif atr <= 0.75:
        score += 15
    elif atr <= 0.85:
        score += 8

    # === BOLLINGER WIDTH (lower = more compressed vs history) ===
    bw_pct = row.get('bb_width_pct', 50)
    if bw_pct <= 10:
        score += 28  # near record narrow
    elif bw_pct <= 20:
        score += 22
    elif bw_pct <= 30:
        score += 15
    elif bw_pct <= 40:
        score += 8

    # === DAYS IN TIGHT RANGE ===
    days = row.get('days_in_range', 0)
    if days >= 10:
        score += 20
    elif days >= 7:
        score += 15
    elif days >= 5:
        score += 10
    elif days >= 3:
        score += 5

    # === RANGE COMPRESSION RATIO ===
    rr = row.get('range_ratio', 1)
    if rr <= 0.5:
        score += 20
    elif rr <= 0.65:
        score += 15
    elif rr <= 0.8:
        score += 8

    # === VOLUME TREND (declining = accumulation) ===
    vt = row.get('vol_trend', 1)
    if vt <= 0.4:
        score += 18  # dramatic volume drop = coiled energy
    elif vt <= 0.6:
        score += 12
    elif vt <= 0.8:
        score += 6

    # === RSI (neutral zone — not overbought, not oversold) ===
    rsi = row.get('rsi', 50)
    if 40 <= rsi <= 65:
        score += 15  # coiled in neutral = room to run
    elif 30 <= rsi < 40:
        score += 10  # approaching oversold = bounce setup
    elif rsi > 70:
        score -= 20  # overbought = risky breakout
    elif rsi < 30:
        score -= 10

    # === TREND ALIGNMENT (ema20 > ema50 > ema200 = coiled for break higher) ===
    if row.get('ema20_above_ema50') and row.get('ema50_above_ema200'):
        score += 20  # full bull stack = strong coil
    elif row.get('ema20_above_ema50'):
        score += 12
    elif row.get('above_ema20'):
        score += 6

    # === MACD HISTOGRAM (building toward break) ===
    mh = row.get('macd_hist', 0)
    if mh > 0:
        score += 10  # bullish momentum building
    elif mh > -0.05:
        score += 5

    # === VWAP (below = compressed under resistance) ===
    vwap = row.get('vwap_dist', 0)
    if -2 <= vwap <= 0:
        score += 8  # coiled just below VWAP = room to run up
    elif vwap < -5:
        score -= 10  # well below VWAP = weak

    # === POSITION IN 10d RANGE (near bottom = better entry, near top = tighter) ===
    pos = row.get('pos_in_range', 50)
    if 20 <= pos <= 60:
        score += 10  # sweet spot — coiling in middle of range
    elif pos < 20:
        score += 15  # near 10d low = coiled near floor
    elif pos > 85:
        score -= 15  # near top of range = already ran, less room

    # === TODAY'S GAP (coiled shouldn't gap — small gap = still compressing) ===
    gap = abs(row.get('gap_today', 0))
    if gap < 0.5:
        score += 10  # no gap = still coiled
    elif gap < 1.0:
        score += 5
    elif gap > 3:
        score -= 15  # big gap = already started running, less coil

    return min(round(score, 1), 100)


def format_flags(row):
    """Flag the key coil signatures."""
    flags = []
    if row.get('atr_ratio', 1) <= 0.65:
        flags.append(f"⚡ ATR squeeze {row['atr_ratio']:.2f}")
    if row.get('bb_width_pct', 99) <= 20:
        flags.append(f"📌 BB compress {row['bb_width_pct']:.0f}%ile")
    if row.get('days_in_range', 0) >= 7:
        flags.append(f"🔒 {row['days_in_range']}d tight range")
    if row.get('vol_trend', 1) <= 0.6:
        flags.append(f"📉 vol {row['vol_trend']:.1f}x")
    if row.get('pos_in_range', 50) < 20:
        flags.append(f"📍 near 10d low")
    if row.get('above_ema20'):
        flags.append("ema20✅")
    else:
        flags.append("ema20❌")
    return " | ".join(flags)


def scan(verbose=True):
    print(f"Scanning {len(UNIVERSE)} stocks for coiled consolidation setups...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("=" * 65)

    results = []
    for i, ticker in enumerate(UNIVERSE):
        if verbose:
            print(f"[{i+1}/{len(UNIVERSE)}] {ticker}...", end=" ", flush=True)

        data = get_coil_data(ticker)
        if not data:
            if verbose:
                print("⚠ no data")
            continue

        score = score_coil(data)
        data['score'] = score
        results.append(data)

        if verbose:
            flags = format_flags(data)
            diltn = " ⚠️ DILUTING" if data.get('dilution_risk') else ""
            print(
                f"BW {data['bb_width']:.1f}% | ATR {data['atr_ratio']:.2f} | "
                f"DR {data['days_in_range']}d | vol {data['vol_trend']:.1f}x | "
                f"RSI {data['rsi']:.0f} | pos {data['pos_in_range']:.0f}% | "
                f"gap {data['gap_today']:+.1f}% | score {score}/100{diltn}"
            )
            if score >= 60 and not data.get('dilution_risk'):
                print(f"  🔥 COIL: {flags}")
            elif data.get('dilution_risk'):
                print(f"  ⚠️ KILLED: dilution risk")

        time.sleep(0.4)  # throttle

    results.sort(key=lambda x: x['score'], reverse=True)

    # Filter dilution
    pre = len(results)
    results = [r for r in results if not r.get('dilution_risk', False)]
    print(f"\n⚠️ Filtered {pre - len(results)} diluting stocks → {len(results)} passing fundamentals\n")

    print(f"\n" + "=" * 65)
    print(f"🔥 TOP COILED SETUPS (score ≥ 55, fundamentals passing):")
    print("=" * 65)

    hot = [r for r in results if r['score'] >= 55]
    if not hot:
        print("  None right now — market may be trending, not ranging.")

    for r in hot[:12]:
        print(f"\n  {r['ticker']} — ${r['price']}")
        print(f"    BW {r['bb_width']:.1f}% ({r['bb_width_pct']:.0f}%ile) | ATR {r['atr_ratio']:.2f} | {r['days_in_range']}d tight")
        print(f"    RSI {r['rsi']:.0f} | vol {r['vol_trend']:.1f}x | gap {r['gap_today']:+.1f}%")
        flags = format_flags(r)
        print(f"    {flags}")
        print(f"    10d range: ${r['window_low']}–${r['window_high']} (${r['10d_range_size']} wide) | pos {r['pos_in_range']:.0f}%")
        print(f"    SCORE: {r['score']}/100 🎯")

    print(f"\n✅ Saved to {RESULTS_FILE}")
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results[:20]
        }, f, indent=2)

    return results


if __name__ == "__main__":
    tickers = sys.argv[1:] if len(sys.argv) > 1 else None
    if tickers:
        UNIVERSE[:] = tickers
    scan()

#!/usr/bin/env python3
"""
Gap Alert Scanner — Catches gap-ups on high SI + news catalysts.
Monitors pre-defined watchlist of high-SI stocks under $50.
Runs every 15 min during market hours.
"""
import yfinance as yf
import numpy as np
import json
import os
import sys
import time
from datetime import datetime, timedelta
from urllib.error import URLError
from fundamental_filter import check_fundamentals

# ─── Watchlist: stocks under $50 with elevated SI potential ───────────────────
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

_fallback_watchlist = [
    "GME", "AMC", "LCID", "SOFI", "SMCI", "PINS", "BB", "DNA", "NAAS",
    "RIVN", "SNAP", "HOOD", "PLTR", "ASTS", "LUNR", "SRAX", "OPK", "CTRM",
    "GRPN", "NCTY", "TIGO", "SENS", "MVST", "AIML",
]

_watchlist = load_universe() or _fallback_watchlist
WATCHLIST = _watchlist

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "gap-alerts.json")
STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "gap-alert-state.json")

ALERT_THRESHOLD_GAP = 5.0   # % gap to trigger alert
ALERT_THRESHOLD_SI = 5.0    # % SI to care
ALERT_THRESHOLD_VOL = 2.0   # volume ratio to trigger


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"alerts_today": [], "last_scan": None}


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


def _ema(prices, period):
    """Compute EMA for a price array."""
    k = 2 / (period + 1)
    ema = float(prices[0])
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return ema


def _get_ma_data(ticker, current_price):
    """Get MA signals for a ticker. Returns dict."""
    try:
        t = yf.Ticker(ticker)
        h = t.history(period="6mo", interval="1d")
        if h.empty or len(h) < 60:
            return {}
        closes = h["Close"].values
        ema9 = _ema(closes, 9)
        ema21 = _ema(closes, 21)
        ema50 = _ema(closes, 50) if len(closes) >= 50 else None
        ema200 = _ema(closes, 200) if len(closes) >= 200 else None
        signal = "NEUTRAL"
        if ema50 and ema200:
            signal = "GOLDEN_CROSS" if ema50 > ema200 else "DEATH_CROSS"
        slope_50 = 0
        if ema50 and len(closes) >= 55:
            ema50_5d = _ema(closes[:-5], 50)
            slope_50 = round(((ema50 - ema50_5d) / ema50_5d) * 100, 2)
        return {
            "ma_signal": signal,
            "short_signal": "ABOVE_EMA21" if current_price > ema21 else "BELOW_EMA21",
            "ema9": round(ema9, 2),
            "ema21": round(ema21, 2),
            "ema50": round(ema50, 2) if ema50 else None,
            "ema200": round(ema200, 2) if ema200 else None,
            "slope_50": slope_50,
        }
    except Exception:
        return {}


def scan_ticker(ticker):
    """Scan one ticker. Returns dict or None."""
    try:
        t = yf.Ticker(ticker)
        h = t.history(period="2d", interval="15m")  # 2d 15min — fast enough for gap detection
        info = t.info

        if h.empty:
            return None

        price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not price or price > 100:  # skip expensive stocks
            return None

        si = (info.get('shortPercentOfFloat', 0) or 0) * 100
        sr = info.get('shortRatio', 0) or 0

        # Get today's OHLCV from intraday
        today = h[h.index.date == datetime.now().date()]
        if today.empty:
            return None

        today_open = today['Open'].iloc[0]
        prev_close = h['Close'].iloc[0]  # yesterday's close

        gap_pct = ((today_open - prev_close) / prev_close) * 100

        # Today's volume vs avg vol per 15min bar
        today_vol = today['Volume'].sum()
        avg_vol = today_vol / len(today) if len(today) > 0 else 1
        vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1

        # High of day
        high = today['High'].max()
        current = today['Close'].iloc[-1]

        # RSI (14d) — use last 14 closes from the 2-day history, not the 5d window
        closes_14 = h["Close"].values
        if len(closes_14) < 14:
            rsi = 50.0
        else:
            deltas = np.diff(closes_14)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            ag = np.mean(gains[-14:])
            al = np.mean(losses[-14:])
            rs = ag / al if al > 0 else 100
            rsi = 100 - (100 / (1 + rs))

        # 52w position — derived from available window (was making separate t.history call)
        h52 = float(np.max(h['High'].values))
        l52 = float(np.min(h['Low'].values))
        pos_52w = (current - l52) / (h52 - l52) * 100 if h52 != l52 else 50

        # Compute how much of today's gap has been filled
        if gap_pct > 0:  # gap up
            gap_total = today_open - prev_close
            gap_filled = max(0, today_open - current)
            gap_filled_pct = min(100, round((gap_filled / gap_total) * 100, 1)) if gap_total > 0 else 0
        elif gap_pct < 0:  # gap down
            gap_total = prev_close - today_open
            gap_filled = max(0, current - today_open)
            gap_filled_pct = min(100, round((gap_filled / gap_total) * 100, 1)) if gap_total > 0 else 0
        else:
            gap_filled_pct = 0

        result = {
            "ticker": ticker,
            "price": round(current, 2),
            "open": round(today_open, 2),
            "prev_close": round(prev_close, 2),
            "gap_pct": round(gap_pct, 2),
            "gap_filled_pct": gap_filled_pct,
            "rsi": round(rsi, 1),
            "si": round(si, 2),
            "short_ratio": round(sr, 2),
            "vol_ratio": round(vol_ratio, 2),
            "52w_pct": round(pos_52w, 1),
            "high_today": round(high, 2),
            "market_cap": info.get('marketCap', 0),
            "sector": info.get('sector', ''),
            "name": info.get('shortName', ticker),
            "score": 0,
        }
        # Add MA signals
        ma_data = _get_ma_data(ticker, current)
        result.update(ma_data)
        return result
    except Exception as e:
        return None


def score_alert(row):
    """Score 0-100 how squeeze-alert this is."""
    score = 0
    gap = row.get('gap_pct', 0)
    si = row.get('si', 0)
    sr = row.get('short_ratio', 0)
    rsi = row.get('rsi', 50)
    vr = row.get('vol_ratio', 1)

    # Gap size
    if gap >= 10:
        score += 35
    elif gap >= 7:
        score += 25
    elif gap >= 5:
        score += 18
    elif gap >= 3:
        score += 10

    # Short interest
    if si >= 20:
        score += 35
    elif si >= 10:
        score += 25
    elif si >= 5:
        score += 15

    # Short ratio (days to cover)
    if sr >= 5:
        score += 15
    elif sr >= 3:
        score += 10
    elif sr >= 1:
        score += 5

    # RSI oversold — good for squeeze
    if rsi < 35:
        score += 10
    elif rsi < 45:
        score += 5
    # RSI overbought — squeeze has no gas left, penalize
    elif rsi > 70:
        score -= 25
    elif rsi > 60:
        score -= 15

    # Gap fill check — if gap is already filling, the squeeze is fading
    gap_filled = row.get('gap_filled_pct', 0)
    if gap > 0 and gap_filled > 50:
        score -= 20  # more than half the gap already filled = weak setup
    elif gap > 0 and gap_filled > 25:
        score -= 10

    # Volume surge
    if vr >= 3:
        score += 10
    elif vr >= 2:
        score += 5

    # ── MA SIGNAL SCORING ─────────────────────────────────────────────
    # Golden cross = strong bullish confirmation for squeeze plays
    ma_signal = row.get('ma_signal')
    if ma_signal == 'GOLDEN_CROSS':
        score += 25
    elif ma_signal == 'DEATH_CROSS':
        score -= 25  # Opposing trend — squeeze unlikely

    # Price vs EMA21 — below = short-term bearish headwind
    short_signal = row.get('short_signal')
    if short_signal == 'BELOW_EMA21':
        score -= 10

    # EMA50 slope — positive = trend strengthening
    slope_50 = row.get('slope_50', 0)
    if slope_50 > 1:
        score += 10
    elif slope_50 < -1:
        score -= 10

    return min(round(score, 1), 100)


def run_scan(verbose=True):
    state = load_state()
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Reset if new day
    if state.get("date") != today_str:
        state = {"date": today_str, "alerts_today": [], "last_scan": None}

    results = []
    for i, ticker in enumerate(WATCHLIST):
        if verbose:
            print(f"[{i+1}/{len(WATCHLIST)}] {ticker}...", end=" ", flush=True)

        row = scan_ticker(ticker)
        if not row:
            if verbose:
                print("no data")
            continue

        row['score'] = score_alert(row)

        # ── FUNDAMENTAL FILTER ──────────────────────────────────────────────
        # Lou's rule: no trade if fundamentals are broken (dilution, earnings, etc.)
        fund = check_fundamentals(ticker)
        fund_verdict = fund.get('fundamental_verdict', 'UNKNOWN')
        if not fund.get('pass', True):
            row['score'] = 0
            row['kill_reason'] = fund_verdict
            if verbose:
                print(f"gap {row['gap_pct']:+.1f}% | score {row['score']} | KILLED: {fund_verdict}")
            results.append(row)
            continue

        if verbose:
            ma_info = row.get('ma_signal', 'N/A')
            print(f"gap {row['gap_pct']:+.1f}% | vol {row['vol_ratio']:.1f}x | SI {row['si']:.1f}% | RSI {row['rsi']} | MA {ma_info} | score {row['score']}")

        # Trigger alert if gap > threshold AND SI > threshold AND score > 50
        if (row['gap_pct'] >= ALERT_THRESHOLD_GAP and
            row['si'] >= ALERT_THRESHOLD_SI and
            row['score'] >= 50 and
            ticker not in state['alerts_today']):

            alert = {
                "ticker": ticker,
                "time": datetime.now().isoformat(),
                "gap_pct": row['gap_pct'],
                "si": row['si'],
                "price": row['price'],
                "score": row['score'],
                "name": row['name'],
            }
            state['alerts_today'].append(ticker)

            if verbose:
                print(f"  🚨 ALERT: {ticker} gapped {row['gap_pct']:+.1f}% with {row['si']:.1f}% SI!")

        results.append(row)

    results.sort(key=lambda x: x['score'], reverse=True)

    state['last_scan'] = datetime.now().isoformat()
    state['top_results'] = [r for r in results if r['score'] >= 40][:15]
    save_state(state)

    # Save results
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "alerts": [r for r in results if r['score'] >= 60]
        }, f, indent=2)

    return results, state


def print_summary(results, state):
    print("\n" + "=" * 65)
    print(f"📊 GAP ALERT SCAN — {datetime.now().strftime('%H:%M:%S')}")
    print(f"   {len(WATCHLIST)} stocks | Threshold: gap >{ALERT_THRESHOLD_GAP}% + SI >{ALERT_THRESHOLD_SI}%")
    print("=" * 65)

    hot = [r for r in results if r['score'] >= 60]
    warm = [r for r in results if 40 <= r['score'] < 60]

    print(f"\n🔥 HOT ALERTS (score ≥ 60):")
    if not hot:
        print("  None right now")
    for r in hot:
        print(f"  🚨 {r['ticker']} | ${r['price']} | gap {r['gap_pct']:+.1f}% | SI {r['si']:.1f}% | vol {r['vol_ratio']:.1f}x | RSI {r['rsi']:.0f} | score {r['score']}/100")

    print(f"\n⚡ WARM (40-59):")
    if not warm:
        print("  None right now")
    for r in warm:
        print(f"  ⚡ {r['ticker']} | ${r['price']} | gap {r['gap_pct']:+.1f}% | SI {r['si']:.1f}% | vol {r['vol_ratio']:.1f}x | RSI {r['rsi']:.0f} | score {r['score']}/100")

    print(f"\n📈 TOP BY SCORE:")
    for r in results[:5]:
        flag = "🚨" if r['score'] >= 60 else "⚡" if r['score'] >= 40 else "  "
        print(f"  {flag} {r['ticker']:6} | ${r['price']:7.2f} | gap {r['gap_pct']:+6.1f}% | RSI {r['rsi']:5.0f} | SI {r['si']:5.1f}% | vol {r['vol_ratio']:.1f}x | 52w {r['52w_pct']:4.0f}% | {r['score']:5.1f}/100")

    alerts_today = state.get('alerts_today', [])
    print(f"\n⏰ Alerts sent today: {len(alerts_today)} — {alerts_today if alerts_today else 'none'}")
    print(f"   Last scan: {state.get('last_scan', 'never')}")


if __name__ == "__main__":
    verbose = "--quiet" not in sys.argv
    results, state = run_scan(verbose=verbose)
    if verbose:
        print_summary(results, state)

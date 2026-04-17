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

        # ── MULTI-DAY GAP DETECTION ─────────────────────────────────────────
        # Compare current price to 5-day max close — catches intraday gaps that
        # don't show as "today's open vs. prev close" (e.g. IOVA $3→$13 intraday)
        h5d = t.history(period="5d", interval="1d")
        price_5d_max = float(h5d['Close'].max()) if not h5d.empty else current
        price_5d_prev = float(h5d['Close'].iloc[0]) if not h5d.empty else prev_close
        multi_day_gap_pct = ((current - price_5d_max) / price_5d_max) * 100 if price_5d_max > 0 else 0

        # ── SHORT SQUEEZE SIGNALS ─────────────────────────────────────────────
        # Get SI change MoM (shorts building = squeeze fuel)
        si_shares = info.get('sharesShort', 0) or 0
        si_prior = info.get('sharesShortPriorMonth', 0) or 0
        si_change_mom = 0
        if si_prior > 0:
            si_change_mom = round(((si_shares - si_prior) / si_prior) * 100, 1)

        # Days-to-cover (short_ratio is the key squeeze indicator)
        dtc = round(sr, 1)  # days to cover = short_ratio

        # ── EARNINGS TIMING ─────────────────────────────────────────────────
        days_to_earnings = 999
        try:
            from datetime import date as dt_class
            cal = t.calendar
            if cal and 'Earnings Date' in cal:
                ed_list = cal['Earnings Date']
                if isinstance(ed_list, list) and len(ed_list) > 0:
                    ed = ed_list[0]
                    if isinstance(ed, dt_class):
                        days_to_earnings = (ed - dt_class.today()).days
                    elif hasattr(ed, 'date') and callable(ed.date):
                        days_to_earnings = (ed.date() - dt_class.today()).days
        except Exception:
            pass

        # ── SQUEEZE COMPOSITE SCORE ───────────────────────────────────────────
        # Combined score for IOVA-type setups: high SI + high DTC + shorts building
        squeeze_score = 0
        if si >= 30: squeeze_score += 40
        elif si >= 20: squeeze_score += 25
        elif si >= 10: squeeze_score += 10
        if dtc >= 5: squeeze_score += 30
        elif dtc >= 3: squeeze_score += 20
        elif dtc >= 1: squeeze_score += 10
        if si_change_mom >= 20: squeeze_score += 20
        elif si_change_mom >= 10: squeeze_score += 15
        elif si_change_mom >= 5: squeeze_score += 8
        # Bottomfishing bonus — stocks near 52w lows have more room
        if pos_52w <= 15: squeeze_score += 15
        elif pos_52w <= 25: squeeze_score += 10
        elif pos_52w <= 35: squeeze_score += 5

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
            "si_change_mom": round(si_change_mom, 1),
            "vol_ratio": round(vol_ratio, 2),
            "52w_pct": round(pos_52w, 1),
            "multi_day_gap_pct": round(multi_day_gap_pct, 2),
            "days_to_earnings": int(days_to_earnings),
            "squeeze_score": int(squeeze_score),
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
    """Score 0-100 how squeeze-alert this is.
    Enhanced with multi-day gap detection + short squeeze composite.
    """
    score = 0
    gap = row.get('gap_pct', 0)
    multi_gap = row.get('multi_day_gap_pct', 0)
    si = row.get('si', 0)
    sr = row.get('short_ratio', 0)
    rsi = row.get('rsi', 50)
    vr = row.get('vol_ratio', 1)
    sq_score = row.get('squeeze_score', 0)
    si_change = row.get('si_change_mom', 0)
    pos_52w = row.get('52w_pct', 50)

    # ── PRIMARY GAP SIGNAL (today's open vs prev close) ────────────────
    if gap >= 10:
        score += 35
    elif gap >= 7:
        score += 25
    elif gap >= 5:
        score += 18
    elif gap >= 3:
        score += 10

    # ── MULTI-DAY GAP (intraday run detection — IOVA's key signal) ──
    # A stock can run 50%+ intraday without a traditional open gap
    if multi_gap >= 50:
        score += 50
    elif multi_gap >= 30:
        score += 35
    elif multi_gap >= 20:
        score += 25
    elif multi_gap >= 10:
        score += 15
    elif multi_gap >= 5:
        score += 8

    # ── SHORT INTEREST ───────────────────────────────────────────────────
    if si >= 30:
        score += 40  # IOVA-tier SI
    elif si >= 20:
        score += 30
    elif si >= 10:
        score += 20
    elif si >= 5:
        score += 10

    # ── DAYS TO COVER (short_ratio = squeeze battery) ──────────────────
    if sr >= 10:
        score += 30
    elif sr >= 5:
        score += 25  # shorts completely trapped
    elif sr >= 3:
        score += 15
    elif sr >= 1:
        score += 8

    # ── SI CHANGE MOM (shorts rapidly building = fuel) ──────────────
    if si_change >= 30:
        score += 20
    elif si_change >= 20:
        score += 15
    elif si_change >= 10:
        score += 10
    elif si_change >= 5:
        score += 5

    # ── SQUEEZE COMPOSITE (pre-built from scan_ticker) ───────────────
    # Use it to boost stocks already flagged as squeeze candidates
    if sq_score >= 60:
        score += 25
    elif sq_score >= 40:
        score += 15
    elif sq_score >= 20:
        score += 8

    # ── RSI OVERSOLD ──────────────────────────────────────────────────
    if rsi < 30:
        score += 15
    elif rsi < 40:
        score += 10
    elif rsi < 50:
        score += 5
    elif rsi > 75:
        score -= 20  # overbought — squeeze may have already run
    elif rsi > 65:
        score -= 10

    # ── BOTTOMFISHING (near 52w lows = more runway) ────────────────────
    if pos_52w <= 15:
        score += 15
    elif pos_52w <= 25:
        score += 10
    elif pos_52w <= 35:
        score += 5

    # ── VOLUME SURGE ───────────────────────────────────────────────────
    if vr >= 5:
        score += 20
    elif vr >= 3:
        score += 12
    elif vr >= 2:
        score += 6

    # ── GAP FILL CHECK ────────────────────────────────────────────────
    gap_filled = row.get('gap_filled_pct', 0)
    if gap > 0 and gap_filled > 50:
        score -= 20
    elif gap > 0 and gap_filled > 25:
        score -= 10

    # ── MA SIGNAL SCORING ─────────────────────────────────────────────
    ma_signal = row.get('ma_signal')
    if ma_signal == 'GOLDEN_CROSS':
        score += 20
    elif ma_signal == 'DEATH_CROSS':
        score -= 20

    short_signal = row.get('short_signal')
    if short_signal == 'BELOW_EMA21':
        score -= 8

    slope_50 = row.get('slope_50', 0)
    if slope_50 > 1:
        score += 8
    elif slope_50 < -1:
        score -= 8

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
            sq = row.get('squeeze_score', 0)
            mg = row.get('multi_day_gap_pct', 0)
            dtc = row.get('short_ratio', 0)
            sq_tag = "🔥" if sq >= 40 else ""
            mg_tag = "📈" if abs(mg) > 10 else ""
            print(f"gap {row['gap_pct']:+.1f}% | mg {mg:+.1f}%{mg_tag} | vol {row['vol_ratio']:.1f}x | SI {row['si']:.1f}% | DTC {dtc:.1f} | sq {sq}{sq_tag} | score {row['score']}")

        # Trigger alert via THREE paths:
        # 1. Traditional: gap > 5% + SI > 5% + score >= 50
        # 2. Multi-day squeeze: multi_day_gap >= 10% + squeeze_score >= 40 + score >= 50
        # 3. Pure squeeze: squeeze_score >= 65 + score >= 55 (no gap required)
        sq_score = row.get('squeeze_score', 0)
        multi_gap = row.get('multi_day_gap_pct', 0)
        si = row.get('si', 0)
        gap = row.get('gap_pct', 0)

        alert_types = []
        if gap >= ALERT_THRESHOLD_GAP and si >= ALERT_THRESHOLD_SI and row['score'] >= 50:
            alert_types.append("GAP")
        if multi_gap >= 10 and sq_score >= 40 and row['score'] >= 50:
            alert_types.append("MULTI_SQUEEZE")
        if sq_score >= 65 and row['score'] >= 55:
            alert_types.append("SQUEEZE")

        if alert_types and ticker not in state['alerts_today']:
            alert = {
                "ticker": ticker,
                "time": datetime.now().isoformat(),
                "gap_pct": row['gap_pct'],
                "multi_day_gap_pct": row['multi_day_gap_pct'],
                "si": row['si'],
                "short_ratio": row['short_ratio'],
                "si_change_mom": row.get('si_change_mom', 0),
                "squeeze_score": sq_score,
                "price": row['price'],
                "score": row['score'],
                "name": row['name'],
                "alert_types": alert_types,
            }
            state['alerts_today'].append(ticker)

            if verbose:
                sq = sq_score
                mg = row.get('multi_day_gap_pct', 0)
                atype = ','.join(alert_types)
                print(f"  🚨 ALERT [{atype}]: {ticker} gap {row['gap_pct']:+.1f}% | multi {mg:+.1f}% | "
                      f"SI {row['si']:.0f}% | DTC {row['short_ratio']:.1f} | sq_score {sq} | score {row['score']}")

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

    # Append SIGBOTTI coin card
    try:
        from coin_sb import get_card
        card = get_card()
        if card:
            print(f"\n{card}")
    except Exception:
        pass


if __name__ == "__main__":
    verbose = "--quiet" not in sys.argv
    results, state = run_scan(verbose=verbose)
    if verbose:
        print_summary(results, state)

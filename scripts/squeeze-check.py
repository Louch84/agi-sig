#!/usr/bin/env python3
"""
Short Squeeze Checker — Consolidated view with world model context.
Pulls fresh data + overlays what we know from the world model.
"""
import numpy as np
import json
import os
import sys
from datetime import datetime
from urllib.request import urlopen, Request
import urllib.error
import yfinance as yf

WORKSPACE = os.path.dirname(os.path.dirname(__file__))
WM_FILE = os.path.join(WORKSPACE, "data", "world-model.json")


def yf_get(ticker, period="5d"):
    """Get Yahoo Finance data via chart API — no yfinance dependency."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range={period}"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            chart = data.get("chart", {}).get("result", [{}])[0]
            timestamps = chart.get("timestamp", [])
            closes = chart.get("indicators", {}).get("quote", [{}])[0].get("close", [])
            opens = chart.get("indicators", {}).get("quote", [{}])[0].get("open", [])
            highs = chart.get("indicators", {}).get("quote", [{}])[0].get("high", [])
            lows = chart.get("indicators", {}).get("quote", [{}])[0].get("low", [])
            volumes = chart.get("indicators", {}).get("quote", [{}])[0].get("volume", [])
            meta = chart.get("meta", {})
            return {
                "timestamps": timestamps, "closes": closes, "opens": opens,
                "highs": highs, "lows": lows, "volumes": volumes,
                "symbol": meta.get("symbol", ticker),
            }
    except Exception as e:
        return None


def yf_info(ticker):
    """Get Yahoo Finance info via rapidapi or fallback."""
    # Try Yahoo Finance info endpoint
    url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=defaultKeyStatistics,summaryDetail,price"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            result = data.get("quoteSummary", {}).get("result", [{}])[0]
            price_data = result.get("price", {})
            stats = result.get("defaultKeyStatistics", {})
            summary = result.get("summaryDetail", {})
            return {
                "shortPercentOfFloat": stats.get("shortPercentOfFloat", {}).get("raw", 0) or 0,
                "shortRatio": stats.get("shortRatio", {}).get("raw", 0) or 0,
                "currentPrice": price_data.get("regularMarketPrice", {}).get("raw") or price_data.get("currentPrice", {}).get("raw") or 0,
                "marketCap": price_data.get("marketCap", {}).get("raw", 0) or 0,
            }
    except Exception as e:
        return {}


def load_world_model():
    if os.path.exists(WM_FILE):
        try:
            with open(WM_FILE) as f:
                return json.load(f)
        except Exception as e:
            pass  # Fallback return is appropriate here
    return {}


def get_wm_entities_by_type(wm, entity_type):
    return {name: e for name, e in wm.get("entities", {}).items() if e.get("type") == entity_type}


def run_check(tickers=None):
    wm = load_world_model()
    stocks_wm = get_wm_entities_by_type(wm, "stock")
    beliefs = wm.get("beliefs", {})
    prefs = wm.get("preferences", {}).get("Lou", {})

    if not tickers:
        # Default squeeze watchlist
        tickers = ["LCID", "LUNR", "GRPN", "AMC", "SNAP", "MVST", "SMCI", "SOFI", "DNA", "PINS"]

    print("=" * 70)
    print(f"📊 SHORT SQUEEZE CONSOLIDATED — {datetime.now().strftime('%a %b %d %H:%M %Z')}")
    print("=" * 70)

    # Context from world model
    ctx = beliefs.get("short_squeeze_strategy", {}).get("claim", "")
    pref = prefs.get("trading", {}).get("value", "") if isinstance(prefs.get("trading"), dict) else str(prefs.get("trading", ""))
    print(f"Strategy: {ctx}")
    if pref:
        print(f"Lou's style: {pref}")
    print()

    for ticker in tickers:
        # Defaults so exception handlers can safely reference these
        price = 0.0
        si = 0.0
        sr = 0.0
        gap = 0.0
        rsi = 50.0
        mc_str = ""
        pos52 = 50.0
        wm_setup = "no prior setup"
        wm_note = ""

        try:
            t = yf.Ticker(ticker)
            info = t.info
            h = t.history(period="5d", interval="1d")

            if h.empty:
                print(f"{ticker}: no data")
                continue

            closes = h['Close'].values
            today_close = closes[-1]
            today_open = h['Open'].iloc[-1]
            prev_close = closes[-2] if len(closes) > 1 else today_close
            gap = ((today_open - prev_close) / prev_close) * 100

            # RSI
            deltas = np.diff(closes)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            ag = np.mean(gains[-14:]) if len(gains) >= 14 else np.mean(gains)
            al = np.mean(losses[-14:]) if len(losses) >= 14 else np.mean(losses)
            rs = ag / al if al > 0 else 100
            rsi = 100 - (100 / (1 + rs))

            si = (info.get('shortPercentOfFloat', 0) or 0) * 100
            sr = info.get('shortRatio', 0) or 0
            price = info.get('currentPrice', today_close)
            mc = info.get('marketCap', 0) or 0
            mc_str = f"${mc/1e9:.1f}B" if mc > 1e9 else f"${mc/1e6:.0f}M" if mc > 1e6 else ""

            # 52w position
            h52 = float(np.max(h['High'].values))
            l52 = float(np.min(h['Low'].values))
            pos52 = (price - l52) / (h52 - l52) * 100 if h52 > l52 else 50

            # World model context
            wm_data = stocks_wm.get(ticker, {})
            wm_setup = wm_data.get("properties", {}).get("setup", "no prior setup")
            wm_note = wm_data.get("properties", {}).get("catalyst", "")

            # Score
            score = 0
            if gap < -5: score += 25
            elif gap < -2: score += 15
            elif gap > 5: score += 15  # already ran
            elif gap > 2: score += 10
            if si >= 20: score += 30
            elif si >= 10: score += 20
            elif si >= 5: score += 10
            if rsi < 30: score += 20
            elif rsi < 40: score += 12
            elif rsi < 50: score += 6
            if sr >= 5: score += 12
            elif sr >= 3: score += 8
            elif sr >= 1: score += 4
            if pos52 < 20: score += 8

            # Direction verdict
            if gap > 5:
                verdict = "⚠️ ALERT"
                verdict_detail = "Already ran hard today"
            elif gap < -5 and si >= 15 and rsi < 50:
                verdict = "🔥 ENTRY"
                verdict_detail = "Gap down + short fuel + room"
            elif gap < -2 and si >= 10:
                verdict = "📋 WATCH"
                verdict_detail = "Watch for continuation"
            elif si >= 20:
                verdict = "💀 HIGH SI"
                verdict_detail = "Massive short fuel"
            else:
                verdict = "👀 MONITOR"
                verdict_detail = ""

            gap_str = f"{gap:+6.1f}%"
            gap_sym = "🔴" if gap < -5 else ("📉" if gap < -2 else ("🟢" if gap > 2 else "➖"))
            rsi_sym = "🔥" if rsi < 30 else ("⚠️" if rsi < 45 else "✅")
            si_sym = "💀" if si >= 20 else ("⚡" if si >= 10 else "  ")
            score_bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))

            print(f"{gap_sym}{rsi_sym}{si_sym} {ticker:6} ${price:7.2f} {mc_str:>8} | gap:{gap_str} | RSI:{rsi:5.0f} | SI:{si:5.1f}% | SR:{sr:.1f}d | 52w:{pos52:4.0f}%")
            print(f"         {verdict} {verdict_detail}")
            if wm_setup != "no prior setup":
                print(f"         📌 Prior: {wm_setup}")
            if wm_note:
                print(f"         💡 Note: {wm_note}")
            print(f"         Score: {score_bar} {score}/100")
            print()

        except yf.exceptions.YfinanceError as e:
            print(f"  {ticker}: yfinance error — {e}")

        except Exception as e:
            print(f"  {ticker}: error — {e}")

    print("=" * 70)
    print("Key: 🔥RSI<30 ⚠️RSI<45 💀SI>20% ⚡SI>10% | 🔴gap<-5% 📉gap<-2% 🟢gap>+2%")
    print(f"Strategy: {ctx}")


if __name__ == "__main__":
    tickers = sys.argv[1:] if len(sys.argv) > 1 else None
    run_check(tickers)

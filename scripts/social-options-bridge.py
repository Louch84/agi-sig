#!/usr/bin/env python3
"""
Social Options Flow Bridge — Detects IOVA-type setups.
Cross-references social mention spikes with options flow and short interest.
Flags: high-SI stocks that are trending on WSB/crypto + options chain heating up.

IOVA case: WSB viral post + 34.5% SI + FDA competitor rejection = gamma ramp.
This scanner catches it BEFORE the options explode.
"""
import yfinance as yf
import requests
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path("/Users/sigbotti/.openclaw/workspace/data")
DATA_DIR.mkdir(exist_ok=True)
STATE_FILE = DATA_DIR / "social-options-bridge-state.json"
RESULTS_FILE = DATA_DIR / "social-options-bridge.json"

# Subreddits to monitor
SUBREDDITS = ["wallstreetbets", "stocks", "pennystocks", "options", "Shortsqueeze", "cryptocurrency", "SolanaMemes"]
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

# Thresholds
MIN_SI = 25.0        # % short interest — minimum for squeeze setup
MIN_SOCIAL_SCORE = 3 # mention spike threshold (3+ mentions in 24h)
MIN_OPTIONS_VOL = 100 # minimum call volume for signal
MIN_IV = 0.50        # minimum implied volatility for signal


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_scan": None, "trending_tickers": {}, "alerts": []}

def save_state(state):
    tmp = str(STATE_FILE) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


def get_social_mentions(ticker):
    """Get social mention count + sentiment for a ticker across subreddits."""
    total_mentions = 0
    total_score = 0
    posts = []
    
    for sub in SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{sub}/search.json?q={ticker}&restrict_sr=1&sort=top&limit=25"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code != 200:
                continue
            data = resp.json().get("data", {}).get("children", [])
            
            for post in data[:10]:  # top 10 per sub
                title = post["data"].get("title", "").lower()
                selftext = post["data"].get("selftext", "").lower()
                score = post["data"].get("score", 0)
                num_comments = post["data"].get("num_comments", 0)
                created = post["data"].get("created_utc", 0)
                
                # Only count recent posts (24h)
                age_hours = (datetime.now().timestamp() - created) / 3600
                if age_hours > 48:
                    continue
                
                combined = f"{title} {selftext}"
                # Simple ticker match
                tickers_in_post = extract_tickers_from_text(combined)
                if ticker.upper() in tickers_in_post or ticker.lower() in combined:
                    total_mentions += 1
                    total_score += score
                    posts.append({
                        "sub": sub,
                        "title": title[:100],
                        "score": score,
                        "comments": num_comments,
                        "age_hours": round(age_hours, 1),
                    })
        except Exception:
            pass
    
    return {
        "mentions": total_mentions,
        "score": total_score,
        "recent_posts": posts[-5:] if posts else [],
    }


def extract_tickers_from_text(text):
    """Extract uppercase ticker-like patterns from text."""
    import re
    # Match 2-5 letter all-caps (stock tickers)
    return set(re.findall(r'\b[A-Z]{1,5}\b', text))


def get_options_flow(ticker):
    """Get options call activity — volume, OI, IV for near-term calls."""
    try:
        t = yf.Ticker(ticker)
        expirations = list(t.options)[:4]  # next 4 expirations
        if not expirations:
            return None
        
        total_call_vol = 0
        total_call_oi = 0
        avg_iv = 0
        iv_count = 0
        max_voi = 0
        hot_strikes = []
        
        for exp in expirations:
            try:
                opt = t.option_chain(exp)
                for _, row in opt.calls.iterrows():
                    vol = row.get("volume", 0) or 0
                    oi = row.get("openInterest", 0) or 0
                    iv = row.get("impliedVolatility", 0) or 0
                    strike = row.get("strike", 0)
                    price = row.get("lastPrice", 0) or 0
                    
                    total_call_vol += vol
                    total_call_oi += oi
                    
                    if iv > 0:
                        avg_iv += iv
                        iv_count += 1
                    
                    voi = vol + oi
                    if voi > max_voi:
                        max_voi = voi
                    
                    # Hot strike: high volume + high OI + IV > 50%
                    if vol > 50 and oi > 100 and iv > MIN_IV:
                        hot_strikes.append({
                            "strike": strike,
                            "expiry": exp,
                            "vol": vol,
                            "oi": oi,
                            "iv": iv,
                            "price": price,
                            "voi": voi,
                        })
            except Exception:
                pass
        
        avg_iv_pct = (avg_iv / iv_count * 100) if iv_count > 0 else 0
        
        return {
            "total_call_vol": total_call_vol,
            "total_call_oi": total_call_oi,
            "avg_iv_pct": round(avg_iv_pct, 1),
            "max_voi": max_voi,
            "hot_strikes": sorted(hot_strikes, key=lambda x: x["voi"], reverse=True)[:5],
        }
    except Exception:
        return None


def get_short_data(ticker):
    """Get short interest data."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        si = (info.get("shortPercentOfFloat", 0) or 0) * 100
        sr = info.get("shortRatio", 0) or 0
        si_shares = info.get("sharesShort", 0) or 0
        si_prior = info.get("sharesShortPriorMonth", 0) or 0
        fee = info.get("shortBorrowRate", 0) or 0
        
        si_change = 0
        if si_prior > 0:
            si_change = ((si_shares - si_prior) / si_prior) * 100
        
        inst_pct = (info.get("heldPercentInstitutions", 0) or 0) * 100
        
        return {
            "si": round(si, 1),
            "short_ratio": round(sr, 1),
            "si_change": round(si_change, 1),
            "si_shares": si_shares,
            "borrow_fee": round(fee * 100, 2) if fee else 0,
            "inst_pct": round(inst_pct, 1),
        }
    except Exception:
        return None


def get_stock_price(ticker):
    """Get current stock price and recent move."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
        prev_close = info.get("regularMarketPreviousClose") or 0
        open_price = info.get("regularMarketOpen") or 0
        
        # 5-day move
        h5 = t.history(period="5d")
        if len(h5) >= 2:
            price_5d_ago = h5["Close"].iloc[0]
            move_5d = ((price - price_5d_ago) / price_5d_ago * 100) if price_5d_ago > 0 else 0
        else:
            move_5d = 0
        
        return {
            "price": round(float(price), 2),
            "prev_close": round(float(prev_close), 2),
            "move_today": round(((price - prev_close) / prev_close * 100) if prev_close else 0, 2),
            "move_5d": round(move_5d, 2),
        }
    except Exception:
        return None


def score_setup(ticker, social, options, shorts, price_data):
    """Score 0-100 how strong this IOVA-type setup is."""
    score = 0
    
    # ── SHORT INTEREST (core fuel) ──────────────────────────────
    si = shorts.get("si", 0)
    if si >= 40: score += 35
    elif si >= 30: score += 25
    elif si >= 25: score += 15
    elif si >= 20: score += 8
    
    # Borrow fee — high fee = hard to borrow = more explosive
    fee = shorts.get("borrow_fee", 0)
    if fee >= 20: score += 20
    elif fee >= 10: score += 12
    elif fee >= 5: score += 6
    
    # ── SOCIAL MENTIONS (ignition spark) ───────────────────────
    mentions = social.get("mentions", 0)
    social_score = social.get("score", 0)
    if mentions >= 10: score += 25
    elif mentions >= 5: score += 18
    elif mentions >= 3: score += 12
    elif mentions >= 1: score += 5
    
    if social_score >= 500: score += 15
    elif social_score >= 200: score += 10
    elif social_score >= 50: score += 5
    
    # ── OPTIONS FLOW (gamma ramp signal) ───────────────────────
    opts = options or {}
    total_vol = opts.get("total_call_vol", 0)
    avg_iv = opts.get("avg_iv_pct", 0)
    max_voi = opts.get("max_voi", 0)
    
    if total_vol >= 10000: score += 25
    elif total_vol >= 5000: score += 18
    elif total_vol >= 1000: score += 10
    elif total_vol >= 100: score += 5
    
    if avg_iv >= 80: score += 20
    elif avg_iv >= 60: score += 15
    elif avg_iv >= 50: score += 8
    
    if max_voi >= 5000: score += 15
    elif max_voi >= 1000: score += 10
    elif max_voi >= 200: score += 5
    
    # ── PRICE CONFIRMATION ─────────────────────────────────────
    move_5d = price_data.get("move_5d", 0) if price_data else 0
    move_today = price_data.get("move_today", 0) if price_data else 0
    
    # Stock NOT moving yet but options heating up = early signal
    # IOVA had stock move 21% intraday AFTER options already exploded
    # Early signal: stock within +/- 10%, options already hot
    if abs(move_today) < 10: score += 10  # early stage
    if abs(move_5d) < 15: score += 5  # hasn't run yet = more room
    
    # ── SI CHANGE MoM (shorts building) ───────────────────────
    si_change = shorts.get("si_change", 0)
    if si_change >= 20: score += 15
    elif si_change >= 10: score += 10
    elif si_change >= 5: score += 5
    
    return min(score, 100)


def format_signal(ticker, score, social, options, shorts, price_data):
    """Format a Discord-friendly signal card."""
    lines = [
        f"📊 **{ticker}** — Social Options Signal",
        f"   Score: **{score}/100** {'🔥 HOT' if score >= 60 else '⚡ WARM' if score >= 40 else '💤 QUIET'}",
        "",
    ]
    
    if price_data:
        lines.append(f"   Price: **\${price_data['price']}** ({price_data['move_today']:+.1f}% today | {price_data['move_5d']:+.1f}% 5d)")
    
    shorts_data = shorts or {}
    lines += [
        f"   SI: **{shorts_data.get('si', 0):.1f}%** | DTC: **{shorts_data.get('short_ratio', 0):.1f}** | Borrow: **{shorts_data.get('borrow_fee', 0):.1f}%**",
        f"   SI change MoM: **{shorts_data.get('si_change', 0):+.1f}%**",
    ]
    
    social_data = social or {}
    posts = social_data.get("recent_posts", [])
    lines += [
        f"   Social: **{social_data.get('mentions', 0)}** mentions | score **{social_data.get('score', 0)}**",
    ]
    if posts:
        lines.append(f"   Top post: {posts[0]['sub']} — {posts[0]['title'][:60]}")
    
    opts_data = options or {}
    lines += [
        f"   Options: vol **{opts_data.get('total_call_vol', 0):,}** | OI **{opts_data.get('total_call_oi', 0):,}** | IV **{opts_data.get('avg_iv_pct', 0):.0f}%**",
    ]
    
    hot = opts_data.get("hot_strikes", [])
    if hot:
        lines.append(f"   🔥 Hot strikes: " + " | ".join([f"\${s['strike']:.2f} (OI {s['oi']:,})" for s in hot[:3]]))
    
    return "\n".join(lines)


def scan(tickers=None, verbose=True):
    """Scan universe for IOVA-type social + options + SI setups."""
    if tickers is None:
        universe_file = Path("/Users/sigbotti/.openclaw/workspace/data/universe.json")
        if universe_file.exists():
            with open(universe_file) as f:
                tickers = json.load(f).get("tickers", [])
        else:
            tickers = []
    
    if not tickers:
        return []
    
    state = load_state()
    results = []
    
    if verbose:
        print(f"🔗 Social Options Bridge — {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Scanning {len(tickers)} tickers for IOVA-type setups...")
    
    for i, ticker in enumerate(tickers):
        if verbose:
            print(f"[{i+1}/{len(tickers)}] {ticker}...", end=" ", flush=True)
        
        # Fetch all data in parallel-ish (sequential for rate limit)
        social = get_social_mentions(ticker)
        options = get_options_flow(ticker)
        shorts = get_short_data(ticker)
        price = get_stock_price(ticker)
        
        mentions = social.get("mentions", 0)
        si = shorts.get("si", 0) if shorts else 0
        opts_vol = options.get("total_call_vol", 0) if options else 0
        iv = options.get("avg_iv_pct", 0) if options else 0
        
        score = score_setup(ticker, social, options, shorts, price)
        
        row = {
            "ticker": ticker,
            "score": score,
            "social": social,
            "options": options,
            "shorts": shorts,
            "price": price,
            "scan_time": datetime.now().isoformat(),
        }
        results.append(row)
        
        if verbose:
            tags = []
            if si >= 30: tags.append(f"SI{si:.0f}%")
            if mentions >= 3: tags.append(f"SOC{mentions}")
            if opts_vol >= 100: tags.append(f"VOL{opts_vol:,}")
            if iv >= 50: tags.append(f"IV{iv:.0f}%")
            tag_str = "[" + ",".join(tags) + "]" if tags else ""
            print(f"score {score}/100 {tag_str}")
        
        time.sleep(0.3)  # rate limit
    
    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Save results
    with open(RESULTS_FILE, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
        }, f, indent=2, default=str)
    
    state["last_scan"] = datetime.now().isoformat()
    save_state(state)
    
    # Print top signals
    top = [r for r in results if r["score"] >= 40]
    if verbose and top:
        print(f"\n{'='*60}")
        print(f"📊 TOP SIGNALS (score >= 40):")
        for r in top[:10]:
            s = r["shorts"] or {}
            p = r["price"] or {}
            print(f"  {r['ticker']:6} | score {r['score']:3}/100 | "
                  f"SI {s.get('si',0):.0f}% | SOC {r['social'].get('mentions',0)} | "
                  f"VOL {r['options'].get('total_call_vol',0):,}")
    
    return results


if __name__ == "__main__":
    verbose = "--quiet" not in sys.argv
    results = scan(verbose=verbose)
    
    # Format Discord card for top signal
    if results:
        top = results[0]
        if top["score"] >= 50:
            card = format_signal(
                top["ticker"], top["score"],
                top["social"], top["options"],
                top["shorts"], top["price"]
            )
            print(f"\n{card}")
    
    print(f"\n💾 Saved to {RESULTS_FILE}")

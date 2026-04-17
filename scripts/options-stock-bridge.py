#!/usr/bin/env python3
"""
Whale Options → Stock Signal Bridge
Cross-references unusual options activity with stock fundamentals + SI + news.
Detects IOVA-type plays: whale calls on high-SI, low-float, news-catalyst stocks.

Logic:
  Whale buys 10,000+ $5 calls on IOVA →
    → Check: Is SI > 30%? YES → gamma ramp fuel
    → Check: Is float low? YES → easy to squeeze  
    → Check: Any news catalyst? → confirms direction
    → SCORE: If all 3 = IOVA-type alert

Lou's IOVA case: $4 calls went $0.01 → $13 on NO company-specific news.
The signal was pure options flow + SI + social. This bridge catches it.
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
RESULTS_FILE = DATA_DIR / "options-stock-bridge.json"
UNUSUAL_FILE = DATA_DIR / "unusual-options-scanner.json"

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

# Thresholds for IOVA-type alert
MIN_VOL = 500       # minimum call volume
MIN_SI = 25.0       # minimum short interest %
MIN_SCORE = 50      # minimum composite score to alert


def get_short_data(ticker):
    """Get SI%, float proxy, DTC, borrow fee."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        
        si = (info.get("shortPercentOfFloat", 0) or 0) * 100
        sr = info.get("shortRatio", 0) or 0
        fee = info.get("shortBorrowRate", 0) or 0
        float_shares = info.get("sharesFloat", 0) or 0
        inst_pct = (info.get("heldPercentInstitutions", 0) or 0) * 100
        
        # Low float proxy: if avg volume >> float, float is tight
        avg_vol = info.get("averageVolume", 0) or 0
        vol_to_float = avg_vol / float_shares if float_shares > 0 else 999
        
        # days to cover relative to avg volume
        dtc = sr
        
        return {
            "si": round(si, 1),
            "short_ratio": round(sr, 1),
            "borrow_fee": round(fee * 100, 2) if fee else 0,
            "float": float_shares,
            "avg_vol": avg_vol,
            "vol_to_float": round(vol_to_float, 1),
            "inst_pct": round(inst_pct, 1),
        }
    except Exception:
        return {"si": 0, "short_ratio": 0, "borrow_fee": 0, "float": 0, "avg_vol": 0, "vol_to_float": 999, "inst_pct": 0}


def get_news(ticker):
    """Get recent news — count + recency."""
    try:
        t = yf.Ticker(ticker)
        news = t.news or []
        
        recent = []
        for n in news[:5]:
            pub = n.get("pubDate", "")
            if pub:
                try:
                    pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                    age_h = (datetime.now(pub_dt.tzinfo) - pub_dt).total_seconds() / 3600
                    recent.append({
                        "title": n.get("title", "")[:80],
                        "age_h": round(age_h, 1),
                    })
                except Exception:
                    pass
        
        return {
            "count": len(news),
            "recent": recent[:3],
        }
    except Exception:
        return {"count": 0, "recent": []}


def get_stock_move(ticker):
    """Get stock price + recent move."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
        prev = info.get("regularMarketPreviousClose") or 0
        open_p = info.get("regularMarketOpen") or 0
        
        h5 = t.history(period="5d")
        move_5d = 0
        if len(h5) >= 2:
            move_5d = ((price - h5["Close"].iloc[0]) / h5["Close"].iloc[0] * 100) if h5["Close"].iloc[0] > 0 else 0
        
        return {
            "price": round(float(price), 2),
            "move_today": round(((price - prev) / prev * 100) if prev else 0, 2),
            "move_5d": round(move_5d, 2),
        }
    except Exception:
        return {"price": 0, "move_today": 0, "move_5d": 0}


def score_whale_play(ticker, option, shorts, news, price_data):
    """Score 0-100 how strong this whale options → stock play is.
    IOVA had: SI 34.5%, whale calls, low float, no news = explosive.
    """
    score = 0
    si = shorts.get("si", 0)
    sr = shorts.get("short_ratio", 0)
    fee = shorts.get("borrow_fee", 0)
    vol = option.get("volume", 0)
    oi = option.get("open_interest", 0)
    voi = vol + oi
    ivt = option.get("sentiment", "NEUTRAL")
    news_count = news.get("count", 0)
    price_move = price_data.get("move_today", 0)
    
    # ── WHALE SIZE (volume + OI) ──────────────────────────────
    if voi >= 10000: score += 30
    elif voi >= 5000: score += 22
    elif voi >= 1000: score += 15
    elif voi >= 500: score += 8
    
    # ── SHORT INTEREST (core squeeze fuel) ────────────────────
    if si >= 40: score += 30
    elif si >= 30: score += 22
    elif si >= 25: score += 15
    elif si >= 20: score += 8
    elif si >= 10: score += 4
    
    # ── BORROW FEE (hard to borrow = explosive) ───────────────
    if fee >= 20: score += 15
    elif fee >= 10: score += 10
    elif fee >= 5: score += 5
    
    # ── CALL SENTIMENT (bullish = squeeze setup) ──────────────
    if ivt == "BULLISH": score += 20
    elif ivt == "NEUTRAL": score += 8
    
    # ── NEWS CATALYST (confirms direction) ────────────────────
    if news_count >= 3: score += 15
    elif news_count >= 1: score += 10
    
    # ── PRICE CONFIRMATION ──────────────────────────────────
    # IOVA: calls went crazy BEFORE stock moved significantly
    # If stock already up big, squeeze may be exhausted
    if abs(price_move) < 5: score += 10  # early stage = more room
    elif abs(price_move) < 10: score += 5
    elif abs(price_move) > 20: score -= 15  # already ran
    
    # ── DTC (days to cover = trapped shorts) ──────────────────
    if sr >= 10: score += 15
    elif sr >= 5: score += 10
    elif sr >= 3: score += 6
    
    # ── VOLUME/OPEN INTEREST RATIO ───────────────────────────
    voi_ratio = option.get("voi_ratio", 0)
    if voi_ratio >= 5: score += 10
    elif voi_ratio >= 2: score += 6
    elif voi_ratio >= 1: score += 3
    
    return min(score, 100)


def run_scan():
    """Run bridge: unusual options + stock data + SI + news."""
    
    # Load unusual options data
    if Path(UNUSUAL_FILE).exists():
        with open(UNUSUAL_FILE) as f:
            unusual_data = json.load(f)
        options_results = unusual_data.get("results", [])
    else:
        print("⚠️ Run unusual-options-scanner.py first to generate options data")
        options_results = []
    
    if not options_results:
        print("No unusual options data found")
        return []
    
    print(f"🐋 Whale Options → Stock Bridge — {datetime.now().strftime('%H:%M:%S')}")
    print(f"   Enriching {len(options_results)} unusual options signals with stock data...\n")
    
    # Deduplicate by ticker (keep highest-VOI per ticker)
    by_ticker = {}
    for o in options_results:
        t = o["ticker"]
        voi = o.get("volume", 0) + o.get("open_interest", 0)
        if t not in by_ticker or voi > by_ticker[t]["voi"]:
            by_ticker[t] = {"option": o, "voi": voi}
    
    enriched = []
    
    for ticker, data in by_ticker.items():
        option = data["option"]
        voi = data["voi"]
        
        if voi < 200:  # skip low-VOI noise
            continue
        
        print(f"{ticker}...", end=" ", flush=True)
        
        shorts = get_short_data(ticker)
        news = get_news(ticker)
        price = get_stock_move(ticker)
        
        si = shorts.get("si", 0)
        score = score_whale_play(ticker, option, shorts, news, price)
        
        row = {
            "ticker": ticker,
            "score": score,
            "option": {
                "type": option.get("type"),
                "strike": option.get("strike"),
                "expiry": option.get("expiration"),
                "price": option.get("last"),
                "volume": option.get("volume"),
                "oi": option.get("open_interest"),
                "voi_ratio": option.get("voi_ratio"),
                "sentiment": option.get("sentiment"),
                "itm_pct": option.get("itm_pct"),
            },
            "shorts": shorts,
            "news": news,
            "price": price,
        }
        enriched.append(row)
        
        if score >= 40:
            si_tag = "🔥" if si >= 30 else "⚡"
            print(f"score {score}/100 | SI {si:.0f}% | VOL {voi:,} {si_tag}")
        else:
            print(f"score {score}/100")
        
        time.sleep(0.2)
    
    enriched.sort(key=lambda x: x["score"], reverse=True)
    
    # Save
    with open(RESULTS_FILE, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": enriched,
        }, f, indent=2, default=str)
    
    # Top signals
    top = [r for r in enriched if r["score"] >= MIN_SCORE]
    if top:
        print(f"\n{'='*65}")
        print(f"🐋 WHALE OPTIONS → STOCK SIGNALS (score >= {MIN_SCORE}):")
        for r in top[:15]:
            o = r["option"]
            s = r["shorts"]
            p = r["price"]
            n = r["news"]
            
            sent = o.get("sentiment", "NEUT")
            sent_emoji = "📈" if sent == "BULLISH" else ("📉" if sent == "BEARISH" else "➡️")
            
            print(f"\n  🚨 {r['ticker']} {sent_emoji} {sent} | Score **{r['score']}/100**")
            print(f"     Call: ${o.get('strike')} exp {o.get('expiry')} | price ${o.get('price')}")
            print(f"     VOL {o.get('volume'):,} | OI {o.get('oi'):,} | V/OI {o.get('voi_ratio')}x")
            print(f"     Stock: ${p.get('price')} ({p.get('move_today'):+.1f}% today)")
            print(f"     SI {s.get('si'):.0f}% | DTC {s.get('short_ratio')} | Fee {s.get('borrow_fee'):.1f}%")
            if n.get("recent"):
                print(f"     📰 {n['recent'][0]['title']}")
    
    print(f"\n💾 Saved to {RESULTS_FILE}")
    return enriched


if __name__ == "__main__":
    run_scan()

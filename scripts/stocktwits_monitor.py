#!/usr/bin/env python3
"""
StockTwits Sentiment Monitor — Tracks social sentiment on stocks.
API: https://api.stocktwits.com/api/2/
Free, no auth required. Returns bull/bear sentiment + trending symbols.
"""
import requests
import json
import os
import re
from datetime import datetime
from collections import Counter

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(STATE_DIR, exist_ok=True)

BASE_URL = "https://api.stocktwits.com/api/2"
HEADERS = {"User-Agent": "SigBotti/1.0"}

# Lou's watchlist + squeeze candidates
WATCHLIST = ["SPY", "QQQ", "IWM", "AMC", "GME", "LCID", "SOUN", "LUNR", "ASTS", "SMCI", "RIVN", "SOFI", "NVDA", "TSLA", "AMD", "PLTR"]

BULL_WORDS = {
    "bull", "bullish", "long", "buy", "calls", "call", "moon", "squeeze",
    "short squeeze", "breakout", "bounce", "rip", "gap up", "to the moon",
    "rocket", "tendies", "hold", "loaded", "cheap", "undervalued", "winner",
    "queeze", " squeez", "call", "calls", "going up", "going long"
}
BEAR_WORDS = {
    "bear", "bearish", "short", "puts", "put", "dump", "crash", "drop",
    "sell", "cover", "breakdown", "rejected", "dead", "tank", "sell",
    "fud", "scam", "overvalued", "hemorrhage", "rug pull", "loser", "fail",
    "bye", " liquidation", "rekt", "puts", "put"
}


def get_symbol_messages(symbol: str, limit: int = 30) -> list:
    """Get recent messages tagged with a specific symbol."""
    try:
        resp = requests.get(
            f"{BASE_URL}/streams/symbol/{symbol}.json",
            params={"limit": limit},
            headers=HEADERS,
            timeout=10
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        msgs = data.get("messages", [])
        # Filter to messages actually tagged with this symbol
        filtered = []
        for m in msgs:
            syms = [s.get("symbol", "").upper() for s in m.get("symbols", [])]
            if symbol.upper() in syms:
                filtered.append(m)
        return filtered
    except Exception:
        return []


def get_trending() -> list:
    """Get trending symbols on StockTwits with mention counts."""
    try:
        resp = requests.get(
            f"{BASE_URL}/streams/trending.json",
            params={"limit": 50},
            headers=HEADERS,
            timeout=10
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        msgs = data.get("messages", [])
        sym_counts = Counter()
        for m in msgs:
            for s in m.get("symbols", []):
                sym_counts[s.get("symbol", "").upper()] += 1
        return [
            {"symbol": s, "twits_mentions": c}
            for s, c in sym_counts.most_common(20)
        ]
    except Exception:
        return []


def text_sentiment(text: str) -> str:
    """Simple text-based bull/bear sentiment analysis."""
    t = text.lower()
    bull_hits = sum(1 for w in BULL_WORDS if w in t)
    bear_hits = sum(1 for w in BEAR_WORDS if w in t)
    if bull_hits > bear_hits:
        return "bullish"
    elif bear_hits > bull_hits:
        return "bearish"
    return "neutral"


def analyze_symbol(symbol: str) -> dict:
    """Get sentiment analysis for a symbol."""
    messages = get_symbol_messages(symbol, 30)

    if not messages:
        return {"symbol": symbol, "error": "no data", "messages_analyzed": 0,
                "bull_pct": 50, "sentiment_label": "NO_DATA", "bullish_count": 0, "bearish_count": 0}

    bull_count = 0
    bear_count = 0

    for msg in messages:
        body = msg.get("body", "")
        sentiment = text_sentiment(body)
        if sentiment == "bullish":
            bull_count += 1
        elif sentiment == "bearish":
            bear_count += 1

    total = bull_count + bear_count
    bull_pct = round(bull_count / total * 100, 1) if total > 0 else 50.0

    if bull_pct >= 65:
        label = "STRONG_BULL"
    elif bull_pct >= 55:
        label = "BULL"
    elif bull_pct <= 35:
        label = "BEAR"
    elif bull_pct <= 45:
        label = "STRONG_BEAR"
    else:
        label = "NEUTRAL"

    return {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "messages_analyzed": len(messages),
        "bullish_count": bull_count,
        "bearish_count": bear_count,
        "bull_pct": bull_pct,
        "sentiment_label": label,
    }


def scan_watchlist() -> list:
    """Analyze all tickers in Lou's watchlist."""
    results = []
    for ticker in WATCHLIST:
        results.append(analyze_symbol(ticker))
    return sorted(results, key=lambda x: x.get("bull_pct", 50), reverse=True)


def get_market_mood() -> dict:
    """Get overall market mood from the most recent trending messages."""
    trending = get_trending()
    if not trending:
        return {"market_mood": "UNKNOWN", "top_symbols": []}

    # Get sample messages from trending to gauge overall sentiment
    sample_msgs = []
    for t in trending[:5]:
        msgs = get_symbol_messages(t["symbol"], 5)
        sample_msgs.extend(msgs)

    bull = sum(1 for m in sample_msgs if text_sentiment(m.get("body", "")) == "bullish")
    bear = sum(1 for m in sample_msgs if text_sentiment(m.get("body", "")) == "bearish")
    total = bull + bear
    bull_pct = round(bull / total * 100) if total > 0 else 50

    mood = "RISK_ON" if bull_pct > 55 else "RISK_OFF" if bull_pct < 45 else "NEUTRAL"

    return {
        "market_mood": mood,
        "bull_pct": bull_pct,
        "top_trending": trending[:10],
        "scanned_at": datetime.now().isoformat(),
    }


def save_scan() -> list:
    """Save watchlist scan + market mood to state file."""
    results = scan_watchlist()
    mood = get_market_mood()
    state_file = os.path.join(STATE_DIR, "stocktwits_sentiment.json")
    with open(state_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "watchlist": results,
            "market_mood": mood,
        }, f, indent=2)
    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2 and sys.argv[1] == "--check":
        ticker = sys.argv[2].upper() if len(sys.argv) > 2 else "AMC"
        result = analyze_symbol(ticker)
        print(f"\nStockTwits Sentiment: {ticker}")
        print(f"  Bull %: {result.get('bull_pct', 'N/A')}%")
        print(f"  Label: {result.get('sentiment_label', 'N/A')}")
        print(f"  Bullish: {result.get('bullish_count', 0)} | Bearish: {result.get('bearish_count', 0)}")
        print(f"  Messages: {result.get('messages_analyzed', 0)}")

    elif len(sys.argv) >= 2 and sys.argv[1] == "--mood":
        mood = get_market_mood()
        print(f"\nMarket Mood: {mood['market_mood']} ({mood['bull_pct']}% bull)")
        print("Top Trending:")
        for t in mood.get("top_trending", [])[:10]:
            print(f"  {t['symbol']:6} | {t['twits_mentions']} mentions")

    elif len(sys.argv) >= 2 and sys.argv[1] == "--trending":
        trending = get_trending()
        print(f"\nTrending on StockTwits:")
        for t in trending[:10]:
            print(f"  {t['symbol']:6} | {t['twits_mentions']} mentions")

    else:
        results = save_scan()
        mood_data = get_market_mood()
        print(f"\n=== StockTwits ({datetime.now().strftime('%H:%M:%S')}) ===")
        print(f"Market Mood: {mood_data['market_mood']} | Bull %: {mood_data['bull_pct']}%")
        print(f"\nWatchlist Sentiment:")
        for r in results:
            emoji = "🟢" if r['bull_pct'] > 55 else "🔴" if r['bull_pct'] < 45 else "⚪"
            label = r.get('sentiment_label', 'N/A')
            print(f"  {emoji} {r['symbol']:6} | {r['bull_pct']:5.1f}% {label:12} | {r.get('messages_analyzed',0)} msgs")

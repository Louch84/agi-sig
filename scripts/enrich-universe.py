#!/usr/bin/env python3
"""
Universe Manager — auto-enriches scanner universe with discovered stocks.
Reads discovered-stocks.json, scores new tickers, adds high-conviction ones
to the universe file (data/universe.json) that scanners read from.
"""
import yfinance as yf
import json
import os
import time
from fundamental_filter import check_fundamentals
from datetime import datetime

UNIVERSE_FILE = "/Users/sigbotti/.openclaw/workspace/data/universe.json"
DISCOVERED_FILE = "/Users/sigbotti/.openclaw/workspace/data/discovered-stocks.json"
COIL_UNIVERSE_FILE = "/Users/sigbotti/.openclaw/workspace/scripts/coil-universe-backup.py"

# Minimum thresholds to add a new stock to universe
MIN_SOURCES = 2        # must be cross-confirmed by 2+ sources
MIN_SI_PCT = 20        # or have 20%+ short interest
MIN_RETURNS_PCT = 15   # or have 15%+ momentum in last 5 days


def load_universe():
    """Load current universe from JSON file."""
    if os.path.exists(UNIVERSE_FILE):
        with open(UNIVERSE_FILE) as f:
            data = json.load(f)
            return data.get('tickers', []), data.get('metadata', {})
    return [], {}


def save_universe(tickers, metadata=None):
    """Save universe to JSON file."""
    os.makedirs(os.path.dirname(UNIVERSE_FILE), exist_ok=True)
    meta = metadata or {}
    meta['last_updated'] = datetime.now().isoformat()
    meta['count'] = len(tickers)
    with open(UNIVERSE_FILE, "w") as f:
        json.dump({'tickers': tickers, 'metadata': meta}, f, indent=2)


def validate_ticker(ticker):
    """Verify ticker is real, tradeable, and fundamentally sound before adding to universe."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        # Must have a price (not delisted) and not too expensive for SI plays
        if not price or price > 500:
            return None, "price out of range"
        # Verify it has enough data
        h = t.history(period="5d", interval="1d")
        if h.empty or len(h) < 3:
            return None, "insufficient data"
        # Check fundamentals
        fund = check_fundamentals(ticker)
        if not fund.get('pass', True):
            return None, f"fundamental fail: {fund.get('fundamental_verdict', 'UNKNOWN')}"
        return {
            'price': round(price, 2),
            'market_cap': info.get('marketCap', 0),
            'short_interest': round((info.get('shortPercentOfFloat', 0) or 0) * 100, 1),
        }, None
    except Exception as e:
        return None, str(e)


def score_discovery_candidates(discovered):
    """Score discovered stocks — how universe-worthy are they?"""
    scored = []
    for stock in discovered:
        score = 0
        sources = stock.get('sources', [stock.get('source', 'unknown')])
        n_sources = len(sources)

        # Multi-source bonus
        score += n_sources * 15

        # SI bonus
        si = stock.get('short_interest_pct', 0)
        if si >= 20:
            score += 25
        elif si >= 15:
            score += 15

        # Momentum bonus
        ret = stock.get('5d_return_pct', 0)
        if ret >= 15:
            score += 20
        elif ret >= 8:
            score += 12

        # Reddit WSB score bonus (organic retail interest)
        if stock.get('score', 0) >= 2000:
            score += 15
        elif stock.get('score', 0) >= 500:
            score += 8

        stock['universe_score'] = round(score, 1)
        stock['n_sources'] = n_sources
        scored.append(stock)

    scored.sort(key=lambda x: -x['universe_score'])
    return scored


def enrich_universe(dry_run=False):
    """Add high-conviction discovered stocks to the universe."""
    print("🔄 Universe enrichment process...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("=" * 55)

    current_tickers, meta = load_universe()
    print(f"Current universe: {len(current_tickers)} stocks")

    if not os.path.exists(DISCOVERED_FILE):
        print("⚠ No discovered-stocks.json found — run stock-discovery.py first")
        return

    with open(DISCOVERED_FILE) as f:
        data = json.load(f)

    discovered = data.get('results', [])
    print(f"Discovered stocks: {len(discovered)}")
    if not discovered:
        print("⚠ No candidates to evaluate")
        return

    # Score and filter candidates
    candidates = score_discovery_candidates(discovered)

    to_add = []
    already_have = set(current_tickers)

    print(f"\n🏆 TOP CANDIDATES FOR ENRICHMENT:")
    print(f"   {'Ticker':<8} | {'Score':>6} | {'Sources':>8} | {'SI%':>5} | {'5dRet%':>6} | {'Verdict'}")
    print(f"   {'-'*8} | {'-'*6} | {'-'*8} | {'-'*5} | {'-'*6} | {'-'*20}")

    for stock in candidates[:20]:
        t = stock['ticker']
        score = stock['universe_score']
        n_src = stock['n_sources']
        si = stock.get('short_interest_pct', 0)
        ret = stock.get('5d_return_pct', 0)

        if t in already_have:
            verdict = "already in universe"
        elif n_src >= MIN_SOURCES:
            verdict = "✅ ADD (multi-source)"
        elif si >= MIN_SI_PCT:
            verdict = "✅ ADD (high SI)"
        elif ret >= MIN_RETURNS_PCT:
            verdict = "✅ ADD (strong momentum)"
        else:
            verdict = "⏳ below threshold"

        print(f"   {t:<8} | {score:>6.1f} | {n_src:>8} | {si:>5.1f} | {ret:>+6.1f} | {verdict}")

        if t not in already_have and score >= 40:
            to_add.append(t)

    print(f"\n📦 {len(to_add)} new stocks to add: {to_add}")

    if dry_run:
        print("\n⚠ DRY RUN — no changes written")
        return

    # Validate new tickers before adding
    print("\n🔍 Validating new tickers (fundamental check + price check)...")
    validated = []
    for t in to_add:
        info, err = validate_ticker(t)
        if info:
            print(f"   ✅ {t}: ${info['price']}, SI {info['short_interest']}%, MC ${info['market_cap']/1e6:.0f}M")
            validated.append(t)
        else:
            print(f"   ❌ {t}: failed validation ({err})")
        time.sleep(0.3)

    if validated:
        new_universe = current_tickers + validated
        save_universe(new_universe, {'added_tickers': validated, 'source': 'discovery-enrichment'})
        print(f"\n✅ Universe updated: {len(current_tickers)} → {len(new_universe)} stocks")
        print(f"   Added: {validated}")
        print(f"   Saved to: {UNIVERSE_FILE}")
    else:
        print("\n⚠ No new stocks validated — universe unchanged")


if __name__ == "__main__":
    dry = "--dry-run" in __import__('sys').argv
    enrich_universe(dry_run=dry)
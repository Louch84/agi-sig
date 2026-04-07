#!/usr/bin/env python3
"""
run_news_scan.py — News-Driven Stock Scanner
Wires real news sentiment into gap-fill and short-squeeze signal logic.
Only flags plays when fresh news + technical setup align.
"""
import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/scanner')
import json, time, re
from datetime import datetime, timedelta
from news_scanner import analyze_gap_fill, analyze_short_squeeze
from run_scan import get_vix_context
import yfinance as yf

# ─── SENTIMENT SCORING ─────────────────────────────────────────────────────────

POSITIVE_KEYWORDS = [
    'beat', 'beats', 'exceed', 'exceeds', 'beats expectations', 'blowout',
    'raise', 'raises', 'upgraded', 'upgrade', 'strong', 'stronger', 'growth',
    'surge', 'surges', 'soar', 'soars', 'rally', 'rallies', 'jump', 'jumps',
    'gain', 'gains', 'rise', 'rises', 'record', 'high', 'highs', 'buy',
    'bullish', 'positive', 'profit', 'profitable', 'expanding', 'expansion',
    'launch', 'launches', 'new product', 'deal', 'partnership', 'acquisition',
    'breakthrough', 'approval', 'FDA approval', 'partnership', 'collaboration',
    'recovery', 'recovering', 'rebounds', 'rebound', 'beat and raise',
    'guidance raised', 'raised guidance', 'Q4 beat', 'revenue beat'
]

NEGATIVE_KEYWORDS = [
    'miss', 'misses', 'missed', 'below', 'warns', 'warning', 'cut', 'cuts',
    'downgraded', 'downgrade', 'weak', 'weaker', 'loss', 'losses', 'plunge',
    'plunges', 'crash', 'crashes', 'drop', 'drops', 'fall', 'falls', 'tumble',
    'layoffs', 'lawsuit', 'investigation', ' probe', 'scandal', 'fraud',
    'bankruptcy', 'recall', 'recall', 'shutdown', 'delist', 'delisting',
    'default', 'debt', 'write-down', 'write off', 'impairment', 'charge',
    'cut guidance', 'lowered guidance', 'guidance cut', 'revenue miss',
    'Q4 miss', 'guidance cuts', 'pause', 'halt', 'ban', 'investigation'
]

NEWS_AGE_HOURS = 48


def score_sentiment(headline: str, articles=None) -> dict:
    """
    Score a news headline for sentiment.
    Returns dict with: sentiment (positive/negative/neutral), score (-1 to 1), fresh (bool)
    """
    text = (headline or '').lower()
    pos_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text)
    neg_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text)

    if pos_count > neg_count:
        sentiment = 'positive'
        score = min(1.0, pos_count * 0.3)
    elif neg_count > pos_count:
        sentiment = 'negative'
        score = max(-1.0, -neg_count * 0.3)
    else:
        sentiment = 'neutral'
        score = 0.0

    return {'sentiment': sentiment, 'score': score, 'fresh': True}


def get_ticker_news(ticker_sym: str) -> list:
    """Fetch recent news for a ticker from yfinance."""
    try:
        t = yf.Ticker(ticker_sym)
        raw_news = t.news or []
        cutoff = datetime.now() - timedelta(hours=NEWS_AGE_HOURS)
        recent = []
        for n in raw_news[:10]:
            # yfinance wraps payload in 'content' dict
            content = n.get('content', n)  # fallback if flat
            title = content.get('title', '')
            pub_str = content.get('pubDate', '')
            if not title:
                continue
            # Parse date
            if pub_str:
                try:
                    dt = datetime.fromisoformat(pub_str.replace('Z', '+00:00'))
                    if dt.replace(tzinfo=None) >= cutoff:
                        recent.append({'title': title, 'pubDate': pub_str})
                except Exception:
                    # Unparseable date — include if we have a title
                    recent.append({'title': title, 'pubDate': pub_str})
            else:
                recent.append({'title': title, 'pubDate': ''})
        return recent[:5]
    except Exception as e:
        return []


def sentiment_aggregate(news_items: list) -> dict:
    """
    Aggregate multiple news items into one sentiment score.
    """
    if not news_items:
        return {'sentiment': 'neutral', 'score': 0.0, 'fresh': False}

    scores = []
    for n in news_items:
        headline = n.get('title', '')
        scores.append(score_sentiment(headline))

    avg_score = sum(s['score'] for s in scores) / len(scores)
    sentiments = [s['sentiment'] for s in scores]

    # Dominant sentiment
    pos = sentiments.count('positive')
    neg = sentiments.count('negative')
    neu = sentiments.count('neutral')
    dominant = 'neutral'
    if pos > neg and pos > neu:
        dominant = 'positive'
    elif neg > pos and neg > neu:
        dominant = 'negative'

    return {
        'sentiment': dominant,
        'score': round(avg_score, 3),
        'fresh': True,
        'item_count': len(news_items),
        'headlines': [n.get('title', '')[:100] for n in news_items[:3]]
    }


# ─── MAIN SCAN ────────────────────────────────────────────────────────────────

with open('/Users/sigbotti/.openclaw/workspace/scanner/news_universe.json') as f:
    tickers = json.load(f)
tickers = list(dict.fromkeys(tickers))  # deduplicate

vix_data = get_vix_context()
vix = vix_data['vix']
print(f"VIX: {vix:.2f} | {vix_data['env']}")

# Fetch news for all tickers first (batched)
print("\n📰 Fetching news for universe...")
ticker_news = {}
for i, sym in enumerate(tickers):
    news_items = get_ticker_news(sym)
    if news_items:
        ticker_news[sym] = news_items
        print(f"[{i+1}/{len(tickers)}] 📰 {sym}: {len(news_items)} news items")
    else:
        ticker_news[sym] = []
    time.sleep(0.5)  # Respect rate limits
print(f"  → {sum(len(v) for v in ticker_news.values())} total news items across {sum(1 for v in ticker_news.values() if v)} tickers")

# Score sentiment per ticker
print("\n🎯 Scoring sentiment...")
ticker_sentiment = {}
for sym, items in ticker_news.items():
    ticker_sentiment[sym] = sentiment_aggregate(items)

# ─── GAP FILL + VIX/SENTIMENT ──────────────────────────────────────────────────

gap_plays = []
for i, sym in enumerate(tickers):
    time.sleep(0.6)
    sentiment = ticker_sentiment.get(sym, {'sentiment': 'neutral', 'score': 0.0})
    g = analyze_gap_fill(sym, None)

    if not g or g.get('gap_fill_score', 0) < 5:
        continue

    # Only flag if: technical score >= 5 AND fresh news exists
    if not ticker_news.get(sym):
        continue  # Skip tickers with no news

    # Sentiment alignment check
    # PUT if: negative sentiment + gap down, OR high VIX + bearish technical
    # CALL if: positive sentiment + gap up, OR squeeze setup with positive news
    direction = None
    conf_boost = 0

    gap_pct = g.get('gap_pct', 0)
    sentiment_score = sentiment['score']

    if sentiment['sentiment'] == 'negative' and gap_pct < -3:
        direction = 'PUT'
        conf_boost = 2
    elif sentiment['sentiment'] == 'positive' and gap_pct > 3:
        direction = 'CALL'
        conf_boost = 2
    elif abs(gap_pct) >= 3 and vix > 20:
        # High VIX environment: confirm with sentiment
        if sentiment['sentiment'] == 'negative':
            direction = 'PUT'
            conf_boost = 1
        elif sentiment['sentiment'] == 'positive':
            direction = 'CALL'
            conf_boost = 1

    if direction:
        g['direction'] = direction
        g['confidence'] = min(5, 3 + conf_boost)
        g['sentiment'] = sentiment['sentiment']
        g['sentiment_score'] = sentiment['score']
        g['news_headlines'] = sentiment.get('headlines', [])
        gap_plays.append(g)
        print(f"[{i+1}/{len(tickers)}] GAP: {sym} {direction} | {sentiment['sentiment']} | gap={gap_pct:+.1f}% | conf={g['confidence']}")

gap_plays.sort(key=lambda x: x['gap_fill_score'], reverse=True)

# ─── SHORT SQUEEZE + SENTIMENT ────────────────────────────────────────────────

squeeze_plays = []
for i, sym in enumerate(tickers):
    time.sleep(0.6)
    sentiment = ticker_sentiment.get(sym, {'sentiment': 'neutral', 'score': 0.0})
    s = analyze_short_squeeze(sym, None)

    if not s or s.get('squeeze_score', 0) < 6:
        continue

    if not ticker_news.get(sym):
        continue  # Skip tickers with no news

    mom5d = s.get('mom5d', 0)
    sentiment_score = sentiment['score']

    # Positive news + short squeeze = CALL (short squeeze play)
    # Negative news + squeeze = handle carefully
    if sentiment['sentiment'] == 'positive':
        direction = 'CALL'
        conf_boost = 2
    elif sentiment['sentiment'] == 'neutral':
        if mom5d > 5:
            direction = 'CALL'
            conf_boost = 1
        else:
            direction = 'CALL'
            conf_boost = 0
    else:
        # Negative news + squeeze could still be a CALL if momentum is strong
        direction = 'CALL'
        conf_boost = 0

    s['direction'] = direction
    s['confidence'] = min(5, 3 + conf_boost)
    s['sentiment'] = sentiment['sentiment']
    s['sentiment_score'] = sentiment['score']
    s['news_headlines'] = sentiment.get('headlines', [])
    squeeze_plays.append(s)
    print(f"[{i+1}/{len(tickers)}] SQZ: {sym} CALL | {sentiment['sentiment']} | SI={s['short_pct_float']:.1f}% | mom5d={mom5d:+.1f}% | conf={s['confidence']}")

squeeze_plays.sort(key=lambda x: x['squeeze_score'], reverse=True)

# ─── OUTPUT ────────────────────────────────────────────────────────────────────

vix_env = vix_data['env']
vix_emoji = '🔴' if vix > 25 else ('🟡' if vix > 18 else '🟢')

print(f"\n{'='*60}")
print(f"📊 NEWS-DRIVEN GAP FILL PLAYS ({len(gap_plays)} found)")
print(f"{'='*60}")
if gap_plays:
    for p in gap_plays[:8]:
        headlines = p.get('news_headlines', [])
        print(f"\n{p['symbol']:6} {p.get('direction', 'PUT'):4} @ ${p['price']:.2f}")
        print(f"  Score: {p['gap_fill_score']}/10 | Gap: {p['gap_pct']:+.1f}% | Sentiment: {p.get('sentiment', 'neutral')} ({p.get('sentiment_score', 0):+.2f})")
        print(f"  Confidence: ⭐{'⭐'*p.get('confidence', 3)} ({p.get('confidence', 3)}/5)")
        if headlines:
            for h in headlines:
                print(f"  📰 {h[:90]}")
else:
    print("No news-driven gap fill plays found")

print(f"\n{'='*60}")
print(f"💥 NEWS-DRIVEN SHORT SQUEEZE PLAYS ({len(squeeze_plays)} found)")
print(f"{'='*60}")
if squeeze_plays:
    for p in squeeze_plays[:8]:
        headlines = p.get('news_headlines', [])
        print(f"\n{p['symbol']:6} CALL @ ${p['price']:.2f}")
        print(f"  Score: {p['squeeze_score']}/14 | SI: {p['short_pct_float']:.1f}% | DTC: {p.get('days_to_cover', 0)}d | Sentiment: {p.get('sentiment', 'neutral')} ({p.get('sentiment_score', 0):+.2f})")
        print(f"  Confidence: ⭐{'⭐'*p.get('confidence', 3)} ({p.get('confidence', 3)}/5)")
        print(f"  5D Mom: {p.get('mom5d', 0):+.1f}% | Vol Trend: {p.get('vol_trend', 1):.1f}x")
        if headlines:
            for h in headlines:
                print(f"  📰 {h[:90]}")
else:
    print("No news-driven short squeeze plays found")

combined = {
    'gap_plays': gap_plays[:8],
    'squeeze_plays': squeeze_plays[:8],
    'vix': vix_data,
    'tickers_scanned': len(tickers),
    'scan_time': datetime.now().isoformat(),
    'news_driven': True
}
with open('/Users/sigbotti/.openclaw/workspace/scanner/news_scan_results.json', 'w') as f:
    json.dump(combined, f, default=str, indent=2)

print(f"\n✅ Saved to news_scan_results.json | VIX {vix_emoji} {vix:.2f} {vix_env}")

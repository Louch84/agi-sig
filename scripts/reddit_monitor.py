#!/usr/bin/env python3
"""
Reddit Sentiment Monitor — Watches WSB and stock subreddits for ticker mentions.
Sources: r/wallstreetbets, r/stocks, r/SqueezePlays
Outputs: trending tickers with mention count + sentiment score.

Lou's trading note: High WSB mentions = potential squeeze fuel, but also risk of pump-and-dump.
Use alongside gap scanner — WSB mentions confirm momentum plays.
"""
import requests
import re
import os
import json
from datetime import datetime, timedelta
from collections import Counter

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(STATE_DIR, exist_ok=True)

SUBREDDITS = ["wallstreetbets", "stocks", "pennystocks", "options"]
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def get_ticker_mentions(subreddit: str, limit: int = 50) -> list:
    """Get recent tickers mentioned in a subreddit."""
    try:
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []

        data = resp.json().get("data", {}).get("children", [])
        mentions = []

        for post in data:
            title = post["data"].get("title", "").lower()
            selftext = post["data"].get("selftext", "").lower()
            score = post["data"].get("score", 0)
            num_comments = post["data"].get("num_comments", 0)
            created = post["data"].get("created_utc", 0)

            combined = f"{title} {selftext}"
            tickers = extract_tickers(combined)

            for ticker in tickers:
                mentions.append({
                    "ticker": ticker,
                    "title": title[:100],
                    "score": score,
                    "comments": num_comments,
                    "created": created,
                    "subreddit": subreddit,
                })
        return mentions
    except Exception as e:
        return []


def extract_tickers(text: str) -> list:
    """Extract stock ticker symbols from text. Uses known tickers + common sense filtering."""
    # Expanded skip words — common English words and acronyms that aren't tickers
    skip_words = {
        # Common words
        "THE", "AND", "FOR", "NOT", "ARE", "BUT", "THIS", "WITH", "HAS", "HAVE",
        "FROM", "THEY", "WILL", "MORE", "THAN", "THEM", "THEN", "THAT", "THIS",
        "POST", "CLICK", "FULL", "LINK", "HTTP", "HTTPS", "WWW", "COM", "ORG",
        # Common acronyms
        "WSB", "DD", "RH", "ETF", "USA", "YOLO", "FD", "YTD", "MTD", "ATH",
        "BTFD", "MOASS", "HODL", "FOMO", "IMHO", "LOL", "AKA", "CEO", "CTO", "CFO",
        "IPO", "SEC", "FDA", "FTC", " DOJ", "EPA", "IRS", "GDP", "CPI", "PPI",
        # Reddit/forum terms
        "MODS", "MOD", "USER", "POST", "THREAD", "REPLY", "UPVOTE", "DOWNVOTE",
        # Single/double letters
        "A", "I", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M",
        "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
        # Known non-tickers (3 chars)
        "THE", "AND", "FOR", "NOT", "ARE", "BUT", "WITH", "HAS", "MORE", "THAN",
        "THEM", "THEN", "THAT", "FROM", "POST", "OVER", "INTO", "OURS", "YOUR",
        # Common tickers to exclude (not actually being discussed as stocks)
        "DNA", "T", "V", "KO", "M", "GM", "F", "KO",
        # Months
        "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC",
        # Numbers
        "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN",
        # Misc
        "CAN", "YOU", "ALL", "GET", "JUST", "LIKE", "EVEN", "ALSO", "NOW", "HERE",
        "YRS", "MO", "WK", "DAY", "AGO", "OLD", "NEW", "TOP", "BEST", "NEXT",
    }

    # Common non-ticker words/phrases to skip (case-insensitive)
    skip_phrases = {"yolo", "fd", "dd", "wsb", "bull", "bear", "moass", "hold",
                    "earn", "news", "dd", "god", "ape", "apes", "reddit",
                    "forum", "sub", "mod", "karma", "award", "comment", "upvote"}

    # Pull words that look like tickers: 1-5 uppercase letters, isolated
    words = re.findall(r'\b[A-Z]{1,5}\b', text.upper())

    tickers = []
    for w in words:
        if w in skip_words or w.lower() in skip_phrases:
            continue
        if re.match(r'^[A-Z]{1,5}$', w) and len(w) >= 1:
            # Filter out very short words that are common
            if w not in ["I", "A"]:
                tickers.append(w)

    return list(set(tickers))[:20]  # dedupe, cap at 20


def aggregate_mentions() -> dict:
    """Aggregate ticker mentions across all subreddits."""
    all_mentions = []
    for sub in SUBREDDITS:
        mentions = get_ticker_mentions(sub, limit=50)
        all_mentions.extend(mentions)

    # Count mentions per ticker
    ticker_counts = Counter(m["ticker"] for m in all_mentions)

    # Compute engagement score
    ticker_scores = {}
    for m in all_mentions:
        t = m["ticker"]
        if t not in ticker_scores:
            ticker_scores[t] = 0
        ticker_scores[t] += m["score"] + m["comments"] * 2

    # Get most recent mention time per ticker
    ticker_latest = {}
    for m in all_mentions:
        t = m["ticker"]
        if t not in ticker_latest or m["created"] > ticker_latest[t]:
            ticker_latest[t] = m["created"]

    return {
        "timestamp": datetime.now().isoformat(),
        "subreddits": SUBREDDITS,
        "total_mentions": len(all_mentions),
        "tickers": [
            {
                "ticker": t,
                "mention_count": ticker_counts[t],
                "engagement_score": ticker_scores.get(t, 0),
                "last_mentioned_hours_ago": round(
                    (datetime.now() - datetime.fromtimestamp(ticker_latest[t])).seconds / 3600
                    if ticker_latest.get(t) else 999, 1
                ),
            }
            for t in ticker_counts
        ],
    }


def get_trending(limit: int = 10) -> list:
    """Get trending tickers, sorted by engagement."""
    data = aggregate_mentions()
    tickers = sorted(data["tickers"], key=lambda x: x["engagement_score"], reverse=True)
    return tickers[:limit]


def check_ticker_sentiment(ticker: str) -> dict:
    """Check sentiment for a specific ticker across subreddits."""
    all_mentions = []
    for sub in SUBREDDITS:
        mentions = get_ticker_mentions(sub, limit=100)
        all_mentions.extend([m for m in mentions if m["ticker"] == ticker])

    if not all_mentions:
        return {"ticker": ticker, "mentions": 0, "sentiment": "UNKNOWN", "posts": []}

    avg_score = sum(m["score"] for m in all_mentions) / len(all_mentions)
    total_comments = sum(m["comments"] for m in all_mentions)
    recent_hours = (datetime.now() - datetime.fromtimestamp(
        max(m["created"] for m in all_mentions)
    )).seconds / 3600 if all_mentions else 999

    sentiment = "BULLISH" if avg_score > 100 else "NEUTRAL" if avg_score > 20 else "BEARISH"

    return {
        "ticker": ticker,
        "mentions": len(all_mentions),
        "avg_post_score": round(avg_score, 0),
        "total_comments": total_comments,
        "last_mentioned_hrs_ago": round(recent_hours, 1),
        "sentiment": sentiment,
        "subreddits": list(set(m["subreddit"] for m in all_mentions)),
    }


def save_trending():
    """Save trending tickers to state file."""
    trending = get_trending(15)
    state_file = os.path.join(STATE_DIR, "reddit_trending.json")
    with open(state_file, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "tickers": trending}, f, indent=2)
    return trending


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == "--check":
        ticker = sys.argv[2].upper() if len(sys.argv) > 2 else "AMC"
        result = check_ticker_sentiment(ticker)
        print(f"\nReddit Sentiment: {ticker}")
        print(f"  Mentions: {result['mentions']}")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Avg Score: {result['avg_post_score']}")
        print(f"  Subreddits: {', '.join(result['subreddits'])}")
    elif len(sys.argv) >= 2 and sys.argv[1] == "--trending":
        trending = get_trending()
        print(f"\nTrending Tickers on WSB/Stocks:")
        for i, t in enumerate(trending, 1):
            print(f"  {i}. {t['ticker']:6} | {t['mention_count']:3} mentions | score: {t['engagement_score']:8.0f}")
    else:
        trending = save_trending()
        print(f"\nReddit Trending Saved ({len(trending)} tickers):")
        for i, t in enumerate(trending[:10], 1):
            print(f"  {i}. {t['ticker']:6} | {t['mention_count']:3} mentions | {t['engagement_score']:8.0f} eng | {t['last_mentioned_hours_ago']}h ago")

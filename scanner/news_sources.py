#!/usr/bin/env python3
"""
Multi-Source News Ticker Discovery
Sources: Finviz, Benzinga, StockTwits, Google News, Reddit WSB, Seeking Alpha
"""
import yfinance as yf
import json
import time
import re
import urllib.request
from datetime import datetime, timedelta
from collections import Counter

def fetch_finviz_news():
    """Get tickers from Finviz market news"""
    tickers = []
    try:
        url = "https://finviz.com/news.ashx"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        # Extract tickers from HTML
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        found = re.findall(ticker_pattern, html)
        # Filter common non-ticker words
        stopwords = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD',
                     'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HAS', 'HAVE', 'BEEN', 'WILL',
                     'WITH', 'THIS', 'THAT', 'FROM', 'THEY', 'MORE', 'WHAT', 'WHEN',
                     'WERE', 'STOCK', 'MARKET', 'SHARES', 'NEWS', 'THIS', 'THAT',
                     'FROM', 'HAVE', 'WERE', 'BEEN', 'WILL', 'MORE', 'WHAT', 'NEWS'}
        tickers = [t for t in found if t not in stopwords and len(t) <= 5 and t.isalpha()]
        print(f"  Finviz: found {len(tickers)} ticker mentions")
    except Exception as e:
        print(f"  Finviz: ERROR - {e}")
    return tickers


def fetch_benzinga_news():
    """Get tickers from Benzinga headlines"""
    tickers = []
    try:
        # Benzinga latest news RSS
        url = "https://www.benzinga.com/news/feed"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml = resp.read().decode('utf-8', errors='ignore')
        # Extract tickers from XML/RSS
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        found = re.findall(ticker_pattern, xml)
        stopwords = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD',
                     'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HAS', 'HAVE', 'BEEN', 'WILL',
                     'WITH', 'THIS', 'THAT', 'FROM', 'THEY', 'MORE', 'WHAT', 'WHEN', 'WERE',
                     'NEWS', 'MARKET', 'STOCKS', 'TRADING', 'ANALYSIS', 'UPDATES', 'LATEST'}
        tickers = [t for t in found if t not in stopwords and len(t) <= 5 and t.isalpha()]
        print(f"  Benzinga: found {len(tickers)} ticker mentions")
    except Exception as e:
        print(f"  Benzinga: ERROR - {e}")
    return tickers


def fetch_stocktwits_trending():
    """Get trending tickers from StockTwits"""
    tickers = []
    try:
        # StockTwits trending API (public)
        url = "https://api.stocktwits.com/api/2/streams/trending.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
        symbols = data.get('symbols', [])
        tickers = [s.get('symbol', '') for s in symbols if s.get('symbol')]
        print(f"  StockTwits trending: found {len(tickers)} tickers")
    except Exception as e:
        print(f"  StockTwits: ERROR - {e}")
    return tickers


def fetch_google_news_rss():
    """Get tickers from Google News RSS"""
    tickers = []
    sources = [
        ("Stocks", "https://news.google.com/rss/search?q=stocks&hl=en-US&gl=US&ceid=US:en"),
        ("Markets", "https://news.google.com/rss/search?q=stock+market&hl=en-US&gl=US&ceid=US:en"),
        ("Crypto", "https://news.google.com/rss/search?q=cryptocurrency&hl=en-US&gl=US&ceid=US:en"),
        ("Tech", "https://news.google.com/rss/search?q=technology+stocks&hl=en-US&gl=US&ceid=US:en"),
    ]
    for name, url in sources:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml = resp.read().decode('utf-8', errors='ignore')
            ticker_pattern = r'\b([A-Z]{2,5})\b'
            found = re.findall(ticker_pattern, xml)
            stopwords = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD',
                         'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HAS', 'HAVE', 'BEEN', 'WILL',
                         'WITH', 'THIS', 'THAT', 'FROM', 'THEY', 'MORE', 'WHAT', 'WHEN', 'WERE',
                         'NEWS', 'MARKET', 'STOCKS', 'TRADING', 'GOOGLE', 'APPLE', 'AMAZON',
                         'MICROSOFT', 'META', 'TESLA', 'START', 'FIRST', 'AFTER', 'BEFORE'}
            filtered = [t for t in found if t not in stopwords and len(t) <= 5 and t.isalpha()]
            tickers.extend(filtered)
            time.sleep(0.5)
        except Exception as e:
            print(f"  Google News ({name}): ERROR - {e}")
    print(f"  Google News RSS: found {len(tickers)} ticker mentions")
    return tickers


def fetch_wsb_trending():
    """Get trending tickers from Reddit WallStreetBets"""
    tickers = []
    try:
        # WSB daily discussion (no auth needed for public RSS)
        url = "https://www.reddit.com/r/wallstreetbets/new.rss"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml = resp.read().decode('utf-8', errors='ignore')
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        found = re.findall(ticker_pattern, xml)
        stopwords = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD',
                     'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HAS', 'HAVE', 'BEEN', 'WILL',
                     'WITH', 'THIS', 'THAT', 'FROM', 'THEY', 'MORE', 'WHAT', 'WHEN', 'WERE',
                     'NEWS', 'POST', 'DD', 'WSB', 'EDIT', 'NOW', 'LIKE', 'JUST', 'THINK',
                     'YOLO', 'IPO', 'ETF', 'GDP', 'SEC', 'FDA', 'USA', 'ONE', 'TWO'}
        tickers = [t for t in found if t not in stopwords and len(t) <= 5 and t.isalpha()]
        print(f"  Reddit WSB: found {len(tickers)} ticker mentions")
    except Exception as e:
        print(f"  Reddit WSB: ERROR - {e}")
    return tickers


def fetch_seeking_alpha():
    """Get tickers from Seeking Alpha trending"""
    tickers = []
    try:
        url = "https://seekingalpha.com/market_currents.xml"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml = resp.read().decode('utf-8', errors='ignore')
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        found = re.findall(ticker_pattern, xml)
        stopwords = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD',
                     'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HAS', 'HAVE', 'BEEN', 'WILL',
                     'WITH', 'THIS', 'THAT', 'FROM', 'THEY', 'MORE', 'WHAT', 'WHEN', 'WERE',
                     'NEWS', 'ALPHA', 'SA', 'MARKET', 'STOCKS', 'SIGNAL'}
        tickers = [t for t in found if t not in stopwords and len(t) <= 5 and t.isalpha()]
        print(f"  Seeking Alpha: found {len(tickers)} ticker mentions")
    except Exception as e:
        print(f"  Seeking Alpha: ERROR - {e}")
    return tickers


def aggregate_news_tickers():
    """Aggregate all sources and find most mentioned tickers"""
    print("🔍 Fetching from multiple news sources...\n")
    
    all_tickers = []
    
    # Fetch from all sources
    sources = [
        ("Finviz", fetch_finviz_news),
        ("Benzinga", fetch_benzinga_news),
        ("StockTwits", fetch_stocktwits_trending),
        ("Google News RSS", fetch_google_news_rss),
        ("Reddit WSB", fetch_wsb_trending),
        ("Seeking Alpha", fetch_seeking_alpha),
    ]
    
    for name, fetcher in sources:
        result = fetcher()
        all_tickers.extend(result)
        time.sleep(0.5)
    
    # Count occurrences
    counter = Counter(all_tickers)
    
    # Must appear in at least 3 sources AND have 2+ letters
    # OR be a known hot ticker
    hot_tickers = {
        'TSLA', 'NVDA', 'AAPL', 'AMD', 'PLTR', 'COIN', 'MSTR', 'GME', 'AMC',
        'BB', 'NOK', 'SOFI', 'UPST', 'RIVN', 'LCID', 'SNAP', 'META', 'NFLX',
        'BA', 'INTC', 'QCOM', 'MU', 'MSFT', 'GOOGL', 'AMZN', 'AMAT', 'ASML',
        'LRCX', 'KLAC', 'SNPS', 'CDNS', 'PANW', 'CRWD', 'ZS', 'NET', 'DDOG',
        'SMCI', 'DELL', 'HPQ', 'STX', 'WDC', 'NKE', 'U', 'DKNG', 'PENN', 'MGM',
        'ABNB', 'MAR', 'RCL', 'CCL', 'AAL', 'DAL', 'UAL', 'LUV', 'SAVE',
        'PLTR', 'ASTS', 'SPCE', 'RBLX', 'HOOD', 'BBAI', 'AST', 'NNDM'
    }
    
    # Common acronyms/non-tickers to exclude
    exclude = {
        'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD',
        'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HAS', 'HAVE', 'BEEN', 'WILL',
        'WITH', 'THIS', 'THAT', 'FROM', 'THEY', 'MORE', 'WHAT', 'WHEN', 'WERE',
        'NEWS', 'MARKET', 'STOCKS', 'TRADING', 'ANALYSIS', 'UPDATES', 'LATEST',
        'YOUR', 'SAY', 'WAY', 'NEW', 'NOW', 'DAY', 'MAY', 'BIG', 'SEE', 'LOOK',
        'MAKE', 'JUST', 'THINK', 'YOLO', 'DD', 'WSB', 'EDIT', 'POST', 'LONG',
        'SHORT', 'CALL', 'PUT', 'IPO', 'ETF', 'GDP', 'SEC', 'FDA', 'USA', 'CEO',
        'CFO', 'COO', 'AI', 'IT', 'IS', 'OF', 'IN', 'TO', 'BY', 'AT', 'OR', 'ON',
        'UP', 'SO', 'IF', 'WE', 'MY', 'GO', 'DO', 'VS', 'BE', 'AN', 'AS', 'AM',
        'NO', 'NZ', 'UK', 'US', 'EU', 'UN', 'WTO', 'OPEC', 'FBI', 'CIA', 'NSA',
        'CNBC', 'CNN', 'NBC', 'CBS', 'ABC', 'FOX', 'BBC', 'WSJ', 'REUTERS',
        'AOL', 'RSS', 'HTML', 'HTTP', 'HTTPS', 'API', 'IPO', 'NYSE', 'NASDAQ',
        'DOW', 'S&P', 'FTSE', 'GLOBE', 'WIRE', 'PRSO', 'ROSEN', 'LAW', 'GMBH',
        'A', 'I', 'U', 'S', 'N', 'L', 'F', 'H', 'K', 'Y', 'E', 'T', 'R', 'O',
        'GMT', 'EST', 'PST', 'UTC', 'CT', 'ET', 'PT', 'WHY', 'HOW', 'WHAT',
        'TRM', 'NATO', 'TSMC', 'REIT', 'LCID', 'RMB', 'EUR', 'USD', 'JPY', 'GBP'
    }
    
    # Build qualified list: exclude noise UNLESS it's a hot ticker
    # Then require 3+ sources OR be in hot_tickers
    qualified = []
    for ticker, count in counter.items():
        if ticker in exclude and ticker not in hot_tickers:
            continue  # Skip noise
        if count >= 3 or ticker in hot_tickers:
            qualified.append(ticker)
    
    print(f"\n📊 Aggregated: {len(all_tickers)} total ticker mentions")
    print(f"📊 Unique tickers: {len(set(all_tickers))}")
    print(f"📊 Qualified (3+ sources OR hot list): {len(qualified)}")
    qualified_counter = Counter({t: counter[t] for t in qualified if t in counter})
    print(f"\nTop 20 by mentions: {qualified_counter.most_common(20)}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for t in qualified:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    
    return unique[:50]  # Max 50 tickers to stay within rate limits


def main():
    print("=" * 60)
    print("🐺 $SIGBOTTI — Multi-Source News Scanner")
    print("=" * 60)
    
    tickers = aggregate_news_tickers()
    
    print(f"\n✅ Final ticker universe ({len(tickers)} stocks):")
    print(", ".join(tickers[:30]))
    if len(tickers) > 30:
        print(f"  ... and {len(tickers) - 30} more")
    
    # Save to file for scanner to pick up
    with open('/Users/sigbotti/.openclaw/workspace/scanner/news_universe.json', 'w') as f:
        json.dump(tickers, f)
    print(f"\n💾 Saved to news_universe.json")
    
    return tickers


if __name__ == "__main__":
    main()

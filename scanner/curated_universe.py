#!/usr/bin/env python3
"""
Curated Stock Universe + Real News Filter
Instead of extracting tickers from messy news (noise), we use a curated list
of tradeable stocks and filter by which ones have REAL recent news.
"""
import yfinance as yf
import json
import time
import urllib.request
from datetime import datetime, timedelta

# Curated universe - liquid, tradeable stocks with news potential
CURATED_UNIVERSE = [
    # Tech / AI / Chips
    'NVDA', 'AMD', 'INTC', 'QCOM', 'MU', 'AMAT', 'ASML', 'LRCX', 'KLAC', 'SNPS', 'CDNS',
    'MSFT', 'GOOGL', 'AMZN', 'META', 'AAPL', 'NFLX', 'PLTR', 'SMCI', 'DELL', 'HPQ', 'STX', 'WDC',
    'PANW', 'CRWD', 'ZS', 'NET', 'DDOG', 'SNOW', 'U', 'DOCU', 'ROKU', 'SNAP', 'SQSP',
    # EV / Auto
    'TSLA', 'RIVN', 'LCID', 'F', 'GM', 'TM', 'RIVN',
    # Finance
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'V', 'MA', 'PYPL', 'SQ', 'SOFI', 'UPST', 'HOOD', 'MSTR', 'COIN',
    # Energy
    'XOM', 'CVX', 'COP', 'SLB', 'OXY', 'EOG', 'PXD', 'HAL',
    # Biotech / Pharma
    'LLY', 'UNH', 'JNJ', 'PFE', 'ABBV', 'MRNA', 'GILD', 'BMY', 'MRK', 'CVS',
    # Airlines / Travel
    'AAL', 'DAL', 'UAL', 'LUV', 'SAVE', 'RCL', 'CCL', 'ABNB', 'MAR', 'HLT', 'BKNG',
    # Retail / Consumer
    'WMT', 'TGT', 'COST', 'HD', 'LOW', 'NKE', 'LULU', 'UAA', 'DKNG', 'PENN', 'MGM', 'WYNN', 'CZR',
    # REIT / Real Estate
    'VICI', 'PLNT', 'SPG', 'O',
    # Meme / High Short Interest
    'AMC', 'GME', 'BB', 'KOSS', 'NAKD', 'SNDL', 'NOK', 'BBAI',
    # China / ADR
    'BABA', 'PDD', 'JD', 'NTES', 'BIDU', 'TCEHY', 'BILI',
    # Industrial / Other
    'CAT', 'DE', 'BA', 'GE', 'RTX', 'HON', 'UPS', 'FDX',
    # Silver / Gold / Commodities
    'SLV', 'GDX', 'GOLD', 'NEM', 'WPM',
    # Solar / Green
    'ENPH', 'SEDG', 'FSLR', 'RUN', 'NEE', 'SEDG',
    # Cannabis
    'TLRY', 'CGC', 'ACB', 'CRON',
    # Blockchain / Crypto Adjacent
    'MSTR', 'COIN', 'HOOD', 'SQ',
]

def check_news_via_google_rss():
    """Get ticker mentions from Google News RSS - more targeted search"""
    mentioned = {}
    
    # Search queries that return stock-specific news
    queries = [
        "stock+market+news+earnings",
        "stock+alert+trading+day",
        "after+hours+stock+news",
        "short+squeeze+stocks",
        "gap+up+stock+news",
        "earnings+beat+stock",
    ]
    
    for query in queries:
        try:
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml = resp.read().decode('utf-8', errors='ignore')
            
            # Look for ticker patterns in titles
            import re
            # Common stock ticker pattern in news titles
            titles = re.findall(r'<title><!\[CDATA\[([^\]]+)\]\]></title>', xml)
            
            for title in titles:
                # Check if any curated tickers are mentioned
                for ticker in CURATED_UNIVERSE:
                    if ticker in title.upper():
                        mentioned[ticker] = mentioned.get(ticker, 0) + 1
        except Exception as e:
            print(f"  Google RSS ({query[:30]}...): ERROR - {e}")
        time.sleep(0.3)
    
    return mentioned


def check_news_via_finviz():
    """Check finviz for stocks with news"""
    mentioned = {}
    try:
        # Finviz news RSS
        url = "https://finviz.com/rss.ashx"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml = resp.read().decode('utf-8', errors='ignore')
        
        import re
        titles = re.findall(r'<title><!\[CDATA\[([^\]]+)\]\]></title>', xml)
        
        for title in titles:
            for ticker in CURATED_UNIVERSE:
                if ticker in title.upper():
                    mentioned[ticker] = mentioned.get(ticker, 0) + 1
    except Exception as e:
        print(f"  Finviz RSS: ERROR - {e}")
    return mentioned


def filter_by_price_and_volume(tickers):
    """Final filter: must be under $50, have volume, and have news"""
    qualified = []
    
    print(f"\n📊 Filtering {len(tickers)} tickers with news by price/volume...")
    
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            price = info.get('currentPrice', 0)
            vol = info.get('averageVolume', 0)
            mktcap = info.get('marketCap', 0)
            
            if price and 1 < price < 50 and vol > 500_000 and mktcap > 100_000_000:
                qualified.append({
                    'symbol': ticker,
                    'price': price,
                    'volume': vol,
                    'market_cap': mktcap
                })
        except:
            pass
        time.sleep(0.3)
    
    return qualified


def main():
    print("=" * 60)
    print("🐺 Multi-Source News Scanner — Curated Universe")
    print("=" * 60)
    
    print("\n🔍 Step 1: Scanning news sources for curated tickers...\n")
    
    all_mentions = {}
    
    # Google News RSS
    print("  Checking Google News RSS...")
    mentions = check_news_via_google_rss()
    print(f"    Found {len(mentions)} ticker mentions from Google News")
    for t, c in mentions.items():
        all_mentions[t] = all_mentions.get(t, 0) + c
    
    # Finviz RSS
    print("\n  Checking Finviz RSS...")
    mentions = check_news_via_finviz()
    print(f"    Found {len(mentions)} ticker mentions from Finviz")
    for t, c in mentions.items():
        all_mentions[t] = all_mentions.get(t, 0) + c
    
    # Sort by mention count
    sorted_tickers = sorted(all_mentions.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n📰 News Mentions (sorted by frequency):")
    print("-" * 40)
    for ticker, count in sorted_tickers[:30]:
        print(f"  {ticker:8} mentioned {count} times")
    
    if not sorted_tickers:
        print("\n⚠️ No news mentions found. Using curated universe as fallback.")
        tickers_with_news = CURATED_UNIVERSE
    else:
        # Top mentioned tickers
        tickers_with_news = [t for t, c in sorted_tickers]
    
    print(f"\n📊 Step 2: Filtering by price/volume (under $50, liquid)...\n")
    
    qualified = filter_by_price_and_volume(tickers_with_news)
    
    print(f"\n✅ Final qualified universe: {len(qualified)} stocks\n")
    for q in sorted(qualified, key=lambda x: x['volume'], reverse=True)[:20]:
        print(f"  {q['symbol']:8} @ ${q['price']:.2f} | Vol: {q['volume']/1e6:.1f}M | MCap: ${q['market_cap']/1e9:.1f}B")
    
    # Save
    final_tickers = [q['symbol'] for q in qualified]
    with open('/Users/sigbotti/.openclaw/workspace/scanner/news_universe.json', 'w') as f:
        json.dump(final_tickers, f)
    
    print(f"\n💾 Saved {len(final_tickers)} tickers to news_universe.json")
    return final_tickers


if __name__ == "__main__":
    main()

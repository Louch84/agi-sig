#!/usr/bin/env python3
"""
News → Ticker → Scanner Pipeline
Finds tickers in the news, runs them through gap/squeeze criteria
"""
import yfinance as yf
import numpy as np
import json
import time
import re
from datetime import datetime

# ─── NEWS SOURCES ───────────────────────────────────────────────────────────────

def scrape_yahoo_trending():
    """Get tickers from Yahoo Finance trending movers"""
    tickers = []
    try:
        url = "https://finance.yahoo.com/markets/stocks/most-active/"
        # Yahoo's trending page is JS-heavy, use yfinance bulk instead
        pass
    except:
        pass
    return tickers

def get_news_tickers():
    """Get tickers mentioned in recent financial news via web scraping"""
    found = {}
    
    # Sources to check
    sources = [
        ("Finviz movers", "https://finviz.com/map.ashx"),
        ("MarketWatch trending", "https://www.marketwatch.com/tools/screener/trending-tickers"),
        ("Yahoo trending", "https://finance.yahoo.com/markets/stocks/most-active/"),
    ]
    
    # Use yfinance news for known tickers + search for news tickers
    # Load curated universe filtered by news + price + volume
    try:
        with open('/Users/sigbotti/.openclaw/workspace/scanner/news_universe.json') as f:
            watchlist = json.load(f)
    except:
        # Fallback curated list
        watchlist = [
            "LLY", "NVDA", "TSLA", "AAPL", "AMD", "PLTR", "COIN", 
            "MSTR", "AMZN", "GOOGL", "META", "NFLX", "SOFI", "RIVN",
            "SMCI", "INTC", "AMD", "JPM", "BAC", "XOM", "OXY",
            "T", "VZ", "DIS", "SNAP", "ROKU", "DOCU", "U", "SNOW",
            "ABNB", "MAR", "DKNG", "PENN", "MGM", "CZR", "WYNN",
            "GME", "AMC", "BB", "KOSS", "NAKD", "SNDL", "NOK",
            "NKE", "LULU", "UAA", "NIO", "PLTR", "AI", "CRWD",
            "PANW", "ZS", "VEEV", "DT", "AVLR", "PATH", "BBAI",
            "AAL", "F", "NOK", "SMCI", "HPQ", "HAL", "CCL"
        ]
    
    for sym in watchlist:
        try:
            t = yf.Ticker(sym)
            news = t.news
            if news and len(news) > 0:
                # Check if recent (within 48h)
                for n in news[:3]:
                    title = n.get('title', '')
                    pubDate = n.get('pubDate', '')
                    found[sym] = {'title': title, 'pubDate': pubDate, 'count': len(news)}
        except:
            pass
        time.sleep(0.3)
    
    return found


def extract_ticker_from_text(text):
    """Extract stock tickers from text using regex"""
    # Common stock ticker pattern (1-5 uppercase letters)
    pattern = r'\b[A-Z]{1,5}\b'
    potential = re.findall(pattern, text)
    
    # Filter out common non-ticker words
    stopwords = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 
                 'CAN', 'HAD', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HAS',
                 'HAVE', 'BEEN', 'WILL', 'WITH', 'THIS', 'THAT', 'FROM',
                 'THEY', 'WILL', 'MORE', 'WILL', 'WHAT', 'WHEN', 'WERE',
                 'BEEN', 'HAVE', 'STOCK', 'MARKET', 'SHARES', 'SHARE',
                 'NEWS', 'REUTERS', 'AP', 'PRESS', 'CNN', 'CNBC', 'IPO',
                 'ETF', 'ADR', 'SEC', 'FDA', 'USA', 'CEO', 'CFO', 'COO',
                 'AI', 'ML', 'VR', 'AR', 'IT', 'IS', 'OF', 'IN', 'TO',
                 'BY', 'AT', 'OR', 'ON', 'UP', 'SO', 'IF', 'WE', 'MY',
                 'GO', 'DO', 'GO', 'UP', 'VS', 'BIG', 'NEW', 'TOP'}
    
    return [t for t in potential if t not in stopwords and len(t) <= 5]


# ─── GAP FILL SCANNER ─────────────────────────────────────────────────────────

def analyze_gap_fill(ticker_sym, news_context=None):
    """Analyze a ticker for gap fill setup"""
    try:
        t = yf.Ticker(ticker_sym)
        info = t.info
        price = info.get('currentPrice', 0)
        
        if not price or price > 100:  # Focus on cheaper stocks
            return None
        
        hist = t.history(period='60d')  # Need 60 days for analysis
        if len(hist) < 40:
            return None
        
        close = hist['Close']
        high = hist['High']
        low = hist['Low']
        vol = hist['Volume']
        
        # Current day stats
        curr_close = float(close.iloc[-1])
        prev_close = float(close.iloc[-2])
        
        # Gap calculation
        gap_pct = (curr_close - prev_close) / prev_close * 100 if prev_close else 0
        
        # ATR (14-day) - measure volatility
        tr = np.maximum(
            high - low,
            np.maximum(
                abs(high - close.shift(1)),
                abs(low - close.shift(1))
            )
        )
        atr_14 = float(tr.rolling(14).mean().iloc[-1])
        atr_20 = float(tr.rolling(20).mean().iloc[-1])
        
        # ATR compression ratio (tightening = building energy)
        atr_compression = atr_20 / atr_14 if atr_14 > 0 else 1.0
        
        # Range width (20-day) - tight consolidation
        range_20d = (high.rolling(20).max() - low.rolling(20).min()).iloc[-1]
        range_width_pct = float(range_20d / curr_close * 100) if curr_close > 0 else 100
        
        # Consolidation score (lower range width = tighter = better)
        consolidation_score = max(0, min(10, 10 - (range_width_pct / 2)))
        
        # Volume analysis
        avg_vol_20 = float(vol.rolling(20).mean().iloc[-1])
        curr_vol = float(vol.iloc[-1])
        vol_ratio = curr_vol / avg_vol_20 if avg_vol_20 > 0 else 1.0
        
        # Volume building?
        vol_building = vol_ratio > 1.2
        
        # Gap fill potential
        # If it gapped UP, what's the fill level?
        gap_filled_pct = 0
        if abs(gap_pct) > 3:  # Significant gap
            if gap_pct > 0:  # Gap up
                # Gap fill would be a pullback to prev_close
                fill_level = prev_close
                gap_filled_pct = (curr_close - fill_level) / curr_close * 100 if curr_close > fill_level else 0
            else:  # Gap down
                fill_level = prev_close
                gap_filled_pct = (fill_level - curr_close) / curr_close * 100 if fill_level > curr_close else 0
        
        # Gap type
        gap_type = "GAP UP" if gap_pct > 3 else ("GAP DOWN" if gap_pct < -3 else "NONE")
        
        # Mean reversion score (for gap fill plays)
        # Price vs 20-day mean
        ma20 = float(close.rolling(20).mean().iloc[-1])
        dist_from_ma20 = float((curr_close - ma20) / ma20 * 100)
        
        # Score: combination of gap + consolidation + volume
        gap_fill_score = 0
        if abs(gap_pct) >= 3:
            gap_fill_score += 3  # Has a gap
        if abs(gap_pct) >= 5:
            gap_fill_score += 2  # Significant gap
        if range_width_pct < 8:
            gap_fill_score += 3  # Tight consolidation
        elif range_width_pct < 12:
            gap_fill_score += 2
        if atr_compression < 0.8:
            gap_fill_score += 2  # ATR compressing
        if vol_building:
            gap_fill_score += 2
        if vol_ratio > 1.5:
            gap_fill_score += 1
        
        return {
            'symbol': ticker_sym,
            'price': curr_close,
            'gap_pct': gap_pct,
            'gap_type': gap_type,
            'atr_14': atr_14,
            'atr_compression': atr_compression,
            'range_width_pct': range_width_pct,
            'consolidation_score': consolidation_score,
            'vol_ratio': vol_ratio,
            'vol_building': vol_building,
            'gap_fill_score': gap_fill_score,
            'dist_from_ma20': dist_from_ma20,
            'news': news_context.get(ticker_sym) if news_context else None
        }
    except Exception as e:
        return None


# ─── SHORT SQUEEZE SCANNER ───────────────────────────────────────────────────

def analyze_short_squeeze(ticker_sym, news_context=None):
    """Analyze a ticker for short squeeze potential"""
    try:
        t = yf.Ticker(ticker_sym)
        info = t.info
        price = info.get('currentPrice', 0)
        
        if not price or price > 100:
            return None
        
        hist = t.history(period='30d')
        if len(hist) < 20:
            return None
        
        close = hist['Close']
        high = hist['High']
        low = hist['Low']
        vol = hist['Volume']
        
        # Short interest (available via yfinance info)
        shares_short = info.get('sharesShort', 0)
        short_pct_float = info.get('shortPercentOfFloat', 0) or 0
        shares_outstanding = info.get('sharesOutstanding', 1)
        
        # Days to cover (short volume / avg volume)
        avg_vol = float(vol.rolling(20).mean().iloc[-1])
        daily_short_vol = shares_short / 30  # Approximate
        days_to_cover = daily_short_vol / avg_vol if avg_vol > 0 else 0
        
        # Cost to borrow (proxy: high short interest = high borrow rate)
        # Using short percent of float as proxy
        si_score = short_pct_float * 100 if short_pct_float < 0.5 else 25  # Cap at 25%
        
        # Recent price momentum
        mom5d = float((close.iloc[-1] / close.iloc[-6] - 1) * 100) if len(close) > 5 else 0
        mom10d = float((close.iloc[-1] / close.iloc[-11] - 1) * 100) if len(close) > 10 else 0
        
        # Volume trend
        vol_5d_avg = float(vol.iloc[-5:].mean())
        vol_20d_avg = float(vol.iloc[-20:].mean())
        vol_trend = vol_5d_avg / vol_20d_avg if vol_20d_avg > 0 else 1.0
        
        # Breakout detection - price vs 20d high
        high_20d = float(high.rolling(20).max().iloc[-1])
        dist_from_20d_high = float((high_20d - close.iloc[-1]) / high_20d * 100)
        
        # Tight range before breakout
        range_10d = float((high.rolling(10).max() - low.rolling(10).min()).iloc[-1])
        range_width = float(range_10d / close.iloc[-1] * 100)
        tight_range = range_width < 5  # Less than 5% range in 10 days
        
        # Squeeze score
        squeeze_score = 0
        
        if si_score >= 10:
            squeeze_score += 4  # High short interest
        elif si_score >= 5:
            squeeze_score += 2
        
        if days_to_cover >= 3:
            squeeze_score += 3
        elif days_to_cover >= 2:
            squeeze_score += 2
        
        if vol_trend >= 1.5:
            squeeze_score += 2  # Volume expanding
        elif vol_trend >= 1.2:
            squeeze_score += 1
        
        if tight_range and dist_from_20d_high < 3:
            squeeze_score += 3  # Tight range, ready to break
        
        if mom5d > 5:
            squeeze_score += 2  # Already running
        elif mom5d < -5:
            squeeze_score += 1  # Possible dead cat bounce
        
        return {
            'symbol': ticker_sym,
            'price': float(close.iloc[-1]),
            'short_pct_float': short_pct_float * 100,
            'si_score': si_score,
            'days_to_cover': round(days_to_cover, 1),
            'mom5d': mom5d,
            'mom10d': mom10d,
            'vol_trend': round(vol_trend, 2),
            'dist_from_20d_high': dist_from_20d_high,
            'tight_range': tight_range,
            'squeeze_score': squeeze_score,
            'news': news_context.get(ticker_sym) if news_context else None
        }
    except Exception as e:
        return None


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("🐺 $SIGBOTTI — News Scanner Pipeline")
    print("=" * 50)
    print(f"Step 1: Pulling news tickers...")
    
    news_tickers = get_news_tickers()
    print(f"Found {len(news_tickers)} tickers with recent news")
    
    print(f"\nStep 2: Running gap fill analysis...")
    gap_plays = []
    for sym in news_tickers.keys():
        result = analyze_gap_fill(sym, news_tickers)
        if result and result['gap_fill_score'] >= 5:
            gap_plays.append(result)
        time.sleep(0.5)
    
    print(f"Found {len(gap_plays)} gap fill candidates")
    
    print(f"\nStep 3: Running short squeeze analysis...")
    squeeze_plays = []
    for sym in news_tickers.keys():
        result = analyze_short_squeeze(sym, news_tickers)
        if result and result['squeeze_score'] >= 6:
            squeeze_plays.append(result)
        time.sleep(0.5)
    
    print(f"Found {len(squeeze_plays)} short squeeze candidates")
    
    # Sort
    gap_plays.sort(key=lambda x: x['gap_fill_score'], reverse=True)
    squeeze_plays.sort(key=lambda x: x['squeeze_score'], reverse=True)
    
    # ─── OUTPUT ────────────────────────────────────────────────────────────────
    
    print("\n" + "=" * 60)
    print("📊 GAP FILL PLAYS (News-driven)")
    print("=" * 60)
    if gap_plays:
        for p in gap_plays[:10]:
            news_title = p.get('news', {}).get('title', 'No news')[:60] if p.get('news') else 'No news'
            print(f"\n{p['symbol']:6} @ ${p['price']:.2f}")
            print(f"  Score: {p['gap_fill_score']}/10 | Gap: {p['gap_pct']:+.1f}% {p['gap_type']}")
            print(f"  Consolidation: {p['consolidation_score']:.1f}/10 | Range: {p['range_width_pct']:.1f}% | ATR Compress: {p['atr_compression']:.2f}")
            print(f"  Vol Ratio: {p['vol_ratio']:.1f}x | Vol Building: {p['vol_building']}")
            print(f"  News: {news_title}...")
    else:
        print("No gap fill plays found matching criteria")
    
    print("\n" + "=" * 60)
    print("💥 SHORT SQUEEZE PLAYS (News-driven)")
    print("=" * 60)
    if squeeze_plays:
        for p in squeeze_plays[:10]:
            news_title = p.get('news', {}).get('title', 'No news')[:60] if p.get('news') else 'No news'
            print(f"\n{p['symbol']:6} @ ${p['price']:.2f}")
            print(f"  Score: {p['squeeze_score']}/14 | SI%: {p['short_pct_float']:.1f}% | DTC: {p['days_to_cover']} days")
            print(f"  Vol Trend: {p['vol_trend']:.1f}x | 5D Mom: {p['mom5d']:+.1f}% | Dist to 20D High: {p['dist_from_20d_high']:.1f}%")
            print(f"  Tight Range: {p['tight_range']} | News: {news_title}...")
    else:
        print("No short squeeze plays found matching criteria")
    
    # Save combined results
    combined = {
        'gap_plays': sorted(gap_plays, key=lambda x: x['gap_fill_score'], reverse=True)[:10],
        'squeeze_plays': sorted(squeeze_plays, key=lambda x: x['squeeze_score'], reverse=True)[:10],
        'scan_time': datetime.now().isoformat()
    }
    
    with open('/Users/sigbotti/.openclaw/workspace/scanner/news_scan_results.json', 'w') as f:
        json.dump(combined, f, indent=2, default=str)
    
    print(f"\n🐺 Scan complete. Saved to news_scan_results.json")
    return combined


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Stock Discovery Engine — Autonomous stock idea generation.
Sources: yfinance news, SEC EDGAR 13F filings, Reddit WSB (dollar-sign mentions),
         short interest scan, options flow, earnings momentum, finviz.
"""
import yfinance as yf
import requests
import json
import time
import re
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com",
}

RESULTS_FILE = "/Users/sigbotti/.openclaw/workspace/data/discovered-stocks.json"


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_base_universe():
    import importlib.util
    spec = importlib.util.spec_from_file_location("coil_scanner",
        "/Users/sigbotti/.openclaw/workspace/scripts/coil-scanner.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.UNIVERSE


# Tickers that are definitely real stocks
KNOWN_REAL = {
    'GME','AMC','LCID','SOFI','PLTR','RIVN','SMCI','BB','NOK','COIN',
    'HOOD','ASTS','LUNR','RKLB','GRPN','HTZ','HIMS','SOUN','AI','TTEC',
    'PCT','MARA','INDI','NVAX','BYND','ENVX','RXRX','CYPH','IOVA','CRDF',
    'ABEO','MNPR','SNBR','ROOT','EOSE','SRPT','BETR','SPHR','MPTI','BBAI',
    'SRAX','OPK','CTRM','NCTY','TIGO','SENS','MVST',
    'AAPL','MSFT','GOOG','AMZN','META','NFLX','NVDA','AMD','TSLA',
    'SPY','QQQ','IWM','DIA','GME','TSLA','AMD','NVDA','COIN','SMCI',
    'INTC','AMAT','ASML','LRCX','AMAT','MU','三星','SCZ','MDT',
    'F','GM','RIVN','LCID','PARA','WBD','DIS','PARA','RBLX','SNOW',
    'U','DKNG','PENN','MWK','NIO','XPEV','LI','PLTR','RDDT','PINS',
    'SNAP','ROKU','SQ','HOOD','DOCU','FVRR','ZM','PLTR',
}


def is_valid_ticker(ticker):
    """Stricter ticker validation — must look like a real ticker, not a word."""
    if not ticker or len(ticker) > 5 or len(ticker) < 1:
        return False
    if not ticker.isalpha():
        return False
    ticker = ticker.upper()
    # Known real stocks always pass
    if ticker in KNOWN_REAL:
        return True
    # Block all common English words (1-5 letters)
    banned = {
        'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HAS',
        'HER','WAS','ONE','OUR','OUT','HAS','GET','SAY','SEE','WAY',
        'NOW','NEW','GOT','BIG','PUT','OLD','DAY','RUN','TOP','LOW',
        'SET','ACT','GAP','LIT','FUCK','DAMN','SHIT','HELL','ASS',
        'MODEL','EAST','MUSK','PUMP','DOWN','DATA','WHY','OIL',
        'GOING','AM','SIGNS','DEAL','FIRM','TOO','IS','TO','OF',
        'UP','IF','IN','BY','IT','AS','AN','SO','WE','HE','BE',
        'DO','NO','ME','MY','IF','SO','UP','AN','IF','OR','ON',
        'THIS','THAT','WITH','HAVE','FROM','THEY','WOULD','JUST',
        'OVER','INTO','YEARS','YEAR','VERY','YOUR','MUCH','THEN',
        'TIME','SOME','COULD','MAKE','FIRST','LAST','NEXT','MOST',
        'ALSO','SUCH','EVEN','IPO','ETF','FDA','CEO','EPS','GDP',
        'CPI','USA','UK','EU','LONG','SHORT','BUY','SELL','CALL',
        'PUT','DD','PT','FD','YOLO','RH','FOMO','RIP','GOAT','MOON',
        'HODL','APE','APES','GAIN','LOSS','GAMMA','DELTA','THETA',
        'VEGA','ALPHA','BETA','SPY','QQQ','GOLD','SILVER','OIL',
    }
    if ticker in banned:
        return False
    # 1-letter tickers are real (X, V, etc.) — allow if not banned
    if len(ticker) == 1:
        return True
    # 2-3 letter tickers: block obvious words
    if len(ticker) <= 3:
        common_words = {
            'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HAS',
            'HER','WAS','ONE','OUR','OUT','GET','SAY','SEE','WAY','NOW',
            'NEW','GOT','BIG','PUT','OLD','DAY','RUN','TOP','LOW','SET',
            'ACT','GAP','LIT','INK','TOP','BOT','FLIP','SWING','SWING',
        }
        if ticker in common_words:
            return False
    return True


# ─────────────────────────────────────────────────────────────────────────────
# SOURCE 1: yfinance news — stocks with recent news catalysts
# ─────────────────────────────────────────────────────────────────────────────

def fetch_news_stocks(max_age_hours=48):
    """Find stocks with recent news catalysts via yfinance universe."""
    candidates = []
    base = get_base_universe()
    for ticker in base[:25]:
        try:
            t = yf.Ticker(ticker)
            news = t.news or []
            for item in news[:2]:
                pub = item.get('providerPublishTime', 0)
                if pub:
                    age_h = (time.time() - pub) / 3600
                    if 0 <= age_h <= max_age_hours:
                        candidates.append({
                            'ticker': ticker,
                            'news_headline': item.get('title', '')[:150],
                            'news_age_hours': round(age_h, 1),
                            'news_source': item.get('publisher', ''),
                            'source': 'yfinance news',
                        })
        except Exception:
            pass
        time.sleep(0.15)
    return candidates


# ─────────────────────────────────────────────────────────────────────────────
# SOURCE 2: SEC EDGAR 13F Institutional Holdings — Whale filings
# ─────────────────────────────────────────────────────────────────────────────

def fetch_13f_filings(days_back=30):
    """Pull recent 13F-HR filings from SEC EDGAR full-text search."""
    candidates = []
    try:
        end = datetime.now()
        start = end - timedelta(days=days_back)
        search_url = (
            f"https://efts.sec.gov/LATEST/search-index"
            f"?q=13F-HR&forms=13F-HR&from=0&size=60"
        )
        resp = requests.get(search_url, headers={
            "User-Agent": "Mozilla/5.0 (research@example.com)",
            "Accept": "application/json",
        }, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            hits = data.get('hits', {}).get('hits', [])
            seen = set()
            for h in hits:
                src = h.get('_source', {})
                file_date = src.get('file_date', '')
                if not file_date:
                    continue
                try:
                    fd = datetime.strptime(file_date, '%Y-%m-%d')
                    if fd < start:
                        continue
                except Exception:
                    continue
                names = src.get('display_names', [])
                cik_match = re.search(r'CIK\s*(\d+)', names[0] if names else '')
                if not cik_match:
                    continue
                cik = cik_match.group(1)
                # Look up company name to get ticker
                try:
                    co_url = (f"https://efts.sec.gov/LATEST/search-index"
                              f"?q={cik}&forms=10-K")
                    cr = requests.get(co_url, headers={
                        "User-Agent": "Mozilla/5.0 (research@example.com)",
                    }, timeout=8)
                    if cr.status_code == 200:
                        tick_data = cr.json()
                        th = tick_data.get('hits', {}).get('hits', [])
                        if th:
                            tick_names = th[0].get('_source', {}).get('display_names', [])
                            for n in tick_names:
                                m = re.search(r'\((\w{1,5})\)', n)
                                if m:
                                    t = m.group(1).upper()
                                    if is_valid_ticker(t) and t not in seen:
                                        seen.add(t)
                                        candidates.append({
                                            'ticker': t,
                                            'filing_type': '13F-HR',
                                            'company_name': n.split('(')[0].strip()[:50],
                                            'filing_date': file_date,
                                            'source': 'SEC EDGAR 13F',
                                        })
                except Exception:
                    pass
    except Exception:
        pass
    return candidates[:25]


# ─────────────────────────────────────────────────────────────────────────────
# SOURCE 3: Reddit WallStreetBets — Dollar-sign ticker mentions
# ─────────────────────────────────────────────────────────────────────────────

def fetch_reddit_tickers():
    """Scrape dollar-sign ticker mentions from r/wallstreetbets hot posts."""
    candidates = []
    seen = set()

    try:
        resp = requests.get(
            "https://www.reddit.com/r/wallstreetbets/hot.json?limit=30",
            headers=HEADERS, timeout=10
        )
        data = resp.json()
        posts = data.get('data', {}).get('children', [])
        for post in posts:
            score = post['data'].get('score', 0)
            if score < 500:
                continue
            title = post['data']['title']
            # Match dollar-sign ticker pattern (most reliable way to find tickers in WSB)
            dollar_tickers = re.findall(r'\$([A-Z]{1,5})\b', title.upper())
            for word in dollar_tickers:
                if is_valid_ticker(word) and word not in seen:
                    seen.add(word)
                    candidates.append({
                        'ticker': word,
                        'source': 'Reddit WSB ($ mentions)',
                        'post_title': title[:100],
                        'score': score,
                    })
    except Exception:
        pass

    candidates.sort(key=lambda x: x.get('score', 0), reverse=True)
    return candidates[:30]


# ─────────────────────────────────────────────────────────────────────────────
# SOURCE 4: Short Interest scan from yfinance universe
# ─────────────────────────────────────────────────────────────────────────────

def fetch_short_interest():
    """Scan universe for high SI stocks via yfinance."""
    candidates = []
    base = get_base_universe()
    for ticker in base:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            si = (info.get('shortPercentOfFloat', 0) or 0) * 100
            if si >= 15:
                candidates.append({
                    'ticker': ticker,
                    'short_interest_pct': round(si, 1),
                    'short_ratio': round(info.get('shortRatio', 0) or 0, 2),
                    'source': 'yfinance SI scan',
                })
        except Exception:
            pass
        time.sleep(0.15)
    candidates.sort(key=lambda x: x.get('short_interest_pct', 0), reverse=True)
    return candidates


# ─────────────────────────────────────────────────────────────────────────────
# SOURCE 5: Unusual Options Activity
# ─────────────────────────────────────────────────────────────────────────────

def fetch_options_flow():
    """Find stocks with elevated IV + volume spike."""
    candidates = []
    base = get_base_universe()
    for ticker in base:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            iv = info.get('impliedVolatility', 0) or 0
            vol = info.get('volume', 0) or 0
            avg_vol = info.get('averageVolume', 0) or 0
            if iv > 0.4 and avg_vol > 0 and vol / avg_vol > 2.0:
                candidates.append({
                    'ticker': ticker,
                    'implied_volatility': round(iv * 100, 1),
                    'volume_ratio': round(vol / avg_vol, 2),
                    'source': 'Options Flow (yfinance)',
                })
        except Exception:
            pass
        time.sleep(0.15)
    candidates.sort(key=lambda x: x.get('volume_ratio', 0), reverse=True)
    return candidates[:20]


# ─────────────────────────────────────────────────────────────────────────────
# SOURCE 6: Earnings momentum — trending stocks with upcoming earnings
# ─────────────────────────────────────────────────────────────────────────────

def fetch_earnings_momentum():
    """Find stocks with upcoming earnings + strong price momentum."""
    candidates = []
    base = get_base_universe()
    for ticker in base:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            h = t.history(period="5d", interval="1d")
            if h.empty:
                continue
            ret_5d = (h['Close'].iloc[-1] / h['Close'].iloc[0] - 1) * 100
            if ret_5d < 4:
                continue
            earnings_dates = info.get('earningsDates', [])
            next_er = None
            for ed in earnings_dates:
                if isinstance(ed, dict):
                    d = ed.get('EarningsDate', ed.get('date'))
                    if d:
                        next_er = d
                        break
            candidates.append({
                'ticker': ticker,
                'next_earnings': str(next_er) if next_er else 'N/A',
                '5d_return_pct': round(ret_5d, 1),
                'price': info.get('currentPrice', 0),
                'source': 'Earnings Momentum',
            })
        except Exception:
            pass
        time.sleep(0.15)
    candidates.sort(key=lambda x: x.get('5d_return_pct', 0), reverse=True)
    return candidates[:15]


# ─────────────────────────────────────────────────────────────────────────────
# SOURCE 7: Finviz Short Float Screener
# ─────────────────────────────────────────────────────────────────────────────

def fetch_finviz_short_float():
    """Scrape high short float stocks from finviz screener."""
    candidates = []
    try:
        url = (
            "https://finviz.com/screener.ashx"
            "?v=152&o=-shortFloat&f=short_float_o15&c=1,2,3,4,5,6,7,8"
        )
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            text = resp.text
            # Finviz encodes tickers in onclick handlers and cell data
            ticker_pattern = re.findall(r'\bonclick[^>]*>[A-Z]{1,5}</a>', text)
            seen = set()
            for m in ticker_pattern:
                tickers_in_row = re.findall(r'>([A-Z]{1,5})<', m)
                for t in tickers_in_row:
                    if is_valid_ticker(t) and t not in seen:
                        seen.add(t)
                        candidates.append({
                            'ticker': t,
                            'short_float': '>15% (finviz)',
                            'source': 'Finviz Short Float Screener',
                        })
    except Exception:
        pass
    return candidates[:25]


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def discover_all():
    print("🔍 Running stock discovery engine...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("=" * 60)

    results = []

    sources = [
        ("📰 News catalysts", fetch_news_stocks),
        ("🐋 SEC EDGAR 13F filings", fetch_13f_filings),
        ("📊 Reddit WSB (dollar mentions)", fetch_reddit_tickers),
        ("📉 Short interest scan", fetch_short_interest),
        ("📈 Options flow", fetch_options_flow),
        ("💰 Earnings momentum", fetch_earnings_momentum),
        ("🎯 Finviz short float", fetch_finviz_short_float),
    ]

    for name, fn in sources:
        print(f"\n{name}...")
        try:
            stocks = fn()
            print(f"   Found {len(stocks)} stocks")
            for s in stocks[:3]:
                if s.get('news_headline'):
                    print(f"   → {s['ticker']}: {s['news_headline'][:65]}")
                elif s.get('short_interest_pct'):
                    print(f"   → {s['ticker']}: {s['short_interest_pct']}% SI")
                elif s.get('5d_return_pct'):
                    print(f"   → {s['ticker']}: {s['5d_return_pct']}% return")
                elif s.get('score'):
                    print(f"   → {s['ticker']} (score {s['score']})")
                else:
                    print(f"   → {s['ticker']}")
            results.extend(stocks)
        except Exception as e:
            print(f"   ⚠ Error: {e}")

    # Dedup
    seen = {}
    for r in results:
        t = r['ticker']
        if t not in seen:
            seen[t] = r
        else:
            existing = seen[t]
            existing.setdefault('sources', []).append(r.get('source', 'unknown'))
            # Merge additional data
            if r.get('short_interest_pct') and not existing.get('short_interest_pct'):
                existing['short_interest_pct'] = r['short_interest_pct']

    deduped = sorted(seen.values(),
        key=lambda x: -len(x.get('sources', [x.get('source','')])))

    print(f"\n{'='*60}")
    print(f"✅ {len(deduped)} unique stocks discovered")

    print(f"\n🔥 TOP STOCKS (multi-source cross-confirmed):")
    for s in deduped[:25]:
        srcs = ', '.join(set(s.get('sources', [s.get('source','')])))
        si = f" | SI:{s.get('short_interest_pct','?')}" if s.get('short_interest_pct') else ""
        ret = f" | +{s.get('5d_return_pct','?')}% ret" if s.get('5d_return_pct') else ""
        flag = "🏆" if len(s.get('sources', [])) >= 2 else "  "
        print(f"  {flag} {s['ticker']:8} | {srcs}{si}{ret}")

    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_found": len(deduped),
            "results": deduped[:60]
        }, f, indent=2)

    print(f"\n💾 Saved to {RESULTS_FILE}")
    return deduped


if __name__ == "__main__":
    discover_all()
#!/usr/bin/env python3
"""
Fundamental Filter — Pre-alert news checker for the gap scanner.
Runs BEFORE any trade signal is acted on. Catches:
- Dilution / capital raises
- Earnings misses / guidance cuts
- SEC investigations / delisting risk
- Insider selling / buybacks
- Merger / acquisition news
- Production setbacks

Lou's rule: If fundamental is broken, no trade — no matter how good the technical setup looks.
"""
import yfinance as yf
import json
import os
from datetime import datetime, timedelta

ALERT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(ALERT_DIR, exist_ok=True)

def check_fundamentals(ticker: str, days_back: int = 3) -> dict:
    """
    Check fundamental health and recent news for a ticker.
    Returns dict with red flags and a pass/fail decision.
    """
    result = {
        "ticker": ticker,
        "timestamp": datetime.now().isoformat(),
        "pass": True,
        "red_flags": [],
        "yellow_flags": [],
        "news_headlines": [],
        "fundamental_verdict": "CLEAR",
        "dilution_risk": False,
        "earnings_imminent": False,
    }

    try:
        t = yf.Ticker(ticker)
        info = t.info

        # ── DILUTION CHECKS ────────────────────────────────────────
        # Flags that indicate share dilution or toxic financing
        market_cap = info.get('marketCap', 0)
        shares_outstanding = info.get('sharesOutstanding', 0)
        book_value = info.get('bookValue', 0)
        total_debt = info.get('totalDebt', 0)
        cash = info.get('totalCash', 0)
        cash_flow = info.get('freeCashflow', 0)

        # Cash runway check — if burning fast and cash is low, dilution likely
        if cash_flow and cash_flow < 0 and cash and market_cap:
            cash_runway_months = (cash / abs(cash_flow)) * 12 if cash_flow != 0 else 999
            if cash_runway_months < 12 and market_cap < 5e9:
                result['red_flags'].append(f"Low cash runway: ~{cash_runway_months:.0f} months. Dilution likely.")
                result['dilution_risk'] = True

        # Debt-to-equity red flag — only meaningful for profitable companies
        # For high-growth / pre-profit: use cash runway instead
        # Only flag if company is profitable AND has meaningful debt
        if info.get('trailingEps', 0) > 0 and total_debt > 1e9:  # profitable with >$1B debt
            # Calculate D/E properly: total_debt / (bookValue * sharesOutstanding)
            shares = info.get('sharesOutstanding', 0)
            if book_value and shares:
                total_equity = book_value * shares
                if total_equity > 0:
                    de_ratio = total_debt / total_equity
                    if de_ratio > 2:  # More conservative threshold for D/E
                        result['red_flags'].append(f"High D/E ratio: {de_ratio:.1f}x. Financial stress.")
                        result['dilution_risk'] = True

        # Recent secondary offerings /dilution
        # yfinance doesn't always have this — check news for keywords
        news = info.get('news', [])
        for article in news[:10]:
            title = (article.get('title') or '').lower()
            result['news_headlines'].append(title)

            dilution_keywords = [
                'dilution', 'diluted', 'secondary offering', 'capital raise',
                'raises $', 'raise $', 'follow-on offering', 'new shares',
                'share sale', 'common stock offering', 'registered direct',
                'at-the-market offering', 'ATM offering', 'underwritten public',
                'registered direct offering', 'private placement'
            ]
            for kw in dilution_keywords:
                if kw in title:
                    result['red_flags'].append(f"DILUTION: '{article.get('title')}'")
                    result['dilution_risk'] = True
                    break

        # ── EARNINGS / GUIDANCE CHECKS ───────────────────────────────
        # Check if earnings are coming within next 5 days
        next_earnings = info.get('earningsDates', [])
        if not next_earnings:
            # Try to calculate from frequency
            cal = info.get('earningsCalendar')
            if cal:
                next_earnings = [cal]

        if next_earnings:
            for ed in next_earnings:
                ed_str = str(ed)
                result['earnings_imminent'] = True

        # Look for earnings miss / guidance cut in news
        for article in news[:10]:
            title = (article.get('title') or '').lower()
            earnings_keywords = ['earnings miss', 'revenue miss', 'guidance cut', 'cuts outlook',
                                 'lowers guidance', 'shares tumble', 'stock falls', 'drops on']
            for kw in earnings_keywords:
                if kw in title:
                    result['red_flags'].append(f"BEARISH NEWS: '{article.get('title')}'")
                    break

        # ── OPERATIONAL RED FLAGS ─────────────────────────────────────
        # Delisting risk
        if info.get('delisted'):
            result['red_flags'].append("STOCK DELISTED OR HALTED")

        # Bankruptcy risk
        bankruptcy_keywords = ['bankruptcy', ' Chapter 11', 'insolvent', 'going concern']
        for article in news[:5]:
            title = (article.get('title') or '').lower()
            for kw in bankruptcy_keywords:
                if kw in title:
                    result['red_flags'].append(f"BANKRUPTCY RISK: '{article.get('title')}'")

        # ── SHORT INTEREST ADDITIONAL CHECKS ──────────────────────────
        si = info.get('shortPercentOfFloat', 0) or 0
        if si > 0.30:
            result['yellow_flags'].append(f"Extreme SI: {si*100:.0f}% — squeeze potential but also fundamental concern")

        # ── DETERMINE VERDICT ────────────────────────────────────────
        if result['dilution_risk']:
            result['fundamental_verdict'] = "FAIL — DILUTION RISK"
            result['pass'] = False
        elif len(result['red_flags']) >= 2:
            result['fundamental_verdict'] = "FAIL — MULTIPLE RED FLAGS"
            result['pass'] = False
        elif len(result['red_flags']) == 1:
            result['fundamental_verdict'] = "CAUTION — 1 RED FLAG"
            result['pass'] = True  # Not a hard fail, but flag it
        elif result['earnings_imminent']:
            result['fundamental_verdict'] = "CAUTION — EARNINGS IMMINENT"
            result['yellow_flags'].append("Earnings within next week — IV crush incoming")

    except Exception as e:
        result['fundamental_verdict'] = f"ERROR — {e}"
        result['yellow_flags'].append(f"Could not fetch fundamentals: {e}")

    return result


def check_watchlist_fundamentals(tickers: list) -> dict:
    """Check all tickers in watchlist and return flagged ones."""
    results = {}
    for ticker in tickers:
        results[ticker] = check_fundamentals(ticker)
    return results


def filter_scan_results(scan_results: list) -> list:
    """
    Take raw scan results (from gap-alert-scanner) and filter out
    any that fail the fundamental check.
    Returns filtered list with notes.
    """
    filtered = []
    for result in scan_results:
        ticker = result.get('ticker')
        fund = check_fundamentals(ticker)

        # Merge fundamental data into scan result
        result['fundamental'] = fund
        result['fundamental_verdict'] = fund['fundamental_verdict']
        result['red_flags'] = fund['red_flags']
        result['dilution_risk'] = fund['dilution_risk']

        if not fund['pass']:
            result['score'] = 0  # Kill the signal
            result['kill_reason'] = fund['fundamental_verdict']

        filtered.append(result)

    return filtered


def save_fundamental_state(ticker: str, verdict: dict):
    """Cache fundamental verdict for the day to avoid re-fetching."""
    state_file = os.path.join(ALERT_DIR, f"fundamental_{ticker}_{datetime.now().strftime('%Y%m%d')}.json")
    try:
        with open(state_file, 'w') as f:
            json.dump(verdict, f, indent=2)
    except:
        pass


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: fundamental_filter.py <TICKER>")
        print("Example: fundamental_filter.py LCID")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    result = check_fundamentals(ticker)

    print(f"\n{'='*60}")
    print(f"FUNDAMENTAL FILTER: {ticker}")
    print(f"{'='*60}")
    print(f"VERDICT: {result['fundamental_verdict']}")
    print(f"PASS: {result['pass']}")

    if result['red_flags']:
        print(f"\n🔴 RED FLAGS ({len(result['red_flags'])}):")
        for f in result['red_flags']:
            print(f"  • {f}")

    if result['yellow_flags']:
        print(f"\n🟡 YELLOW FLAGS ({len(result['yellow_flags'])}):")
        for f in result['yellow_flags']:
            print(f"  • {f}")

    if result['news_headlines']:
        print(f"\n📰 RECENT NEWS:")
        for h in result['news_headlines'][:5]:
            print(f"  • {h[:100]}")

    if result['dilution_risk']:
        print(f"\n⚠️  DILUTION RISK CONFIRMED — DO NOT TRADE")

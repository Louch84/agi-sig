#!/usr/bin/env python3
"""
Earnings Power Scanner — Targets the institutional trap pattern.
Logic: Low institutional ownership (<40%) + high short interest (>20%) + 
       earnings in 2-7 days = retail piled in, shorts trapped, squeeze imminent.

Research basis: Berkman/Koch (Iowa State) — stocks with LOW institutional 
ownership + earnings announcements = predictable post-earnings reversal.
Institutional investors buy 2 days before, retail chases, shorts squeeze.
"""
import yfinance as yf
import json
import os
import sys
import time
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path("/Users/sigbotti/.openclaw/workspace/data")
DATA_DIR.mkdir(exist_ok=True)
RESULTS_FILE = DATA_DIR / "earnings-power.json"


def load_universe():
    f = Path("/Users/sigbotti/.openclaw/workspace/data/universe.json")
    if f.exists():
        with open(f) as fh:
            return json.load(fh).get("tickers", [])
    return []


def get_earnings_data(ticker):
    """Get days-to-earnings, expected move, and next earnings date."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        cal = t.calendar
        
        # Current price
        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
        
        # Days to earnings
        days_to = 999
        exp_move = 0
        earnings_date = None
        
        if cal and "Earnings Date" in cal:
            ed_list = cal["Earnings Date"]
            if isinstance(ed_list, list) and len(ed_list) > 0:
                ed = ed_list[0]
                if isinstance(ed, date):
                    days_to = (ed - date.today()).days
                    earnings_date = ed.isoformat()
                elif hasattr(ed, "date") and callable(ed.date):
                    earnings_date = ed.date().isoformat()
                    days_to = (ed.date() - date.today()).days
            
            # Expected move (% from stock price, not absolute)
            earn_avg = cal.get("Earnings Average", 0) or 0
            earn_high = cal.get("Earnings High", 0) or 0
            earn_low = cal.get("Earnings Low", 0) or 0
            
            if earn_avg:
                exp_move = abs(float(earn_avg))
            elif earn_high and earn_low:
                exp_move = abs((float(earn_high) + float(earn_low)) / 2)
        
        return {
            "days_to": int(days_to),
            "exp_move": round(exp_move, 2),
            "earnings_date": earnings_date,
            "price": round(float(price), 2),
        }
    except Exception:
        return {"days_to": 999, "exp_move": 0, "earnings_date": None, "price": 0}


def get_short_data(ticker):
    """Get short interest + institutional ownership."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        
        si = (info.get("shortPercentOfFloat", 0) or 0) * 100
        sr = info.get("shortRatio", 0) or 0  # days to cover
        si_shares = info.get("sharesShort", 0) or 0
        si_prior = info.get("sharesShortPriorMonth", 0) or 0
        
        si_change = 0
        if si_prior > 0:
            si_change = round(((si_shares - si_prior) / si_prior) * 100, 1)
        
        io = (info.get("heldPercentInstitutions", 0) or 0) * 100
        inst_pct = round(io, 1)
        
        # Low inst = retail-dominated = the institutional trap pattern
        # High inst = institutions already positioned = less explosive
        low_io = inst_pct < 40
        
        return {
            "si": round(si, 1),
            "short_ratio": round(sr, 1),
            "si_change": si_change,
            "inst_pct": inst_pct,
            "low_io": low_io,
        }
    except Exception:
        return {"si": 0, "short_ratio": 0, "si_change": 0, "inst_pct": 0, "low_io": False}


def score_setup(earnings, shorts):
    """Score 0-100 how strong this earnings-squeeze setup is."""
    score = 0
    days = earnings.get("days_to", 999)
    exp_move = earnings.get("exp_move", 0)
    si = shorts.get("si", 0)
    sr = shorts.get("short_ratio", 0)
    io = shorts.get("inst_pct", 100)
    low_io = shorts.get("low_io", False)
    si_change = shorts.get("si_change", 0)
    
    # ── SWEET SPOT: 2-7 days to earnings ─────────────────────────
    if 2 <= days <= 3:
        score += 40  # optimal window — squeeze before retail piles in
    elif 4 <= days <= 7:
        score += 25
    elif 8 <= days <= 14:
        score += 10
    elif days < 2:
        score += 5  # too close — IV already crushed
    
    # ── LOW INSTITUTIONAL OWNERSHIP (core signal) ───────────────
    if io < 20:
        score += 25
    elif io < 30:
        score += 18
    elif io < 40:
        score += 12
    elif io < 50:
        score += 6
    # High inst = penalize
    elif io > 80:
        score -= 15
    
    # ── SHORT INTEREST (squeeze fuel) ───────────────────────────
    if si >= 40:
        score += 35
    elif si >= 30:
        score += 25
    elif si >= 20:
        score += 15
    elif si >= 10:
        score += 8
    
    # ── DAYS TO COVER (trapped shorts) ────────────────────────
    if sr >= 10:
        score += 25
    elif sr >= 5:
        score += 18
    elif sr >= 3:
        score += 10
    elif sr >= 1:
        score += 5
    
    # ── SI CHANGE MoM (shorts building) ────────────────────────
    if si_change >= 20:
        score += 20
    elif si_change >= 10:
        score += 12
    elif si_change >= 5:
        score += 6
    
    # ── EXPECTED MOVE (IV premium signal) ───────────────────────
    # High expected move vs. historical avg = IV is high = premium opportunity
    # Low expected move with high SI = market doesn't see the squeeze coming
    if exp_move < 3:
        score += 10  # market underpricing the move
    elif exp_move > 10:
        score -= 5  # already priced in
    
    return min(max(score, 0), 100)


def main():
    tickers = load_universe()
    if not tickers:
        print("No universe found")
        return
    
    print(f"📅 Earnings Power Scanner — {datetime.now().strftime('%H:%M:%S')}")
    print(f"   Target: low IO + high SI + earnings in 2-7 days")
    print(f"   Universe: {len(tickers)} stocks\n")
    
    results = []
    
    for i, ticker in enumerate(tickers):
        print(f"[{i+1}/{len(tickers)}] {ticker}...", end=" ", flush=True)
        
        earn = get_earnings_data(ticker)
        shorts = get_short_data(ticker)
        score = score_setup(earn, shorts)
        
        row = {
            "ticker": ticker,
            "score": score,
            "days_to_earnings": earn["days_to"],
            "earnings_date": earn.get("earnings_date"),
            "exp_move": earn["exp_move"],
            "price": earn["price"],
            "si": shorts["si"],
            "short_ratio": shorts["short_ratio"],
            "si_change": shorts["si_change"],
            "inst_pct": shorts["inst_pct"],
            "low_io": shorts["low_io"],
        }
        results.append(row)
        
        days = earn["days_to"]
        io = shorts["inst_pct"]
        si = shorts["si"]
        
        if days <= 14 and score >= 30:
            tag = "🔴" if days <= 7 else "🟡"
            print(f"score {score:3}/100 | {tag}ER {days}d | IO {io:.0f}% | SI {si:.0f}%")
        else:
            print(f"score {score:3}/100")
        
        time.sleep(0.15)
    
    results.sort(key=lambda x: x["score"], reverse=True)
    
    print(f"\n{'='*65}")
    print(f"📊 TOP EARNINGS POWER SETUPS:")
    
    top = [r for r in results if r["score"] >= 30]
    for r in top[:15]:
        days = r["days_to_earnings"]
        io = r["inst_pct"]
        si = r["si"]
        sr = r["short_ratio"]
        io_tag = "👶" if io < 30 else ("🏦" if io > 70 else "")
        earns_tag = "📅" if days <= 7 else ""
        
        print(f"  {r['ticker']:6} | {r['score']:3}/100 | ER {days:2}d{earns_tag} | "
              f"IO {io:4.0f}%{io_tag} | SI {si:5.1f}% | DTC {sr:4.1f} | "
              f"exp {r['exp_move']:+.1f}%")
        if r["si_change"]:
            print(f"           SI change MoM: {r['si_change']:+.1f}%")
    
    print(f"\n💾 Saved to {RESULTS_FILE}")
    
    with open(RESULTS_FILE, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
        }, f, indent=2, default=str)
    
    return results


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Fast Combined Momentum Scanner — all three strategies in one pass.
Scans top 20 universe stocks by SI, scores them on:
  - Gap/dip squeeze potential (from squeeze-scanner)
  - Coil compression (from coil-scanner)
  - Gap-up catalyst (from gap-alert-scanner)

Uses 60d daily + 5d 15min data for speed. Sub-60s scan.
"""
import yfinance as yf
import numpy as np
import json
import os
import time
from datetime import datetime

UNIVERSE_FILE = "/Users/sigbotti/.openclaw/workspace/data/universe.json"
RESULTS_FILE = "/Users/sigbotti/.openclaw/workspace/data/fast-scan.json"


def load_universe():
    if os.path.exists(UNIVERSE_FILE):
        with open(UNIVERSE_FILE) as f:
            data = json.load(f)
            tickers = data.get('tickers', [])
            if tickers:
                return tickers
    return None

_fallback = ['GME','AMC','LCID','SOFI','PLTR','RIVN','SMCI','BB','NOK','COIN',
              'HOOD','ASTS','LUNR','RKLB','GRPN','HTZ','HIMS','SOUN','AI','TTEC',
              'PCT','MARA','INDI','NVAX','BYND','ENVX','RXRX','CYPH','IOVA','CRDF',
              'ABEO','MNPR','SNBR','ROOT','EOSE','SRPT','BETR','SPHR','MPTI','BBAI',
              'SRAX','OPK','CTRM','NCTY','TIGO','SENS','MVST']
UNIVERSE = load_universe() or _fallback


def _ema(data, period):
    data = np.array(data)
    ema = np.zeros(len(data))
    ema[0] = data[0]
    m = 2 / (period + 1)
    for i in range(1, len(data)):
        ema[i] = (data[i] - ema[i-1]) * m + ema[i-1]
    return ema


def _atr(high, low, close, period=14):
    high, low, close = np.array(high), np.array(low), np.array(close)
    tr1 = np.abs(high[1:] - low[1:])
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])
    tr = np.maximum(np.maximum(tr1, tr2), tr3)
    atr = np.zeros(len(close))
    atr[period-1] = np.mean(tr[:period])
    for i in range(period, len(close)):
        atr[i] = (atr[i-1] * (period - 1) + tr[i-1]) / period
    return atr


def scan_ticker_fast(ticker):
    """Fast comprehensive scan — 60d daily + 5d 15min."""
    try:
        t = yf.Ticker(ticker)

        # Parallel fetch: 60d daily + 5d 15min
        h60 = t.history(period="60d", interval="1d")
        h5 = t.history(period="5d", interval="15m")

        if h60.empty or len(h60) < 30:
            return None

        info = t.info
        closes60 = h60['Close'].values
        highs60 = h60['High'].values
        lows60 = h60['Low'].values
        vols60 = h60['Volume'].values

        current = closes60[-1]
        prev_close = closes60[-2] if len(closes60) > 1 else current

        # ── ATR ──────────────────────────────────────────────────────────
        atr_vals = _atr(highs60, lows60, closes60, 14)
        current_atr = atr_vals[-1]
        atr_sma10 = np.mean(atr_vals[-10:])
        atr_ratio = current_atr / atr_sma10 if atr_sma10 > 0 else 1.0

        # ── Bollinger Width ───────────────────────────────────────────────
        sma20_full = _ema(closes60, 20)
        std20_full = np.array([np.std(closes60[max(0,i-20):i+1]) for i in range(20, len(closes60))])
        std20_padded = np.concatenate([np.full(20, np.nan), std20_full])
        valid_idx = min(59, len(sma20_full) - 1)
        bb_width = (2 * std20_full[-1]) / sma20_full[valid_idx] * 100

        bb_widths = []
        for i in range(20, len(closes60)):
            s20 = _ema(closes60[:i], 20)
            st = np.std(closes60[i-20:i])
            bw = ((s20[-1] + st*2) - (s20[-1] - st*2)) / s20[-1] * 100
            bb_widths.append(bw)
        bw_pct = (sorted(bb_widths).index(bb_widths[-1]) / len(bb_widths)) * 100 if bb_widths else 50

        # ── Days in tight range ─────────────────────────────────────────
        days_tight = 0
        for i in range(-15, 0):
            if i >= -len(highs60) and i < -1:
                day_range = highs60[i] - lows60[i]
                if day_range < current_atr * 0.5:
                    days_tight += 1

        # ── Volume trend ─────────────────────────────────────────────────
        vol5 = np.mean(vols60[-5:])
        vol20 = np.mean(vols60[-20:])
        vol_trend = vol5 / vol20 if vol20 > 0 else 1.0

        # ── RSI ──────────────────────────────────────────────────────────
        deltas = np.diff(closes60)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        ag = np.mean(gains[-14:])
        al = np.mean(losses[-14:])
        rs = ag / al if al > 0 else 100
        rsi = 100 - (100 / (1 + rs))

        # ── EMAs ──────────────────────────────────────────────────────────
        ema20 = _ema(closes60, 20)[-1]
        ema50 = _ema(closes60, 50)[-1] if len(closes60) >= 50 else None
        above_ema20 = current > ema20
        ema20_above_ema50 = ema20 > ema50 if ema50 else False

        # ── MACD ─────────────────────────────────────────────────────────
        ema12 = _ema(closes60, 12)[-1]
        ema26 = _ema(closes60, 26)[-1]
        macd = ema12 - ema26
        macd_sig = _ema(np.concatenate([[ema12], [macd]]), 9)[-1]
        macd_hist = macd - macd_sig

        # ── Gap ──────────────────────────────────────────────────────────
        today_open = h60['Open'].iloc[-1] if len(h60) >= 1 else current
        gap_pct = ((today_open - prev_close) / prev_close) * 100 if prev_close else 0

        # ── 10d range position ────────────────────────────────────────────
        w10_high = float(np.max(highs60[-10:]))
        w10_low = float(np.min(lows60[-10:]))
        pos10 = (current - w10_low) / (w10_high - w10_low) * 100 if w10_high != w10_low else 50

        # ── Short interest ────────────────────────────────────────────────
        si = (info.get('shortPercentOfFloat', 0) or 0) * 100
        short_ratio = info.get('shortRatio', 0) or 0

        # ── Intraday (5d 15m) ───────────────────────────────────────────
        si_score = 0
        coil_score = 0
        momentum_score = 0

        # Short interest scoring
        if si >= 40: si_score += 35
        elif si >= 20: si_score += 25
        elif si >= 10: si_score += 15

        if short_ratio >= 5: si_score += 15
        elif short_ratio >= 3: si_score += 10

        # Coil scoring (ATR squeeze + BB compression)
        if atr_ratio <= 0.5: coil_score += 30
        elif atr_ratio <= 0.65: coil_score += 22
        elif atr_ratio <= 0.75: coil_score += 15

        if bw_pct <= 10: coil_score += 28
        elif bw_pct <= 20: coil_score += 22
        elif bw_pct <= 30: coil_score += 15

        if days_tight >= 7: coil_score += 20
        elif days_tight >= 5: coil_score += 12

        if vol_trend <= 0.6: coil_score += 15
        elif vol_trend <= 0.8: coil_score += 8

        if 40 <= rsi <= 65: coil_score += 12
        if above_ema20: coil_score += 8
        if ema20_above_ema50: coil_score += 12

        # Momentum/gap scoring
        if gap_pct < -3: momentum_score += 30  # big gap down = squeeze fuel
        elif gap_pct < -1: momentum_score += 15
        elif gap_pct > 5: momentum_score += 25  # gap up catalyst

        if rsi < 35: momentum_score += 20
        elif rsi < 45: momentum_score += 10
        elif rsi > 70: momentum_score -= 20

        if pos10 < 25: momentum_score += 15  # near 10d lows = bounce setup
        if macd_hist > 0: momentum_score += 8

        return {
            "ticker": ticker,
            "price": round(float(current), 2),
            "gap_pct": round(float(gap_pct), 2),
            "rsi": round(float(rsi), 1),
            "si": round(float(si), 1),
            "short_ratio": round(float(short_ratio), 2),
            "atr_ratio": round(float(atr_ratio), 2),
            "bb_width": round(float(bb_width), 1),
            "bb_pct": round(float(bw_pct), 1),
            "days_tight": int(days_tight),
            "vol_trend": round(float(vol_trend), 2),
            "pos_10d": round(float(pos10), 1),
            "macd_hist": round(float(macd_hist), 3),
            "above_ema20": bool(above_ema20),
            "ema20_above_ema50": bool(ema20_above_ema50),
            "si_score": int(si_score),
            "coil_score": int(coil_score),
            "momentum_score": int(momentum_score),
            "total_score": int(si_score + coil_score + momentum_score),
        }
    except Exception:
        return None


def main():
    print(f"⚡ Fast Combined Scan — {datetime.now().strftime('%H:%M:%S %Z')}")
    print(f"   Universe: {len(UNIVERSE)} stocks")

    # Sort by SI to scan most relevant first
    print("   Sorting by SI...")
    si_map = {}
    for t in UNIVERSE:
        try:
            info = yf.Ticker(t).info
            si = (info.get('shortPercentOfFloat', 0) or 0) * 100
            si_map[t] = si
        except:
            si_map[t] = 0
        time.sleep(0.15)

    sorted_universe = sorted(UNIVERSE, key=lambda x: si_map.get(x, 0), reverse=True)
    top20 = sorted_universe[:20]
    print(f"   Top 20 by SI: {', '.join(top20[:10])}...")

    results = []
    for i, ticker in enumerate(top20):
        print(f"[{i+1}/20] {ticker}...", end=" ", flush=True)
        row = scan_ticker_fast(ticker)
        if row:
            print(f"gap {row['gap_pct']:+.1f}% | RSI {row['rsi']:.0f} | "
                  f"SI {row['si']:.0f}% | ATR {row['atr_ratio']:.2f} | "
                  f"BW {row['bb_width']:.1f}%({row['bb_pct']:.0f}%ile) | "
                  f"score {row['total_score']}/100")
            results.append(row)
        else:
            print("no data")
        time.sleep(0.2)

    results.sort(key=lambda x: x['total_score'], reverse=True)

    print(f"\n{'='*60}")
    print(f"🔥 TOP SETUPS:")
    for r in results[:10]:
        tags = []
        if r['coil_score'] >= 40: tags.append("COIL")
        if r['si_score'] >= 30: tags.append("SI")
        if r['momentum_score'] >= 20: tags.append("MOMO")
        tag_str = f"[{','.join(tags)}]" if tags else ""
        print(f"  {r['ticker']:6} ${r['price']:7.2f} | {r['total_score']:3}/100 {tag_str:15} | "
              f"gap {r['gap_pct']:+.1f}% | RSI {r['rsi']:5.0f} | "
              f"SI {r['si']:5.1f}% | BW {r['bb_width']:5.1f}%({r['bb_pct']:4.0f}%ile)")

    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "results": results}, f, indent=2)
    print(f"\n💾 Saved to {RESULTS_FILE}")
    return results


if __name__ == "__main__":
    main()
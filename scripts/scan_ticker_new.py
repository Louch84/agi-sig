#!/usr/bin/env python3
"""
Short Squeeze Ticker Scanner — lightweight single-ticker scan for squeeze setup.
Used by gap-alert-scanner.py via subprocess for detailed ticker analysis.
"""
import numpy as np
import json
import os
import sys
from datetime import datetime
from urllib.request import urlopen, Request
import urllib.error
import yfinance as yf

WORKSPACE = os.path.dirname(os.path.dirname(__file__))


def _ema(data, period):
    """Compute EMA for an array of prices."""
    k = 2 / (period + 1)
    ema = float(data[0])
    for price in data[1:]:
        ema = price * k + ema * (1 - k)
    return ema


def _get_ma_data(ticker, current_price):
    """Get MA signals for a ticker. Returns dict with MA data."""
    try:
        t = yf.Ticker(ticker)
        h = t.history(period="6mo", interval="1d")
        if h.empty or len(h) < 60:
            return {}

        closes = h["Close"].values
        ema9 = _ema(closes, 9)
        ema21 = _ema(closes, 21)
        ema50 = _ema(closes, 50) if len(closes) >= 50 else None
        ema200 = _ema(closes, 200) if len(closes) >= 200 else None

        # Golden / Death cross
        signal = "NEUTRAL"
        if ema50 and ema200:
            signal = "GOLDEN_CROSS" if ema50 > ema200 else "DEATH_CROSS"

        # EMA50 slope
        slope_50 = 0
        if ema50 and len(closes) >= 55:
            ema50_5d_ago = _ema(closes[:-5], 50)
            slope_50 = round(((ema50 - ema50_5d_ago) / ema50_5d_ago) * 100, 2)

        return {
            "ma_signal": signal,
            "short_signal": "ABOVE_EMA21" if current_price > ema21 else "BELOW_EMA21",
            "ema9": round(ema9, 2),
            "ema21": round(ema21, 2),
            "ema50": round(ema50, 2) if ema50 else None,
            "ema200": round(ema200, 2) if ema200 else None,
            "slope_50": slope_50,
        }
    except Exception:
        return {}


def scan_ticker(ticker):
    """Scan one ticker. Returns dict or None."""
    try:
        t = yf.Ticker(ticker)
        h = t.history(period="2d", interval="15m")
        info = t.info

        if h.empty:
            return None

        price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not price or price > 100:
            return None

        si = (info.get('shortPercentOfFloat', 0) or 0) * 100
        sr = info.get('shortRatio', 0) or 0

        today = h[h.index.date == datetime.now().date()]
        if today.empty:
            return None

        today_open = today['Open'].iloc[0]
        prev_close = h['Close'].iloc[0]
        current = today['Close'].iloc[-1]
        gap_pct = ((today_open - prev_close) / prev_close) * 100
        high = today['High'].max()

        today_vol = today['Volume'].sum()
        avg_vol = today_vol / len(today) if len(today) > 0 else 1
        vol_ratio = today_vol / avg_vol if avg_vol > 0 else 1

        closes_14 = h["Close"].values
        if len(closes_14) < 14:
            rsi = 50.0
        else:
            deltas = np.diff(closes_14)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            ag = np.mean(gains[-14:])
            al = np.mean(losses[-14:])
            rs = ag / al if al > 0 else 100
            rsi = 100 - (100 / (1 + rs))

        h52 = float(np.max(h['High'].values))
        l52 = float(np.min(h['Low'].values))
        pos_52w = (current - l52) / (h52 - l52) * 100 if h52 != l52 else 50

        if gap_pct > 0:
            gap_total = today_open - prev_close
            gap_filled = max(0, today_open - current)
            gap_filled_pct = min(100, round((gap_filled / gap_total) * 100, 1)) if gap_total > 0 else 0
        elif gap_pct < 0:
            gap_total = prev_close - today_open
            gap_filled = max(0, current - today_open)
            gap_filled_pct = min(100, round((gap_filled / gap_total) * 100, 1)) if gap_total > 0 else 0
        else:
            gap_filled_pct = 0

        result = {
            "ticker": ticker,
            "price": round(current, 2),
            "open": round(today_open, 2),
            "prev_close": round(prev_close, 2),
            "gap_pct": round(gap_pct, 2),
            "gap_filled_pct": gap_filled_pct,
            "rsi": round(rsi, 1),
            "si": round(si, 2),
            "short_ratio": round(sr, 2),
            "vol_ratio": round(vol_ratio, 2),
            "52w_pct": round(pos_52w, 1),
            "high_today": round(high, 2),
            "market_cap": info.get('marketCap', 0),
            "sector": info.get('sector', ''),
            "name": info.get('shortName', ticker),
            "score": 0,
        }

        # Add MA signals
        ma_data = _get_ma_data(ticker, current)
        result.update(ma_data)
        return result

    except Exception:
        return None

#!/usr/bin/env python3
"""
$SIGBOTTI Options Scanner
Stocks under $50 | Calls & Puts | Technical + Flow Analysis
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# ─── CONFIG ───────────────────────────────────────────────────────────────────
MAX_PRICE = 50
MIN_PRICE = 1
MIN_VOLUME = 2_000_000  # 2M average volume
MIN_MARKET_CAP = 50_000_000  # $50M floor to filter out nano-caps
RSI_OVERSOLD = 45  # Relaxed: was 40
RSI_OVERBOUGHT = 55  # Relaxed: was 60
SIGNAL_THRESHOLD = 2  # Relaxed: was 3 (min score to trigger signal)
SCAN_UNIVERSE_SIZE = 100  # How many tickers to scan
# ────────────────────────────────────────────────────────────────────────────────

# Popular stocks under $50 (universe seed)
UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",  # Mega-cap (will filter by price)
    "AMD", "INTC", "NFLX", "PLTR", "COIN",     # Tech/Crypto
    "SNAP", "META", "PYPL", "SQ",               # Internet
    "DIS", "CMCSA", "T", "VZ",                  # Media/Telecom
    "JNJ", "PFE", "ABBV", "MRNA", "LLY",       # Healthcare/Biotech
    "XOM", "CVX", "COP", "SLB", "OXY",         # Energy
    "WMT", "TGT", "COST", "HD", "LOW",          # Retail
    "JPM", "BAC", "WFC", "GS", "MS",            # Banks
    "F", "GM", "TM", "RIVN", "LCID",           # Auto/EV
    "SPOT", "SQSP", "DOCU", "ROKU", "SNOW",    # Growth Tech
    "SOFI", "UPST", "COIN", "MSTR", "HOOD",    # Fintech
    "NKE", "U", "ABNB", "MAR", "HLT",          # Consumer/Travel
    "BABA", "PDD", "JD", "NTES",               # China/ADR
    "TNA", "SOXL", "TECL", "EDZ", "WEAT",     # 3x ETFs (risky)
    "AAL", "DAL", "UAL", "LUV", "SAVE",        # Airlines
    "RCL", "NCLH", "CCL", "VICI", "WYNN",      # Cruise/Casino/REITs
    "GILD", "BMY", "MRK", "CVS", "CI",         # Big Pharma
    "ENPH", "SEDG", "FSLR", "RUN", "NEE",     # Solar/Green
    "DKNG", "PENN", "MGM", "WYNN", "CZR",     # Gaming
    "BB", "NOK", "TMUS", "DISH",             # Turnaround plays
    "AMC", "GME", "BBBYQ", "KOSS",            # Meme stocks
]


def get_technicals(ticker_symbol):
    """Fetch data and compute technical indicators"""
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        # Skip if no price data
        if info.get('currentPrice') is None or info['currentPrice'] > MAX_PRICE:
            return None
        if info.get('currentPrice') < MIN_PRICE:
            return None
            
        current_price = info.get('currentPrice', 0)
        volume = info.get('averageVolume', 0)
        market_cap = info.get('marketCap', 0)
        
        # Filter by volume
        if volume < MIN_VOLUME:
            return None
            
        # Skip low market cap
        if market_cap < MIN_MARKET_CAP:
            return None
        
        # Get historical data for indicators
        hist = ticker.history(period="3mo")
        if len(hist) < 60:
            return None
        
        close = hist['Close']
        high = hist['High']
        low = hist['Low']
        vol = hist['Volume']
        
        # RSI (14-day)
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        rsi_current = rsi.iloc[-1]
        
        # MACD (12, 26, 9)
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        macd_hist = macd_line - signal_line
        macd_current = macd_hist.iloc[-1]
        macd_prev = macd_hist.iloc[-3]  # 3 days ago
        
        # Moving Averages
        sma20 = close.rolling(20).mean().iloc[-1]
        sma50 = close.rolling(50).mean().iloc[-1]
        sma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None
        
        # Price vs MAs
        above_sma20 = close.iloc[-1] > sma20
        above_sma50 = close.iloc[-1] > sma50
        
        # Support/Resistance (20-day)
        resistance = high.rolling(20).max().iloc[-1]
        support = low.rolling(20).min().iloc[-1]
        range_pct = (resistance - support) / support * 100
        
        # Distance from support/resistance
        dist_from_support = (close.iloc[-1] - support) / support * 100
        dist_from_resistance = (resistance - close.iloc[-1]) / resistance * 100
        
        # 52-week context
        high_52w = high.rolling(252).max().iloc[-1]
        low_52w = low.rolling(252).min().iloc[-1]
        price_vs_52w_high = (close.iloc[-1] - high_52w) / high_52w * 100
        price_vs_52w_low = (close.iloc[-1] - low_52w) / low_52w * 100
        
        # Recent momentum (5-day return)
        mom_5d = (close.iloc[-1] / close.iloc[-6] - 1) * 100 if len(close) > 5 else 0
        mom_20d = (close.iloc[-1] / close.iloc[-21] - 1) * 100 if len(close) > 20 else 0
        
        # Options data (if available)
        options_available = False
        put_volume = 0
        call_volume = 0
        put_oi = 0
        call_oi = 0
        
        try:
            opt = ticker.option_chain()
            if opt is not None:
                options_available = True
                puts = opt.puts
                calls = opt.calls
                if len(puts) > 0:
                    put_volume = puts['volume'].sum()
                    put_oi = puts['openInterest'].sum()
                if len(calls) > 0:
                    call_volume = calls['volume'].sum()
                    call_oi = calls['openInterest'].sum()
        except:
            pass
        
        return {
            'symbol': ticker_symbol,
            'price': current_price,
            'volume': volume,
            'market_cap': market_cap,
            'rsi': rsi_current,
            'macd': macd_current,
            'macd_cross': macd_prev < 0 < macd_current,  # Bullish MACD cross
            'above_sma20': above_sma20,
            'above_sma50': above_sma50,
            'sma20': sma20,
            'sma50': sma50,
            'resistance': resistance,
            'support': support,
            'range_pct': range_pct,
            'dist_from_support': dist_from_support,
            'dist_from_resistance': dist_from_resistance,
            'high_52w': high_52w,
            'low_52w': low_52w,
            'price_vs_52w_high': price_vs_52w_high,
            'price_vs_52w_low': price_vs_52w_low,
            'momentum_5d': mom_5d,
            'momentum_20d': mom_20d,
            'options_available': options_available,
            'put_volume': put_volume,
            'call_volume': call_volume,
            'put_oi': put_oi,
            'call_oi': call_oi,
        }
    except Exception as e:
        return None


def generate_signal(data):
    """Generate call/put signal based on technicals"""
    if data is None:
        return None
    if 'symbol' not in data:
        return None
    
    signals = []
    reasons = []
    
    price = data['price']
    rsi = data['rsi']
    macd = data['macd']
    macd_cross = data['macd_cross']
    
    # ─── BULLISH / CALL SIGNALS ───────────────────────────────────────────────
    call_score = 0
    
    # RSI oversold → potential bounce
    if rsi < RSI_OVERSOLD:
        call_score += 2
        reasons.append(f"RSI oversold ({rsi:.0f})")
    elif rsi < 45:
        call_score += 1
        reasons.append(f"RSI neutral-low ({rsi:.0f})")
    
    # MACD bullish cross
    if macd_cross:
        call_score += 2
        reasons.append("MACD bullish cross")
    elif macd > 0:
        call_score += 1
        reasons.append("MACD positive")
    
    # Price near 52-week low (potential breakout setup)
    if data['price_vs_52w_low'] < 10:
        call_score += 1
        reasons.append(f"Near 52W low ({data['price_vs_52w_low']:.0f}%)")
    
    # Strong momentum
    if data['momentum_5d'] > 5:
        call_score += 1
        reasons.append(f"Strong 5D momentum ({data['momentum_5d']:.1f}%)")
    
    # Above key MAs
    if data['above_sma20'] and data['above_sma50']:
        call_score += 1
        reasons.append("Above SMA20 & SMA50")
    
    # Heavy call buying (options flow)
    if data['options_available'] and data['call_volume'] > data['put_volume'] * 1.5:
        call_score += 2
        reasons.append(f"Call volume dominant ({data['call_volume']:,} vs {data['put_volume']:,})")
    
    # ─── BEARISH / PUT SIGNALS ───────────────────────────────────────────────
    put_score = 0
    
    # RSI overbought → potential pullback
    if rsi > RSI_OVERBOUGHT:
        put_score += 2
        reasons.append(f"RSI overbought ({rsi:.0f})")
    elif rsi > 55:
        put_score += 1
        reasons.append(f"RSI neutral-high ({rsi:.0f})")
    
    # MACD negative and getting more negative
    if macd < 0:
        put_score += 1
        reasons.append("MACD negative")
    
    # Price near 52-week high (potential reversal)
    if data['price_vs_52w_high'] > -5:
        put_score += 1
        reasons.append(f"Near 52W high ({data['price_vs_52w_high']:.0f}%)")
    
    # Negative momentum
    if data['momentum_5d'] < -5:
        put_score += 1
        reasons.append(f"Weak 5D momentum ({data['momentum_5d']:.1f}%)")
    
    # Below key MAs
    if not data['above_sma20'] and not data['above_sma50']:
        put_score += 1
        reasons.append("Below SMA20 & SMA50")
    
    # Heavy put buying (smart money hedging)
    if data['options_available'] and data['put_volume'] > data['call_volume'] * 1.5:
        put_score += 2
        reasons.append(f"Put volume dominant ({data['put_volume']:,} vs {data['call_volume']:,})")
    
    # Determine signal
    signal = None
    direction = None
    confidence = 0
    
    if call_score >= SIGNAL_THRESHOLD and call_score > put_score:
        signal = "📈 CALL"
        direction = "call"
        confidence = min(call_score, 5)
    elif put_score >= SIGNAL_THRESHOLD and put_score > call_score:
        signal = "📉 PUT"
        direction = "put"
        confidence = min(put_score, 5)
    
    if signal:
        return {
            'signal': signal,
            'direction': direction,
            'confidence': confidence,
            'reasons': reasons,
            'call_score': call_score,
            'put_score': put_score,
            'price': data['price'],
            'rsi': data['rsi'],
            'macd': data['macd'],
            'momentum_5d': data['momentum_5d'],
            'volume': data['volume'],
            'resistance': data['resistance'],
            'support': data['support'],
            'range_pct': data['range_pct'],
            'price_vs_52w_low': data['price_vs_52w_low'],
            'price_vs_52w_high': data['price_vs_52w_high'],
            'options': data['options_available'],
        }
    
    return None


def format_for_discord(result):
    """Format scan result as plain text (Discord webhook compatible)"""
    try:
        sig = result.get('signal', 'UNKNOWN')
        conf = "⭐" * result.get('confidence', 0)
        
        emoji = "🟢" if result.get('direction') == 'call' else "🔴"
        
        reasons = result.get('reasons', [])
        reasons_text = " | ".join(reasons) if reasons else "Mixed signals"
        
        # Confidence bar
        conf_val = result.get('confidence', 0)
        conf_bar = "▰" * conf_val + "▱" * (5 - conf_val)
        
        msg = f"""{emoji} **{sig}** {conf}
**{result.get('symbol', '???')}** @ ${result.get('price', 0):.2f}
> Confidence: {conf_bar} ({conf_val}/5)
> RSI: {result.get('rsi', 0):.0f} | MACD: {result.get('macd', 0):.4f}
> 5D Momentum: {result.get('momentum_5d', 0):+.1f}%
> 52W: {result.get('price_vs_52w_low', 0):.0f}% from low / {result.get('price_vs_52w_high', 0):.0f}% from high
> Support: ${result.get('support', 0):.2f} | Resistance: ${result.get('resistance', 0):.2f}
> Vol: {result.get('volume', 0)/1_000_000:.1f}M | Options: {'yes' if result.get('options') else 'no'}
> Why: {reasons_text}"""
        return msg
    except Exception as e:
        return f"FORMAT ERROR: {result} | {e}"


def main():
    print("🐺 $SIGBOTTI Options Scanner — Initializing...\n")
    print(f"Filters: Under ${MAX_PRICE} | Min Vol: {MIN_VOLUME/1e6:.0f}M | RSI oversold <{RSI_OVERSOLD} / overbought >{RSI_OVERBOUGHT}")
    print(f"Universe: {len(UNIVERSE)} stocks\n")
    
    results = []
    scanned = 0
    errors = []
    
    for ticker_symbol in UNIVERSE:
        scanned += 1
        print(f"[{scanned}/{len(UNIVERSE)}] Scanning {ticker_symbol}...", end="\r")
        
        try:
            data = get_technicals(ticker_symbol)
            if data and 'symbol' in data:
                signal = generate_signal(data)
                if signal and 'symbol' in signal:
                    signal['scanned_data'] = data
                    results.append(signal)
        except Exception as e:
            errors.append(f"{ticker_symbol}: {e}")
    
    if errors:
        print(f"\n⚠️ Errors scanning {len(errors)} tickers: {errors[:5]}")
    
    print(f"\n\n✅ Scanned {scanned} stocks | {len(results)} signals generated\n")
    print("━" * 50)
    
    if not results:
        print("No signals triggered today. Market may be in neutral phase.")
        print("Try adjusting RSI thresholds or wait for clearer setups.")
        return
    
    # Sort: calls first then puts
    calls = sorted([r for r in results if r['direction'] == 'call'], 
                   key=lambda x: x['confidence'], reverse=True)
    puts = sorted([r for r in results if r['direction'] == 'put'],
                  key=lambda x: x['confidence'], reverse=True)
    
    print(f"\n\n📈 CALLS ({len(calls)} signals):\n")
    for i, r in enumerate(calls, 1):
        print(f"[{i}] " + "=" * 40)
        print(format_for_discord(r))
        print()
    
    print(f"\n📉 PUTS ({len(puts)} signals):\n")
    for i, r in enumerate(puts, 1):
        print(f"[{i}] " + "=" * 40)
        print(format_for_discord(r))
        print()
    
    # Summary table
    print("\n📋 QUICK SUMMARY:\n")
    print(f"{'Symbol':<8} {'Price':>7} {'Dir':<5} {'Conf':>5} {'RSI':>5} {'5D Mom':>8}")
    print("-" * 45)
    for r in results:
        d = "CALL" if r['direction'] == 'call' else "PUT"
        print(f"{r['symbol']:<8} ${r['price']:>6.2f} {d:<5} {r['confidence']:>5} {r['rsi']:>5.0f} {r['momentum_5d']:>+8.1f}%")
    
    print(f"\n🐺 Scanned {scanned} stocks | {len(results)} signals | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("⚠️  Not financial advice. Do your own DD before trading.")


if __name__ == "__main__":
    main()

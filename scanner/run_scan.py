#!/usr/bin/env python3
import yfinance as yf
import numpy as np
import json
import time

UNIVERSE = ['SNAP', 'PYPL', 'CMCSA', 'T', 'VZ', 'PFE', 'MRNA', 'SLB', 'BAC', 'F', 'RIVN', 'LCID', 'DOCU', 'SOFI', 'UPST', 'NKE', 'U', 'JD', 'AAL', 'LUV', 'NCLH', 'CCL', 'VICI', 'ENPH', 'SEDG', 'RUN', 'DKNG', 'PENN', 'MGM', 'CZR', 'BB', 'NOK', 'AMC', 'GME']

def get_vix_context():
    """Get VIX level and market direction context"""
    try:
        vix = yf.Ticker('^VIX')
        hist = vix.history(period='5d')
        if len(hist) >= 2:
            current = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[-2])
            change = (current / prev - 1) * 100
            mom5d = float((hist['Close'].iloc[-1] / hist['Close'].iloc[-6] - 1) * 100) if len(hist) > 5 else 0
            
            # Determine environment
            if current < 15:
                env = "🟢 LOW FEAR — Bullish environment (calls favored)"
                vix_conf_call = True
                vix_conf_put = False
            elif current < 20:
                env = "🟡 MODERATE — Mixed signals"
                vix_conf_call = True
                vix_conf_put = True
            elif current < 25:
                env = "🟠 ELEVATED — Some fear present (neutral)"
                vix_conf_call = False
                vix_conf_put = True
            elif current < 35:
                env = "🔴 HIGH FEAR — Bearish environment (puts favored)"
                vix_conf_call = False
                vix_conf_put = True
            else:
                env = "⚫ PANIC — Extreme fear (puts favored)"
                vix_conf_call = False
                vix_conf_put = True
            
            return {
                'vix': current,
                'change': change,
                'mom5d': mom5d,
                'env': env,
                'conf_call': vix_conf_call,
                'conf_put': vix_conf_put
            }
    except:
        pass
    return None

results = []
vix_data = get_vix_context()
vix_conf = {'call': vix_data['conf_call'], 'put': vix_data['conf_put']} if vix_data else {'call': False, 'put': False}
print(f"VIX Context: {vix_data['env'] if vix_data else 'N/A'}")
print()

for i, sym in enumerate(UNIVERSE):
    time.sleep(1.0)
    try:
        t = yf.Ticker(sym)
        info = t.info
        price = info.get('currentPrice', 0)
        vol = info.get('averageVolume', 0)
        mktcap = info.get('marketCap', 0)
        
        if not price or price > 50 or price < 1:
            continue
        if vol < 2_000_000 or mktcap < 50_000_000:
            continue
        
        hist = t.history(period='3mo')
        if len(hist) < 60:
            continue
        
        close = hist['Close']
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        macd_hist = macd_line - signal_line
        macd_current = macd_hist.iloc[-1]
        macd_prev = macd_hist.iloc[-3]
        macd_cross = bool(macd_prev < 0 < macd_current)
        
        sma20 = close.rolling(20).mean().iloc[-1]
        sma50 = close.rolling(50).mean().iloc[-1]
        above20 = bool(close.iloc[-1] > sma20)
        above50 = bool(close.iloc[-1] > sma50)
        
        mom5d = float((close.iloc[-1] / close.iloc[-6] - 1) * 100) if len(close) > 5 else 0.0
        
        call_score = 0
        put_score = 0
        reasons_c = []
        reasons_p = []
        
        if rsi < 45: call_score += 2; reasons_c.append(f'RSI {rsi:.0f}<45')
        if rsi > 55: put_score += 2; reasons_p.append(f'RSI {rsi:.0f}>55')
        if macd_cross: call_score += 2; reasons_c.append('MACDcross')
        elif macd_current > 0: call_score += 1
        if macd_current < 0: put_score += 1
        if mom5d > 5: call_score += 1; reasons_c.append(f'+5D:{mom5d:.1f}%')
        if mom5d < -5: put_score += 1; reasons_p.append(f'-5D:{mom5d:.1f}%')
        if above20 and above50: call_score += 1
        if not above20 and not above50: put_score += 1
        
        if call_score >= 2 and call_score > put_score:
            vix_confirmed = vix_conf['call']
            results.append({'symbol': sym, 'price': float(price), 'signal': 'CALL', 'direction': 'call', 'confidence': call_score, 'rsi': float(rsi), 'macd': float(macd_current), 'mom5d': mom5d, 'reasons': reasons_c, 'vix_confirmed': vix_confirmed})
        elif put_score >= 2 and put_score > call_score:
            vix_confirmed = vix_conf['put']
            results.append({'symbol': sym, 'price': float(price), 'signal': 'PUT', 'direction': 'put', 'confidence': put_score, 'rsi': float(rsi), 'macd': float(macd_current), 'mom5d': mom5d, 'reasons': reasons_p, 'vix_confirmed': vix_confirmed})
    except Exception as e:
        pass
    print(f"[{i+1}/{len(UNIVERSE)}] {sym} -> {len(results)} signals so far", end='\r', flush=True)

results.sort(key=lambda x: x['confidence'], reverse=True)

# VIX header
vix_str = f"VIX: {vix_data['vix']:.2f} ({vix_data['change']:+.1f}% today)"
if vix_data:
    print(f"\n{'='*50}")
    print(f"🐺 MARKET CONTEXT: {vix_data['env']}")
    print(f"   {vix_str} | 5D: {vix_data['mom5d']:+.1f}%")
    print(f"{'='*50}")

print(f"\n=== SCAN COMPLETE: {len(results)} signals ===\n")
for r in results:
    reasons = ' | '.join(r.get('reasons', []))
    vix_mark = " ✅ VIX CONFIRMED" if r.get('vix_confirmed') else " ⚠️ VIX UNCONFIRMED"
    conf_stars = "⭐" * r['confidence']
    print(f"  {r['symbol']:8} {r['signal']:4} {conf_stars} conf={r['confidence']} RSI={r['rsi']:5.1f} MACD={r['macd']:+.4f} 5D={r['mom5d']:+7.1f}%{vix_mark}")
    print(f"          Why: {reasons}")
    print()

with open('/Users/sigbotti/.openclaw/workspace/scanner/latest_signals.json', 'w') as f:
    json.dump(results, f, indent=2)
print("Saved to latest_signals.json")

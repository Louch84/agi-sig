import sys
sys.path.insert(0, '/Users/sigbotti/.openclaw/workspace/scanner')
import json, time
from news_scanner import analyze_gap_fill, analyze_short_squeeze
from run_scan import get_vix_context

with open('/Users/sigbotti/.openclaw/workspace/scanner/news_universe.json') as f:
    tickers = json.load(f)

tickers = list(dict.fromkeys(tickers))  # Remove duplicates

vix_data = get_vix_context()
print(f"VIX: {vix_data['vix']:.2f} | {vix_data['env']}")

gap_plays = []
squeeze_plays = []

for i, sym in enumerate(tickers):
    time.sleep(0.8)
    try:
        g = analyze_gap_fill(sym, None)
        if g and g.get('gap_fill_score', 0) >= 5:
            gap_plays.append(g)
            print(f"[{i+1}/{len(tickers)}] GAP: {sym} score={g['gap_fill_score']}")
    except Exception as e:
        print(f"[{i+1}/{len(tickers)}] GAP ERROR {sym}: {e}")
    
    time.sleep(0.8)
    try:
        s = analyze_short_squeeze(sym, None)
        if s and s.get('squeeze_score', 0) >= 6:
            squeeze_plays.append(s)
            print(f"[{i+1}/{len(tickers)}] SQZ: {sym} score={s['squeeze_score']}")
    except Exception as e:
        print(f"[{i+1}/{len(tickers)}] SQZ ERROR {sym}: {e}")

gap_plays.sort(key=lambda x: x['gap_fill_score'], reverse=True)
squeeze_plays.sort(key=lambda x: x['squeeze_score'], reverse=True)

print(f"\n=== GAP FILL ({len(gap_plays)} plays) ===")
for p in gap_plays[:8]:
    print(f"  {p['symbol']:6} gap={p['gap_pct']:+.1f}% score={p['gap_fill_score']}/10")

print(f"\n=== SHORT SQUEEZE ({len(squeeze_plays)} plays) ===")
for p in squeeze_plays[:8]:
    print(f"  {p['symbol']:6} SI={p['short_pct_float']:.1f}% score={p['squeeze_score']}/14")

combined = {
    'gap_plays': gap_plays[:8],
    'squeeze_plays': squeeze_plays[:8],
    'vix': vix_data,
    'tickers_scanned': len(tickers)
}
with open('/Users/sigbotti/.openclaw/workspace/scanner/news_scan_results.json', 'w') as f:
    json.dump(combined, f, default=str, indent=2)
print(f"\nSaved to news_scan_results.json")

#!/bin/bash
# Gap Alert Scanner — runs every 15 min during market hours
# Alert threshold: gap >5% + SI >5% + score >50

cd /Users/sigbotti/.openclaw/workspace

RESULT=$(python3 scripts/gap-alert-scanner.py --quiet 2>/dev/null)
ALERTS=$(echo "$RESULT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
alerts = data.get('alerts', [])
print(f'ALERTS:{len(alerts)}')
for a in alerts:
    print(f'{a[\"ticker\"]}|{a[\"gap_pct\"]}|{a[\"si\"]}|{a[\"price\"]}|{a[\"score\"]}')
")

ALERT_COUNT=$(echo "$ALERTS" | grep -c "ALERTS" || echo "ALERTS:0")

if [ "$ALERT_COUNT" != "ALERTS:0" ]; then
    echo "🚨 GAP ALERT — $(date)"
    echo "$ALERTS" | grep -v "^ALERTS" | while IFS='|' read -r ticker gap si price score; do
        echo "@Lou — $ticker gapped ${gap}% with ${si}% SI at \$$price | score ${score}/100"
    done
fi

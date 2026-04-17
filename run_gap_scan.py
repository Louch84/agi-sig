#!/usr/bin/env python3
import subprocess
import json
import sys

# Run scanner
subprocess.run([sys.executable, "scripts/gap-alert-scanner.py"])

# Load and filter alerts
with open("data/gap-alerts.json") as f:
    d = json.load(f)

alerts = [a for a in d.get("results", []) if a.get("score", 0) >= 60]
print(f"FLOUD: {len(alerts)} hot alerts")
for a in alerts[:5]:
    print(f'{a["ticker"]} gap {a["gap_pct"]:+.1f}% SI {a["si"]:.1f}% price ${a["price"]} score {a["score"]}/100')

# Check alert state
try:
    with open("data/gap-alert-state.json") as f:
        state = json.load(f)
    sent = len(state.get("alerts_today", []))
    print(f"ALERT_SENT: {'YES' if sent > 0 else 'NO'}")
except:
    print("ALERT_SENT: NO")

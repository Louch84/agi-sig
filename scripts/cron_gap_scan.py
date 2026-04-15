#!/usr/bin/env python3
import json, subprocess, sys

subprocess.run(["python3", "scripts/gap-alert-scanner.py"])

with open("data/gap-alerts.json") as f:
    d = json.load(f)

alerts = [a for a in d.get("results", []) if a.get("score", 0) >= 60]
print(f"FLOUD: {len(alerts)} hot alerts")
for a in alerts[:5]:
    print(f'{a["ticker"]} gap {a["gap_pct"]:+.1f}% SI {a["si"]:.1f}% price ${a["price"]} score {a["score"]}/100')

try:
    with open("data/gap-alert-state.json") as f:
        state = json.load(f)
    if state.get("alerts_today"):
        print(f"ALERT_SENT: YES ({len(state['alerts_today'])} sent)")
except:
    pass

#!/usr/bin/env python3
"""Post scanner results to Discord webhook"""
import json, sys, os, urllib.request, urllib.parse, datetime

DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"  # Replace with actual webhook

def post_to_discord(signals, webhook_url):
    if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print("No Discord webhook set. Skipping Discord notification.")
        print(json.dumps(signals, indent=2))
        return
    
    calls = [s for s in signals if s.get('direction') == 'call']
    puts = [s for s in signals if s.get('direction') == 'put']
    
    # Sort by confidence
    calls.sort(key=lambda x: x.get('confidence', 0), reverse=True)
    puts.sort(key=lambda x: x.get('confidence', 0), reverse=True)
    
    # Build Discord embed
    fields = []
    
    # Calls section
    if calls:
        calls_text = "\n".join([
            f"**{s['symbol']}** @ ${s.get('price', 0):.2f} | ⭐{'⭐' * s.get('confidence', 0)} | RSI: {s.get('rsi', 0):.0f} | 5D: {s.get('momentum_5d', 0):+.1f}%"
            for s in calls[:5]
        ])
        fields.append({"name": "📈 CALLS", "value": calls_text, "inline": False})
    
    # Puts section
    if puts:
        puts_text = "\n".join([
            f"**{s['symbol']}** @ ${s.get('price', 0):.2f} | ⭐{'⭐' * s.get('confidence', 0)} | RSI: {s.get('rsi', 0):.0f} | 5D: {s.get('momentum_5d', 0):+.1f}%"
            for s in puts[:5]
        ])
        fields.append({"name": "📉 PUTS", "value": puts_text, "inline": False})
    
    embed = {
        "title": "🐺 $SIGBOTTI Options Scanner — Monday Morning Plays",
        "description": f"Scanned 100+ stocks | Filter: under $50 | Based on Friday close",
        "color": 0x00FF00,  # Green
        "fields": fields,
        "footer": {"text": "Not financial advice. Do your own DD."},
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    
    payload = json.dumps({"embeds": [embed]}).encode('utf-8')
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"Discord notification sent! Response: {resp.status}")
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

if __name__ == "__main__":
    try:
        with open('/Users/sigbotti/.openclaw/workspace/scanner/latest_signals.json') as f:
            signals = json.load(f)
        
        webhook_url = os.environ.get('DISCORD_WEBHOOK', '')
        post_to_discord(signals, webhook_url)
    except FileNotFoundError:
        print("No signals file found. Run scanner first.")
    except Exception as e:
        print(f"Error: {e}")

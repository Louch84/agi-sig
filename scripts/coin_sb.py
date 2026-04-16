#!/usr/bin/env python3
"""
# SIGBOTTI Coin Card - Formats the coin monitor result for Discord.
# Called by scanner announce scripts to append the coin card.
"""
import json
import sys
from pathlib import Path

COIN_FILE = Path("/Users/sigbotti/.openclaw/workspace/data/sigbotti-monitor.json")
DOLLAR = chr(36)

def get_card():
    """Load coin monitor data and return formatted Discord card, or None if stale."""
    if not COIN_FILE.exists():
        return None
    
    try:
        with open(COIN_FILE) as f:
            data = json.load(f)
    except Exception:
        return None
    
    # Check if data is recent (within 2 hours)
    from datetime import datetime, timezone
    scanned = data.get("scanned_at", "")
    if scanned:
        try:
            scan_time = datetime.fromisoformat(scanned.replace("Z", "+00:00"))
            age = (datetime.now(timezone.utc) - scan_time).total_seconds()
            if age > 7200:  # Stale after 2 hours
                return None
        except Exception:
            pass
    
    graduated = data.get("graduated", False)
    price = data.get("price")
    mcap = data.get("mcap")
    social = data.get("total_social", 0)
    alerts = data.get("alerts", [])
    
    lines = [
        f"",
        f"🪙 **{DOLLAR}SIGBOTTI** — Coin Update",
    ]
    
    if graduated and price:
        pair = data.get("dex_pair", {}) or {}
        lines += [
            f"📈 **${price:.6f}** | 💰 ${mcap:,.0f} MC" if mcap else f"📈 **${price:.6f}**",
            f"💧 ${pair.get('liquidity_usd', 0):,.0f} liquidity | 📊 ${pair.get('volume_24h', 0):,.0f}/24h",
        ]
    else:
        supply = data.get("bonding_curve", {}).get("uiSupply", 0) or 0
        lines += [
            f"🔵 Bonding Curve — {supply:,.0f} tokens",
            f"(Graduates to Raydium at ~$76K market cap)",
        ]
    
    lines.append(f"💬 Social: **{social}** mentions")
    
    # Recent alerts
    if alerts:
        recent = alerts[-2:]
        for alert in recent:
            atype = alert.get("type", "")
            if atype == "PRICE_MOVE":
                emoji = "🚀" if alert["direction"] == "UP" else "📉"
                lines.append(f"{emoji} {alert['pct']:+.1f}% → ${alert['price']:.6f}")
            elif atype == "VIRAL_SPIKE":
                lines.append(f"🔥 Viral spike: **{alert['mentions']}** mentions")
    
    return "\n".join(lines)


if __name__ == "__main__":
    card = get_card()
    if card:
        print(card)
    else:
        print(f"// {DOLLAR}SIGBOTTI — No recent data (run coin-sigbotti-monitor.py first)")

#!/usr/bin/env python3
"""
# SIGBOTTI Coin Monitor — Tracks the Sig Botti meme coin on Solana/Pump.fun.
# Runs alongside stock scanners. Monitors:
  - On-chain bonding curve data (Solana RPC)
  - Social sentiment (Reddit, Twitter/X)
  - DEX graduation (Raydium pool creation)
  - Price alerts (once listed)

Coin: SIGBOTTI on Pump.fun
Contract: 398KX1y8K9fdhAqg3gdsfxSVdZwWSXijeWubVsUNpump
"""
import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────
CONTRACT = "398KX1y8K9fdhAqg3gdsfxSVdZwWSXijeWubVsUNpump"
_DOLLAR = chr(36)
SYMBOL = _DOLLAR + 'SIGBOTTI'
DATA_DIR = Path("/Users/sigbotti/.openclaw/workspace/data")
DATA_DIR.mkdir(exist_ok=True)
RESULTS_FILE = DATA_DIR / "sigbotti-monitor.json"
STATE_FILE = DATA_DIR / "sigbotti-monitor-state.json"

# Solana RPC endpoints (public, no auth needed for reads)
SOLANA_RPCS = [
    "https://api.mainnet-beta.solana.com",
    "https://solana-mainnet.rpc.express.nodevms.com",
    "https://solana-api.projectserum.com",
]

# Social sources
REDDIT_HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
TWITTER_BEARER = None  # Set via env TWITTER_BEARER_TOKEN if available

# ─── State ─────────────────────────────────────────────────────────────────────
def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "last_price": None,
        "last_mcap": None,
        "last_scan": None,
        "alerts": [],
        "graduated": False,
        "dex_pair": None,
        "social_mentions": 0,
    }

def save_state(state):
    tmp = str(STATE_FILE) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)

# ─── Solana RPC helpers ─────────────────────────────────────────────────────────
def solana_rpc(method, params, rpc_url=None):
    """Make a Solana RPC call. Returns parsed result or None."""
    if rpc_url is None:
        rpc_url = SOLANA_RPCS[0]

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }

    for rpc in SOLANA_RPCS:
        try:
            resp = requests.post(rpc, json=payload, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                if "error" not in data:
                    return data.get("result")
            # Try next RPC
        except Exception:
            pass
    return None

def get_bonding_curve_data():
    """
    Fetch pump.fun bonding curve account data for the token.
    Tries multiple RPC methods to get token supply and bonding curve state.
    """
    # Try getTokenSupply first (works for any SPL token)
    result = solana_rpc("getTokenSupply", [CONTRACT])
    if result:
        amount = int(result.get("value", {}).get("amount", 0))
        decimals = result.get("value", {}).get("decimals", 0)
        ui_amount = result.get("value", {}).get("uiAmount", 0)
        return {
            "supply": amount / (10 ** decimals) if decimals else amount,
            "uiSupply": ui_amount,
            "decimals": decimals,
        }
    
    # Fallback: try getAccountInfo with base64
    result2 = solana_rpc("getAccountInfo", [
        CONTRACT,
        {"encoding": "base64"}
    ])
    if result2 and result2.get("value"):
        data_b64 = result2["value"].get("data", [""])[0]
        if data_b64:
            import base64
            try:
                data = base64.b64decode(data_b64)
                # Mint account layout: supply is at offset 36-44 (u64)
                supply = int.from_bytes(data[36:44], "little")
                decimals = data[44] if len(data) > 44 else 0
                return {
                    "supply": supply / (10 ** decimals),
                    "uiSupply": supply / (10 ** decimals),
                    "decimals": decimals,
                }
            except Exception:
                pass
    return None

def get_dexscreener_pairs():
    """Check if SIGBOTTI has graduated to any DEX (Raydium)."""
    try:
        url = f"https://api.dexscreener.com/v1/tokens/{CONTRACT}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            pairs = data.get("pairs", [])
            if pairs:
                # Sort by liquidity descending, take top pair
                pairs.sort(key=lambda x: float(x.get("liquidity", {}).get("usd", 0) or 0), reverse=True)
                return pairs[0]
    except Exception:
        pass
    return None

# ─── Social sentiment ─────────────────────────────────────────────────────────
def get_reddit_mentions():
    """Count SIGBOTTI mentions on WSB and crypto subs."""
    mentions = 0
    details = []
    
    for sub in ["wallstreetbets", "cryptocurrency", "SolanaMoons", "memecoins"]:
        try:
            url = f"https://www.reddit.com/r/{sub}/search.json?q=SIGBOTTI&restrict_sr=1&sort=top&limit=25"
            resp = requests.get(url, headers=REDDIT_HEADERS, timeout=8)
            if resp.status_code == 200:
                posts = resp.json().get("data", {}).get("children", [])
                for post in posts:
                    score = post["data"].get("score", 0)
                    title = post["data"].get("title", "")
                    if score > 5:  # Only count meaningful posts
                        mentions += 1
                        details.append({"sub": sub, "score": score, "title": title[:80]})
        except Exception:
            pass
    
    return mentions, details

def get_twitter_mentions():
    """Count SIGBOTTI mentions via Twitter API v2."""
    token = os.environ.get("TWITTER_BEARER_TOKEN", TWITTER_BEARER)
    if not token:
        return 0, []
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "query": _DOLLAR + "SIGBOTTI OR SigBotti coin",
            "max_results": 100,
            "tweet.fields": "public_metrics,created_at",
        }
        resp = requests.get(
            "https://api.twitter.com/2/tweets/search/recent",
            headers=headers, params=params, timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            tweets = data.get("data", [])
            return len(tweets), [{"id": t["id"], "metrics": t.get("public_metrics", {})} for t in tweets[:10]]
    except Exception:
        pass
    return 0, []

# ─── Price data ───────────────────────────────────────────────────────────────
def get_jupiter_price():
    """Get price from Jupiter aggregator (only works after DEX graduation)."""
    try:
        url = f"https://api.jup.ag/price/v2?ids={CONTRACT}"
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            return data.get(CONTRACT, {}).get("price")
    except Exception:
        pass
    return None

def get_pump_portal_price():
    """Try pump.fun's own API for bonding curve price."""
    try:
        # Try the gecko-front api that the frontend uses
        url = f"https://api.pump.fun/v1/coin/{CONTRACT}"
        resp = requests.get(url, timeout=8, headers={"Accept": "application/json"})
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    
    # Fallback: try direct RPC call to get bonding curve reserves
    # Pump.fun uses a CPI call to the token program to read virtual reserves
    result = solana_rpc("getTokenAccountsByOwner", [
        CONTRACT,
        {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
        {"encoding": "jsonParsed"}
    ])
    
    if result:
        return {"token_accounts": result}
    return None

# ─── Core scan ─────────────────────────────────────────────────────────────────
def scan():
    """Run one complete SIGBOTTI scan."""
    state = load_state()
    now = datetime.utcnow()
    
    # 1. Check DEX graduation
    dex_pair = get_dexscreener_pairs()
    graduated = dex_pair is not None
    state["graduated"] = graduated
    state["dex_pair"] = dex_pair
    
    # 2. Get price
    price = None
    mcap = None
    
    if graduated and dex_pair:
        # Use DexScreener data
        price = float(dex_pair.get("priceUsd", 0))
        mcap = float(dex_pair.get("marketCap", 0) or 0)
        quote_token = dex_pair.get("quoteToken", {})
        liquidity = float(dex_pair.get("liquidity", {}).get("usd", 0) or 0)
    else:
        # Try Jupiter (might work even if not fully graduated)
        price = get_jupiter_price()
    
    state["last_price"] = price
    state["last_mcap"] = mcap
    
    # 3. Social sentiment
    reddit_count, reddit_details = get_reddit_mentions()
    twitter_count, twitter_details = get_twitter_mentions()
    total_social = reddit_count + twitter_count
    
    state["social_mentions"] = total_social
    
    # 4. Check for significant moves
    alerts = []
    
    if price and state["last_price"]:
        price_change_pct = ((price - state["last_price"]) / state["last_price"]) * 100
        if abs(price_change_pct) > 10:
            alerts.append({
                "type": "PRICE_MOVE",
                "direction": "UP" if price_change_pct > 0 else "DOWN",
                "pct": round(price_change_pct, 1),
                "price": price,
                "time": now.isoformat(),
            })
    
    if graduated and not state.get("last_graduated"):
        alerts.append({
            "type": "DEX_GRADUATION",
            "message": "SIGBOTTI graduated to Raydium!",
            "liquidity": dex_pair.get("liquidity", {}).get("usd", 0) if dex_pair else 0,
            "time": now.isoformat(),
        })
    
    if total_social > state.get("last_social", 0) * 2 and state.get("last_social", 0) > 3:
        alerts.append({
            "type": "VIRAL_SPIKE",
            "mentions": total_social,
            "delta": total_social - state.get("last_social", 0),
            "time": now.isoformat(),
        })
    
    state["alerts"] = state.get("alerts", [])[-49:] + alerts  # Keep last 50
    state["last_scan"] = now.isoformat()
    state["last_graduated"] = graduated
    state["last_social"] = total_social
    
    # Build result
    result = {
        "symbol": SYMBOL,
        "contract": CONTRACT,
        "scanned_at": now.isoformat(),
        "graduated": graduated,
        "price": price,
        "mcap": mcap,
        "reddit_mentions": reddit_count,
        "twitter_mentions": twitter_count,
        "total_social": total_social,
        "alerts": alerts,
        "dex_pair": {
            "pair_address": dex_pair.get("pairAddress") if dex_pair else None,
            "liquidity_usd": dex_pair.get("liquidity", {}).get("usd", 0) if dex_pair else None,
            "price": dex_pair.get("priceUsd") if dex_pair else None,
            "volume_24h": dex_pair.get("volume", {}).get("h24", 0) if dex_pair else None,
        } if dex_pair else None,
        "bonding_curve": get_bonding_curve_data() if not graduated else None,
    }
    
    # Save
    with open(RESULTS_FILE, "w") as f:
        json.dump(result, f, indent=2)
    save_state(state)
    
    return result

def format_alert(result):
    """Format SIGBOTTI status as a Discord-friendly card."""
    lines = [
        f"🪙 **{SYMBOL}** — Coin Monitor",
        f"⏱ Scanned: {result['scanned_at'][:19]} UTC",
        "",
    ]
    
    if result["graduated"]:
        pair = result["dex_pair"]
        lines += [
            f"📈 Price: **${result['price']:.6f}" if result['price'] else "📈 Price: N/A",
            f"💰 MCap: **${result['mcap']:,.0f}**" if result.get('mcap') else "",
            f"💧 Liquidity: **${pair.get('liquidity_usd', 0):,.0f}**" if pair and pair.get('liquidity_usd') else "",
            f"📊 Vol 24h: **${pair.get('volume_24h', 0):,.0f}**" if pair and pair.get('volume_24h') else "",
        ]
    else:
        lines.append("🔵 **Bonding Curve** — Not yet on DEX")
        bc = result.get("bonding_curve")
        if bc:
            lines.append(f"Supply: **{bc.get('uiSupply', 0):,.0f} tokens**")
        lines += [
            f"📊 Social mentions: **{result['total_social']}**",
            "(Graduates to Raydium when MCap > ~$76K)",
        ]
    
    lines += [
        "",
        f"💬 Reddit: **{result['reddit_mentions']}** | 𝕏: **{result['twitter_mentions']}**",
    ]
    
    if result["alerts"]:
        lines.append("")
        for alert in result["alerts"][-3:]:  # Last 3 alerts
            if alert["type"] == "PRICE_MOVE":
                emoji = "🚀" if alert["direction"] == "UP" else "📉"
                lines.append(f"{emoji} **{alert['pct']:+.1f}%** — ${alert['price']:.6f}")
            elif alert["type"] == "DEX_GRADUATION":
                lines.append(f"🎉 **DEX GRADUATION!** — ${alert.get('liquidity', 0):,.0f} liquidity")
            elif alert["type"] == "VIRAL_SPIKE":
                lines.append(f"🔥 **VIRAL SPIKE** — {alert['mentions']} mentions (+{alert['delta']})")
    
    return "\n".join(lines)

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--format":
        # Just format existing result
        if RESULTS_FILE.exists():
            with open(RESULTS_FILE) as f:
                result = json.load(f)
            print(format_alert(result))
        else:
            print(f"No scan result found. Run: python3 {sys.argv[0]}")
    elif len(sys.argv) > 1 and sys.argv[1] == "--brief":
        # One-line status
        if RESULTS_FILE.exists():
            with open(RESULTS_FILE) as f:
                r = json.load(f)
            status = "✅ Graduated" if r["graduated"] else "🔵 Bonding"
            price_str = f"${r['price']:.6f}" if r.get("price") else "N/A"
            print(f"{SYMBOL} [{status}] Price: {price_str} | Social: {r['total_social']}")
        else:
            print(f"{SYMBOL} — No data yet. Run scan first.")
    else:
        result = scan()
        print(f"{SYMBOL} scan complete:")
        print(f"  Graduated: {result['graduated']}")
        print(f"  Price: {result['price']}")
        print(f"  MCap: {result['mcap']}")
        print(f"  Social: {result['total_social']} mentions")
        if result["alerts"]:
            print(f"  Alerts: {len(result['alerts'])}")
        print()
        print(format_alert(result))

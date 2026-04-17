#!/usr/bin/env python3
"""
Scanner Dashboard — Unified view across ALL scanners.
Aggregates: gap-alerts, fast-scan, earnings-power, options-stock-bridge, 
            unusual-options, social-options-bridge, squeeze-scanner, coil-scanner.
Ranks tickers by COMPOSITE score (highest number of scanners confirming the signal).

Lou's IOVA case: would show:
  - gap-alert: score 95
  - fast-scan: total_score 100  
  - options-bridge: score 93
  = 3 scanners confirming = HIGH conviction
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("/Users/sigbotti/.openclaw/workspace/data")

# Scanner output files + field names
SCANNERS = {
    "gap-alert": {
        "file": "gap-alerts.json",
        "score_field": "score",
        "ticker_field": "ticker",
        "signal_fields": ["gap_pct", "si", "rsi", "short_ratio", "52w_pct"],
        "alerts_key": "alerts",
        "results_key": "results",
        "tag": "📈 GAP",
        "threshold": 50,
    },
    "fast-scan": {
        "file": "fast-scan.json",
        "score_field": "total_score",
        "ticker_field": "ticker",
        "signal_fields": ["si", "io_pct", "days_to_earnings", "coil_score", "momentum_score", "si_score"],
        "alerts_key": None,
        "results_key": "results",
        "tag": "⚡ FAST",
        "threshold": 60,
    },
    "earnings-power": {
        "file": "earnings-power.json",
        "score_field": "score",
        "ticker_field": "ticker",
        "signal_fields": ["days_to_earnings", "si", "short_ratio", "inst_pct", "exp_move"],
        "alerts_key": None,
        "results_key": "results",
        "tag": "📅 ER",
        "threshold": 40,
    },
    "options-bridge": {
        "file": "options-stock-bridge.json",
        "score_field": "score",
        "ticker_field": "ticker",
        "signal_fields": ["short_ratio", "si", "borrow_fee", "vol", "oi"],
        "alerts_key": None,
        "results_key": "results",
        "tag": "🐋 OPTIONS",
        "threshold": 50,
    },
    "squeeze": {
        "file": "squeeze-scanner.json",
        "score_field": "score",
        "ticker_field": "ticker",
        "signal_fields": ["si", "short_ratio", "vol_ratio", "rsi", "days_to_cover"],
        "alerts_key": None,
        "results_key": "results",
        "tag": "🔥 SQUEEZE",
        "threshold": 50,
    },
    "coil": {
        "file": "coil-scanner.json",
        "score_field": "score",
        "ticker_field": "ticker",
        "signal_fields": ["coil_score", "atr_ratio", "bb_width", "rsi", "si"],
        "alerts_key": None,
        "results_key": "results",
        "tag": "🔵 COIL",
        "threshold": 40,
    },
}


def load_scanner(name, config):
    """Load results from a scanner output file."""
    path = DATA_DIR / config["file"]
    if not path.exists():
        return []
    
    try:
        with open(path) as f:
            data = json.load(f)
        
        # Some files use 'alerts' key, some use 'results'
        key = config.get("alerts_key") or config.get("results_key")
        if key and key in data:
            return data[key]
        elif isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Try both keys
            for k in ["results", "alerts"]:
                if k in data:
                    return data[k]
    except Exception:
        pass
    
    return []


def aggregate():
    """Aggregate all scanner results into a unified ticker map."""
    ticker_map = {}  # ticker -> {scores: {}, signals: {}, sources: []}
    
    for name, config in SCANNERS.items():
        results = load_scanner(name, config)
        if not results:
            continue
        
        score_field = config["score_field"]
        ticker_field = config["ticker_field"]
        tag = config["tag"]
        threshold = config["threshold"]
        
        for row in results:
            ticker = row.get(ticker_field)
            if not ticker:
                continue
            
            score = row.get(score_field, 0)
            if score < threshold:
                continue
            
            if ticker not in ticker_map:
                ticker_map[ticker] = {
                    "scores": {},
                    "signals": {},
                    "sources": [],
                }
            
            ticker_map[ticker]["scores"][name] = score
            ticker_map[ticker]["sources"].append(tag)
            
            # Collect key signal fields
            for sig_field in config["signal_fields"]:
                val = row.get(sig_field)
                if val is not None:
                    if sig_field not in ticker_map[ticker]["signals"]:
                        ticker_map[ticker]["signals"][sig_field] = val
    
    return ticker_map


def composite_score(ticker_data):
    """Calculate composite conviction score."""
    scores = ticker_data["scores"]
    if not scores:
        return 0
    
    # Average of all scanner scores
    avg = sum(scores.values()) / len(scores)
    
    # Bonus for multiple scanners confirming the same ticker
    scanner_count = len(scores)
    multi_bonus = (scanner_count - 1) * 5  # +5 per additional confirming scanner
    
    return min(round(avg + multi_bonus, 1), 120)


def format_dashboard(ticker_map):
    """Format the unified dashboard for Discord."""
    lines = [
        f"📊 **UNIFIED SCANNER DASHBOARD** — {datetime.now().strftime('%H:%M %m/%d')}",
        f"   {len(ticker_map)} tickers firing across {len(SCANNERS)} scanner types\n",
    ]
    
    # Sort by composite score
    ranked = []
    for ticker, data in ticker_map.items():
        cs = composite_score(data)
        if cs > 0:
            ranked.append((ticker, cs, data))
    
    ranked.sort(key=lambda x: x[1], reverse=True)
    
    if not ranked:
        lines.append("No signals above threshold. Run scanners first.")
        return "\n".join(lines)
    
    # Top conviction: tickers with 2+ scanners confirming
    multi = [(t, cs, d) for t, cs, d in ranked if len(d["sources"]) >= 2]
    single = [(t, cs, d) for t, cs, d in ranked if len(d["sources"]) == 1]
    
    if multi:
        lines.append(f"🔥 **HIGH CONVICTION ({len(multi)} tickers — 2+ scanners confirming)**\n")
        for ticker, cs, data in multi[:10]:
            sources = " + ".join(data["sources"])
            s = data["signals"]
            
            si = s.get("si", 0) or 0
            rsi = s.get("rsi", 0) or 0
            gap = s.get("gap_pct", 0) or 0
            dtc = s.get("short_ratio", 0) or 0
            days_er = s.get("days_to_earnings", 999)
            io = s.get("io_pct", 0) or 0
            coil = s.get("coil_score", 0) or 0
            voi = s.get("oi", 0) or s.get("vol", 0) or 0
            
            tags = []
            if gap and abs(gap) > 3: tags.append(f"gap {gap:+.1f}%")
            if si and si > 20: tags.append(f"SI {si:.0f}%")
            if rsi and (rsi < 40 or rsi > 65): tags.append(f"RSI {rsi:.0f}")
            if dtc and dtc > 3: tags.append(f"DTC {dtc:.1f}")
            if days_er and days_er <= 14: tags.append(f"ER {days_er}d")
            if io and io < 30: tags.append(f"IO {io:.0f}%👶")
            if coil and coil >= 40: tags.append(f"COIL {coil}")
            if voi and voi > 500: tags.append(f"🐋 OI {voi:,}")
            
            tag_str = " | ".join(tags) if tags else ""
            
            lines.append(
                f"  **{ticker}** [{sources}] — CS **{cs}/100**\n"
                f"     {tag_str}"
            )
            lines.append("")
    
    if single:
        lines.append(f"⚡ **SINGLE SCANNER HITS ({len(single)} tickers)**\n")
        for ticker, cs, data in single[:8]:
            sources = " + ".join(data["sources"])
            s = data["signals"]
            si = s.get("si", 0) or 0
            gap = s.get("gap_pct", 0) or 0
            
            tags = []
            if gap and abs(gap) > 3: tags.append(f"gap {gap:+.1f}%")
            if si and si > 20: tags.append(f"SI {si:.0f}%")
            
            lines.append(
                f"  **{ticker}** [{sources}] — CS **{cs}/100**"
                + (f" | {' | '.join(tags)}" if tags else "")
            )
    
    return "\n".join(lines)


def main():
    print("📊 Building unified scanner dashboard...\n")
    
    ticker_map = aggregate()
    
    if not ticker_map:
        print("⚠️ No scanner data found. Run scanners first:")
        print("  python3 scripts/gap-alert-scanner.py")
        print("  python3 scripts/fast-scan.py")
        print("  python3 scripts/unusual-options-scanner.py && python3 scripts/options-stock-bridge.py")
        return
    
    output = format_dashboard(ticker_map)
    print(output)
    
    # Save to file
    out_path = DATA_DIR / "scanner-dashboard.json"
    ranked = sorted(
        [
            (t, composite_score(d), d)
            for t, d in ticker_map.items()
        ],
        key=lambda x: x[1], reverse=True
    )
    
    with open(out_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "ranked": [
                {"ticker": t, "composite_score": cs, "sources": d["sources"], "signals": d["signals"]}
                for t, cs, d in ranked
            ],
        }, f, indent=2)
    
    print(f"\n💾 Saved to {out_path}")


if __name__ == "__main__":
    main()

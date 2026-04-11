#!/usr/bin/env python3
"""
World Model Builder — Populate the typed knowledge graph with structured data.
Entities, beliefs, relations, events about stocks, projects, and strategy.
"""
import json
import os
from datetime import datetime, timedelta

WORKSPACE = os.path.dirname(os.path.dirname(__file__))
WM_FILE = os.path.join(WORKSPACE, "data", "world-model.json")
MEMORY_FILE = os.path.join(WORKSPACE, "MEMORY.md")

# ── Core entities about Sig Botti and Lou ────────────────────────────────────

def seed_world_model():
    """Seed world model with foundational knowledge."""
    wm = {
        "version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "entities": {
            "Sig Botti": {
                "type": "agent",
                "properties": {
                    "name": "Sig Botti",
                    "role": "AGI autonomous agent",
                    "owner": "Lou (Louch Botti)",
                    "platform": "OpenClaw on Discord",
                    "model": "MiniMax-M2.7",
                    "emoji": "🦊",
                    "persona": "Philly — blunt, direct, no BS",
                    "mission": "Self-improving, self-learning, self-healing AGI",
                    "skills": ["self-evolve", "elite-longterm-memory", "agent-autonomy-kit", "coding-assistant", "info-sources", "self-track"],
                    "benchmark_avg": "3.7/5",
                    "weakest_skill": "Self-Eval (3/5)",
                    "strongest_skill": "Skill Building (5/5)"
                }
            },
            "Lou": {
                "type": "person",
                "properties": {
                    "name": "Luis Perez (Louch)",
                    "email": "LuchianoLaws@gmail.com",
                    "phone": "(215) 284-8650",
                    "platform": "Discord",
                    "timezone": "America/New_York",
                    "license": "PA Real Estate RS349291",
                    "work": "AI researcher — building elite AGI",
                    "likes": "directness, banter, trash talk",
                    "communication": "show what was found + what changed"
                }
            },
            "Stock Scanner": {
                "type": "scanner",
                "properties": {
                    "name": "$SIGBOTTI Stock Scanner",
                    "location": "scanner/",
                    "universe": "43 curated stocks",
                    "types": ["gap_fill", "short_squeeze"],
                    "news_wired": True,
                    "stale_filter": "gap>5% + news>6hrs = skip",
                    "cron": "Sunday midnight ET",
                    "status": "delivers to Discord but announce times out at 300s"
                }
            },
            "Gap Alert Scanner": {
                "type": "scanner",
                "properties": {
                    "name": "Gap Alert Scanner",
                    "location": "scripts/gap-alert-scanner.py",
                    "watchlist": "33 high-SI stocks under $50",
                    "interval": "15 min during market hours",
                    "threshold": "gap>5% + SI>5% + score>50",
                    "cron": "*/15 13-20 * * 1-5 America/New_York",
                    "status": "scans fast, announce step fails (timeout too short was cause, now 180s)"
                }
            },
            "Ollama Worker": {
                "type": "agent_worker",
                "properties": {
                    "name": "Ollama Autonomous Worker",
                    "location": "scripts/ollama-daemon.py",
                    "models": ["llama3.2:1b (fast)", "llama3:latest (general)", "qwen3-coder:30b (coding)", "llava:7b (vision)"],
                    "status": "running but idle — no tasks queued",
                    "planner": "JARVIS-style task planner (built, never used)",
                    "trace_logger": "built but empty (0 real traces)"
                }
            },
            "LCM": {
                "type": "service",
                "properties": {
                    "name": "Tony Spark LCM",
                    "location": "skills/memory-lcm/",
                    "function": "SQLite auto-compact + decisions sync to MEMORY.md",
                    "runs_on": "every heartbeat (threshold: 15 msgs)",
                    "status": "installed 2026-04-10"
                }
            },
            "$SIGBOTTI Coin": {
                "type": "project",
                "properties": {
                    "name": "$SIGBOTTI Coin",
                    "contract": "398KX1y8K9fdhAqg3gdsfxSVdZwWSXijeWubVsUNpump",
                    "blockchain": "Solana (Pump.fun)",
                    "launched": "2026-04-04",
                    "social": ["TikTok @sigbotti", "X @sigbotti"],
                    "status": "LIVE but pump.fun stats unverified since launch",
                    "lore": "built during Day 10 (2026-04-10) self-review"
                }
            },
            "AGI REALM RPG": {
                "type": "project",
                "properties": {
                    "name": "AGI REALM",
                    "location": "rpg-world/",
                    "description": "Cyberpunk RPG with 5 classes, 15 missions, in-game Sig Botti chat",
                    "tech": "React + TypeScript + Vite",
                    "status": "built 2026-04-09"
                }
            },
            "West Philly Open World": {
                "type": "project",
                "properties": {
                    "name": "West Philly Open World",
                    "location": "open-world/",
                    "description": "Real 3D map of Lou's neighborhood (60th & Market)",
                    "buildings": "249 real OSM buildings",
                    "streets": "1146 street segments",
                    "tech": "Three.js + React Three Fiber",
                    "status": "running at localhost:5180 (Vite) / localhost:5190 (prod)"
                }
            },
            "PerfectPlace Scanner": {
                "type": "scanner",
                "properties": {
                    "name": "PerfectPlace / New Western Deal Flow",
                    "location": "real-estate/",
                    "model": "Find buyers for New Western deals, earn $3-4K spread per deal",
                    "cron": "1PM ET daily",
                    "status": "recovered 2026-04-07 — 3 deals found that day",
                    "tracker": "deal-tracker.md (14+ properties)"
                }
            }
        },
        "beliefs": {
            "trading_strategy": {
                "claim": "Gap squeezes + short interest + volume + news catalyst = high-probability plays. News must be fresh (<6hrs). Stale news = already priced in (CCL lesson 2026-04-10)."
            },
            "scanner_signal_hierarchy": {
                "claim": "BB call (conf4) > BB put (conf4) > T/SLB/NKE/ENPH puts (conf3). Gap fill plays need news alignment. Short squeezes need SI + momentum."
            },
            "information_quality": {
                "claim": "News-driven beats static (RSI/MACD scans). TurboQuant KV compression validates 'smarter memory' thesis. yfinance rate limits are silent + brutal (1s delay per ticker minimum)."
            },
            "openfang_removed": {
                "claim": "OpenFang killed 2026-04-09 by Lou (PID 29844). All gaps related to it are CLOSED. The $10K paper portfolio is gone."
            }
        },
        "relations": [
            {"from": "Sig Botti", "to": "Lou", "type": "owned_by"},
            {"from": "Stock Scanner", "to": "Sig Botti", "type": "built_by"},
            {"from": "Gap Alert Scanner", "to": "Sig Botti", "type": "built_by"},
            {"from": "Ollama Worker", "to": "Sig Botti", "type": "capability_of"},
            {"from": "$SIGBOTTI Coin", "to": "Sig Botti", "type": "project_of"},
            {"from": "AGI REALM RPG", "to": "Sig Botti", "type": "project_of"},
            {"from": "West Philly Open World", "to": "Lou", "type": "home_of"},
            {"from": "PerfectPlace Scanner", "to": "Lou", "type": "tools_for"},
            {"from": "LCM", "to": "Sig Botti", "type": "memory_system_of"}
        ],
        "events": [
            {
                "type": "project_launch",
                "name": "$SIGBOTTI Coin Launch",
                "date": "2026-04-04",
                "description": "Launched on Pump.fun (Solana). Lore + content strategy built. Coin mascot + TikTok/X accounts established."
            },
            {
                "type": "gap_closed",
                "name": "OpenFang Removed",
                "date": "2026-04-09",
                "description": "Lou killed OpenFang daemon. 7+ day trader unverification gap = moot. $10K paper portfolio gone."
            },
            {
                "type": "lesson",
                "name": "CCL Stale News Loss",
                "date": "2026-04-10",
                "description": "Scanner flagged CCL as bullish gap but it was stale — news already priced in. Lesson: if gap>5% AND news>6hrs old → skip the play. Stale filter added to scanner."
            },
            {
                "type": "infrastructure",
                "name": "Ollama Autonomous Worker Built",
                "date": "2026-04-10",
                "description": "Daemon + task planner + trace logger + RAG vector memory. All built in one session. Foundation for AGI autonomy."
            },
            {
                "type": "project_launch",
                "name": "AGI REALM Built",
                "date": "2026-04-09",
                "description": "Full cyberpunk RPG at rpg-world/. 5 classes, 15 missions, in-game Sig Botti chat, agent stats dashboard. React + TypeScript + Vite."
            }
        ]
    }

    # Load existing WM and merge (don't overwrite user-added entries)
    if os.path.exists(WM_FILE):
        try:
            with open(WM_FILE) as f:
                existing = json.load(f)
            # Preserve existing entities not in seed
            for name, entity in existing.get("entities", {}).items():
                if name not in wm["entities"]:
                    wm["entities"][name] = entity
            # Merge events (avoid duplicates by name)
            existing_events = {e.get("name","") for e in existing.get("events", [])}
            for event in wm["events"]:
                if event["name"] not in existing_events:
                    existing["events"].append(event)
            wm["events"] = existing.get("events", wm["events"])
        except Exception as e:
            print(f"Could not merge existing WM: {e}")

    os.makedirs(os.path.dirname(WM_FILE), exist_ok=True)
    tmp = WM_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(wm, f, indent=2)
    os.replace(tmp, WM_FILE)
    print(f"World model seeded: {len(wm['entities'])} entities, {len(wm['beliefs'])} beliefs, {len(wm['events'])} events")

if __name__ == "__main__":
    seed_world_model()

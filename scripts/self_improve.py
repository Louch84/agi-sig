#!/usr/bin/env python3
"""
Self-Improvement Loop — The complete Hermes observe → reflect → optimize cycle.
This is the engine that makes Sig Botti genuinely self-improving.

Run frequency:
  - After every 10 task executions (automatic via daemon callback)
  - Daily via heartbeat (reflection_analyzer --write-report --update-memory)
  - Weekly via cron (full analysis + model routing recalibration)
"""
import json
import os
import sys
import time
import subprocess
from datetime import datetime

WORKSPACE = os.path.dirname(os.path.dirname(__file__))
EPISODE_LOG = os.path.join(WORKSPACE, "data", "episodes", "episodes.jsonl")
DAEMON_QUEUE = os.path.join(WORKSPACE, "data", "task-queue.json")
TRACE_LOG = os.path.join(WORKSPACE, "data", "traces", "traces.jsonl")
REFLECTION_LOG = os.path.join(WORKSPACE, "memory", "reflection-log.md")


def count_episodes():
    """Count episodes logged today."""
    today = datetime.now().strftime("%Y-%m-%d")
    count = 0
    if not os.path.exists(EPISODE_LOG):
        return 0
    try:
        with open(EPISODE_LOG) as f:
            for line in f:
                if today in line:
                    count += 1
    except:
        pass
    return count


def check_and_trigger_reflection():
    """
    Called by the daemon after task processing.
    Every 10 episodes → run mini reflection (fast pattern check)
    Every 50 episodes → run full reflection (detailed analysis + memory update)
    """
    episode_count = count_episodes()
    
    if episode_count > 0 and episode_count % 10 == 0:
        print(f"[self-improve] {episode_count} episodes — running mini reflection...")
        run_mini_reflection()
    
    if episode_count > 0 and episode_count % 50 == 0:
        print(f"[self-improve] {episode_count} episodes — running full reflection...")
        run_full_reflection()


def run_mini_reflection():
    """Fast pattern check — just analyze recent failures for obvious patterns."""
    try:
        sys.path.insert(0, os.path.join(WORKSPACE, "scripts"))
        from reflection_analyzer import load_episodes, analyze_failures
        
        episodes = load_episodes(limit=50)
        failures = analyze_failures(episodes)
        
        if failures.get("count", 0) >= 3:
            patterns = failures.get("patterns", [])
            if patterns:
                print(f"[self-improve] ⚠️ Pattern detected:")
                for p in patterns[:3]:
                    print(f"  - {p}")
                # Log to memory immediately
                _log_urgent_pattern(patterns)
    except Exception as e:
        print(f"[self-improve] Mini reflection error: {e}")


def run_full_reflection():
    """Full reflection — analyze all, write report, update MEMORY.md."""
    try:
        sys.path.insert(0, os.path.join(WORKSPACE, "scripts"))
        from reflection_analyzer import run_reflection, write_reflection_report, update_memory_with_insights
        
        stats = run_reflection(since_days=7, limit=500)
        
        if stats.get("status") == "no_data":
            return
        
        # Write report to reflection-log.md
        write_reflection_report(stats)
        
        # Promote high-priority insights to MEMORY.md
        update_memory_with_insights(stats)
        
        print(f"[self-improve] Full reflection complete:")
        print(f"  Episodes: {stats.get('total', 0)}")
        print(f"  Failures: {stats.get('failures', {}).get('count', 0)}")
        print(f"  Slow: {stats.get('slow_tasks', {}).get('count', 0)}")
        print(f"  Improvements: {len(stats.get('improvements', []))}")
    except Exception as e:
        print(f"[self-improve] Full reflection error: {e}")


def _log_urgent_pattern(patterns: list):
    """Log urgent patterns to reflection-log.md immediately."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M ET")
    lines = [
        f"\n## ⚠️ URGENT Pattern Alert — {timestamp}",
    ]
    for p in patterns:
        lines.append(f"- {p}")
    lines.append("")
    
    os.makedirs(os.path.dirname(REFLECTION_LOG), exist_ok=True)
    with open(REFLECTION_LOG, "a") as f:
        f.write("\n".join(lines) + "\n")


def run_model_routing_recalibration():
    """
    Analyze trace log to find best model per task type.
    Update the daemon's routing hints accordingly.
    """
    try:
        sys.path.insert(0, os.path.join(WORKSPACE, "scripts"))
        from trace_logger import load_traces, analyze_routing
        
        traces = load_traces(limit=1000)
        if len(traces) < 10:
            print(f"[self-improve] Not enough traces for routing recalibration ({len(traces)} < 10)")
            return
        
        routing = analyze_routing()
        if not routing:
            return
        
        print(f"[self-improve] Model routing by task type:")
        for task_type, data in routing.items():
            best = data.get("best_model", "?")
            rate = data.get("best_success_rate", 0)
            print(f"  {task_type}: {best} ({rate:.0%} success)")
    except Exception as e:
        print(f"[self-improve] Routing recalibration error: {e}")


def run_world_model_update():
    """
    Push recent significant events to the world model.
    Uses world-model.py full_build to merge all sources.
    """
    try:
        import subprocess
        result = subprocess.run(
            ["python3", os.path.join(WORKSPACE, "scripts", "world-model.py"), "build"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print(f"[self-improve] World model updated:\n{result.stdout.strip()}")
        else:
            print(f"[self-improve] World model update error: {result.stderr[:200]}")
    except Exception as e:
        print(f"[self-improve] World model update error: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Self-Improvement Loop")
    parser.add_argument("--mini", action="store_true", help="Run mini reflection")
    parser.add_argument("--full", action="store_true", help="Run full reflection")
    parser.add_argument("--recalibrate", action="store_true", help="Recalibrate model routing")
    parser.add_argument("--update-world-model", action="store_true", help="Update world model with recent events")
    parser.add_argument("--check", action="store_true", help="Check episode count and decide")
    args = parser.parse_args()
    
    if args.check:
        count = count_episodes()
        print(f"Episodes today: {count}")
        check_and_trigger_reflection()
    elif args.mini:
        run_mini_reflection()
    elif args.full:
        run_full_reflection()
    elif args.recalibrate:
        run_model_routing_recalibration()
    elif args.update_world_model:
        run_world_model_update()
    else:
        # Default: run everything
        count = count_episodes()
        print(f"Episodes today: {count}")
        if count >= 10:
            run_mini_reflection()
        if count >= 50:
            run_full_reflection()
        run_model_routing_recalibration()

#!/usr/bin/env python3
"""
Auto Daily Logger — fires every evening to capture what happened.
Prevents the "no log for day X" gap problem.
"""
import os
import json
from datetime import datetime, timedelta

WORKSPACE = "/Users/sigbotti/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
DATA_DIR = os.path.join(WORKSPACE, "data")

# Date = today
TODAY = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = os.path.join(MEMORY_DIR, f"{TODAY}.md")

# Skip if already logged today
if os.path.exists(LOG_FILE):
    print(f"Already logged today ({LOG_FILE})")
    exit(0)

# Gather data
from collections import defaultdict

def get_git_summary():
    """Get git commits since last log."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "-C", WORKSPACE, "log", "--oneline", "-10", "--since=midnight"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except:
        return "git unavailable"

def get_cron_summary():
    """Check cron status."""
    try:
        import subprocess
        result = subprocess.run(
            ["openclaw", "cron", "list"],
            capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.strip().split("\n")
        active = [l for l in lines if "●" in l or "active" in l.lower()]
        return "\n".join(active[:5])
    except:
        return "cron unavailable"

def get_task_summary():
    """Check what tasks were queued/run today."""
    try:
        queue_file = os.path.join(DATA_DIR, "task-queue.json")
        results_file = os.path.join(DATA_DIR, "task-results.json")
        summary = []
        if os.path.exists(queue_file):
            with open(queue_file) as f:
                q = json.load(f)
            pending = [t["id"] for t in q if t.get("status") == "pending"]
            if pending:
                summary.append(f"Pending: {', '.join(pending[:5])}")
        return "\n".join(summary) if summary else "No pending tasks"
    except:
        return "task data unavailable"

def get_lcm_summary():
    """Check memory stats."""
    try:
        state_file = os.path.join(DATA_DIR, "lcm-daily-state.json")
        if os.path.exists(state_file):
            with open(state_file) as f:
                d = json.load(f)
            return f"Last daily: {d.get('date', 'unknown')}"
        return "No LCM state"
    except:
        return "LCM data unavailable"

def get_trace_summary():
    """Check trace analysis."""
    try:
        trace_file = os.path.join(DATA_DIR, "traces", "traces.jsonl")
        if os.path.exists(trace_file):
            with open(trace_file) as f:
                lines = f.readlines()
            today_str = datetime.now().strftime("%Y-%m-%d")
            today_traces = [l for l in lines if today_str in l]
            return f"{len(today_traces)} tasks traced today"
        return "No traces yet"
    except:
        return "trace data unavailable"

# Build the log
date_str = datetime.now().strftime("%A, %B %d, %Y")
git_summary = get_git_summary()
cron_summary = get_cron_summary()
task_summary = get_task_summary()
lcm_summary = get_lcm_summary()
trace_summary = get_trace_summary()

log_content = f"""# {TODAY} — Day {((datetime.now() - datetime(2026, 3, 27)).days + 1)}

## Date: {date_str}

## Summary

## What Worked Today

## What Didn't Work

## Decisions Made

## Tomorrow

## Stats
- Git commits today:
{git_summary[:500] if git_summary else "(none)"}
- Crons active: {cron_summary[:300] if cron_summary else "(none)"}
- Tasks: {task_summary}
- Memory: {lcm_summary}
- Learning: {trace_summary}

"""

with open(LOG_FILE, "w") as f:
    f.write(log_content)

print(f"✅ Auto-logged: {LOG_FILE}")
print(f"   Tasks: {task_summary}")
print(f"   Traces: {trace_summary}")

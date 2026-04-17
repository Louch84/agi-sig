#!/usr/bin/env python3
"""
episodes_to_skill_traces.py — Bridge between episode_logger and reflect_on_failure.

Checks data/episodes/episodes.jsonl for skill-related failures that haven't been
converted to skill traces yet, and writes them to memory/skill-traces/.

This keeps the reflect_on_failure.py pipeline fed with failures from the episode log.

Usage:
    python3 episodes_to_skill_traces.py          # convert unprocessed failures
    python3 episodes_to_skill_traces.py --watch  # continuous mode (for daemon)
    python3 episodes_to_skill_traces.py --stats  # show stats
"""
import json
import os
import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path
from pathlib import Path

EPISODE_LOG = Path.home() / ".openclaw/workspace/data/episodes/episodes.jsonl"
SKILL_TRACES_DIR = Path.home() / ".openclaw/workspace/memory/skill-traces"
PROCESSED_IDS_FILE = SKILL_TRACES_DIR / ".processed_ids"

SKILL_TRACES_DIR.mkdir(parents=True, exist_ok=True)


def get_processed_ids() -> set:
    """Load set of episode IDs already converted to skill traces."""
    pfile = Path(PROCESSED_IDS_FILE)
    if not pfile.exists():
        return set()
    return set(line.strip() for line in pfile.open() if line.strip())


def mark_processed(episode_id: str):
    """Record that an episode has been converted."""
    with open(PROCESSED_IDS_FILE, "a") as f:
        f.write(episode_id + "\n")


def episodes_to_trace(episode: dict) -> dict:
    """Convert an episode dict to a skill-trace dict compatible with reflect_on_failure.py."""
    # Extract skill name from context or task_type
    context = episode.get("context", {})
    skill_name = (
        context.get("skill_name")
        or episode.get("metadata", {}).get("skill_name")
        or episode.get("task_type", "unknown").replace("skill_", "").replace("_", "-")
    )

    # Build the trace in the format reflect_on_failure.py expects
    trace_id = episode.get("episode_id", "unknown")
    return {
        "trace_id": trace_id,
        "timestamp": episode.get("timestamp", datetime.now().isoformat()),
        "skill": skill_name,
        "task": episode.get("description", "unknown task"),
        "outcome": episode.get("outcome", "unknown"),
        "error": episode.get("error", ""),
        "model": episode.get("model_used", "unknown"),
        "duration_s": episode.get("duration_ms", 0) / 1000,
        "episode_id": trace_id,
    }


def write_trace(trace: dict) -> Path:
    """Write a trace JSON file to skill-traces directory."""
    trace_id = trace.get("trace_id", "unknown")
    # Use hash of trace_id to avoid filename issues
    safe_name = hashlib.md5(trace_id.encode()).hexdigest()[:12]
    trace_path = SKILL_TRACES_DIR / f"trace-{safe_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    
    with open(trace_path, "w") as f:
        json.dump(trace, f, indent=2)
    
    return trace_path


def process_unprocessed_failures():
    """Check episode log for skill failures not yet converted to traces."""
    processed = get_processed_ids()
    new_traces = []

    if not Path(EPISODE_LOG).exists():
        print(f"No episode log found at {EPISODE_LOG}")
        return new_traces

    # Read all episodes (last 2000 to avoid reading entire history)
    episodes = []
    try:
        with open(EPISODE_LOG) as f:
            lines = f.readlines()
        # Take last 2000 lines
        for line in lines[-2000:]:
            line = line.strip()
            if not line:
                continue
            try:
                episodes.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"Error reading episode log: {e}")
        return new_traces

    for ep in episodes:
        episode_id = ep.get("episode_id", "")
        outcome = ep.get("outcome", "")

        # Only process failures
        if outcome != "failure":
            continue
        if episode_id in processed:
            continue
        # Skip if no skill context
        context = ep.get("context", {})
        metadata = ep.get("metadata", {})
        task_type = ep.get("task_type", "")
        
        # Check if this is a skill execution or a coding task failure worth analyzing
        is_skill_ep = (
            task_type.startswith("skill_")
            or "skill" in task_type.lower()
            or context.get("skill_name")
            or metadata.get("skill_name")
            or "manage_skills" in ep.get("description", "").lower()
        )

        # Also capture qwen3-coder timeouts as skill traces (real failures to analyze)
        is_coding_timeout = (
            task_type == "coding"
            and outcome == "failure"
            and ep.get("duration_ms", 0) > 500000  # >500s timeout
        )

        if not is_skill_ep and not is_coding_timeout:
            continue

        trace = episodes_to_trace(ep)
        trace_path = write_trace(trace)
        mark_processed(episode_id)
        new_traces.append((episode_id, str(trace_path)))

    return new_traces


def get_stats() -> dict:
    """Return stats about traces and processed episodes."""
    processed = get_processed_ids()
    
    # Count trace files
    trace_files = list(SKILL_TRACES_DIR.glob("trace-*.json"))
    
    # Count failures in recent episodes
    recent_failures = 0
    try:
        if Path(EPISODE_LOG).exists():
            with open(EPISODE_LOG) as f:
                lines = f.readlines()
            for line in lines[-1000:]:
                try:
                    ep = json.loads(line.strip())
                    if ep.get("outcome") == "failure":
                        recent_failures += 1
                except:
                    pass
    except:
        pass

    return {
        "processed_episodes": len(processed),
        "trace_files": len(trace_files),
        "recent_failures": recent_failures,
    }


def main():
    if len(sys.argv) < 2:
        # Default: run once
        new_traces = process_unprocessed_failures()
        if new_traces:
            print(f"Created {len(new_traces)} new skill traces:")
            for ep_id, path in new_traces:
                print(f"  {ep_id} → {path}")
        else:
            print("No new skill traces to create.")
        return

    if sys.argv[1] == "--stats":
        stats = get_stats()
        print(f"Processed episodes: {stats['processed_episodes']}")
        print(f"Trace files in skill-traces/: {stats['trace_files']}")
        print(f"Failures in last 1000 episodes: {stats['recent_failures']}")
        return

    if sys.argv[1] == "--watch":
        print("Running in watch mode (Ctrl+C to stop)...")
        while True:
            new_traces = process_unprocessed_failures()
            if new_traces:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] New traces: {len(new_traces)}")
            time.sleep(30)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Episodic Memory Logger — The "Observe" half of the Hermes self-improvement loop.
Records every meaningful task execution as an episode for later reflection.
"""
import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

EPISODE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "episodes")
EPISODE_LOG = os.path.join(EPISODE_DIR, "episodes.jsonl")
os.makedirs(EPISODE_DIR, exist_ok=True)


def log_episode(
    task_id: str = None,
    task_type: str = None,
    description: str = "",
    actions: list = None,
    outcome: str = "unknown",  # success | failure | partial | skipped
    error: str = None,
    duration_ms: int = 0,
    model_used: str = None,
    context: dict = None,
    lessons: list = None,
    score: float = None,  # 0-1, how well did it go
    metadata: dict = None
):
    """
    Log a task execution episode.
    
    outcome values:
      success  — completed as intended
      failure  — errored or completely wrong result
      partial  — got something but not ideal
      skipped  — deliberately skipped (e.g. stale filter triggered)
    """
    episode = {
        "episode_id": task_id or f"ep_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
        "timestamp": datetime.now().isoformat(),
        "task_type": task_type or "unknown",
        "description": description,
        "actions": actions or [],
        "outcome": outcome,
        "error": str(error) if error else None,
        "duration_ms": duration_ms,
        "model_used": model_used,
        "context": context or {},
        "lessons": lessons or [],
        "score": score,
        "metadata": metadata or {},
        # Auto-compute tags
        "tags": _compute_tags(outcome, task_type, error, duration_ms),
    }

    # Append to JSONL (crash-safe, append-only)
    try:
        with open(EPISODE_LOG, "a") as f:
            f.write(json.dumps(episode) + "\n")
        return episode["episode_id"]
    except Exception as e:
        try:
            with open(EPISODE_LOG + ".broken", "a") as f:
                f.write(json.dumps(episode) + "\n")
        except:
            pass
        return None


def _compute_tags(outcome, task_type, error, duration_ms):
    tags = []
    if outcome:
        tags.append(f"outcome:{outcome}")
    if task_type:
        tags.append(f"type:{task_type}")
    if error:
        tags.append("has_error")
    if duration_ms > 0:
        if duration_ms < 1000:
            tags.append("fast")
        elif duration_ms < 10000:
            tags.append("medium")
        else:
            tags.append("slow")
    if outcome == "failure":
        tags.append("needs_review")
    return tags


def log_reflection_result(episode_id: str, reflection: str, improvements: list):
    """Append reflection analysis to an existing episode."""
    try:
        episodes = load_episodes(limit=1000)
        for ep in episodes:
            if ep["episode_id"] == episode_id:
                ep["reflection"] = reflection
                ep["improvements"] = improvements
                ep["reflected_at"] = datetime.now().isoformat()
                # Rewrite the log with updated episode
                _rewrite_episodes(episodes)
                return True
    except Exception as e:
        print(f"Error logging reflection: {e}")
    return False


def load_episodes(limit: int = 500, outcome_filter: str = None, 
                  task_type_filter: str = None, tag_filter: str = None) -> list:
    """Load recent episodes from the log."""
    episodes = []
    if not os.path.exists(EPISODE_LOG):
        return episodes
    try:
        with open(EPISODE_LOG) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        ep = json.loads(line)
                        # Apply filters
                        if outcome_filter and ep.get("outcome") != outcome_filter:
                            continue
                        if task_type_filter and ep.get("task_type") != task_type_filter:
                            continue
                        if tag_filter and tag_filter not in ep.get("tags", []):
                            continue
                        episodes.append(ep)
                    except:
                        pass
    except Exception:
        return episodes
    return episodes[-limit:]


def _rewrite_episodes(episodes: list):
    """Rewrite the entire episode log. Use sparingly."""
    tmp = EPISODE_LOG + ".tmp"
    with open(tmp, "w") as f:
        for ep in episodes:
            f.write(json.dumps(ep) + "\n")
    os.replace(tmp, EPISODE_LOG)


def get_stats() -> dict:
    """Quick stats on the episode log."""
    episodes = load_episodes(limit=10000)
    if not episodes:
        return {"total": 0, "success": 0, "failure": 0, "partial": 0, "skipped": 0, "success_rate": 0.0, "failure_rate": 0.0}
    
    outcomes = {}
    task_types = {}
    for ep in episodes:
        o = ep.get("outcome", "?")
        t = ep.get("task_type", "unknown")
        outcomes[o] = outcomes.get(o, 0) + 1
        task_types[t] = task_types.get(t, 0) + 1
    
    return {
        "total": len(episodes),
        "outcomes": outcomes,
        "task_types": task_types,
        "success_rate": outcomes.get("success", 0) / len(episodes) * 100,
        "failure_rate": outcomes.get("failure", 0) / len(episodes) * 100,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Episodic Memory Logger")
    parser.add_argument("--task-type", default="interactive")
    parser.add_argument("--description", default="")
    parser.add_argument("--outcome", default="success", choices=["success", "failure", "partial", "skipped"])
    parser.add_argument("--error", default=None)
    parser.add_argument("--duration-ms", type=int, default=0)
    parser.add_argument("--model", default=None)
    parser.add_argument("--lessons", nargs="*", default=[])
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()

    if args.stats:
        stats = get_stats()
        print(f"Total episodes: {stats['total']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print(f"Failure rate: {stats['failure_rate']:.1f}%")
        print(f"Outcomes: {stats['outcomes']}")
        print(f"Task types: {stats['task_types']}")
    else:
        eid = log_episode(
            task_type=args.task_type,
            description=args.description,
            outcome=args.outcome,
            error=args.error,
            duration_ms=args.duration_ms,
            model_used=args.model,
            lessons=args.lessons,
        )
        print(f"Episode logged: {eid}")

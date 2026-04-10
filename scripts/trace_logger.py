#!/usr/bin/env python3
"""
Trace Logger + Learning System — OpenJarvis-inspired.
Logs every task execution for feedback-driven routing improvements.
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path

TRACE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "traces")
TRACE_FILE = os.path.join(TRACE_DIR, "traces.jsonl")  # Append-only log

os.makedirs(TRACE_DIR, exist_ok=True)


def log_trace(task_id: str, model: str, task_type: str, prompt: str,
              response: str, duration_ms: int, success: bool,
              subtask_results: list = None, plan: dict = None,
              error: str = None):
    """Log a task execution trace for learning."""
    trace = {
        "task_id": task_id,
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "task_type": task_type,
        "prompt": prompt[:500],  # Truncate long prompts
        "prompt_len": len(prompt),
        "response_len": len(response) if response else 0,
        "duration_ms": duration_ms,
        "success": success,
        "error": error,
        "tokens_approx": (len(prompt) + len(response)) // 4,  # rough estimate
        "subtasks": subtask_results,
        "plan_summary": plan.get("summary") if plan else None,
    }

    # Append to JSONL file (append-only, crash-safe)
    try:
        with open(TRACE_FILE, "a") as f:
            f.write(json.dumps(trace) + "\n")
    except Exception as e:
        # Last resort: just append raw to a fallback file
        try:
            with open(TRACE_FILE + ".broken", "a") as f:
                f.write(json.dumps(trace) + "\n")
        except:
            pass


def load_traces(limit: int = 1000) -> list:
    """Load recent traces from the log."""
    traces = []
    if not os.path.exists(TRACE_FILE):
        return traces
    try:
        with open(TRACE_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        traces.append(json.loads(line))
                    except:
                        pass
    except Exception:
        return traces
    return traces[-limit:]


def analyze_routing() -> dict:
    """Analyze traces to find best model for each task type."""
    traces = load_traces(limit=500)
    if not traces:
        return {}

    stats = {}  # task_type -> {model -> {count, success_rate, avg_duration, avg_tokens}}

    for trace in traces:
        tt = trace.get("task_type", "unknown")
        model = trace.get("model", "unknown")
        success = trace.get("success", False)
        duration = trace.get("duration_ms", 0)
        tokens = trace.get("tokens_approx", 0)

        if tt not in stats:
            stats[tt] = {}
        if model not in stats[tt]:
            stats[tt][model] = {"count": 0, "successes": 0, "total_duration": 0, "total_tokens": 0}

        s = stats[tt][model]
        s["count"] += 1
        s["successes"] += 1 if success else 0
        s["total_duration"] += duration
        s["total_tokens"] += tokens

    # Compute averages and scores
    recommendations = {}
    for tt, models in stats.items():
        best_model = None
        best_score = -1
        for model, s in models.items():
            success_rate = s["successes"] / s["count"] if s["count"] > 0 else 0
            avg_duration = s["total_duration"] / s["count"] if s["count"] > 0 else 0
            # Score: 70% success rate, 30% speed (inverse normalized)
            score = success_rate * 0.7 + (1 / (avg_duration / 1000 + 1)) * 0.3
            if score > best_score:
                best_score = score
                best_model = model

        recommendations[tt] = {
            "recommended_model": best_model,
            "score": best_score,
            "models": {
                m: {
                    "count": s["count"],
                    "success_rate": round(s["successes"] / s["count"] * 100, 1) if s["count"] > 0 else 0,
                    "avg_duration_ms": round(s["total_duration"] / s["count"]) if s["count"] > 0 else 0,
                    "avg_tokens": round(s["total_tokens"] / s["count"]) if s["count"] > 0 else 0,
                }
                for m, s in models.items()
            }
        }

    return recommendations


def get_routing_hints() -> dict:
    """Get routing hints for the dispatcher — based on trace analysis."""
    recommendations = analyze_routing()
    hints = {}
    for tt, data in recommendations.items():
        hints[tt] = data["recommended_model"]
    return hints


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: trace_logger.py analyze|traces [limit]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "analyze":
        recs = analyze_routing()
        print("=== Routing Analysis ===")
        for tt, data in recs.items():
            print(f"\n[{tt}]")
            print(f"  Best: {data['recommended_model']} (score: {data['score']:.2f})")
            for m, s in data["models"].items():
                print(f"  {m}: {s['success_rate']}% success, {s['avg_duration_ms']}ms avg, {s['count']} tasks")
    elif cmd == "traces":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        traces = load_traces(limit)
        print(f"=== Last {len(traces)} traces ===")
        for t in traces[-limit:]:
            status = "✅" if t.get("success") else "❌"
            print(f"{status} [{t['task_type']}] {t['model']} | {t.get('duration_ms',0)}ms | {t.get('prompt','')[:50]}...")

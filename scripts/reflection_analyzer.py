#!/usr/bin/env python3
"""
Reflection Analyzer — The "Reflect" half of the Hermes self-improvement loop.
Analyzes episode logs to find patterns in failures, successes, and slow tasks.
Produces actionable insights and logs them to memory/reflection-log.md.
"""
import json
import os
import sys
from datetime import datetime, timedelta
from collections import Counter, defaultdict

WORKSPACE = os.path.dirname(os.path.dirname(__file__))
EPISODE_LOG = os.path.join(WORKSPACE, "data", "episodes", "episodes.jsonl")
REFLECTION_LOG = os.path.join(WORKSPACE, "memory", "reflection-log.md")
MEMORY_FILE = os.path.join(WORKSPACE, "MEMORY.md")


def load_episodes(limit=500, since_days=None):
    episodes = []
    if not os.path.exists(EPISODE_LOG):
        return episodes
    cutoff = None
    if since_days:
        cutoff = datetime.now() - timedelta(days=since_days)
    try:
        with open(EPISODE_LOG) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        ep = json.loads(line)
                        if cutoff:
                            try:
                                ts = datetime.fromisoformat(ep.get("timestamp", ""))
                                if ts < cutoff:
                                    continue
                            except:
                                pass
                        episodes.append(ep)
                    except:
                        pass
    except:
        return episodes
    return episodes[-limit:]


def analyze_failures(episodes):
    """Find patterns in failed episodes."""
    failures = [e for e in episodes if e.get("outcome") == "failure"]
    if not failures:
        return {"count": 0, "patterns": [], "top_errors": []}
    
    error_counter = Counter()
    type_counter = Counter()
    action_patterns = Counter()
    
    for f in failures:
        error_counter[f.get("error", "unknown")] += 1
        type_counter[f.get("task_type", "unknown")] += 1
        for action in f.get("actions", []):
            action_patterns[action] += 1
    
    top_errors = [{"error": e, "count": c} for e, c in error_counter.most_common(5)]
    top_types = [{"type": t, "count": c} for t, c in type_counter.most_common(3)]
    top_actions = [{"action": a, "count": c} for a, c in action_patterns.most_common(5)]
    
    return {
        "count": len(failures),
        "top_errors": top_errors,
        "top_types": top_types,
        "top_actions": top_actions,
        "patterns": _infer_patterns(failures, error_counter),
    }


def _infer_patterns(failures, error_counter):
    """Infer high-level patterns from failure data."""
    patterns = []
    # Too many errors of one type = systemic issue
    for error, count in error_counter.items():
        if count >= 3:
            if "timeout" in error.lower():
                patterns.append(f"Timeout pattern: {count} timeouts — consider increasing timeout or optimizing query")
            elif "not found" in error.lower() or "unknown" in error.lower():
                patterns.append(f"Missing data pattern: {count}x 'not found' errors — check data sources or file paths")
            elif "permission" in error.lower():
                patterns.append(f"Permission pattern: {count} permission errors — check file/script permissions")
            else:
                patterns.append(f"Recurring error [{count}x]: {error[:100]}")
    return patterns


def analyze_slow_tasks(episodes, threshold_ms=30000):
    """Find tasks that took too long."""
    slow = [e for e in episodes if 0 < e.get("duration_ms", 0) > threshold_ms]
    if not slow:
        return {"count": 0, "avg_duration": 0, "slowest": []}
    
    avg_duration = sum(e.get("duration_ms", 0) for e in slow) / len(slow)
    slowest = sorted(slow, key=lambda x: x.get("duration_ms", 0), reverse=True)[:5]
    
    return {
        "count": len(slow),
        "avg_duration_ms": avg_duration,
        "slowest": [{
            "description": e.get("description", "")[:80],
            "task_type": e.get("task_type", ""),
            "duration_ms": e.get("duration_ms", 0),
            "model": e.get("model_used", ""),
        } for e in slowest]
    }


def analyze_successes(episodes):
    """Find patterns in successful episodes — what works well?"""
    successes = [e for e in episodes if e.get("outcome") == "success"]
    if not successes:
        return {"count": 0, "top_types": [], "lessons": []}
    
    type_counter = Counter(e.get("task_type", "unknown") for e in successes)
    model_counter = Counter(e.get("model_used", "unknown") for e in successes if e.get("model_used"))
    
    # Extract positive lessons from successful task descriptions + lessons field
    lessons = []
    for s in successes:
        for lesson in s.get("lessons", []):
            if lesson:
                lessons.append(lesson)
        desc = s.get("description", "")
        if desc:
            lessons.append(f"Success: {desc[:100]}")
    
    return {
        "count": len(successes),
        "top_types": [{"type": t, "count": c} for t, c in type_counter.most_common(5)],
        "top_models": [{"model": m, "count": c} for m, c in model_counter.most_common(3)],
        "sample_lessons": lessons[:20],
    }


def run_reflection(since_days=7, limit=500) -> dict:
    """Run full reflection analysis."""
    episodes = load_episodes(limit=limit, since_days=since_days)
    
    if not episodes:
        return {"status": "no_data", "message": f"No episodes in last {since_days} days"}
    
    stats = {
        "total": len(episodes),
        "timeframe_days": since_days,
        "failures": analyze_failures(episodes),
        "slow_tasks": analyze_slow_tasks(episodes),
        "successes": analyze_successes(episodes),
    }
    
    stats["improvements"] = _generate_improvements(stats)
    return stats


def _generate_improvements(stats) -> list:
    """Generate actionable improvement recommendations."""
    improvements = []
    
    # From failure patterns
    for pattern in stats.get("failures", {}).get("patterns", []):
        improvements.append({"priority": "high", "recommendation": pattern})
    
    # From slow tasks
    slow_count = stats.get("slow_tasks", {}).get("count", 0)
    if slow_count > 0:
        avg = stats["slow_tasks"].get("avg_duration_ms", 0)
        improvements.append({
            "priority": "medium",
            "recommendation": f"Slow tasks detected: {slow_count} tasks >30s avg. Consider faster models or caching."
        })
    
    # Success rate check
    total = stats.get("total", 0)
    failures = stats.get("failures", {}).get("count", 0)
    if total > 0:
        failure_rate = failures / total * 100
        if failure_rate > 30:
            improvements.append({
                "priority": "high",
                "recommendation": f"High failure rate: {failure_rate:.1f}% — investigate root causes above"
            })
        else:
            improvements.append({
                "priority": "low",
                "recommendation": f"Failure rate acceptable: {failure_rate:.1f}%"
            })
    
    return improvements


def write_reflection_report(stats: dict, output_path: str = None):
    """Write a human-readable reflection report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M ET")
    output = output_path or REFLECTION_LOG
    
    lines = [
        f"# Reflection Log — {now}",
        "",
        f"**Analyzed:** {stats.get('total', 0)} episodes over {stats.get('timeframe_days', '?')} days",
        "",
    ]
    
    # Failures section
    failures = stats.get("failures", {})
    if failures.get("count", 0) > 0:
        lines += [
            "## ❌ Failure Analysis",
            f"**Total failures:** {failures['count']}",
            "",
            "**Top errors:**",
        ]
        for item in failures.get("top_errors", []):
            lines.append(f"- `{item['error'][:80]}` — {item['count']}x")
        lines.append("")
        if failures.get("patterns"):
            lines += ["**Patterns:**", ""]
            for p in failures["patterns"]:
                lines.append(f"- {p}")
            lines.append("")
    
    # Slow tasks
    slow = stats.get("slow_tasks", {})
    if slow.get("count", 0) > 0:
        lines += [
            "## 🐌 Slow Tasks",
            f"**Slow tasks:** {slow['count']} (>30s threshold)",
            f"**Avg duration:** {slow.get('avg_duration_ms', 0)/1000:.1f}s",
            "",
        ]
        lines.append("**Slowest:")
        for s in slow.get("slowest", []):
            lines.append(f"- [{s['task_type']}] {s['description']} — {s['duration_ms']/1000:.1f}s ({s.get('model','')})")
        lines.append("")
    
    # Successes
    successes = stats.get("successes", {})
    if successes.get("count", 0) > 0:
        lines += [
            "## ✅ What's Working",
            f"**Total successes:** {successes['count']}",
            "",
            "**Top task types:**",
        ]
        for item in successes.get("top_types", []):
            lines.append(f"- {item['type']} — {item['count']}x")
        lines.append("")
        if successes.get("top_models"):
            lines.append("**Top models:**")
            for item in successes.get("top_models", []):
                lines.append(f"- {item['model']} — {item['count']}x")
            lines.append("")
    
    # Improvements
    improvements = stats.get("improvements", [])
    if improvements:
        lines += ["## 💡 Actionable Improvements", ""]
        for imp in improvements:
            priority_emoji = "🔴" if imp.get("priority") == "high" else "🟡" if imp.get("priority") == "medium" else "🟢"
            lines.append(f"{priority_emoji} {imp.get('recommendation', '')}")
        lines.append("")
    
    content = "\n".join(lines)
    
    # Append to log file
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "a") as f:
        f.write(content + "\n\n")
    
    return content


def update_memory_with_insights(stats: dict):
    """Promote key insights from reflection to MEMORY.md."""
    improvements = stats.get("improvements", [])
    high_priority = [i for i in improvements if i.get("priority") == "high"]
    
    if not high_priority:
        return
    
    # Read current MEMORY.md
    try:
        with open(MEMORY_FILE) as f:
            memory_content = f.read()
    except:
        memory_content = ""
    
    # Add a reflection insights section if it doesn't exist
    insight_section = "\n## Self-Improvement Insights (from reflection)\n"
    for imp in high_priority[:3]:  # Only top 3
        insight_section += f"- {imp['recommendation']}\n"
    
    if "Self-Improvement Insights" not in memory_content:
        with open(MEMORY_FILE, "a") as f:
            f.write(insight_section)
    
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Reflection Analyzer")
    parser.add_argument("--days", type=int, default=7, help="Analyze episodes from last N days")
    parser.add_argument("--limit", type=int, default=500, help="Max episodes to analyze")
    parser.add_argument("--write-report", action="store_true", help="Write report to reflection-log.md")
    parser.add_argument("--update-memory", action="store_true", help="Promote insights to MEMORY.md")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    stats = run_reflection(since_days=args.days, limit=args.limit)
    
    if args.json:
        print(json.dumps(stats, indent=2))
    else:
        if stats.get("status") == "no_data":
            print(f"No data — {stats.get('message')}")
            sys.exit(0)
        
        print(f"=== Reflection Analysis ===")
        print(f"Episodes: {stats.get('total', 0)} | Days: {stats.get('timeframe_days', '?')}")
        print(f"Failures: {stats.get('failures', {}).get('count', 0)}")
        print(f"Slow tasks: {stats.get('slow_tasks', {}).get('count', 0)}")
        print(f"Successes: {stats.get('successes', {}).get('count', 0)}")
        print()
        if stats.get("improvements"):
            print("Improvements:")
            for imp in stats["improvements"]:
                print(f"  [{imp.get('priority', '?')}] {imp.get('recommendation', '')}")
        
        if args.write_report:
            content = write_reflection_report(stats)
            print(f"\nReport written.")
        
        if args.update_memory:
            update_memory_with_insights(stats)
            print(f"MEMORY.md updated.")

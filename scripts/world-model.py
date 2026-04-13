#!/usr/bin/env python3
"""
World Model — The living knowledge graph for Sig Botti.
A typed graph of entities, beliefs, relations, and events that grows over time.

Auto-update sources:
- `world-model.py add-entity <name> <type> <props_json>` — add/update an entity
- `world-model.py add-event <name> <type> <description>` — log a significant event
- `world-model.py add-belief <key> "<claim>"` — record a belief/fact
- `world-model.py context <topic>` — query relevant context for a topic
- `world-model.py sync-from-reflection` — pull recent events from reflection log
- `world-model.py build` — full rebuild from all sources (called by self_improve.py --update-world-model)
"""
import json
import os
import re
import sys
import glob
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = os.path.dirname(os.path.dirname(__file__))
WM_FILE = os.path.join(WORKSPACE, "data", "world-model.json")
EPISODE_LOG = os.path.join(WORKSPACE, "data", "episodes", "episodes.jsonl")
REFLECTION_LOG = os.path.join(WORKSPACE, "memory", "reflection-log.md")
WM_EVENTS_FILE = os.path.join(WORKSPACE, "data", "world-model-events.jsonl")


def load_wm():
    """Load existing world model or return base structure."""
    if os.path.exists(WM_FILE):
        try:
            with open(WM_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"version": "1.0", "entities": {}, "beliefs": {}, "relations": [], "events": []}


def save_wm(wm):
    """Save world model atomically."""
    os.makedirs(os.path.dirname(WM_FILE), exist_ok=True)
    wm["last_updated"] = datetime.now().isoformat()
    tmp = WM_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(wm, f, indent=2)
    os.replace(tmp, WM_FILE)


def add_entity(name: str, entity_type: str, properties: dict):
    """Add or update an entity."""
    wm = load_wm()
    if name not in wm["entities"]:
        wm["entities"][name] = {"type": entity_type, "properties": {}}
    wm["entities"][name]["type"] = entity_type
    wm["entities"][name]["properties"].update(properties)
    save_wm(wm)
    print(f"Added/updated entity: {name} ({entity_type})")


def add_event(name: str, event_type: str, description: str, date: str = None):
    """Log a significant event."""
    wm = load_wm()
    # Check for duplicate (same name, same day)
    today = date or datetime.now().strftime("%Y-%m-%d")
    for existing in wm.get("events", []):
        if existing.get("name") == name and existing.get("date", "").startswith(today):
            # Update existing event instead of duplicating
            existing["description"] = description
            save_wm(wm)
            print(f"Updated event: {name} ({today})")
            return
    
    event = {
        "type": event_type,
        "name": name,
        "date": date or datetime.now().strftime("%Y-%m-%d"),
        "description": description
    }
    wm.setdefault("events", []).insert(0, event)  # newest first
    save_wm(wm)
    print(f"Logged event: {name} [{event_type}]")


def add_belief(key: str, claim: str):
    """Record a belief or fact."""
    wm = load_wm()
    wm["beliefs"][key] = {"claim": claim, "updated": datetime.now().isoformat()}
    save_wm(wm)
    print(f"Belief updated: {key}")


def add_relation(from_entity: str, to_entity: str, relation_type: str):
    """Add a relation between entities."""
    wm = load_wm()
    # Avoid duplicate relations
    for rel in wm.get("relations", []):
        if rel["from"] == from_entity and rel["to"] == to_entity and rel["type"] == relation_type:
            return
    wm.setdefault("relations", []).append({
        "from": from_entity, "to": to_entity, "type": relation_type
    })
    save_wm(wm)
    print(f"Relation added: {from_entity} --[{relation_type}]--> {to_entity}")


def query_context(topic: str, top_k: int = 5) -> str:
    """Query world model for context relevant to a topic."""
    wm = load_wm()
    if not wm.get("entities"):
        return ""
    
    topic_lower = topic.lower()
    topic_words = set(re.sub(r"[^\w\s]", " ", topic_lower).split())
    
    # Score entities by relevance
    scored = []
    for name, entity in wm.get("entities", {}).items():
        text = f"{name} {json.dumps(entity.get('properties', {}))}".lower()
        score = sum(1 for w in topic_words if w in text)
        if score > 0:
            scored.append((score, name, entity))
    
    scored.sort(reverse=True)
    results = scored[:top_k]
    
    if not results:
        return ""
    
    lines = []
    for score, name, entity in results:
        props = entity.get("properties", {})
        parts = [f"**{name}**"]
        for k, v in list(props.items())[:8]:  # limit props per entity
            if isinstance(v, str) and len(v) < 100:
                parts.append(f"  {k}: {v}")
            elif isinstance(v, list):
                parts.append(f"  {k}: {', '.join(str(x) for x in v[:5])}")
        lines.append("\n".join(parts))
    
    return "\n\n".join(lines)


def sync_from_reflection():
    """Pull significant events from reflection log into world model."""
    if not os.path.exists(REFLECTION_LOG):
        print("No reflection log found")
        return
    
    try:
        with open(REFLECTION_LOG) as f:
            content = f.read()
    except:
        return
    
    wm = load_wm()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Look for patterns in reflection log
    # Patterns: "Failure Analysis", "Slow Tasks", "What's Working", "Improvements"
    import re
    
    # Extract high-priority improvements
    improvements = re.findall(r'🔴 (.+)', content)
    for imp in improvements[:5]:
        event_name = f"Action item: {imp[:60]}"
        add_event(event_name, "improvement", imp, today)
    
    # Extract failure patterns
    patterns = re.findall(r'Pattern: (.+)', content)
    for p in patterns[:3]:
        add_event(f"Failure pattern: {p[:60]}", "lesson", p, today)
    
    print(f"Synced from reflection log")


def update_from_episodes():
    """Analyze recent episodes and update world model with patterns."""
    if not os.path.exists(EPISODE_LOG):
        return
    
    try:
        episodes = []
        with open(EPISODE_LOG) as f:
            for line in f:
                try:
                    ep = json.loads(line.strip())
                    episodes.append(ep)
                except:
                    pass
    except:
        return
    
    if not episodes:
        return
    
    # Get recent episodes (last 50)
    recent = episodes[-50:]
    
    # Count outcomes by type
    from collections import Counter
    task_types = Counter(e.get("task_type") for e in recent)
    outcomes = Counter(e.get("outcome") for e in recent)
    
    # Find top failure types
    failures = [e for e in recent if e.get("outcome") == "failure"]
    failure_types = Counter(e.get("task_type") for e in failures)
    
    wm = load_wm()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Update beliefs with current stats
    total = len(recent)
    fail_count = outcomes.get("failure", 0)
    wm["beliefs"]["agent_stats"] = {
        "claim": f"Recent {total} episodes: {outcomes.get('success',0)} success, {fail_count} failures",
        "updated": today,
        "top_task_types": dict(task_types.most_common(5)),
        "failure_rate": f"{fail_count/total*100:.1f}%" if total > 0 else "0%"
    }
    
    # Log if failure rate is concerning
    if total > 5 and fail_count / total > 0.3:
        add_event(f"High failure rate: {fail_count/total*100:.0f}%", "alert", 
                  f"Recent failure rate is {fail_count/total*100:.0f}% — review reflection log", today)
    
    save_wm(wm)
    print(f"Updated from episodes: {total} recent, {fail_count} failures")


def full_build():
    """Full world model rebuild from all sources. Called by self_improve.py."""
    # Load existing WM to preserve manually-added entities
    wm = load_wm()
    
    # Sync from reflection log
    try:
        sync_from_reflection()
    except Exception as e:
        print(f"Reflection sync error: {e}")
    
    # Update from episode stats
    try:
        update_from_episodes()
    except Exception as e:
        print(f"Episode update error: {e}")
    
    # Load any pending events from the events queue file
    if os.path.exists(WM_EVENTS_FILE):
        try:
            with open(WM_EVENTS_FILE) as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        add_event(
                            event.get("name", "Unknown event"),
                            event.get("type", "event"),
                            event.get("description", ""),
                            event.get("date")
                        )
                    except:
                        pass
            # Clear the events file after processing
            os.replace(WM_EVENTS_FILE, WM_EVENTS_FILE + ".bak")
        except Exception as e:
            print(f"Events file error: {e}")
    
    # Update last_updated
    wm["last_updated"] = datetime.now().isoformat()
    save_wm(wm)
    
    # Stats
    print(f"World model build complete: {len(wm['entities'])} entities, {len(wm['events'])} events, {len(wm['beliefs'])} beliefs")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="World Model CLI")
    sub = parser.add_subparsers(dest="cmd")
    
    sub.add_parser("build", help="Full rebuild from all sources")
    sub.add_parser("sync-from-reflection", help="Sync events from reflection log")
    sub.add_parser("update-from-episodes", help="Update stats from episode log")
    
    ctx = sub.add_parser("context", help="Query context for a topic")
    ctx.add_argument("topic", nargs="*", help="Topic to query (defaults to stdin if empty)")
    
    add_ent = sub.add_parser("add-entity", help="Add/update an entity")
    add_ent.add_argument("name")
    add_ent.add_argument("type")
    add_ent.add_argument("props", help="JSON props string")
    
    add_ev = sub.add_parser("add-event", help="Log a significant event")
    add_ev.add_argument("name")
    add_ev.add_argument("type")
    add_ev.add_argument("description")
    add_ev.add_argument("--date", default=None)
    
    add_bel = sub.add_parser("add-belief", help="Record a belief")
    add_bel.add_argument("key")
    add_bel.add_argument("claim")
    
    add_rel = sub.add_parser("add-relation", help="Add a relation")
    add_rel.add_argument("from_entity")
    add_rel.add_argument("to_entity")
    add_rel.add_argument("relation_type")
    
    args = parser.parse_args()
    
    if args.cmd == "build":
        full_build()
    elif args.cmd == "context":
        topic = " ".join(args.topic) if args.topic else ""
        if not topic:
            print("Usage: world-model.py context <topic>")
        else:
            result = query_context(topic)
            print(result if result else "No relevant context found")
    elif args.cmd == "add-entity":
        props = json.loads(args.props)
        add_entity(args.name, args.type, props)
    elif args.cmd == "add-event":
        add_event(args.name, args.type, args.description, args.date)
    elif args.cmd == "add-belief":
        add_belief(args.key, args.claim)
    elif args.cmd == "add-relation":
        add_relation(args.from_entity, args.to_entity, args.relation_type)
    elif args.cmd == "sync-from-reflection":
        sync_from_reflection()
    elif args.cmd == "update-from-episodes":
        update_from_episodes()
    else:
        # Default: show current state
        wm = load_wm()
        print(f"World Model: {len(wm.get('entities', {}))} entities, {len(wm.get('events', []))} events, {len(wm.get('beliefs', {}))} beliefs")
        print(f"Last updated: {wm.get('last_updated', 'never')}")
        print("\nEntities:")
        for name, entity in list(wm.get('entities', {}).items())[:10]:
            print(f"  {name} [{entity.get('type', '?')}]")

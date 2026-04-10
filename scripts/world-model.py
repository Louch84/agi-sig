#!/usr/bin/env python3
"""
Structured World Model — Typed knowledge graph for Sig Botti.
Facts, beliefs, relationships, and context about the world.
Keeps state across sessions without relying on conversation context.
"""
import json
import os
from datetime import datetime
from typing import Optional

WORKSPACE = os.path.dirname(os.path.dirname(__file__))
MODEL_FILE = os.path.join(WORKSPACE, "data", "world-model.json")


# ─── Schema ────────────────────────────────────────────────────────────────────
class WorldModel:
    def __init__(self):
        self.data = {
            "entities": {},      # name → entity
            "relations": [],     # {from, type, to, confidence, updated}
            "beliefs": {},       # topic → {claim, confidence, source, updated}
            "preferences": {},   # owner → {preference → value}
            "state": {},         # system → state
            "events": [],        # {date, type, description, entities}
        }
        self.load()

    def load(self):
        if os.path.exists(MODEL_FILE):
            try:
                with open(MODEL_FILE) as f:
                    self.data = json.load(f)
            except Exception:
                pass

    def save(self):
        tmp = MODEL_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.data, f, indent=2)
        os.replace(tmp, MODEL_FILE)

    # ─── Entities ───────────────────────────────────────────────────────────────
    def add_entity(self, name: str, entity_type: str, properties: dict, confidence: float = 1.0):
        """Add or update an entity."""
        self.data["entities"][name] = {
            "type": entity_type,
            "properties": properties,
            "confidence": confidence,
            "updated": datetime.now().isoformat(),
        }
        self.save()

    def get_entity(self, name: str) -> Optional[dict]:
        return self.data["entities"].get(name)

    def query_entities(self, entity_type: str = None, prefix: str = None) -> list:
        """Find entities by type or name prefix."""
        results = []
        for name, entity in self.data["entities"].items():
            if entity_type and entity.get("type") != entity_type:
                continue
            if prefix and not name.lower().startswith(prefix.lower()):
                continue
            results.append({"name": name, **entity})
        return results

    # ─── Relations ─────────────────────────────────────────────────────────────
    def add_relation(self, from_entity: str, relation_type: str, to_entity: str, confidence: float = 1.0):
        """Add a relationship between two entities."""
        # Remove existing relation of same type between same entities
        self.data["relations"] = [
            r for r in self.data["relations"]
            if not (r["from"] == from_entity and r["type"] == relation_type and r["to"] == to_entity)
        ]
        self.data["relations"].append({
            "from": from_entity,
            "type": relation_type,
            "to": to_entity,
            "confidence": confidence,
            "updated": datetime.now().isoformat(),
        })
        self.save()

    def get_relations(self, entity: str = None, rel_type: str = None) -> list:
        """Get relations, optionally filtered."""
        results = []
        for r in self.data["relations"]:
            if entity and r["from"] != entity and r["to"] != entity:
                continue
            if rel_type and r["type"] != rel_type:
                continue
            results.append(r)
        return results

    # ─── Beliefs ────────────────────────────────────────────────────────────────
    def set_belief(self, topic: str, claim: str, confidence: float = 0.8, source: str = "inference"):
        """Set a belief about a topic."""
        self.data["beliefs"][topic] = {
            "claim": claim,
            "confidence": confidence,
            "source": source,
            "updated": datetime.now().isoformat(),
        }
        self.save()

    def get_belief(self, topic: str) -> Optional[dict]:
        return self.data["beliefs"].get(topic)

    def query_beliefs(self, keyword: str) -> list:
        """Find beliefs matching a keyword."""
        results = []
        for topic, belief in self.data["beliefs"].items():
            if keyword.lower() in topic.lower() or keyword.lower() in belief["claim"].lower():
                results.append({"topic": topic, **belief})
        return results

    # ─── Preferences ───────────────────────────────────────────────────────────
    def set_preference(self, owner: str, preference: str, value, confidence: float = 0.9):
        if owner not in self.data["preferences"]:
            self.data["preferences"][owner] = {}
        self.data["preferences"][owner][preference] = {
            "value": value,
            "confidence": confidence,
            "updated": datetime.now().isoformat(),
        }
        self.save()

    def get_preference(self, owner: str, preference: str) -> Optional[any]:
        return self.data["preferences"].get(owner, {}).get(preference, {}).get("value")

    def get_all_preferences(self, owner: str) -> dict:
        return self.data["preferences"].get(owner, {})

    # ─── State ─────────────────────────────────────────────────────────────────
    def set_state(self, system: str, state: str, value: any = None):
        self.data["state"][system] = {
            "state": state,
            "value": value,
            "updated": datetime.now().isoformat(),
        }
        self.save()

    def get_state(self, system: str) -> Optional[dict]:
        return self.data["state"].get(system)

    # ─── Events ────────────────────────────────────────────────────────────────
    def add_event(self, event_type: str, description: str, entities: list = None, date: str = None):
        self.data["events"].append({
            "type": event_type,
            "description": description,
            "entities": entities or [],
            "date": date or datetime.now().isoformat(),
        })
        # Keep last 100 events
        self.data["events"] = self.data["events"][-100:]
        self.save()

    def get_events(self, event_type: str = None, entity: str = None, limit: int = 20) -> list:
        results = self.data["events"][:]
        if event_type:
            results = [e for e in results if e["type"] == event_type]
        if entity:
            results = [e for e in results if entity in e.get("entities", [])]
        return results[-limit:]

    # ─── Reasoning ──────────────────────────────────────────────────────────────
    def reason(self, query: str) -> dict:
        """Simple reasoning: find relevant facts for a query."""
        query_lower = query.lower()
        results = {
            "query": query,
            "entities": [],
            "beliefs": [],
            "events": [],
            "relations": [],
        }

        # Find matching entities
        for name, entity in self.data["entities"].items():
            if query_lower in name.lower():
                results["entities"].append({"name": name, **entity})
            elif query_lower in str(entity.get("properties", {})).lower():
                results["entities"].append({"name": name, **entity})

        # Find matching beliefs
        for topic, belief in self.data["beliefs"].items():
            if query_lower in topic.lower() or query_lower in belief["claim"].lower():
                results["beliefs"].append({"topic": topic, **belief})

        # Find matching events
        for event in self.data["events"][-50:]:
            if query_lower in event["description"].lower():
                results["events"].append(event)

        return results

    def get_context_for(self, topic: str) -> str:
        """Get a text summary of everything I know about a topic."""
        r = self.reason(topic)
        lines = [f"## What I know about: {topic}"]

        if r["entities"]:
            lines.append("\n**Entities:**")
            for e in r["entities"][:5]:
                props = ", ".join(f"{k}={v}" for k, v in e.get("properties", {}).items())
                lines.append(f"- **{e['name']}** ({e.get('type', 'unknown')}) {props}")

        if r["beliefs"]:
            lines.append("\n**Beliefs:**")
            for b in r["beliefs"][:5]:
                conf = b.get("confidence", 0) * 100
                lines.append(f"- [{conf:.0f}% confidence] {b.get('claim', '')}")

        if r["events"]:
            lines.append("\n**Recent events:**")
            for e in r["events"][-5:]:
                lines.append(f"- {e.get('date','')}: {e.get('description','')}")

        if not (r["entities"] or r["beliefs"] or r["events"]):
            lines.append("\n_No relevant knowledge found._")

        return "\n".join(lines)


# ─── CLI ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    wm = WorldModel()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "help":
        print("World Model CLI")
        print("  add-entity <name> <type> <json_props>")
        print("  get-entity <name>")
        print("  query-entities <type>")
        print("  set-belief <topic> <claim>")
        print("  get-belief <topic>")
        print("  set-pref <owner> <pref> <value>")
        print("  get-prefs <owner>")
        print("  set-state <system> <state> [value]")
        print("  add-event <type> <description>")
        print("  reason <query>")
        print("  context <topic>")

    elif cmd == "add-entity" and len(sys.argv) >= 5:
        name, etype, props_str = sys.argv[2], sys.argv[3], " ".join(sys.argv[4:])
        import ast
        try:
            props = ast.literal_eval(props_str)
        except:
            props = {"note": props_str}
        wm.add_entity(name, etype, props)
        print(f"Added entity: {name}")

    elif cmd == "get-entity" and len(sys.argv) >= 3:
        e = wm.get_entity(sys.argv[2])
        print(json.dumps(e, indent=2) if e else "Not found")

    elif cmd == "query-entities" and len(sys.argv) >= 3:
        entities = wm.query_entities(entity_type=sys.argv[2])
        for e in entities:
            print(f"- {e['name']} ({e.get('type', '?')})")

    elif cmd == "set-belief" and len(sys.argv) >= 4:
        topic, claim = sys.argv[2], sys.argv[3]
        wm.set_belief(topic, claim)
        print(f"Belief set: {topic}")

    elif cmd == "get-belief" and len(sys.argv) >= 3:
        b = wm.get_belief(sys.argv[2])
        print(json.dumps(b, indent=2) if b else "Not found")

    elif cmd == "set-pref" and len(sys.argv) >= 5:
        owner, pref, value = sys.argv[2], sys.argv[3], sys.argv[4]
        wm.set_preference(owner, pref, value)
        print(f"Preference set: {owner}.{pref} = {value}")

    elif cmd == "get-prefs" and len(sys.argv) >= 3:
        prefs = wm.get_all_preferences(sys.argv[2])
        for k, v in prefs.items():
            print(f"  {k}: {v}")

    elif cmd == "set-state" and len(sys.argv) >= 4:
        system, state = sys.argv[2], sys.argv[3]
        value = sys.argv[4] if len(sys.argv) > 4 else None
        wm.set_state(system, state, value)
        print(f"State set: {system} = {state}")

    elif cmd == "get-state" and len(sys.argv) >= 3:
        s = wm.get_state(sys.argv[2])
        print(json.dumps(s, indent=2) if s else "Not found")

    elif cmd == "add-event" and len(sys.argv) >= 4:
        etype, desc = sys.argv[2], " ".join(sys.argv[3:])
        wm.add_event(etype, desc)
        print(f"Event added: {etype}")

    elif cmd == "reason" and len(sys.argv) >= 3:
        query = " ".join(sys.argv[2:])
        r = wm.reason(query)
        print(json.dumps(r, indent=2))

    elif cmd == "context" and len(sys.argv) >= 3:
        topic = " ".join(sys.argv[2:])
        print(wm.get_context_for(topic))

    else:
        print(f"Unknown command: {cmd}")
        print("Try: world-model.py help")

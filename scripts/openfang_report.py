#!/usr/bin/env python3
"""
OpenFang Daily Report — reads OpenFang DB and prints a report.
Run via cron to report to Discord.
"""
import sqlite3
import json
from datetime import datetime, timedelta

DB = "/Users/sigbotti/.openfang/data/openfang.db"

def get_kv(key):
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT value FROM kv_store WHERE key = ?", (key,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {}
        val = row[0]
        if isinstance(val, str):
            return json.loads(val)
        return val
    except:
        return {}

def get_memories_since(days=1):
    try:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            "SELECT content, created_at FROM memories ORDER BY created_at DESC LIMIT 20"
        )
        rows = cur.fetchall()
        conn.close()
        return [(r[0], r[1]) for r in rows if r[1] > cutoff]
    except:
        return []

def main():
    report = []
    report.append("📊 **OpenFang Daily Report**")
    report.append(f"_{datetime.now().strftime('%Y-%m-%d %H:%M ET')}_\n")

    # Collector state
    coll = get_kv("collector_hand_state")
    if coll and isinstance(coll, dict):
        report.append(f"**🔍 Collector**")
        report.append(f"- Status: {coll.get('status', 'unknown')}")
        report.append(f"- Cycle count: {coll.get('cycle_count', 0)}")
        report.append(f"- Entities tracked: {coll.get('entities_tracked', 0)}")
        report.append(f"- Last run: {coll.get('last_run', 'never')}")
        report.append("")

    # Researcher state
    res = get_kv("researcher_hand_state")
    if res and isinstance(res, dict):
        report.append(f"**🧪 Researcher**")
        report.append(f"- Queries solved: {res.get('total_queries', 0)}")
        report.append(f"- Sources cited: {res.get('total_sources_cited', 0)}")
        report.append(f"- Reports generated: {res.get('reports_generated', 0)}")
        report.append(f"- Active investigations: {res.get('active_investigations', 0)}")
        report.append("")

    # Predictor state
    pred = get_kv("predictor_hand_state")
    if pred and isinstance(pred, dict):
        report.append(f"**🔮 Predictor**")
        report.append(f"- Total predictions: {pred.get('total_predictions', 0)}")
        report.append(f"- Active predictions: {pred.get('active_predictions', 0)}")
        report.append(f"- Reports generated: {pred.get('reports_generated', 0)}")
        report.append(f"- Accuracy tracking: {pred.get('accuracy_pct', 'N/A')}")
        report.append("")

    # Recent memories from hands
    memories = get_memories_since(days=1)
    if memories:
        report.append(f"**📝 Recent Hand Activity** ({len(memories)} events)")
        for content, ts in memories[:5]:
            # Shorten content
            if len(content) > 200:
                content = content[:200] + "..."
            # Extract agent name if present
            if "Agent:" in content:
                agent = content.split("Agent:")[1].split("\n")[0].strip()
                content = content.split("I responded:")[1].strip() if "I responded:" in content else content
                report.append(f"- [{agent}] {content[:150]}")
            else:
                report.append(f"- {content[:150]}")
        report.append("")

    # Footer
    report.append("---")
    report.append("_OpenFang hands running continuously. Full dashboard: http://127.0.0.1:50051/ _")

    print("\n".join(report))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Ollama Vector Memory — lightweight semantic memory using Ollama embeddings.
Stores memories in a JSON file. Search via cosine similarity against Ollama nomic-embed-text.
No external DB needed. Free and local.
"""
import json
import os
import sys
import math
import requests

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "memory", "vector_memory.json")
OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

def get_embedding(text):
    """Get embedding for text via Ollama."""
    resp = requests.post(OLLAMA_URL, json={"model": EMBED_MODEL, "prompt": text}, timeout=30)
    resp.raise_for_status()
    return resp.json()["embedding"]

def cosine_sim(a, b):
    """Compute cosine similarity between two vectors."""
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def load_memory():
    """Load memory store from disk."""
    if not os.path.exists(MEMORY_FILE):
        return {"memories": []}
    with open(MEMORY_FILE) as f:
        return json.load(f)

def save_memory(data):
    """Save memory store to disk."""
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add(text, category="general", importance=0.5, metadata=None):
    """Add a memory with its embedding."""
    emb = get_embedding(text)
    entry = {
        "text": text,
        "embedding": emb,
        "category": category,
        "importance": importance,
        "metadata": metadata or {}
    }
    data = load_memory()
    data["memories"].append(entry)
    save_memory(data)
    return len(data["memories"])

def search(query, top_k=5, min_score=0.5, category=None):
    """Search memories by semantic similarity."""
    query_emb = get_embedding(query)
    data = load_memory()
    results = []
    for entry in data["memories"]:
        if category and entry.get("category") != category:
            continue
        score = cosine_sim(query_emb, entry["embedding"])
        if score >= min_score:
            results.append({
                "text": entry["text"],
                "category": entry.get("category"),
                "importance": entry.get("importance"),
                "score": round(score, 4),
                "metadata": entry.get("metadata", {})
            })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def stats():
    """Show memory stats."""
    data = load_memory()
    by_cat = {}
    for m in data["memories"]:
        cat = m.get("category", "unknown")
        by_cat[cat] = by_cat.get(cat, 0) + 1
    return {"total": len(data["memories"]), "by_category": by_cat}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if cmd == "add":
        # python3 ollama_mem.py add "text to remember" --category work --importance 0.8
        text = sys.argv[2] if len(sys.argv) > 2 else input("Memory text: ")
        category = "general"
        importance = 0.5
        for i, arg in enumerate(sys.argv):
            if arg == "--category" and i+1 < len(sys.argv):
                category = sys.argv[i+1]
            if arg == "--importance" and i+1 < len(sys.argv):
                importance = float(sys.argv[i+1])
        count = add(text, category, importance)
        print(f"✓ Added memory (total: {count})")
    
    elif cmd == "search":
        # python3 ollama_mem.py search "query" --top 5 --min 0.5
        query = sys.argv[2] if len(sys.argv) > 2 else input("Query: ")
        top_k = 5
        min_score = 0.5
        for i, arg in enumerate(sys.argv):
            if arg == "--top" and i+1 < len(sys.argv):
                top_k = int(sys.argv[i+1])
            if arg == "--min" and i+1 < len(sys.argv):
                min_score = float(sys.argv[i+1])
        results = search(query, top_k, min_score)
        if not results:
            print("No matching memories found.")
        for r in results:
            print(f"\n[{r['score']}] [{r['category']}] {r['text']}")
    
    elif cmd == "stats":
        s = stats()
        print(f"Total memories: {s['total']}")
        for cat, count in s["by_category"].items():
            print(f"  {cat}: {count}")
    
    elif cmd == "init":
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        save_memory({"memories": []})
        print(f"✓ Initialized at {MEMORY_FILE}")
    
    else:
        print("Usage:")
        print("  ollama_mem.py add 'text' [--category cat] [--importance 0.9]")
        print("  ollama_mem.py search 'query' [--top N] [--min 0.5]")
        print("  ollama_mem.py stats")
        print("  ollama_mem.py init")

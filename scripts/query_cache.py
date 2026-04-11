#!/usr/bin/env python3
"""
Query Cache — Cache repeated/simple query responses for instant return.
Integrated with model_router for the complete fast-path system.
"""
import json
import os
import sys
import time
import hashlib
from typing import Optional, Tuple

WORKSPACE = os.path.dirname(os.path.dirname(__file__))
CACHE_FILE = os.path.join(WORKSPACE, "data", "query-cache.json")

# Ollama fast model
OLLAMA_BASE = "http://localhost:11434"
FAST_MODEL = "llama3.2:1b"


def _load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except:
        return {}


def _save_cache(cache: dict):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    tmp = CACHE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(cache, f, indent=2)
    os.replace(tmp, CACHE_FILE)


def get_cached(query: str) -> Optional[Tuple[str, str]]:
    """Check cache. Returns (response, model) or None if not found/expired."""
    cache = _load_cache()
    query_hash = hashlib.sha256(query.encode()).hexdigest()
    
    if query_hash not in cache:
        return None
    
    entry = cache[query_hash]
    max_age = 86400 if entry.get("model") == FAST_MODEL else 3600
    if time.time() - entry.get("cached_at", 0) > max_age:
        return None
    
    return entry.get("response"), entry.get("model")


def cache_response(query: str, response: str, model: str = FAST_MODEL):
    """Cache a query response."""
    cache = _load_cache()
    query_hash = hashlib.sha256(query.encode()).hexdigest()
    
    cache[query_hash] = {
        "response": response,
        "model": model,
        "cached_at": time.time(),
        "query_preview": query[:80],
    }
    
    # Prune to 500 entries
    if len(cache) > 500:
        sorted_entries = sorted(cache.items(), key=lambda x: x[1].get("cached_at", 0))
        cache = dict(sorted_entries[-400:])
    
    _save_cache(cache)


def query_ollama(model: str, prompt: str, timeout: int = 30) -> str:
    """Query local Ollama."""
    import urllib.request
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "temperature": 0.1,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["message"]["content"]
    except Exception as e:
        return f"[Error: {e}]"


# Simple query fast-track indicators
FAST_INDICATORS = {
    "hey", "hi", "yo", "hello", "sup", "what's up", "wassup",
    "thanks", "thank you", "ok", "okay", "sure", "yeah", "yep", "nice",
    "lol", "haha", "lmao", "cool", "got it", "understood",
    "good", "great", "👍", "👋", "🦊", "nice", "sounds good",
    "perfect", "awesome", "noted", "will do", "on it",
}

COMPLEX_INDICATORS = {
    "research", "analyze", "compare", "audit", "review", "evaluate",
    "build", "write code", "create", "implement", "fix", "debug",
    "explain", "understand", "how does", "what is", "why does",
    "find all", "search for", "investigate", "deep dive",
    "self-improve", "reflect", "remember", "archive",
    "write a script", "run a scan", "search the web", "look up",
    "code", "python", "javascript", "sql",
    "summarize", "translate", "rewrite",
    "plan", "design", "architecture",
    "multiple", "several", "all of", "both", "between",
    " every ", " all ", "evaluate", "figuring out", "setting up",
}


def is_fast_query(query: str) -> bool:
    """Classify query as simple enough for fast model."""
    q = query.lower().strip()
    
    # Very short + no complex indicators
    if len(q) < 80:
        if not any(ind in q for ind in COMPLEX_INDICATORS):
            return True
    
    # Starts with fast indicators
    for ind in FAST_INDICATORS:
        if q.startswith(ind) or q == ind:
            return True
    
    return False


def fast_response(query: str, use_cache: bool = True) -> tuple[str, float]:
    if not is_fast_query(query):
        return None, 0.0
    
    start = time.time()
    
    # Check cache first
    if use_cache:
        cached = get_cached(query)
        if cached:
            return cached[0], time.time() - start
    
    # Query Ollama fast model
    response = query_ollama(FAST_MODEL, query, timeout=20)
    
    if response.startswith("[Error"):
        return None, time.time() - start
    
    # Cache it
    if use_cache:
        cache_response(query, response, FAST_MODEL)
    
    return response, time.time() - start


def get_stats() -> dict:
    """Return cache statistics."""
    cache = _load_cache()
    if not cache:
        return {"entries": 0, "by_model": {}}
    
    from collections import Counter
    models = Counter(v.get("model", "?") for v in cache.values())
    return {
        "entries": len(cache),
        "by_model": dict(models),
        "oldest_entry": min(v.get("cached_at", 0) for v in cache.values()),
        "newest_entry": max(v.get("cached_at", 0) for v in cache.values()),
    }


if __name__ == "__main__":
    parser = __import__("argparse").ArgumentParser(description="Query Cache CLI")
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()
    
    if args.stats:
        stats = get_stats()
        print(f"Cached queries: {stats['entries']}")
        print(f"By model: {stats['by_model']}")
        if stats['entries'] > 0:
            oldest = datetime.fromtimestamp(stats['oldest_entry']).isoformat() if stats['oldest_entry'] else "?"
            newest = datetime.fromtimestamp(stats['newest_entry']).isoformat() if stats['newest_entry'] else "?"
            print(f"Oldest: {oldest}")
            print(f"Newest: {newest}")
    else:
        print("Query cache management. Use model_router.py for fast-path routing.")

#!/usr/bin/env python3
"""
Model Router — Route queries to the optimal model based on complexity.
Simple queries → local Ollama llama3.2:1b (fast, <1s)
Complex queries → MiniMax (reasoning, depth)

Classification heuristics:
- Short queries (<50 chars, no complex indicators) → fast
- greetings, acknowledgments, simple questions → fast  
- Multi-part, analysis, code, research, comparisons → MiniMax
- Anything ambiguous → MiniMax
"""
import json
import os
import sys
import time
import hashlib
from datetime import datetime, timedelta

WORKSPACE = os.path.dirname(os.path.dirname(__file__))
CACHE_FILE = os.path.join(WORKSPACE, "data", "query-cache.json")
OLLAMA_BASE = "http://localhost:11434"

# Simple query indicators — these go to fast model
FAST_INDICATORS = [
    "hey", "hi", "yo", "hello", "sup", "what's up",
    "thanks", "thank you", "ok", "okay", "sure", "yeah", "yep", "nice",
    "lol", "haha", "lmao", "cool", "nice", "got it", "understood",
    "good", "great", "👍", "👋", "🦊",
]

# Complex query indicators — these need MiniMax
COMPLEX_INDICATORS = [
    "research", "analyze", "compare", "audit", "review", "evaluate",
    "build", "write code", "create", "implement", "fix", "debug",
    "explain", "understand", "how does", "what is", "why does",
    "find all", "search for", "investigate", "deep dive",
    "self-improve", "reflect", "remember", "archive",
    "write a script", "run a scan", "search the web", "look up",
    "code", "python", "javascript", "sql", "query",
    "summarize", "explain", "translate", "rewrite",
    "plan", "design", "architecture", "architecture",
    "multiple", "several", "all of", "both", "between",
]

# Minimum length for complex classification
FAST_MAX_LEN = 100


def classify_query(query: str) -> str:
    """
    Classify a query as 'fast' or 'complex'.
    Returns model identifier string.
    """
    query_lower = query.lower().strip()
    
    # Very short queries → fast
    if len(query_lower) < FAST_MAX_LEN:
        # Check if any complex indicator present
        if not any(ind in query_lower for ind in COMPLEX_INDICATORS):
            return "fast"
    
    # Check for fast indicators (only if no complex indicators)
    if not any(ind in query_lower for ind in COMPLEX_INDICATORS):
        if any(ind in query_lower for ind in FAST_INDICATORS):
            return "fast"
    
    # Default to complex
    return "complex"


def check_cache(query: str) -> str:
    """Check if we have a cached response for this query."""
    if not os.path.exists(CACHE_FILE):
        return None
    
    try:
        with open(CACHE_FILE) as f:
            cache = json.load(f)
    except:
        return None
    
    # Hash the query for cache key
    query_hash = hashlib.sha256(query.encode()).hexdigest()
    
    if query_hash not in cache:
        return None
    
    entry = cache[query_hash]
    
    # Check expiry (24h for simple queries, 1h for complex)
    model = entry.get("model", "fast")
    max_age = 86400 if model == "fast" else 3600
    age = time.time() - entry.get("cached_at", 0)
    
    if age > max_age:
        return None
    
    return entry.get("response")


def save_to_cache(query: str, response: str, model: str):
    """Cache a query response."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    
    # Load existing cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE) as f:
                cache = json.load(f)
        except:
            cache = {}
    else:
        cache = {}
    
    query_hash = hashlib.sha256(query.encode()).hexdigest()
    cache[query_hash] = {
        "response": response,
        "model": model,
        "cached_at": time.time(),
        "query_preview": query[:50],
    }
    
    # Prune old entries (keep cache under 500 entries)
    if len(cache) > 500:
        sorted_entries = sorted(cache.items(), key=lambda x: x[1].get("cached_at", 0))
        cache = dict(sorted_entries[-400:])  # Keep newest 400
    
    with open(CACHE_FILE + ".tmp", "w") as f:
        json.dump(cache, f)
    os.replace(CACHE_FILE + ".tmp", CACHE_FILE)


def query_ollama(model: str, prompt: str, timeout: int = 30) -> str:
    """Query local Ollama model."""
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


def route_and_respond(query: str, use_cache: bool = True) -> tuple[str, str, float]:
    """
    Main entry point: classify query, route to appropriate model, return response.
    
    Returns: (response, model_used, duration_seconds)
    """
    start = time.time()
    
    # Check cache first
    if use_cache:
        cached = check_cache(query)
        if cached:
            duration = time.time() - start
            return cached, "cache", duration
    
    # Classify
    model_key = classify_query(query)
    
    if model_key == "fast":
        model = "llama3.2:1b"
        response = query_ollama(model, query, timeout=15)
    else:
        # Complex query → use MiniMax via OpenClaw's normal routing
        # We return a marker that tells the caller to use MiniMax
        # In practice, this is handled by the calling context (main session)
        duration = time.time() - start
        return None, "miniMax", duration
    
    # Cache simple query results
    if use_cache and response and not response.startswith("[Error"):
        save_to_cache(query, response, model)
    
    duration = time.time() - start
    return response, model, duration


# CLI for testing
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Model Router")
    parser.add_argument("query", nargs="+", help="Query to route")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()
    
    query = " ".join(args.query)
    
    if args.stats:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as f:
                cache = json.load(f)
            print(f"Cached queries: {len(cache)}")
            # Count by model
            from collections import Counter
            models = Counter(v.get("model") for v in cache.values())
            print(f"By model: {dict(models)}")
        else:
            print("No cache file found")
    else:
        response, model, duration = route_and_respond(query, use_cache=not args.no_cache)
        print(f"Model: {model} ({duration:.2f}s)")
        print(f"Response: {response[:500] if response else '[None — MiniMax required]'}")


# ── Classification for the agent to use ───────────────────────────────────────
"""
Quick reference for when to use which model:

Use llama3.2:1b (fast, <1s) when:
- "hey", "yo", "hi", "hello"
- "thanks", "ok", "sure", "got it"
- Simple factual questions
- Greetings and acknowledgments
- Short commands that don't need reasoning

Use MiniMax when:
- Multi-step tasks
- Code writing, debugging, analysis
- Research, comparisons, deep dives
- Self-reflection, memory tasks
- Building or creating things
- Long or complex queries
- Anything ambiguous

Query cache: repeated simple queries return cached response in <10ms.
"""

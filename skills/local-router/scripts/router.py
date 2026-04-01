#!/usr/bin/env python3
"""
Local Router v3 — FREE local Ollama routing only.
Routes tasks to the best FREE local Ollama model based on complexity.

Usage:
  python3 scripts/router.py "<task>" [--tier FAST|MODERATE|COMPLEX]
"""
import sys
import json
import urllib.request
import urllib.error

OLLAMA_BASE = "http://localhost:11434"

# FREE models only — no cloud, no cost
TIERS = {
    "FAST": {
        "model": "llama3.2:1b",
        "system": """You are a fast, concise Q&A assistant. Give brief, direct answers. No elaboration unless asked.
RULES:
1. If you don't know something, say "I don't know" — do NOT guess.
2. For factual claims, only answer if you are certain.
3. For calculations, verify your math.""",
    },
    "MODERATE": {
        "model": "llama3:latest",
        "system": """You are a helpful assistant. Be thorough when needed, concise when not.
RULES:
1. If you don't know something, say "I don't know" — do NOT guess.
2. For factual claims, be careful. Only state facts you are confident are correct.
3. When uncertain, qualify your answer or say "I don't know".""",
    },
    "COMPLEX": {
        "model": "qwen3-coder:30b",
        "system": """You are an expert programmer and problem solver. Think step by step.
RULES:
1. Break down complex problems into steps.
2. State assumptions clearly.
3. Note confidence levels and alternatives.
4. For code: write clean, efficient, well-documented code.""",
    },
}


def classify_task(task: str) -> str:
    """Classify task into FAST, MODERATE, or COMPLEX."""
    task_lower = task.lower()
    words = set(task_lower.replace("?", " ").replace(".", " ").split())

    # COMPLEX signals → qwen3-coder:30b
    complex_signals = {
        "debug", "architect", "design", "security", "why", "explain why",
        "complex", "difficult", "hard", "novel", "ambiguous",
        "refactor", "optimize performance", "scalability",
        "multi-step", "distributed", "concurrent",
    }
    if any(sig in words or sig in task_lower for sig in complex_signals):
        return "COMPLEX"

    # Has coding/programming signals → MODERATE (llama3)
    coding_signals = {
        "code", "programming", "function", "script", "algorithm",
        "bug", "fix", "class", "method", "api", "database", "sql",
        "git", "terminal", "python", "javascript", "java", "rust",
        "write code", "generate code", "implement",
    }
    if any(sig in words or sig in task_lower for sig in coding_signals):
        return "MODERATE"

    # MODERATE signals → llama3
    moderate_signals = {
        "write", "summarize", "analyze", "compare", "evaluate",
        "research", "explain", "review", "generate", "create",
        "build", "develop", "plan", "implement",
    }
    if any(sig in words or sig in task_lower for sig in moderate_signals):
        return "MODERATE"

    # FAST signals → llama3.2:1b
    routine_signals = {
        "hi", "hey", "hello", "goodbye", "thanks",
        "what is", "who is", "when did", "where is", "how many",
        "define", "definition", "meaning", "translate",
        "weather", "temperature", "forecast",
        "calculate", "convert", "what's", "whats",
        "yes or no", "true or false", "quick question",
        "check", "status", "fetch", "format", "list",
    }
    if any(sig in words or sig in task_lower for sig in routine_signals):
        return "FAST"

    # Default: FAST
    return "FAST"


def ollama_chat(model: str, prompt: str, system: str = "") -> str:
    """Call Ollama /api/chat endpoint."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.1},
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"[HTTP Error {e.code}]: {e.reason}"
    except urllib.error.URLError as e:
        return f"[Connection Error]: {e.reason}"
    except Exception as e:
        return f"[Error]: {e}"


def main():
    args = sys.argv[1:]
    force_tier = None
    task = None

    i = 0
    while i < len(args):
        if args[i] == "--tier" and i + 1 < len(args):
            force_tier = args[i + 1].upper()
            i += 2
        else:
            task = args[i] if not task else task + " " + args[i]
            i += 1

    if not task:
        print("Usage: python3 router.py <task> [--tier FAST|MODERATE|COMPLEX]")
        print("Default: auto-classify based on task complexity")
        sys.exit(1)

    # Classify or use forced tier
    if force_tier and force_tier in TIERS:
        tier = force_tier
    else:
        tier = classify_task(task)

    config = TIERS[tier]
    model = config["model"]
    system = config["system"]

    print(f"[{tier}] → {model}", flush=True)

    response = ollama_chat(model, task, system)
    print(f"\n{response}")


if __name__ == "__main__":
    main()

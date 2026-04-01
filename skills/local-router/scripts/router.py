#!/usr/bin/env python3
"""
Local Router v2 — Tiered LLM routing combining FREE (Ollama) + CLOUD (model-hierarchy).

Usage:
  python3 scripts/router.py "<task>" [--tier TIER]
  TIER can be: free, tier1, tier2, tier3, auto (default)
"""
import sys
import json
import os

# Configuration
OLLAMA_BASE = "http://localhost:11434"

# Model tiers (from model-hierarchy)
TIERS = {
    "FREE": {
        "llama3.2:1b": {"type": "ollama", "cost": 0},
        "llama3:latest": {"type": "ollama", "cost": 0},
    },
    "TIER1": {
        "deepseek-v3": {"type": "openrouter", "cost_input": 0.14, "cost_output": 0.28},
        "gpt-4o-mini": {"type": "openrouter", "cost_input": 0.15, "cost_output": 0.60},
        "claude-haiku": {"type": "openrouter", "cost_input": 0.25, "cost_output": 1.25},
        "gemini-flash": {"type": "openrouter", "cost_input": 0.075, "cost_output": 0.30},
        "kimi-k2.5": {"type": "openrouter", "cost_input": 0.45, "cost_output": 2.25},
    },
    "TIER2": {
        "claude-sonnet": {"type": "openrouter", "cost_input": 3.00, "cost_output": 15.00},
        "gpt-4o": {"type": "openrouter", "cost_input": 2.50, "cost_output": 10.00},
        "gemini-pro": {"type": "openrouter", "cost_input": 1.25, "cost_output": 5.00},
    },
    "TIER3": {
        "claude-opus": {"type": "openrouter", "cost_input": 15.00, "cost_output": 75.00},
        "o1": {"type": "openrouter", "cost_input": 15.00, "cost_output": 60.00},
        "o3-mini": {"type": "openrouter", "cost_input": 1.10, "cost_output": 4.40},
    },
}

SYSTEM_PROMPTS = {
    "FREE": """You are a fast, concise assistant. Give brief, direct answers. No elaboration unless asked.
RULES: If uncertain, say "I don't know". For factual questions, only answer if certain.""",

    "TIER1": """You are a helpful assistant. Be thorough when needed, concise when not.
RULES: If uncertain, say "I don't know" or qualify your uncertainty. Do not guess.""",

    "TIER2": """You are an expert assistant. Give thorough, well-reasoned responses.
RULES: State confidence level. Note if you're uncertain. Provide nuance when appropriate.""",

    "TIER3": """You are an expert at complex reasoning and problem-solving. Think step by step.
RULES: Break down complex problems. State assumptions clearly. Note confidence and alternatives.""",
}


def classify_task(task: str) -> str:
    """Classify task into ROUTINE, MODERATE, or COMPLEX."""
    task_lower = task.lower()
    words = set(task_lower.replace("?", " ").replace(".", " ").split())

    # Order matters! Check in specificity order:

    # Has code/programming signals → MODERATE (not routine even if it looks simple)
    coding_signals = {
        "code", "programming", "function", "script", "algorithm",
        "bug", "fix", "refactor", "optimize", "class", "method",
        "api", "database", "sql", "git", "terminal", "python", "javascript",
    }
    if any(sig in words or sig in task_lower for sig in coding_signals):
        return "MODERATE"

    # MODERATE signals (before routine — "write" could match routine otherwise)
    moderate_signals = {
        "write", "summarize", "analyze", "compare", "evaluate",
        "research", "explain", "review", "generate", "create",
        "build", "develop", "design", "plan", "implement",
    }
    if any(sig in words or sig in task_lower for sig in moderate_signals):
        return "MODERATE"

    # COMPLEX signals → TIER3
    complex_signals = {
        "debug", "architect", "design", "security", "why", "explain why",
        "complex", "difficult", "hard", "novel", "ambiguous",
    }
    if any(sig in words or sig in task_lower for sig in complex_signals):
        return "COMPLEX"

    # ROUTINE signals → FREE (most specific, lowest tier)
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
        return "ROUTINE"

    # Default: ROUTINE (use free)
    return "ROUTINE"


def select_tier(classification: str, has_vision: bool = False, force_tier: str = None) -> str:
    """Select the tier based on classification and constraints."""
    if force_tier and force_tier != "auto":
        return force_tier

    if classification == "ROUTINE":
        return "FREE"
    elif classification == "MODERATE":
        if has_vision:
            return "TIER2"  # Need vision-capable
        return "TIER1"
    else:  # COMPLEX
        return "TIER3"


def select_model(tier: str, has_vision: bool = False) -> str:
    """Select the best model for the tier and requirements."""
    models = list(TIERS[tier].keys())

    # For vision tasks, prefer multimodal models
    if has_vision and tier in ("TIER1", "TIER2"):
        vision_preferred = {
            "TIER1": "kimi-k2.5",
            "TIER2": "gpt-4o",
        }
        if vision_preferred.get(tier) in models:
            return vision_preferred[tier]

    # Default to first model in tier (best value)
    return models[0]


def ollama_chat(model: str, prompt: str, system: str = "") -> str:
    """Call Ollama /api/chat endpoint."""
    import urllib.request
    import urllib.error

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
    except Exception as e:
        return f"[Ollama Error]: {e}"


def openrouter_chat(model: str, prompt: str, system: str = "") -> str:
    """Call OpenRouter API."""
    import urllib.request
    import urllib.error

    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return "[OpenRouter Error]: OPENROUTER_API_KEY not set"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else str(e)
        return f"[OpenRouter HTTP {e.code}]: {body[:200]}"
    except Exception as e:
        return f"[OpenRouter Error]: {e}"


def estimate_cost(tier: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost in cents."""
    if tier == "FREE":
        return 0.0
    models = TIERS[tier]
    model_key = list(models.keys())[0]
    info = models[model_key]
    if info["type"] == "ollama":
        return 0.0
    cost = (input_tokens * info["cost_input"] + output_tokens * info["cost_output"]) / 100
    return cost


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
        print("Usage: python3 router.py <task> [--tier TIER]")
        print("TIER: free, tier1, tier2, tier3, auto (default)")
        sys.exit(1)

    # Detect vision requirement
    has_vision = any(kw in task.lower() for kw in ["image", "screenshot", "photo", "picture", "vision", "visual"])

    # Classify and select tier
    classification = classify_task(task)
    tier = select_tier(classification, has_vision, force_tier)
    model = select_model(tier, has_vision)
    model_info = TIERS[tier][model]
    model_type = model_info["type"]

    # Get cost estimate
    est_cost = estimate_cost(tier, 500, 200)  # rough estimate

    print(f"[{classification}] → {tier} → {model}", flush=True)
    if est_cost > 0:
        print(f"(~{est_cost:.3f}c estimated)", flush=True)
    print(flush=True)

    # Call the appropriate model
    system = SYSTEM_PROMPTS.get(tier, SYSTEM_PROMPTS["TIER1"])

    if model_type == "ollama":
        response = ollama_chat(model, task, system)
    else:
        response = openrouter_chat(model, task, system)

    print(response)


if __name__ == "__main__":
    main()

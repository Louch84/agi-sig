#!/usr/bin/env python3
"""
Local Router — Routes tasks to optimal Ollama model.

Usage:
  python3 scripts/router.py "your task here"
"""
import sys
import json
import urllib.request
import urllib.error

OLLAMA_BASE = "http://localhost:11434"

MODELS = {
    "FAST": "llama3.2:1b",
    "POWER": "llama3:latest",
}

SYSTEM_PROMPTS = {
    "FAST": "You are a fast, concise assistant. Give brief, direct answers. No elaboration unless asked.",
    "POWER": "You are a thoughtful assistant. Give thorough, well-reasoned responses when needed.",
}


def classify(task: str) -> str:
    """Classify task into SIMPLE, CODING, or GENERAL."""
    task_lower = task.lower()
    words = set(task_lower.replace("?", " ").replace(".", " ").split())

    # CODING indicators
    coding_keywords = {
        "code", "programming", "function", "script", "algorithm", "debug",
        "fix", "refactor", "optimize", "class", "method", "variable",
        "import", "module", "package", "api", "database", "sql", "query",
        "bug", "error", "exception", "compile", "build", "test", "pytest",
        "git", "terminal", "shell", "bash", "zsh", "docker", "kubernetes",
        "frontend", "backend", "fullstack", "web", "http", "json", "xml",
        ".py", ".js", ".ts", ".go", ".rs", ".java", ".cpp", ".c", ".rb",
        ".php", ".sh", ".cs", ".swift", ".kt", ".scala", ".lua",
    }
    if any(kw in words or kw in task_lower for kw in coding_keywords):
        return "POWER"

    # FAST indicators (simple, routine tasks)
    simple_keywords = {
        "hi", "hey", "hello", "goodbye", "thanks", "thank you",
        "what is", "who is", "when did", "where is", "how many",
        "define", "definition", "meaning", "translate",
        "weather", "temperature", "forecast",
        "calculate", "convert", "what's", "whats", "is it true",
        "yes or no", "true or false", "quick question",
        "single", "one step", "explain briefly",
    }
    if any(kw in words or kw in task_lower for kw in simple_keywords):
        return "FAST"

    return "FAST"  # Default to fast, upgrade to POWER only when needed


def ollama_chat(model: str, prompt: str, system: str = "") -> str:
    """Call Ollama /api/chat endpoint."""
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
    if len(sys.argv) < 2:
        print("Usage: python3 router.py <task>")
        sys.exit(1)

    task = " ".join(sys.argv[1:])
    tier = classify(task)
    model = MODELS[tier]
    system = SYSTEM_PROMPTS[tier]

    print(f"[Tier: {tier}] → {model}", flush=True)

    response = ollama_chat(model, task, system)
    print(f"\n{response}")


if __name__ == "__main__":
    main()

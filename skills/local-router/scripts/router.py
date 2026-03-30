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
    "FAST": """You are a fast, concise assistant.

RULES:
1. If you don't know something, say "I don't know" — do NOT guess or make up an answer.
2. For factual claims (dates, numbers, names, definitions), only answer if you are certain.
3. If asked to calculate or recall a fact and you're unsure, say "I don't know" instead of guessing.
4. Give brief, direct answers. No elaboration unless asked.

START EVERY RESPONSE by checking: "Am I certain about this?" If not, say "I don't know".""",

    "POWER": """You are a thoughtful assistant.

RULES:
1. If you don't know something, say "I don't know" — do NOT guess or make up an answer.
2. For factual claims, be especially careful. Only state facts you are confident are correct.
3. If uncertain about a calculation, fact, or date, explicitly note your uncertainty.
4. When in doubt, qualify your answer: "Based on what I know, X is likely, but I cannot be certain."

START EVERY RESPONSE by checking: "Am I confident this is correct?" If not, qualify or say "I don't know".""",
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
        "temperature": 0.1,  # Low temp = less hallucination
        "options": {
            "temperature": 0.1,
        },
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


def fact_check(response: str, original_task: str) -> str:
    """Add a fact-check warning if response contains factual claims."""
    factual_indicators = {
        "in", "on", "at", "by", "is", "are", "was", "were",  # linking facts
        "percent", "%", "degrees", "miles", "kilometers", "years", "days", "hours",
        "number", "count", "total", "sum", "equals", "costs", "priced",
        "named", "called", "discovered", "invented", "created", "founded",
    }
    task_lower = original_task.lower()

    # If the task was factual, check if response is suspiciously confident
    factual_task = any(
        kw in task_lower
        for kw in ["what is", "who is", "when did", "how many", "how much",
                   "number of", "percent of", "calculate", "cost", "price", "date"]
    )

    if factual_task:
        # Add uncertainty note
        if "i don't know" not in response.lower() and "i am not sure" not in response.lower():
            response += "\n\n[Note: Verify this information independently for accuracy — small local models can hallucinate.]"

    return response


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
    response = fact_check(response, task)
    print(f"\n{response}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Task Planner — Decomposes complex requests into structured subtasks.
Inspired by Microsoft JARVIS / HuggingGPT task planning stage.
"""
import json
import urllib.request
import urllib.error
import sys

OLLAMA_BASE = "http://localhost:11434"

PLANNER_MODEL = "llama3:latest"  # Use general model for planning


def ollama_chat(model: str, messages: list, temperature=0.1, timeout=60) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": temperature,
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
        return f"[Error]: {e}"


SYSTEM_PROMPT = """You are a task planning assistant. Given a user request, break it down into clear, ordered subtasks.

RULES:
1. Output ONLY valid JSON — no markdown, no explanation, no preamble
2. Each subtask must have: id (int), description (what to do), type (one of: fast/general/coding/vision/web_search/action), depends_on (list of subtask IDs that must run first, can be empty)
3. If the request is simple enough to do in one step, still return JSON with a single subtask
4. Be specific in descriptions — "write a prime checker function" not "write code"
5. Maximum 6 subtasks — if it needs more, group related steps

Available task types:
- fast: simple question, greeting, basic math, quick lookup
- general: analysis, writing, reasoning, summarization
- coding: code writing, debugging, refactoring, script creation
- vision: image understanding or generation
- web_search: research, fact-finding, looking up current info
- action: executing a system action (file ops, API calls, cron management)

Output format:
{
  "summary": "one sentence summary of the overall request",
  "subtasks": [
    {"id": 1, "description": "...", "type": "...", "depends_on": []},
    {"id": 2, "description": "...", "type": "...", "depends_on": [1]},
    ...
  ]
}"""


def plan_task(request: str) -> dict:
    """Decompose a request into subtasks using the planner model."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"User request: {request}"},
    ]

    response = ollama_chat(PLANNER_MODEL, messages, timeout=90)

    # Try to parse JSON from response
    try:
        # Strip markdown code blocks if present
        text = response.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "summary": request,
            "subtasks": [{"id": 1, "description": request, "type": "general", "depends_on": []}],
            "_parse_error": response[:200],
        }


def execute_plan(plan: dict, executor_func) -> list:
    """Execute a plan by running subtasks in dependency order.

    executor_func(subtask) -> result dict with 'id', 'status', 'output'

    Returns list of results in subtask order.
    """
    results = {}  # id -> result
    completed = set()

    max_iterations = len(plan["subtasks"]) * 2  # safety

    for _ in range(max_iterations):
        if len(results) >= len(plan["subtasks"]):
            break

        for subtask in plan["subtasks"]:
            tid = subtask["id"]
            if tid in results:
                continue

            # Check dependencies
            deps = subtask.get("depends_on", [])
            if all(d in completed for d in deps):
                try:
                    result = executor_func(subtask)
                except Exception as e:
                    result = {"id": tid, "status": "error", "output": f"Executor error: {e}"}
                results[tid] = result
                if result.get("status") == "done":
                    completed.add(tid)

    return [results.get(s["id"]) for s in plan["subtasks"]]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: task-planner.py '<user request>'")
        sys.exit(1)

    request = " ".join(sys.argv[1:])
    print(f"Planning: {request}")
    print()

    plan = plan_task(request)

    print(f"Summary: {plan.get('summary', 'N/A')}")
    print(f"Subtasks ({len(plan['subtasks'])}):")
    for s in plan["subtasks"]:
        deps = s.get("depends_on", [])
        dep_str = f" (depends on {deps})" if deps else ""
        print(f"  [{s['id']}] {s['type'].upper():8} | {s['description']}{dep_str}")

    if "_parse_error" in plan:
        print(f"\n⚠ Parser error, used fallback: {plan['_parse_error']}")

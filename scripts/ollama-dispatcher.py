#!/usr/bin/env python3
"""
Ollama Autonomous Dispatcher
Watches task queue and processes tasks using the optimal local model.
"""
import sys
import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

OLLAMA_BASE = "http://localhost:11434"
QUEUE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "task-queue.json")
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "task-results.json")
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "dispatcher.log")

MODELS = {
    "fast": "llama3.2:1b",
    "general": "llama3:latest",
    "coding": "qwen3-coder:30b",
    "vision": "llava:7b",
}

SYSTEM_PROMPTS = {
    "fast": "You are a fast, concise assistant. Give brief, direct answers. If you don't know, say so.",
    "general": "You are a thoughtful assistant. Be thorough but concise. If uncertain, say so.",
    "coding": """You are an expert coding assistant. Write clean, complete, working code.
RULES:
1. Write complete, runnable code - no placeholders or TODOs
2. Prefer Python unless specified otherwise
3. Include comments explaining key decisions
4. Test edge cases
5. If asked to fix a bug, provide the full fixed function/file""",
    "vision": "You are an expert at analyzing images. Describe what you see in detail. Be specific about objects, colors, text, and scene composition.",
}


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass


def ollama_chat(model: str, messages: list, temperature=0.1, timeout=120) -> str:
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


def load_queue():
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE) as f:
                return json.load(f)
        except:
            return []
    return []


def save_queue(queue):
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)


def load_results():
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE) as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_results(results):
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)


def route_task(task: dict) -> str:
    """Determine model tier based on task type."""
    t = task.get("type", "general").lower()
    if t == "vision":
        return "vision"
    elif t == "coding":
        return "coding"
    elif t == "fast":
        return "fast"
    return "general"


def ensure_model(model: str, timeout: int = 300) -> bool:
    """Check if a model is loaded in Ollama, load if not."""
    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/tags",
        headers={"Content-Type": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            models = json.loads(resp.read().decode("utf-8"))
            loaded = [m["name"] for m in models.get("models", [])]
            if model in loaded:
                return True
        # Model not loaded — trigger load via a generate call
        payload = {"model": model, "prompt": "hello", "stream": False}
        data = json.dumps(payload).encode("utf-8")
        load_req = urllib.request.Request(
            f"{OLLAMA_BASE}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(load_req, timeout=timeout) as resp:
            resp.read()
        return True
    except Exception:
        return False


def process_task(task: dict) -> dict:
    """Process a single task and return result."""
    task_id = task.get("id", "unknown")
    task_type = route_task(task)
    model = MODELS[task_type]
    prompt = task.get("prompt", task.get("content", ""))
    context = task.get("context", "")

    log(f"Processing task {task_id} with {model} ({task_type})")

    if not ensure_model(model):
        return {
            "id": task_id,
            "status": "error",
            "model": model,
            "response": f"Failed to load model {model}",
            "completed_at": datetime.now().isoformat(),
        }

    messages = []
    if context:
        messages.append({"role": "system", "content": f"Context:\n{context}"})
    messages.append({"role": "user", "content": prompt})

    timeout = task.get("timeout", 120)
    if task_type == "coding":
        timeout = 180
    elif task_type == "vision":
        timeout = 60

    response = ollama_chat(model, messages, timeout=timeout)

    return {
        "id": task_id,
        "status": "done",
        "model": model,
        "response": response,
        "completed_at": datetime.now().isoformat(),
    }


def dispatch():
    queue = load_queue()
    results = load_results()

    pending = [t for t in queue if t.get("status") == "pending"]
    if not pending:
        return 0

    log(f"Dispatcher found {len(pending)} pending tasks")

    processed = 0
    for task in pending:
        try:
            result = process_task(task)
            results[task["id"]] = result
            task["status"] = "done"
            processed += 1
            log(f"Task {task['id']} completed")
        except Exception as e:
            log(f"Task {task.get('id','?')} failed: {e}")
            task["status"] = "error"
            task["error"] = str(e)

    # Remove completed tasks from queue (keep last 20 errors for review)
    new_queue = [t for t in queue if t.get("status") == "pending"]
    # Re-add tasks that errored but with retry count
    for t in [t for t in queue if t.get("status") == "error"]:
        retry = t.get("retry", 0) + 1
        if retry < 3:
            t["retry"] = retry
            t["status"] = "pending"
            new_queue.append(t)
        else:
            log(f"Task {t['id']} dropped after {retry} retries")

    save_queue(new_queue)
    save_results(results)
    return processed


def status():
    queue = load_queue()
    results = load_results()
    pending = [t for t in queue if t.get("status") == "pending"]
    done = len([r for r in results.values() if r.get("status") == "done"])
    errors = len([r for r in results.values() if r.get("status") == "error"])
    return {
        "pending": len(pending),
        "completed": done,
        "errors": errors,
        "queue": pending,
    }


def add_task(prompt: str, task_type: str = "general", context: str = "", timeout: int = 120) -> str:
    """Add a task to the queue. Returns task ID."""
    queue = load_queue()
    task_id = f"task-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(queue)}"
    task = {
        "id": task_id,
        "type": task_type,
        "prompt": prompt,
        "context": context,
        "timeout": timeout,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }
    queue.append(task)
    save_queue(queue)
    log(f"Added task {task_id}: {task_type} - {prompt[:60]}...")
    return task_id


def get_result(task_id: str):
    results = load_results()
    return results.get(task_id)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "dispatch"

    if cmd == "dispatch":
        count = dispatch()
        print(f"Processed {count} tasks")
    elif cmd == "status":
        s = status()
        print(f"Pending: {s['pending']} | Completed: {s['completed']} | Errors: {s['errors']}")
        if s["pending"]:
            print("\nPending tasks:")
            for t in s["queue"]:
                print(f"  [{t['id']}] {t['type']}: {t.get('prompt','')[:70]}...")
    elif cmd == "add" and len(sys.argv) > 2:
        prompt = " ".join(sys.argv[2:])
        task_type = "general"
        if any(k in prompt.lower() for k in ["code", "python", "script", "fix", "debug"]):
            task_type = "coding"
        tid = add_task(prompt, task_type)
        print(f"Added: {tid}")
    elif cmd == "result" and len(sys.argv) > 2:
        rid = sys.argv[2]
        r = get_result(rid)
        if r:
            print(f"=== {rid} ({r.get('model')}) ===")
            print(r.get("response", "No response"))
        else:
            print("Result not found or task still pending")
    else:
        print("Usage:")
        print("  ollama-dispatcher.py dispatch          # Process pending tasks")
        print("  ollama-dispatcher.py status            # Show queue status")
        print("  ollama-dispatcher.py add <prompt>      # Add a task")
        print("  ollama-dispatcher.py result <id>       # Get task result")

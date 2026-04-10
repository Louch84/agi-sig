#!/usr/bin/env python3
"""
Ollama Autonomous Worker — Long-running daemon that processes tasks.
Keeps models loaded in memory for fast subsequent responses.
"""
import sys
import json
import os
import time
import urllib.request
import urllib.error
import threading
from datetime import datetime

OLLAMA_BASE = "http://localhost:11434"
QUEUE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "task-queue.json")
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "task-results.json")
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "dispatcher.log")

# Model pool — keep these loaded
MODEL_POOL = {
    "fast": {"model": "llama3.2:1b", "loaded": False},
    "general": {"model": "llama3:latest", "loaded": False},
    "coding": {"model": "qwen3-coder:30b", "loaded": False},
    "vision": {"model": "llava:7b", "loaded": False},
}

LOAD_TIMEOUT = 300  # 5 min to load a model
REQUEST_TIMEOUT = 600  # 10 min — qwen3-coder:30b on CPU needs time

loaded_models = {}  # model_name -> True
model_lock = threading.Lock()


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


def ensure_model(model_name: str):
    """Make sure a model is loaded in Ollama."""
    with model_lock:
        if model_name in loaded_models:
            return True
        
        log(f"Loading model: {model_name}...")
        # Hit /api/generate once to trigger load
        payload = {"model": model_name, "prompt": "hello", "stream": False}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_BASE}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=LOAD_TIMEOUT) as resp:
                resp.read()
                loaded_models[model_name] = True
                log(f"Model loaded: {model_name}")
                return True
        except Exception as e:
            log(f"Failed to load {model_name}: {e}")
            return False


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
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE) as f:
                return json.load(f)
        except:
            return []
    return []


def save_queue(queue):
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    tmp = QUEUE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(queue, f, indent=2)
    os.replace(tmp, QUEUE_FILE)  # atomic on POSIX


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
    tmp = RESULTS_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(results, f, indent=2)
    os.replace(tmp, RESULTS_FILE)  # atomic on POSIX


def route_task(task: dict) -> str:
    t = task.get("type", "general").lower()
    if t == "vision":
        return "vision"
    elif t == "coding":
        return "coding"
    elif t == "fast":
        return "fast"
    return "general"


def process_task(task: dict) -> dict:
    task_id = task.get("id", "unknown")
    task_type = route_task(task)
    model_info = MODEL_POOL.get(task_type, MODEL_POOL["general"])
    model = model_info["model"]

    log(f"Processing {task_id} with {model} ({task_type})")

    prompt = task.get("prompt", task.get("content", ""))
    context = task.get("context", "")

    # Ensure model is loaded
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

    timeout = REQUEST_TIMEOUT
    response = ollama_chat(model, messages, timeout=timeout)

    return {
        "id": task_id,
        "status": "done",
        "model": model,
        "response": response,
        "completed_at": datetime.now().isoformat(),
    }


def dispatch_once():
    queue = load_queue()
    results = load_results()
    pending = [t for t in queue if t.get("status") == "pending"]
    if not pending:
        return 0

    processed = 0
    for task in pending:
        try:
            result = process_task(task)
            results[task["id"]] = result
            task["status"] = "done"
            processed += 1
            log(f"Task {task['id']} done")
        except Exception as e:
            log(f"Task {task.get('id','?')} error: {e}")
            task["status"] = "error"
            task["error"] = str(e)

    new_queue = [t for t in queue if t.get("status") == "pending"]
    for t in [t for t in queue if t.get("status") == "error"]:
        retry = t.get("retry", 0) + 1
        if retry < 3:
            t["retry"] = retry
            t["status"] = "pending"
            new_queue.append(t)
        else:
            log(f"Dropping task {t['id']} after {retry} retries")

    save_queue(new_queue)
    save_results(results)
    return processed


def daemon(poll_interval=30):
    log(f"Ollama Autonomous Worker started (poll interval: {poll_interval}s)")
    
    # Pre-load fast model
    ensure_model(MODEL_POOL["fast"]["model"])
    
    while True:
        try:
            count = dispatch_once()
            if count:
                log(f"Processed {count} tasks")
        except Exception as e:
            log(f"Dispatch error: {e}")
        
        time.sleep(poll_interval)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ollama-daemon.py run [poll_secs]   # Run as daemon")
        print("  ollama-daemon.py dispatch          # Process pending tasks once")
        print("  ollama-daemon.py status            # Show queue status")
        print("  ollama-daemon.py add <prompt> [type] # Add task")
        print("  ollama-daemon.py result <id>       # Get result")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "run":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        daemon(interval)
    elif cmd == "dispatch":
        count = dispatch_once()
        print(f"Processed {count} tasks")
    elif cmd == "status":
        queue = load_queue()
        results = load_results()
        pending = [t for t in queue if t.get("status") == "pending"]
        done = len([r for r in results.values() if r.get("status") == "done"])
        errors = len([r for r in results.values() if r.get("status") == "error"])
        print(f"Pending: {len(pending)} | Completed: {done} | Errors: {errors}")
        for t in pending:
            print(f"  [{t['id']}] {t.get('type','general')}: {t.get('prompt','')[:60]}...")
    elif cmd == "add":
        prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        task_type = "general"
        if not prompt:
            print("Usage: add <prompt> [type]")
            sys.exit(1)
        # Auto-detect type
        pl = prompt.lower()
        if any(k in pl for k in ["code", "python", "script", "fix", "debug", "write ", "function"]):
            task_type = "coding"
        elif any(k in pl for k in ["image", "picture", "photo", "screenshot", "see"]):
            task_type = "vision"
        elif any(k in pl for k in ["hi", "hello", "hey", "what is", "who is", "when did"]):
            task_type = "fast"
        
        queue = load_queue()
        task_id = f"task-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(queue)}"
        task = {
            "id": task_id, "type": task_type, "prompt": prompt,
            "context": "", "timeout": 120,
            "status": "pending", "created_at": datetime.now().isoformat(),
        }
        queue.append(task)
        save_queue(queue)
        log(f"Added {task_id} ({task_type}): {prompt[:60]}...")
        print(f"Added: {task_id} [{task_type}]")
    elif cmd == "result":
        rid = sys.argv[2] if len(sys.argv) > 2 else ""
        if not rid:
            print("Usage: result <task_id>")
            sys.exit(1)
        results = load_results()
        r = results.get(rid)
        if r:
            print(f"=== {rid} ({r.get('model')}) [{r.get('status')}] ===")
            print(r.get("response", "No response"))
        else:
            print("Not found or still pending")
    else:
        print(f"Unknown command: {cmd}")

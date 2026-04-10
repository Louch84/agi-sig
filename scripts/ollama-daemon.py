#!/usr/bin/env python3
"""
Ollama Autonomous Worker — Long-running daemon that processes tasks.
Keeps models loaded in memory for fast subsequent responses.
JARVIS-style task planning: complex requests get decomposed before execution.
Learning system: trace logging + feedback-driven routing.
"""
import sys
import json
import os
import time
import urllib.request
import urllib.error
import threading
from datetime import datetime

# Import trace logger
sys.path.insert(0, os.path.dirname(__file__))
try:
    from trace_logger import log_trace, get_routing_hints, load_traces, analyze_routing
    HAS_TRACING = True
except ImportError:
    HAS_TRACING = False

OLLAMA_BASE = "http://localhost:11434"
QUEUE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "task-queue.json")
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "task-results.json")
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "dispatcher.log")
PLANNER_SCRIPT = os.path.join(os.path.dirname(__file__), "task-planner.py")

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


def plan_complex_task(prompt: str) -> dict:
    """Use JARVIS-style task planning for complex requests."""
    import subprocess

    try:
        result = subprocess.run(
            ["python3", PLANNER_SCRIPT, prompt],
            capture_output=True,
            text=True,
            timeout=90,
        )
        output = result.stdout.strip()

        # Extract JSON from output
        lines = output.split("\n")
        json_start = -1
        json_end = len(lines)
        for i, line in enumerate(lines):
            if line.strip().startswith("{"):
                json_start = i
            if line.strip() == "}" and json_start >= 0:
                json_end = i + 1
                break

        if json_start >= 0:
            json_text = "\n".join(lines[json_start:json_end])
            plan = json.loads(json_text)
            return plan
        return None
    except Exception as e:
        log(f"Planner error: {e}")
        return None


def process_task_with_planner(task: dict) -> dict:
    """Process a task using JARVIS-style decomposition for complex requests."""
    task_id = task.get("id", "unknown")
    prompt = task.get("prompt", task.get("content", ""))

    # Check if task is complex enough to warrant planning
    complexity_indicators = [" and ", " also ", " plus ", " then ", " after ",
                              "fix", "write", "build", "create", "research",
                              "analyze", "compare", "audit", "review"]
    is_complex = sum(1 for i in complexity_indicators if i in prompt.lower()) >= 2

    if not is_complex:
        # Simple task — process directly
        return process_task_simple(task)

    log(f"Task {task_id} is complex — running JARVIS-style planner")
    plan = plan_complex_task(prompt)

    if not plan or "subtasks" not in plan:
        log(f"Planner failed for {task_id}, falling back to direct execution")
        return process_task(task)

    log(f"Plan: {plan.get('summary', 'N/A')} — {len(plan['subtasks'])} subtasks")

    subtask_results = []
    completed = set()

    for iteration in range(len(plan["subtasks"]) * 2):
        for subtask in plan["subtasks"]:
            tid = subtask["id"]
            if tid in completed:
                continue

            deps = subtask.get("depends_on", [])
            if not all(d in completed for d in deps):
                continue

            # Build context from completed subtask results
            context_parts = []
            for prev_result in subtask_results:
                if prev_result["subtask_id"] in deps:
                    context_parts.append(f"[Subtask {prev_result['subtask_id']}]: {prev_result.get('output', '')[:500]}")

            context = "\n".join(context_parts)

            # Execute subtask
            sub_result = execute_subtask(subtask, context)
            sub_result["subtask_id"] = tid
            subtask_results.append(sub_result)

            if sub_result.get("status") == "done":
                completed.add(tid)

        if len(completed) >= len(plan["subtasks"]):
            break

    # Synthesize results
    synthesis = synthesize_results(plan, subtask_results)

    return {
        "id": task_id,
        "status": "done",
        "model": "planner:" + ",".join([s.get("model", "?") for s in subtask_results]),
        "response": synthesis,
        "plan": plan,
        "subtask_results": subtask_results,
        "completed_at": datetime.now().isoformat(),
    }


def execute_subtask(subtask: dict, context: str = "") -> dict:
    """Execute a single subtask."""
    model_info = MODEL_POOL.get(subtask.get("type", "general"), MODEL_POOL["general"])
    model = model_info["model"]
    task_type = subtask.get("type", "general")

    prompt = subtask.get("description", "")
    if context:
        prompt = f"Context from previous steps:\n{context}\n\nTask: {prompt}"

    if not ensure_model(model):
        return {"status": "error", "model": model, "output": f"Failed to load {model}"}

    messages = [{"role": "user", "content": prompt}]
    start = time.time()
    response = ollama_chat(model, messages, timeout=REQUEST_TIMEOUT)
    duration_ms = int((time.time() - start) * 1000)

    success = not response.startswith("[Error]")
    if HAS_TRACING:
        sub_id = f"subtask-{subtask.get('id', 0)}"
        log_trace(sub_id, model, task_type, prompt, response, duration_ms, success)

    return {"status": "done", "model": model, "output": response}


def synthesize_results(plan: dict, subtask_results: list) -> str:
    """Use llama3 to synthesize subtask results into a coherent response."""
    if len(subtask_results) == 1:
        return subtask_results[0].get("output", "")

    synthesis_prompt = f"Original request: {plan.get('summary', '')}\n\n"
    synthesis_prompt += "Subtask results:\n"
    for r in subtask_results:
        synthesis_prompt += f"- {r.get('output', '')}\n\n"
    synthesis_prompt += "Synthesize all results into a single, coherent answer to the original request."

    messages = [{"role": "user", "content": synthesis_prompt}]
    result = ollama_chat(MODEL_POOL["general"]["model"], messages, timeout=REQUEST_TIMEOUT)
    return result


def process_task_simple(task: dict) -> dict:
    """Direct execution for simple tasks — no planning."""
    task_id = task.get("id", "unknown")
    task_type = route_task(task)
    
    # Learning: check routing hints for best model for this task type
    if HAS_TRACING:
        hints = get_routing_hints()
        if task_type in hints:
            hinted_model = hints[task_type]
            if hinted_model in [m["model"] for m in MODEL_POOL.values()]:
                model = hinted_model
                log(f"Routing {task_id} to {model} (learned hint for {task_type})")
            else:
                model_info = MODEL_POOL.get(task_type, MODEL_POOL["general"])
                model = model_info["model"]
        else:
            model_info = MODEL_POOL.get(task_type, MODEL_POOL["general"])
            model = model_info["model"]
    else:
        model_info = MODEL_POOL.get(task_type, MODEL_POOL["general"])
        model = model_info["model"]

    log(f"Processing {task_id} with {model} ({task_type})")

    prompt = task.get("prompt", task.get("content", ""))
    context = task.get("context", "")

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

    start = time.time()
    response = ollama_chat(model, messages, timeout=REQUEST_TIMEOUT)
    duration_ms = int((time.time() - start) * 1000)

    success = not response.startswith("[Error]")

    # Log trace for learning
    if HAS_TRACING:
        log_trace(task_id, model, task_type, prompt, response, duration_ms, success)

    return {
        "id": task_id,
        "status": "done",
        "model": model,
        "response": response,
        "completed_at": datetime.now().isoformat(),
    }


def process_task(task: dict) -> dict:
    """Entry point — uses JARVIS-style planning for complex tasks."""
    prompt = task.get("prompt", task.get("content", ""))

    # Simple tasks: 2 or fewer complexity indicators
    complexity_indicators = [" and ", " also ", " plus ", " then ", " after ",
                              "fix", "write", "build", "create", "research",
                              "analyze", "compare", "audit", "review"]
    complexity_score = sum(1 for i in complexity_indicators if i in prompt.lower())

    if complexity_score >= 2:
        return process_task_with_planner(task)
    else:
        return process_task_simple(task)


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
    elif cmd == "feedback":
        # Allow rating a task outcome to improve routing
        rid = sys.argv[2] if len(sys.argv) > 2 else ""
        rating = sys.argv[3] if len(sys.argv) > 3 else ""
        if not rid or not rating:
            print("Usage: feedback <task_id> <good|bad>")
            sys.exit(1)
        if rating not in ("good", "bad"):
            print("Rating must be: good | bad")
            sys.exit(1)
        if HAS_TRACING:
            traces = load_traces(limit=1000)
            # Find and update matching trace
            updated = False
            updated_traces = []
            for t in traces:
                if t.get("task_id") == rid:
                    t["feedback"] = rating
                    t["feedback_time"] = datetime.now().isoformat()
                    updated = True
                updated_traces.append(t)
            if updated:
                # Rewrite traces (append-only would be better with a proper DB)
                with open(os.path.join(os.path.dirname(__file__), "..", "data", "traces", "traces.jsonl"), "w") as f:
                    for t in updated_traces:
                        f.write(json.dumps(t) + "\n")
                print(f"✅ Feedback recorded: {rid} rated {rating}")
            else:
                print(f"Task {rid} not found in recent traces")
        else:
            print("Tracing not available")
    elif cmd == "analyze":
        if HAS_TRACING:
            recs = analyze_routing()
            print("=== Model Routing Analysis ===")
            for tt, data in recs.items():
                print(f"\n[{tt}] → {data['recommended_model']} (score: {data['score']:.2f})")
                for m, s in data["models"].items():
                    print(f"  {m}: {s['success_rate']}% success, {s['avg_duration_ms']}ms avg, {s['count']} runs")
        else:
            print("Tracing not available")
    else:
        print(f"Unknown command: {cmd}")

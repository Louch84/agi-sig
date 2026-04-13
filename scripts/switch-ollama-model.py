#!/usr/bin/env python3
"""
Switch between local Ollama model modes for 8GB MacBook Air.
Usage: python3 switch-ollama-model.py [fast|quality|status]

fast   — qwen2.5:0.5b (397MB, sub-second, good enough for日常)
quality — llama3:latest (4.6GB, 10-30s response, much better reasoning)
status  — show current model + memory
"""
import subprocess
import sys
import time
import json
import os

OLLAMA_API = "http://127.0.0.1:11434"
WORKSPACE = os.path.dirname(os.path.dirname(__file__))
DAEMON_CFG = os.path.join(WORKSPACE, "scripts", "ollama-daemon.py")

MODELS = {
    "fast": {
        "model": "qwen2.5:0.5b",
        "desc": "qwen2.5:0.5b — 397MB, sub-second响应",
        "size_mb": 397,
    },
    "quality": {
        "model": "llama3:latest",
        "desc": "llama3:latest — 4.6GB, 10-30s response, much better reasoning",
        "size_mb": 4600,
    },
}


def curl_post(endpoint, payload, timeout=60):
    data = json.dumps(payload).encode()
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", str(timeout), "-X", "POST",
             f"{OLLAMA_API}{endpoint}",
             "-H", "Content-Type: application/json",
             "-d", data],
            capture_output=True, text=True, timeout=timeout + 5
        )
        if result.stdout:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"  ERROR: {e}")
    return None


def curl_get(endpoint, timeout=10):
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", str(timeout), f"{OLLAMA_API}{endpoint}"],
            capture_output=True, text=True, timeout=timeout + 5
        )
        if result.stdout:
            return json.loads(result.stdout)
    except:
        pass
    return None


def get_current_model():
    """Check which model is currently loaded."""
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "5", f"{OLLAMA_API}/api/tags"],
            capture_output=True, text=True, timeout=10
        )
        # Trigger a fast generation to see what's loaded
        resp = curl_post("/api/generate",
                         {"model": "qwen2.5:0.5b", "prompt": "hi", "stream": False},
                         timeout=10)
        if resp and "error" not in resp:
            return "qwen2.5:0.5b"
    except:
        pass

    # Check if llama3 is responsive
    resp = curl_post("/api/generate",
                     {"model": "llama3:latest", "prompt": "hi", "stream": False},
                     timeout=30)
    if resp and "error" not in resp:
        return "llama3:latest"

    return "unknown"


def get_memory():
    """Get free memory from system."""
    try:
        result = subprocess.run(
            ["sysctl", "-a"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split("\n"):
            if "hw.memsize" in line:
                total_gb = int(line.split(":")[1].strip()) / (1024**3)
            if "HW_MEMSIZE" in line:
                total_gb = int(line.split(":")[1].strip()) / (1024**3)
    except:
        total_gb = 8.0

    # Check free memory via vm_stat
    try:
        result = subprocess.run(
            ["vm_stat"],
            capture_output=True, text=True, timeout=5
        )
        free_mb = 0
        for line in result.stdout.split("\n"):
            if "Pages free" in line or "Pages inactive" in line:
                parts = line.split(":")
                if len(parts) == 2:
                    pages = int(parts[1].strip().rstrip("."))
                    free_mb += pages * 4096 / (1024**2)
    except:
        free_mb = 2900

    return total_gb, free_mb


def switch_to(mode):
    """Switch to the specified model mode."""
    if mode not in MODELS:
        print(f"Unknown mode: {mode}")
        return False

    cfg = MODELS[mode]
    target = cfg["model"]
    print(f"\n🔄 Switching to {cfg['desc']}...")

    # Check memory
    total_gb, free_mb = get_memory()
    required_mb = cfg["size_mb"]
    if free_mb < required_mb * 1.5:
        print(f"  ⚠️  Low memory: {free_mb:.0f}MB free, {required_mb}MB needed.")
        print(f"  Trying anyway...")

    # Kill existing runners
    print("  Killing existing runners...")
    subprocess.run(["pkill", "-f", "ollama runner"], capture_output=True)
    time.sleep(2)

    # Load the target model
    print(f"  Loading {target} (may take 10-60s for llama3)...")
    resp = curl_post("/api/generate",
                     {"model": target, "prompt": "respond with OK", "stream": False},
                     timeout=120)
    if resp and "error" not in resp:
        print(f"  ✅ {target} loaded successfully")
        return True
    elif resp and "error" in resp:
        print(f"  ❌ Error: {resp['error']}")
        return False
    else:
        print(f"  ❌ No response from Ollama")
        return False


def show_status():
    """Show current model and memory status."""
    total_gb, free_mb = get_memory()
    current = get_current_model()

    print(f"\n📊 Ollama Status")
    print(f"  RAM: {total_gb:.1f}GB total / ~{free_mb:.0f}MB free")
    print(f"  Current model: {current}")
    print(f"\nAvailable modes:")
    for m, cfg in MODELS.items():
        marker = "◀ current" if cfg["model"] == current else ""
        print(f"  [{m}] {cfg['desc']} {marker}")
    print(f"\nUsage: python3 switch-ollama-model.py [fast|quality|status]")
    return True


def update_daemon_config(mode):
    """Update the daemon MODEL_POOL to match the switched mode."""
    if mode == "fast":
        pool_model = "qwen2.5:0.5b"
    else:
        pool_model = "llama3:latest"

    try:
        with open(DAEMON_CFG) as f:
            content = f.read()
    except:
        return

    # Find and replace MODEL_POOL
    import re
    new_pool = f'''# Model pool — tuned for 8GB MacBook Air (no GPU, no swap)
# Only ONE model loaded at a time to avoid OOM
MODEL_POOL = {{
    "fast": {{"model": "{pool_model}", "loaded": False}},
    "general": {{"model": "{pool_model}", "loaded": False}},
    "coding": {{"model": "{pool_model}", "loaded": False}},
}}'''
    # Only replace the MODEL_POOL block
    pattern = r'(# Model pool.*?)^[ ]*}'
    if re.search(pattern, content, re.MULTILINE | re.DOTALL):
        content = re.sub(pattern, new_pool + "}", content, flags=re.MULTILINE | re.DOTALL)
        with open(DAEMON_CFG, "w") as f:
            f.write(content)
        print(f"  ✅ Daemon config updated to use {pool_model}")
    else:
        print(f"  ⚠️  Could not update daemon config automatically")


def main():
    if len(sys.argv) < 2:
        return show_status()

    cmd = sys.argv[1].lower()

    if cmd == "status":
        return show_status()
    elif cmd in MODELS:
        ok = switch_to(cmd)
        if ok:
            update_daemon_config(cmd)
        return 0 if ok else 1
    else:
        print(f"Unknown command: {cmd}")
        print(f"Usage: python3 switch-ollama-model.py [fast|quality|status]")
        return 1


if __name__ == "__main__":
    sys.exit(main())

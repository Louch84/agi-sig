#!/usr/bin/env python3
"""Quick system health check."""
import subprocess
import sys
import os

WORKSPACE = "/Users/sigbotti/.openclaw/workspace"

def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=WORKSPACE)
        return r.returncode == 0, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "TIMEOUT"
    except Exception as e:
        return False, "", str(e)

checks = [
    ("Git workspace clean", lambda: run("git status --short")[0]),
    ("Ollama responding", lambda: run("curl -s http://localhost:11434/api/tags")[0]),
    ("blogwatcher installed", lambda: run("which blogwatcher")[0]),
    ("RSS feeds configured", lambda: len(run("blogwatcher blogs 2>/dev/null")[1]) > 10),
    ("Python3 available", lambda: run("python3 --version")[0]),
    ("Vector memory script exists", lambda: os.path.exists(f"{WORKSPACE}/scripts/ollama_mem.py")),
]

print("=" * 50)
print("QUICK CHECK")
print("=" * 50)
passed = 0
for name, check in checks:
    try:
        ok = check()
        status = "PASS" if ok else "FAIL"
        if ok: passed += 1
        print(f"  [{status}] {name}")
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
print()
print(f"Result: {passed}/{len(checks)} passed")

#!/usr/bin/env python3
"""
Ollama Daemon Watchdog — keeps the autonomous worker alive.
Run as a LaunchAgent or via cron. Checks every 5 minutes.
"""
import os
import sys
import time
import signal
import subprocess

PID_FILE = "/tmp/ollama-daemon.pid"
LOG_FILE = "/Users/sigbotti/.openclaw/logs/watchdog.log"
START_SCRIPT = "/Users/sigbotti/.openclaw/workspace/scripts/start-ollama-daemon.sh"
WORKSPACE = "/Users/sigbotti/.openclaw/workspace"
CHECK_INTERVAL = 300  # 5 minutes


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def is_alive():
    """Check if daemon process is actually running."""
    if not os.path.exists(PID_FILE):
        return False
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return True
    except:
        return False


def restart_daemon():
    """Restart the Ollama daemon via start script."""
    log("Daemon dead — restarting...")
    # Kill any stale processes
    subprocess.run(["pkill", "-9", "-f", "ollama-daemon.py"], capture_output=True)
    time.sleep(2)
    # Start fresh
    result = subprocess.run(
        ["bash", START_SCRIPT],
        capture_output=True, text=True, cwd=WORKSPACE
    )
    if result.returncode == 0:
        log("Daemon restarted successfully")
    else:
        log(f"Restart failed: {result.stderr[:200]}")


def main():
    if is_alive():
        log("Daemon alive — no action needed")
        return
    
    restart_daemon()


if __name__ == "__main__":
    main()

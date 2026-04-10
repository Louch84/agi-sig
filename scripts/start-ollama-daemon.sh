#!/bin/bash
# Start Ollama Autonomous Worker daemon
# Run this at login or via LaunchAgent

DAEMON_SCRIPT="/Users/sigbotti/.openclaw/workspace/scripts/ollama-daemon.py"
LOG_DIR="/Users/sigbotti/.openclaw/workspace/logs"
PID_FILE="/tmp/ollama-daemon.pid"

# Check if already running
if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
    echo "Ollama daemon already running (PID $(cat $PID_FILE))"
    exit 0
fi

mkdir -p "$LOG_DIR"
nohup python3 "$DAEMON_SCRIPT" run 30 >> "$LOG_DIR/ollama-daemon.log" 2>&1 &
echo $! > "$PID_FILE"
echo "Ollama daemon started (PID $(cat $PID_FILE))"

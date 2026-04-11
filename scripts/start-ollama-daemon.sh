#!/bin/bash
# Start Ollama Autonomous Worker daemon
# Run this at login or via LaunchAgent
# Includes pre-flight check: verifies Ollama server is healthy before starting daemon

DAEMON_SCRIPT="/Users/sigbotti/.openclaw/workspace/scripts/ollama-daemon.py"
LOG_DIR="/Users/sigbotti/.openclaw/workspace/logs"
PID_FILE="/tmp/ollama-daemon.pid"
WORKSPACE="/Users/sigbotti/.openclaw/workspace"
OLLAMA_BASE="http://localhost:11434"
MAX_RETRIES=12
RETRY_INTERVAL=5

# ── Pre-flight: verify Ollama server is running ──────────────────────────────
echo "[$(date)] Checking Ollama server availability..."

for i in $(seq 1 $MAX_RETRIES); do
    if curl -s --max-time 5 "$OLLAMA_BASE/api/tags" > /dev/null 2>&1; then
        echo "[$(date)] Ollama server is healthy"
        break
    fi
    
    if [ $i -eq $MAX_RETRIES ]; then
        echo "[$(date)] FATAL: Ollama server not reachable after ${MAX_RETRIES} attempts"
        echo "[$(date)] Start Ollama first: ollama serve"
        exit 1
    fi
    
    echo "[$(date)] Ollama not ready (attempt $i/${MAX_RETRIES}), waiting ${RETRY_INTERVAL}s..."
    sleep $RETRY_INTERVAL
done

# ── Check if already running ─────────────────────────────────────────────────
if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
    echo "[$(date)] Ollama daemon already running (PID $(cat $PID_FILE))"
    exit 0
fi

# ── Start daemon ─────────────────────────────────────────────────────────────
mkdir -p "$LOG_DIR"
cd "$WORKSPACE"

nohup python3 "$DAEMON_SCRIPT" run 30 >> "$LOG_DIR/ollama-daemon.log" 2>&1 &
DAEMON_PID=$!
echo $DAEMON_PID > "$PID_FILE"

echo "[$(date)] Ollama daemon started (PID $DAEMON_PID)"

# ── Verify daemon started successfully ────────────────────────────────────────
sleep 3
if kill -0 $DAEMON_PID 2>/dev/null; then
    echo "[$(date)] Daemon verified alive"
else
    echo "[$(date)] WARNING: Daemon exited immediately — check $LOG_DIR/ollama-daemon.log"
    exit 1
fi

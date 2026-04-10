#!/bin/bash
# LCM Heartbeat — compact messages + sync decisions to MEMORY.md
# Run from workspace root

SKILL_DIR="/Users/sigbotti/.openclaw/workspace/skills/memory-lcm"
SESSION="${1:-main}"
LCM="node $SKILL_DIR/bin/tony-lcm.js"
DATA_DIR="$HOME/.openclaw/workspace/data"
STATE_FILE="$DATA_DIR/lcm-daily-state.json"

mkdir -p "$DATA_DIR"

echo "=== LCM Heartbeat ==="

# Check stats first
STATS=$($LCM status 2>/dev/null)
TOTAL=$(echo "$STATS" | awk '/Total messages/{print $NF}')
ACTIVE=$(echo "$STATS" | awk '/Active/{for(i=1;i<=NF;i++) if($i~/^[0-9]+$/) print $i}')

echo "Total: $TOTAL | Active: $ACTIVE"

# Compact if we have enough uncompacted messages
if [ -n "$ACTIVE" ] && [ "$ACTIVE" -gt 15 ]; then
  echo "Compacting $ACTIVE messages..."
  $LCM compact $SESSION 2>/dev/null
  echo "Syncing decisions to MEMORY.md..."
  $LCM sync $SESSION 2>/dev/null
else
  echo "Not enough messages to compact (threshold: 15)"
fi

# Daily summary (runs once per day)
TODAY=$(date +%Y-%m-%d)
LAST_RUN=""
[ -f "$STATE_FILE" ] && LAST_RUN=$(awk -F'"date":"' '{print $2}' "$STATE_FILE" 2>/dev/null | awk -F'"' '{print $1}')

if [ "$LAST_RUN" != "$TODAY" ]; then
  echo "Running daily summary..."
  $LCM daily $SESSION 2>/dev/null
  echo "{\"date\":\"$TODAY\"}" > "$STATE_FILE"
  echo "Daily summary complete."
else
  echo "Daily already run today ($LAST_RUN)"
fi

echo "=== Done ==="

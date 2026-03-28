#!/bin/bash
# auto-backup.sh — Commit and push current state to agi-sig
# Run via cron or heartbeat. Ensures state survives gateway restart.
# Usage: ./auto-backup.sh

set -e

WORKSPACE="/Users/sigbotti/.openclaw/workspace"
cd "$WORKSPACE"

GIT_STATUS=$(git status --short)
if [ -n "$GIT_STATUS" ]; then
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
    git add -A
    git commit -m "Auto-backup: $TIMESTAMP"
    git push origin main 2>&1 || echo "Push failed — will retry next cycle"
    echo "[$TIMESTAMP] Backed up: $GIT_STATUS"
else
    # Still push if we're ahead of remote
    git push origin main 2>&1 || true
fi

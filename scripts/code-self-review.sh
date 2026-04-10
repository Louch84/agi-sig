#!/bin/bash
# Daily Code Self-Review — queues a code audit task for the Ollama autonomous worker
# Runs every day at 2AM ET (when you're asleep and CPU is free)

AUDIT_SCRIPT="/Users/sigbotti/.openclaw/workspace/scripts/ollama-daemon.py"
WORKSPACE="/Users/sigbotti/.openclaw/workspace"

AUDIT_PROMPT="You are a senior code reviewer. Audit the Sig Botti agent codebase at /Users/sigbotti/.openclaw/workspace/.

Focus on:
1. Bugs, errors, race conditions, missing error handling
2. Performance issues (N+1 queries, inefficient loops, memory leaks)
3. Security vulnerabilities (hardcoded secrets, injection risks, path traversal)
4. Code smells ( duplicated code, overly complex functions, magic numbers)
5. Missing tests or documentation

For each issue found, provide:
- File and line number
- Severity (critical/high/medium/low)
- Description of the problem
- Specific fix with code

Also identify the top 3 most impactful improvements and implement them directly in the code files.

Be thorough but practical — fix real problems, don't bikeshed."

echo "[$(date)] Daily code self-review: queuing audit task..."
python3 "$AUDIT_SCRIPT" add "$AUDIT_PROMPT" coding
echo "[$(date)] Audit task queued."

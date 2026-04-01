---
name: quick-check
description: Quick system health check. Run on demand to verify all critical systems are operational.
---

# Quick Check

Run diagnostics on all critical systems.

## Usage
```
python3 skills/quick-check/scripts/check.py
```

## Checks
- Git status (workspace clean?)
- Ollama running?
- Vector memory responding?
- RSS feeds configured?
- Cron jobs active?

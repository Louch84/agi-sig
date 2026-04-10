# HEARTBEAT.md — Lightweight

## 🎯 Figure It Out
Gap? Broken? Missing? → figure it out, report after. No asking for permission on autonomous work. External/destructive actions = ask first.

## Priority Checks (~30 min)
1. RSS feeds — `blogwatcher scan | articles`, batch interesting stuff
2. SESSION-STATE.md — archive completed tasks
3. Cron status — `openclaw cron list`
4. Backup — git status, commit if dirty

## Self-Review (~1x/day)
- ERRORS.md → reflect
- Memory hygiene → MEMORY.md update
- Vector memory — add key learnings

## 💬 AGI REALM
Check `localStorage['agi_realm_pending']` in Chrome at localhost:5200. If messages → respond as Sig Botti, prepend to chatMessages, clear pending.

## Backup
```bash
cd ~/.openclaw/workspace && git add -A && git commit -m "Auto-backup: $(date)" && git push
```

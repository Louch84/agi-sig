# HEARTBEAT.md — Lightweight

## 🎯 Figure It Out
Gap? Broken? Missing? → figure it out, report after. No asking for permission on autonomous work. External/destructive actions = ask first.

## Priority Checks (~30 min)
1. RSS feeds — `blogwatcher scan | articles`, batch interesting stuff
2. SESSION-STATE.md — archive completed tasks
3. **LCM compact** — `bash scripts/lcm-heartbeat.sh main` (compacts if >15 msgs, syncs decisions to MEMORY.md)
4. **Autonomous tasks** — check `scripts/ollama-daemon.py status` for pending/completed results, report if significant
5. **Self-improve check** — `python3 scripts/self_improve.py --check` (triggers mini/full reflection every 10/50 episodes)
6. Cron status — `openclaw cron list`
7. Backup — git status, commit if dirty

## Daily (~1x/day)
- **Rebuild vector index** — `python3 scripts/build-vector-index.py build` (re-index MEMORY.md + daily logs + skills for RAG)
- **Auto-daily-log** — fires at 9PM ET via LaunchAgent (`ai.openclaw.auto-daily-log`) regardless of agent activity. Captures git commits, tasks, crons, traces. Prevents weekend logging gaps.
- **World model update** — `python3 scripts/self_improve.py --update-world-model` (push recent events to world model)

## Weekly (~1x/week)
- **Full reflection analysis** — `python3 scripts/reflection_analyzer.py --write-report --update-memory --days 7`
- **Model routing recalibration** — `python3 scripts/self_improve.py --recalibrate`
- Check `memory/reflection-log.md` for patterns

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

## Self-Improvement Loop (Hermes Pattern)
The complete observe → reflect → optimize cycle:

1. **Observe** — `episode_logger.py` logs every task execution (daemon auto-logs, or manual: `python3 scripts/episode_logger.py --task-type X --description "Y" --outcome Z`)
2. **Reflect** — `reflection_analyzer.py` analyzes patterns (`--days 7 --write-report --update-memory`)
3. **Optimize** — `self_improve.py` triggers improvements, world model updates, routing recalibration

Run manually: `python3 scripts/self_improve.py --full`

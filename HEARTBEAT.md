# HEARTBEAT.md

## Priority Checks (every heartbeat, ~30 min)

1. **RSS feeds** — run `blogwatcher scan` and `blogwatcher articles`. If new articles found, decide: read now or batch for later.
2. **SESSION-STATE.md** — check for stale state, archive completed tasks
3. **Cron jobs** — verify daily self-review at 9AM ET is still scheduled (`openclaw cron list`)

## Self-Review Checks (~1x/day)

1. **Check ERRORS.md** — any new errors to reflect on?
2. **Memory hygiene** — consolidate insights from recent daily logs into MEMORY.md
3. **Vector memory** — add significant learnings via `python3 scripts/ollama_mem.py add`
4. **Gap tracker** — update any gaps closed or new gaps discovered
5. **If significant improvement made** → log to INSIGHTS.md

## Proactive Autonomy (~2-4x/day when idle)

When running heartbeat and nothing urgent is pending:
- Scan RSS feeds (blogwatcher scan)
- Check memory/YYYY-MM-DD.md for recent context
- Look for stale state in SESSION-STATE.md
- Add important context to vector memory

## Information Sources

- RSS: HackerNews, Reddit AI, VentureBeat AI News (via blogwatcher)
- Web search: DuckDuckGo (default), Perplexity (if API key set)
- Vector memory: `python3 scripts/ollama_mem.py add "text" --category X --importance 0.9`

## Cron Monitoring

Verify these crons are live:
- Daily Sig Botti Self-Review: 9:00 AM ET (isolated, Discord announce)

Check: `openclaw cron list`

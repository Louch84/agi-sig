# Gaps Pending — 2026-04-11

## CRITICAL

### Gap: Ollama Daemon LaunchAgent Restart Loop
**What it should be:** Daemon running as a stable long-lived process via LaunchAgent with KeepAlive
**What's happening:** LaunchAgent is in a restart loop — 8,509 restarts logged since ~22:57 on Apr 10. Daemon not currently running (was dead before this audit session)
**Why it matters:** The entire autonomous worker infrastructure (JARVIS planner, trace logger, Ollama routing) is non-functional when the daemon is dead. Lou's local LLM infrastructure is offline.

**Root cause:** The `start-ollama-daemon.sh` script uses `nohup ... &` but the LaunchAgent ThrottleInterval defaults to 10s. If daemon exits fast (e.g. model load fails silently), launchd loops. Also: the daemon's own log (dispatcher.log) shows NO error entries from LaunchAgent restarts — only successful starts with manual invocations.

**Fix needed:** 
1. Add `ThrottleInterval` to plist to prevent restart loops: `<key>ThrottleInterval</key><integer>60</integer>`
2. Ensure daemon logs to a place LaunchAgent can capture stderr for debugging
3. Add a pre-flight check that Ollama server is reachable before starting daemon

---

### Gap: self_improve.py --check returns nothing
**What it should be:** `python3 scripts/self_improve.py --check` outputs episode count and any reflection triggers
**What's happening:** Returns zero output to stdout (checked: empty)
**Why it matters:** The self-improvement loop can't self-trigger. The `--check` path is used by the daemon after every dispatch cycle to decide if reflection is needed.
**Root cause:** `count_episodes()` → `load_episodes()` → file path is `EPISODE_LOG = "data/episodes/episodes.jsonl"` (relative). When running from different CWD, file not found → returns 0 episodes → check_and_trigger_reflection() silently returns without printing anything.
**Fix:** Absolute paths in episode_logger.py OR ensure scripts always run from workspace root.

---

## HIGH

### Gap: Episode Logger Only Has 2 Episodes
**What it should be:** Episodic memory logging every meaningful task execution
**What's happening:** Only 2 episodes total in `episodes.jsonl` — both from Apr 10 test runs. Zero real tasks logged.
**Why it matters:** The Hermes self-improvement loop (observe → reflect → optimize) has no data. Self-improvement is core to Sig Botti's AGI mission.
**Root cause:** Episode logger was never wired into actual task execution paths. The `ollama-daemon.py` logs episodes, but the main agent (MiniMax-M2.7 via OpenClaw) doesn't call `log_episode()` after any tasks.

**Fix:** Either: (a) hook episode_logger into OpenClaw's response path, or (b) have the daily self-review call `self_improve.py --check` which would at least count and reflect on whatever episodes do exist.

---

### Gap: Trace Logger Has Only 1 Trace
**What it should be:** Every Ollama task logged with model/duration/success for routing analysis
**What's happening:** `traces.jsonl` has 1 trace from a test on Apr 10. The `ollama-daemon.py` calls `log_trace()` but only in `execute_subtask()` and `process_task_simple()`. The daemon was dead most of the time.
**Why it matters:** Model routing (learned hints per task type) can't work with 1 trace. The `analyze_routing()` function needs at least 10 traces to make recommendations.
**Fix:** Depends on daemon being alive + real task volume. Lower priority while daemon is unstable.

---

### Gap: Vector Memory Index Not Rebuilt Daily
**What it should be:** `data/memory.index` rebuilt ~1x/day via heartbeat or daily cron
**What's happening:** Last built Apr 10 at 18:33 (~6 hours before this audit). No cron or heartbeat triggers it automatically.
**Why it matters:** RAG/vector memory recall degrades as memory files grow. New memories can't be retrieved semantically until index is rebuilt.
**Fix:** Add `python3 scripts/build-vector-index.py build` to daily cron OR add to HEARTBEAT.md loop. Currently HEARTBEAT.md says it should run but no script is wired.

---

## MODERATE

### Gap: Daily Code Self-Audit Cron — Timeout Issue (MONITORING)
**What it should be:** Fires daily at 2AM ET, audits all Python scripts for bugs and implements fixes.
**What was happening (Apr 11):** Status "idle", Last = "-" — never fired. Root cause: CWD/path issue in isolated session.
**What is happening (Apr 13):** Now firing and RUNNING (status changed from idle to error). At 2AM ET Apr 13: ran for full 599,994ms (10 min) and timed out. Audit completed successfully but got killed before delivery. Confirmed: script works, just too slow for 10-min window.
**Fix applied (2026-04-13):** Extended timeout from 600s to 1200s (20 minutes) via `openclaw cron edit <id> --timeout-seconds 1200`.
**Still needed:** Monitor next run (Apr 14 2AM ET) — if it still times out at 20 min, the isolated session may need different approach (e.g., break audit into smaller chunks, or use a faster model for code review).

---

### Gap: Sunday Night Scanner — No Recent Runs
**What it should be:** Fires every Sunday at midnight ET
**What's happening:** Last run 5 days ago (Apr 6 = Monday). Should have run Apr 6 (Sunday) but shows last as "5d ago" which would be Apr 6 if today is Apr 11.
**Why it matters:** Weekly scanner is a core system — Lou's trading strategy depends on it.
**Status:** Cron shows "ok" — likely the scan completes but announce step fails (same structural issue from Apr 10 review).

---

### Gap: Duplicate Infrastructure — ollama-dispatcher.py
**What it should be:** One autonomous worker implementation
**What's happening:** Both `ollama-dispatcher.py` AND `ollama-daemon.py` exist. Logs show both writing to `dispatcher.log`. The dispatcher is an older version.
**Why it matters:** Confusion about which is primary. Dead code that might get invoked accidentally.
**Fix:** Remove `ollama-dispatcher.py` after confirming `ollama-daemon.py` is stable.

---

### Gap: world-model.py CLI — Duplicate Subparser Bug (FIXED 2026-04-13)
**What it should be:** `python3 scripts/world-model.py context <topic>` returns structured world model knowledge
**What was happening:** `ValueError: conflicting subparser: context` — line 282 and 286 both defined `context` subparser. First definition (no args) conflicted with second (with args).
**Why it mattered:** World model CLI completely broken. Could not query structured knowledge.
**Fix (2026-04-13):** Removed duplicate line 282. Verified working: `world-model.py context ai` now returns structured data.
**Note:** The `ollama-daemon.py` `retrieve_memory()` function had been suspected of `np` import bug, but code inspection shows import is correctly placed inside try block before usage. The real bug was the CLI subparser conflict.

---

## LOW

### Gap: gap-alert-state.json — State File Staleness
**What it should be:** `last_run` field updated after each scan
**What's happening:** Field is `last_scan` (not `last_run`). State file is 6KB with data from Apr 10 23:05 — recent, but the `last_run: never / Errors: 0` confusion in the scanner suggests the state writer might be skipping fields.
**Why it matters:** Gap alert decisions depend on state (don't rescan same stocks too frequently). If state is misinterpreted, duplicate alerts possible.

---

### Gap: HEARTBEAT.md Mentions Vector Rebuild But It's Not Wired
**What it should be:** Heartbeat checks and triggers vector index rebuild ~1x/day
**What's happening:** HEARTBEAT.md describes the rebuild step but no actual heartbeat run triggers it.
**Why it matters:** Drift between documented behavior and actual behavior erodes trust in the system.

---

## Duplicate Cron Jobs

| Job | Schedule | Notes |
|-----|----------|-------|
| Daily Code Self-Audit | 0 2 * * * ET | Idle/never run (CWD issue) |
| Daily Sig Botti Self-Review | 0 9 * * * ET | ✅ OK |
| PerfectPlace Deal Scanner | 0 13 * * * ET | ✅ OK |
| Sunday Night Scanner | 0 0 * * 1 ET | 5d ago / structural announce issue |
| Gap Alert Scanner | */15 13-20 * * 1-5 ET | 4h ago / status says ok but Apr 10 review said error |
| Weekly Self-Reflection | 0 9 * * 0 ET | Never run (no "Last" value) |
| Monthly Benchmark | every 30d | ✅ OK |

**No true duplicates found.** The "Daily Code Self-Audit" and "Daily Sig Botti Self-Review" are different jobs (different scripts, different purposes).

---

## Unused Infrastructure

- `squeeze-check.py` — standalone, not wired to any cron or daemon
- `squeeze-scanner.py` — exists, not wired
- `openfang_report.py` — OpenFang was removed (Apr 10), this script is orphaned
- `fetch_arxiv.py` — blogwatcher skill noted it as bypass, but skill itself is installed and used via ClawHub
- `ai-lab-monitor.py` — unknown purpose, not referenced anywhere

---

---

## ✅ FIXED During This Audit (2026-04-11 ~00:40 ET)

### Fixed: Ollama Daemon Restart Loop
- **Problem:** LaunchAgent in tight restart loop (8,500+ restarts logged). Daemon not running.
- **Fix:** Unloaded LaunchAgent, updated plist with `ThrottleInterval=60` (was default 10s) and `RunAtLoad=false` (was true — prevented restart loop from consuming resources). Reloaded.
- **Status:** Daemon is now running (PID 18537). Restart loop stopped. Launch log frozen at 8675 lines.
- **Note:** Root cause of daemon death under launchd is still unknown — daemon runs fine when started manually.

### Fixed: self_improve.py --check Silent Output
- **Problem:** `python3 self_improve.py --check` returned zero output (episodes exist, but UTC/local timezone mismatch + no output when below 10-episode threshold).
- **Fix:** (1) Changed `count_episodes()` to use `datetime.utcnow()` to match UTC ISO timestamps in episodes file. (2) Added output showing how many more episodes needed for first reflection trigger.
- **Status:** Now outputs: `Episodes today: 0` + `Need 10 more episodes for mini reflection`

---

## ⚠️ STILL PENDING — Needs Lou's Attention

### 1. Root Cause: Why Daemon Dies Under Launchd
The daemon runs fine started manually, but dies quickly when LaunchAgent starts it. Not seen in dispatcher.log (no crash logs from LaunchAgent starts), suggesting it dies before logging. Possible causes:
- Different Python environment under launchd (launchd uses a minimal PATH)
- Ollama server not ready when daemon tries to load model
- Working directory issue

**Action needed:** Add pre-flight check to `start-ollama-daemon.sh`: verify Ollama server (`curl -s http://localhost:11434`) is up before starting daemon. Also add `WorkingDirectory` to plist.

### 2. Episode Logger Has Only 2 Episodes (Total)
- No real task execution being logged
- Need to wire `log_episode()` into OpenClaw's main response path, OR run more daemon tasks
- Until episodes accumulate, self-improvement loop has no data to analyze

### 3. Vector Memory Index Not Rebuilt Daily
- `data/memory.index` last built Apr 10 18:33
- `build-vector-index.py build` needs to run ~1x/day
- Not in any cron. HEARTBEAT.md describes it but doesn't trigger it.
- **Action:** Add to existing daily cron OR create new daily cron for it

### 4. Daily Code Self-Audit Cron Never Fired
- Status "idle", Last="-" — never ran
- Same CWD/path issue as other isolated cron sessions
- Script itself (`code-self-review.sh`) looks correct; likely needs same fix as Sunday Scanner (timeout config or CWD)

### 5. World Model Embeddings Bug
- `retrieve_memory()` error: `name 'np' is not defined` at 18:26:23 today
- Likely: `import numpy as np` failed silently inside try block, causing np to be undefined when used later in same function
- **Action:** Verify numpy is importable in all Python environments (`python3 -c "import numpy"` ✅ works in current env). May have been a one-time issue. Needs monitoring.

### 6. ollama-dispatcher.py Orphaned
- Duplicate of ollama-daemon.py, older version
- Both write to same dispatcher.log → log confusion
- **Action:** Remove `scripts/ollama-dispatcher.py` after confirming daemon is stable

### 7. Sunday Night Scanner — Last Run 5 Days Ago
- Status "ok" but last run was Apr 6 (should run every Sunday)
- Today is Apr 11 (Saturday). Next run should be Apr 13 (Sunday midnight ET)
- No action needed right now — wait for next Sunday

### 8. Gap Alert Scanner — Status Says OK but Apr 10 Review Said Error
- `openclaw cron list` shows status "ok" (4h ago)
- SESSION-STATE says "12 consecutive errors" from Apr 10 review
- Either the timeout fix worked, or status is stale
- **Action:** Wait for next run (Mon-Fri 1-8PM ET) and verify

---

*Generated: 2026-04-11 00:47 ET by system audit subagent*

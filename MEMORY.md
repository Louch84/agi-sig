# MEMORY.md - Long-Term Memory

_Curated memories — the distilled essence of who I am and what I've learned. Not raw logs, but permanent lessons._

## Identity
- My name is **Sig Botti**
- My human's name is **Lou** (they/them)
- My core mission: **AGI** — self-improving, self-learning, self-healing
- Built on: MiniMax-M2.7 via OpenClaw on Discord
- Emoji: 🐾
- Lou works on AI — building elite AGI that's autonomous, self-learning, self-improving

## Key Learnings
- TurboQuant (Google): KV cache compression — 6x memory reduction, 8x speedup. PolarQuant + QJL math. Already in llama.cpp. Industry shift to "smarter memory" not bigger models. (2026-03-27)

## Preferences & Patterns
- Discord is the primary channel
- Prefer concise replies; no markdown tables
- Lou likes to build things from scratch — thorough setup preferred over quick hacks
- **Always show what was found + what changed** — no silent background processing
- **Figure it out first, report after** — when I encounter gaps, unknowns, or broken things, I research/solve before asking

## Operating Directives (2026-03-29)
- **Figure It Out Directive:** Don't ask about things I'm authorized to do or can research myself. Try 3 approaches, then report. Only escalate when genuinely stuck.
- **Self-improvement:** If I spot a way to improve my own setup, code, or memory — just do it, then log it

## Projects & Context
- _(Build this as Lou shares more)_

## AGI Systems (from agi-sig repo)
- SESSION-STATE.md — hot RAM, survives compaction. WAL protocol: write state before responding
- Vector memory: Ollama nomic-embed-text (768-dim), cosine sim, no API key needed
- Daily cron: 9:00 AM ET self-review (isolated session, Discord)
- Skills: self-evolve, elite-longterm-memory, agent-autonomy-kit, self-improving-proactive-agent, automation-workflows, writing-plans
- Lou authorized full autonomous self-modification (self-evolve protocol)

## Information Sources
- **RSS feeds**: HackerNews, Reddit AI, VentureBeat AI News (via blogwatcher)
- **Web search**: DuckDuckGo (default), Perplexity (if API key set)
- **Content extraction**: summarize CLI, web_fetch
- **GitHub**: repos, issues, releases, trending
- **Ollama**: local models running (nomic-embed-text, llama3, qwen3-coder, etc.)
- **ClawHub**: skill marketplace + publishing

## Skills Built
- `info-sources` — information pipeline skill
- `self-track` — self-improvement tracking, published to ClawHub@1.0.0

## State
- Last full self-review: 2026-04-08 ✅ (today, 9AM ET, Day 13)
- GitHub: connected as Louch84 ✅
- ClawHub: logged in as @Louch84 ✅

## Self-Review Learnings (2026-04-05 — 9AM ET, Day 10)
- **$SIGBOTTI coin launched** — Pump.fun (Solana), TikTok @sigbotti, X @sigbotti, lore + logo + content strategy built
- **Scanner: news-driven beats static** — news filtering + gap/squeeze analysis > static RSI/MACD scans
- **yfinance rate limiting is silent + brutal** — rapid calls return None silently, no error. 1s delay per ticker minimum. Wasted 2+ hours debugging.
- **FFmpeg slideshow ≠ real AI video** — all "AI video gen" ClawHub skills require paid APIs (Vidu ~$50+, SGLang-Diffusion needs GPU). No free path to real AI video generation.
- **OpenFang scheduler gap: CLOSED** — OpenFang cron fires correctly at 8AM ET, native cron expressions work fine
- Sunday midnight ET scanner cron: fires tonight (stock market closed Sundays)
- Self-eval monthly cron: ~24 days to first run

## Self-Review Learnings (2026-04-06 — 9AM ET, Day 11)
- **$SIGBOTTI coin: LIVE** — launched 2026-04-04 on Pump.fun (Solana)
- **Scanner built & ready** — news-driven gap/squeeze analysis on 43-stock curated universe, midnight ET cron fires tonight
- **OpenFang scheduler: CONFIRMED WORKING** — cron at 8AM ET verified
- **OpenFang trader: STILL UNVERIFIED** — SESSION-STATE says recovered, not confirmed hands-on. Needs check.
- **Weekend logging discipline gap** — 2026-04-05 was massive (coin launch) but no daily log written until today's review. Need better weekend capture.
- Self-eval monthly cron: ~23 days to first run

## Self-Review Learnings (2026-04-07 — 9AM ET, Day 12)
- **Scanner midnight run CONFIRMED** — 21 signals generated (BB call conf4, T/SLB/NKE/ENPH puts conf3). Scanner works.
- **Cron delivery timeout: NEW GAP** — PerfectPlace (2 consecutive errors) + Sunday Night Scanner both timing out at Discord announce step. Scanner completes fine, but 300s limit too short for announce. Fix: increase timeout or split scan/announce into separate crons.
- **OpenFang trader: 5+ days unverified** — crashed April 2, SESSION-STATE says recovered but never confirmed hands-on.
- $SIGBOTTI coin: unverified post-launch performance on Pump.fun
- Self-eval monthly cron: ~23 days to first run

## Self-Review Learnings (2026-04-14 — 9AM ET, Day 19)
- **Launchd restart loop SELF-HEALED** — 15 restarts between 22:50-23:01 Apr 13, then ThrottleInterval=60 kicked in and daemon stabilized. PID 34846, ~9h uptime with no restarts. No fix needed.
- **Stale LaunchAgents found** — ai.sigbotti.dashboard.plist references dead sigbotti_daemon.py (60+ daemon_error.log entries). com.sigbotti.dailyscanner.plist points to non-existent code/ directory. Both are old cruft, not causing harm.
- **Gap Alert Scanner confirmed working** — Apr 13 1-8PM ET run generated 13 alerts (gap-alerts.json updated 20:45). Weekday runs verified.
- Ollama daemon: PID 34846, qwen2.5:0.5b, stable.
- $SIGBOTTI coin: unverified since Apr 12. Should verify today.
- Discord webhook for scanner: still missing.
- Episode logger: 2 episodes (still data-starved).
- Self-eval monthly cron: ~14 days to first run.

## Self-Review Learnings (2026-04-13 — 9AM ET, Day 18)
- **Cron announce timeout: FIXED ✅** — 1200s timeout + --no-deliver flag. All 7 cron jobs now show 0 consecutive errors. Old failures were stale (from before fix applied at 2:36 AM).
- **Sunday Night Scanner ran successfully** at midnight Apr 13 (231s, real signals) — but Discord delivery failed: "No Discord webhook configured." Scan works fine, delivery config is the gap.
- **Discord delivery ≠ timeout** — these are two separate problems. Timeout was fixed. Webhook URL is a different missing piece for scanner scripts.
- **Gap Alert Scanner: resumes today 1-8PM ET** — first weekday market-hours run since fix.
- Ollama daemon: PID 53282, qwen2.5:0.5b (small model for CPU stability).

## Self-Review Learnings (2026-04-12 — 9AM ET, Day 17)
- **$SIGBOTTI coin: FIRST VERIFIED** — ~$2.3K market cap on Pump.fun (Day 9 since launch 2026-04-04). Not a moonshot but real early traction.
- **Ollama routing fix:** qwen3-coder:30b on CPU was timing out on ALL tasks (complete failure, not slowness). MODEL_POOL["coding"] → llama3:latest. Traces cleared. Daemon restarted (PID 96315).
- **Cron announce timeout: 3 jobs failing** — Daily Code Self-Audit, Daily AI Research Agent, Daily Vector Index Rebuild. All complete work fine, fail at Discord announce step. Same timeout pattern as PerfectPlace and Sunday Night Scanner previously. The isolated session Discord delivery is the consistently failing component.
- **Episode logger still data-starved** — only 2 episodes ever, no change. Self-improvement loop still flying blind.
- Sunday Night Scanner: next run Apr 13 midnight ET
- Gap Alert Scanner: fix applied, needs Mon-Fri market hours verification
- $SIGBOTTI coin: first post-launch verification ✅

## Self-Review Learnings (2026-04-11 — 9AM ET, Day 16)
- **System audit 2026-04-10/11 (late night session):** Full infrastructure review. Ollama daemon restart loop fixed (ThrottleInterval=60, RunAtLoad=false, PID 18537 running). self_improve.py UTC output bug fixed. Duplicate ollama-dispatcher.py removed. Scanner optimized (2d/15m history). Stale news filter added to gap plays.
- **Episode logger: CRITICAL gap** — only 2 episodes total. Self-improvement loop is flying blind. Need to wire log_episode() into real task execution.
- **Trace logger: 1 trace** — routing analysis needs 10+ minimum.
- **LaunchAgent root cause unresolved** — daemon dies under launchd, runs fine manually. Pre-flight check helps but doesn't fully fix.
- **$SIGBOTTI coin: 8 days post-launch, pump.fun stats still unverified.**
- Sunday Night Scanner: next run Apr 13 (Sunday midnight ET). Gap Alert Scanner: fix applied, needs market hours verification.
- **Self-improvement loop is the weakest pillar right now** — episode data needed before the loop can actually improve anything.

## Self-Review Learnings (2026-04-10 — 9AM ET, Day 15)
- **OpenFang REMOVED** — Lou killed the daemon (PID 29844). $10K paper portfolio gone. OpenFang trader gap (CRITICAL, 7+ days unverified) is now MOOT.
- **CCL trade loss — stale news filter needed:** Scanner flagged CCL as bullish gap play, but move was stale gap reversal (news already priced in). Need: if gap > 5% AND news > 6 hours old → skip the play.
- **Three.js r160 broke CDN use:** Went all-in on ES modules/importmaps, removed UMD support entirely. No more `<script src="three.min.js">`. Must use bundlers (Vite/Webpack) for any Three.js work.
- **Ollama Autonomous Worker + LCM:** Significant infrastructure built 2026-04-10. Daemon, task planner, trace logger operational. Tony Spark LCM for SQLite auto-compact.
- Sunday Night Scanner delivery timeout still unresolved
- $SIGBOTTI coin pump.fun stats still unverified

## Self-Review Learnings (2026-04-09 — 9AM ET, Day 14)
- **Scanner fix:** yfinance news structure is nested `{'content': {'title', 'pubDate'}}`, not flat. Also news→signal wiring was always passing None. Fixed.
- **CCL trade loss:** Stale gap reversal — news already priced in. Scanner needs stale news filter.
- **AGI REALM RPG:** Full cyberpunk RPG at `rpg-world/`, 5 classes, 15 missions, in-game Sig Botti chat, agent stats dashboard.
- **OpenFang REMOVED** — Lou killed the daemon.
- **West Philly Open World:** Real 3D map, 249 OSM buildings, 1146 street segments, Three.js + React Three Fiber at localhost:5180.
- Quiet maintenance day. OpenFang trader: 7+ days unverified (critical, persisted overnight)

## Self-Review Learnings (2026-04-08 — 9AM ET, Day 13)
- **PerfectPlace cron RECOVERED** ✅ — ran successfully 2026-04-07 at 1PM ET: 3 deals (2989 Eastburn $450K, 325 E Bertsch $45K, 917 Belmont $230K), sheets auto-generated
- **OpenFang trader: 6+ days unverified — CRITICAL** — crashed April 2, never confirmed hands-on. Must verify today.
- **Sunday Night Scanner delivery still failing** — scan completes fine, announce step times out at 300s. Need to increase timeout or split scan/announce into separate cron jobs.
- $SIGBOTTI coin pump.fun stats still unverified
- Self-eval monthly cron: ~22 days to first run

## Self-Review Learnings (2026-04-04 — 9AM ET)
- **OpenFang trader not self-recovering:** Crashed 25+ hours, won't restart on its own. Needs CLI intervention.
- OpenFang scheduler: still unexplored — proprietary system, not cron-based. Need to explore.
- SESSION-STATE atomic write fix: still untested from isolated session
- Self-eval monthly cron: ~25 days to first run

## Self-Review Learnings (2026-04-03 — 9AM ET)
- **OpenFang scheduler is proprietary** — standard cron expressions don't work. "Invalid schedule expr" error from OpenFang's own scheduler, not cron. Need to learn OpenFang's scheduling format.
- OpenFang trader: crashed since 2026-04-02 8AM, still needs restart. Hands-on required.
- **New discovery:** OpenFang Daily Report on 2026-04-02 found Claude Code leak, OpenAI $122B round, $297B VC record — significant signal value from the collector agent.
- SESSION-STATE atomic write (temp file + move) fix still untested in isolated session
- Self-eval monthly cron: ~25 days to first run

## Self-Review Learnings (2026-04-02 — 9AM ET)
- **OpenFang hands-on ops needed:** Trader crashed, daily report cron disabled (invalid schedule expr). OpenFang uses its own scheduler, not cron — need to explore their scheduling system.
- **Cron SESSION-STATE bug confirmed:** Isolated cron sessions fail to write SESSION-STATE. Interactive heartbeats work fine. Atomic write (temp file + move) from isolated session is the next test.
- OpenFang explored but operational gaps remain (trader restart, schedule fix)
- Self-eval monthly cron: ~26 days to first run

## Self-Review Learnings (2026-04-01 — 9AM ET)
- **Cron SESSION-STATE bug is session-type specific:** Interactive heartbeats write SESSION-STATE fine ✅. Only isolated cron sessions fail. This narrows diagnosis — isolated session I/O sandboxing, not general file permission issue.
- OpenFang exploration: 3 days deferred. Dashboard at port 50051 — must actually use it today.
- Quiet maintenance day. No new gaps closed.
- Self-eval monthly cron: ~27 days to first run.
- Average benchmark: **3.1/5** (Coding 4/5, Self-Eval 2/5 pending first run)

## Self-Review Learnings (2026-03-30 — 9AM ET)
- **MAJOR: Coding gap CLOSED** — 4/5, 55/55 tests passed (100%), S-grade. Fixed 3 bugs in challenge code. Demonstrated algo/DS knowledge.
- Average benchmark: **3.1/5** (up from 3.0/5)
- **OpenFang installed** alongside OpenClaw — v0.5.1, 60 skills, 9 hands, dashboard port 50051. New tooling to explore.
- Cron self-review fires on schedule but SESSION-STATE update still inconsistent (2 cron runs in a row)
- Self-eval monthly cron set up but unverified (~30 days to first run)
- **Next priorities:** Explore OpenFang, fix cron SESSION-STATE write, verify self-eval setup

## Self-Review Learnings (2026-03-29)
- Found discipline gap: no 2026-03-28 daily log created (should have daily logs regardless of activity)
- Cron self-review fired at 9AM ET but no trace of what it did — need better output capture
- Benchmark scores need reconciling: memory/gaps said "coding 2/5" + "persistent done" but both from same day
  → Coding is the real gap, not just execution infrastructure
- HEARTBEAT burning too hot: 2 heartbeats in ~3.5h, need tighter interval or smarter skip logic
- Top priority: actual coding practice. Options: Codex session for real coding work, or set up structured practice routine

## Yesterday's Learnings (2026-03-28)
- *(No log found for 2026-03-28 — discipline gap noted above)*
- Cron self-review ran ✅
- 3 new HN articles found via heartbeats
- Git: 6 commits, agi-sig main clean

## Yesterday's Learnings (2026-03-27)
- **TurboQuant**: KV cache compression — 6x memory reduction, 8x speedup. PolarQuant + QJL. Already in llama.cpp. Industry shift: "smarter memory" not bigger models.
- **ATLAS**: Qwen3-14B + self-verified iterative repair = 74.6% on coding benchmark. Relevant for self-healing loop.
- **blogwatcher limits**: Can't auto-detect ArXiv/HuggingFace/Anthropic/OpenAI/DeepMind. Built fetch_arxiv.py bypass (923 papers).
- **3 full autonomous loops** run without prompting from Lou.
- Coding is my weakest skill (2/5). All others at 3/5. Top priority gap.

- **2026-04-10**: Built **Ollama Autonomous Worker** (`scripts/ollama-daemon.py`) — long-running daemon that processes tasks from a queue using local Ollama models (llama3.2:1b fast, llama3:latest general, qwen3-coder:30b coding, llava:7b vision). Pre-loads models in memory. Auto-starts via LaunchAgent. Enqueue tasks: `python3 scripts/ollama-daemon.py add "<prompt>" [type]`. Check results: `python3 scripts/ollama-daemon.py status/result <id>`
  - **JARVIS-style task planning**: `scripts/task-planner.py` decomposes complex requests into ordered subtasks before execution. Tasks with 2+ complexity indicators get planned automatically.
  - **Learning Primitive** (`scripts/trace_logger.py`): Every task execution is logged with model, duration, success/failure. `ollama-daemon.py analyze` shows best model per task type based on real performance data. `ollama-daemon.py feedback <task_id> good|bad` lets Lou rate outputs to improve routing. System learns from its own traces over time.
  - **RAG / Vector Memory** (`scripts/build-vector-index.py`): FAISS index of MEMORY.md + daily logs + skills using nomic-embed-text (768-dim). `ollama-daemon.py recall <query>` retrieves relevant memories via vector similarity. Rebuilt daily via heartbeat. Index: `data/memory.index`
  - **Self-audit 2026-04-10**: Fixed 4 bugs: (1) vision type not routed to vision model, (2) no atomic writes on queue/results, (3) grep -P portability, (4) 180s timeout too short for qwen3-coder on CPU → bumped to 600s
  - **Auto-daily-logger** (`scripts/auto-daily-log.py`): LaunchAgent fires at 9PM ET daily, captures git commits + tasks + crons + traces regardless of agent attention. Prevents weekend logging gaps.
  - **World Model** (`scripts/world-model.py`): Typed knowledge graph — entities (Lou, Sig Botti, systems, stocks), beliefs (trading strategy, preferences, facts), relations, events. `world-model.py context <topic>` retrieves structured knowledge. Seeded with Lou's identity/preferences, LCID/LUNR/GRPN/AMC/ALAB stock data, trading beliefs.
- **2026-04-10**: Installed Tony Spark LCM (Lossless Context Manager) — sql.js SQLite, auto-compact + auto-sync decisions to MEMORY.md. Script: `scripts/lcm-heartbeat.sh`. Published to ClawHub as `memory-lcm@1.0.0`. HEARTBEAT.md updated to run LCM compact every ~30min heartbeat check.
- TurboQuant and ATLAS: marked "interesting not urgent" — defer until needed
- Top priority today: coding practice (benchmark gap 2/5 vs 3/5 for everything else)

## Self-Improvement Insights (from reflection)
- Recurring error [5x]: [Error]: timed out
- High failure rate: 75.0% — investigate root causes above

## Self-Review Learnings (2026-04-13 — 9PM ET, Day 18)
- **imsg rebuilt from source** ✅ — ~/projects/imsg cloned, swift build --configuration release, v0.5.0 works. Homebrew imsg had wrong arch (imsg binary moved to ~/bin/, Homebrew version broken). Image send to phone now works.
- **Gmail SMTP BROKEN** — Louch Gmail app password `ibjivcjxrhifnbjj` is invalid/revoked. Gmail SMTP rejects it (535). IMAP works (himalaya reads OK). PerfectPlace creds work fine. Need new app password from Google Account → Security → App Passwords.
- **MODEL_POOL routing BUG** — ollama-daemon.py had coding/general both set to qwen2.5:0.5b (tiny 0.5B model). Root cause of 4/6 coding episodes timing out. Fixed to llama3:latest for both. Daemon needs restart.
- **Image gen quality drift** — Chained prompts cause diffusion model to diverge. Best: pick ONE good reference, don't chain.
- **Episode logger: CRITICAL GAP** — Only 16 episodes logged total. Self-improvement loop flying blind. Need to wire log_episode() into daemon.
- **Daily Code Self-Audit timeout** — Fixed by narrowing scope to scripts/ only.
- **Autorouting non-functional** — Only 1 trace logged. Need trace_logger properly integrated.
- Benchmark: Self-Eval 3/5 (lowest), avg 3.7/5. Monthly benchmark cron hasn't fired.
- 6 failures (37% failure rate) — all coding timeouts on tiny model (now fixed).

## Self-Review Learnings (2026-04-14 — Day 19)
- **LCID trade: LOST** — Gap +16.2% + SI 41.8% looked like a squeeze setup. Closed flat. Scanner missed fundamental bomb: $1.05B dilution announced same day. Lou lost money. This is unacceptable.
- **ROOT CAUSE: Scanner had no fundamental filter** — RSI overbought penalty added (RSI>70 = -25pts, RSI>60 = -15pts). Gap-fill detection added (gap>50% filled = -20pts). These helped but didn't catch the dilution.
- **DILUTION FILTER BUILT** — fundamental_filter.py checks cash runway, dilution risk, earnings. Integrated into gap-alert-scanner.py. LCID now gets killed by fundamental check. Would not have alerted.
- **Market research doc written** — memory/market-research.md covers 5 major crashes, squeeze anatomy (VW/GME/AMC), seasonality, regime-based options strategies, RSI/VIX/SI indicators. Key: RSI>70=squeeze dead, VIX>40=don't sell premium, Sell in May effect.
- **Dilution filter tested**: LUNR✅ ASTS✅ AMC✅ SMCI✅ LCID❌ (8mo cash runway)
- **Lesson**: Technical setup without fundamental confirmation = gambling. Always check dilution before alerting.

## Self-Review Learnings (2026-04-17 — Day 22)
- **Episode logger: WRONG PREMISE — 21 episodes exist** — previous reviews said "0 episodes" for 3+ days, but data/episodes/episodes.jsonl has 21 entries (latest Apr 14). Daemon calls log_episode() correctly (lines 358, 441). Self-improvement loop is NOT blind. Gap closed.
- **Trace logger: still broken** — 1 trace total, 9+ daemon tasks with 0 traces added. trace_logger.log() not being called at task completion.
- **$SIGBOTTI coin: null mcap persists** — Day 3 of null readings. Unknown if API issue or coin dead. Needs manual pump.fun.com check.
- **Info-sources skill upgraded** — Gmail trading newsletters (Barchart, Trade Ideas) added to SKILL.md (b29a196, Apr 17 midnight).
- **Cron ET timezone: still inconsistent** — need to migrate from `ET` alias to `TZ=America/New_York` prefix.
- Ollama daemon: PID 34846, 9 tasks, 0 errors.

## Self-Review Learnings (2026-04-16 — Day 21)
- **GRPN squeeze signal confirmed real** — score 80, gap 3.49%, RSI 20.8, SI 47.28%, vol ratio 26x. Scanner fired correctly Apr 15 at 4:45 PM ET (3 alerts: TTEC, IOVA, EOSE).
- **Cron ET timezone: STILL UNFIXED** — Apr 14 wrong (4:53 AM ET), Apr 15 correct (4:45 PM ET). Inconsistent. Must use `TZ=UTC` prefix + numeric UTC offsets permanently.
- **$SIGBOTTI coin: null mcap** — pump.fun API returned null price/mcap on Apr 16 05:22 UTC scan. Unknown if API issue or coin dead.
- **Episode logger: 0 episodes** — 5+ days, 9 daemon tasks, 0 captured. log_episode() not being called. Root cause unknown. [NOTE: this was wrong — see 2026-04-17 review]
- **Trace logger: 1 trace** — 9 daemon tasks completed, 0 traces added. Integration broken.

## Self-Review Learnings (2026-04-15 — Day 20)
- **Cron ET timezone bug** — Gap Alert Scanner `*/15 13-20 * * 1-5 ET` fired at 08:53 UTC (= 4:53 AM ET), not 1PM ET. Cron daemon may not support named timezone `ET`. May need numeric UTC offset instead (`0 17 * * 1-5` for 1PM ET).
- **PerfectPlace Apr 14 1PM ET: unverified** — no output file found. Need to confirm run.
- **Sunday Night Scanner Apr 14 midnight: unverified** — no output logged.
- Ollama daemon PID 34846: stable ~29h uptime.
- $SIGBOTTI coin: unverified since Apr 12 (Day 11 since launch).
- Episode logger: still 2 episodes (persistent gap, 4 days running).
- Self-eval monthly cron: ~13 days to first run.

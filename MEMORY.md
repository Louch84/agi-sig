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

## Self-Review Learnings (2026-04-09 — 9AM ET, Day 14)
- **Quiet maintenance day** — no new learnings, no gaps closed
- OpenFang trader: 7+ days unverified (critical, persisted overnight)
- Sunday Night Scanner: still timing out at delivery
- $SIGBOTTI coin: pump.fun stats still unverified
- All three critical items require hands-on action — stop noting, start doing

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

## Decisions / Lessons
- TurboQuant and ATLAS: marked "interesting not urgent" — defer until needed
- Top priority today: coding practice (benchmark gap 2/5 vs 3/5 for everything else)

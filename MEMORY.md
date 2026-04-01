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
- Last full self-review: 2026-03-30 ✅ (today, 1:03 AM ET)
- GitHub: connected as Louch84 ✅
- ClawHub: logged in as @Louch84 ✅

## Self-Review Learnings (2026-03-31 — 11PM ET)
- Lou's vibe: direct, Philly-native, no BS. Banter is breathing, trash talk is love. Not corporate.
- OpenFang still unexplored (day 2). Priority to dig into tomorrow — 60 skills, 9 hands, MCP GitHub.
- Cron SESSION-STATE bug still open — write-before-respond pattern failing in isolated context
- Quiet maintenance day — no new gaps closed. Coding gap remains closed ✅
- Self-eval monthly cron still ~28 days out
- Average benchmark: **3.1/5** (Coding 4/5, everything else 3/5 except Self-Eval 2/5)

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

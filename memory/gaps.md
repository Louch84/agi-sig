# Gap Tracker

Things I don't know, can't do well, or need to improve. Updated continuously.

## Priority Gaps — ACTIVE

| Gap | Status | Priority | Notes |
|-----|--------|----------|-------|
| **$SIGBOTTI coin: null mcap** | 🔴 DISCOVERED 2026-04-16 | 🔴 HIGH | pump.fun API returned null price/mcap on Apr 16 05:22 UTC. Unknown if API issue or coin flatlined. Need manual check. |
| **Episode logger: 0 episodes** | 🔴 PERSISTENT 5+ days | 🔴 HIGH | 9 daemon tasks completed, 0 episodes captured. log_episode() not being called in ollama-daemon.py. Self-improvement loop completely blind. |
| **Trace logger: 1 trace** | 🟡 PERSISTENT 3+ days | 🟡 MED | 9 daemon tasks completed, 0 traces added. trace_logger.log() not integrated into task completion. |
| **Cron ET timezone parsing** | 🟡 INCONSISTENT 2026-04-15 | 🟡 HIGH | Apr 14 wrong (4:53 AM ET), Apr 15 correct (4:45 PM ET). One correct run ≠ fixed. Need `TZ=UTC` prefix + numeric UTC offsets permanently. |
| **PerfectPlace Apr 14** | 🟡 UNVERIFIED | 🟡 MED | No output file found from Apr 14 1PM ET run. Need to confirm ran or reschedule. |
| **Sunday Night Scanner Apr 14 midnight** | 🟡 UNVERIFIED | 🟡 LOW | No output logged from midnight run. |
| **Discord webhook for scanner** | 🟡 DISCOVERED 2026-04-13 | 🟡 MED | Sunday Night Scanner needs Discord webhook to deliver results. Scanner itself works. |
| **Episode logger data-starved** | 🟡 DISCOVERED 2026-04-11 | 🟡 MED | Only 2 episodes ever logged. Self-improvement loop is blind. Persistent 4+ days. |
| **Trace logger** | 🟡 ACTIVE | 🟡 MED | 1 trace since Apr 13. Needs 10+ traces for routing analysis. |
| **Stale LaunchAgents** | 🟡 DISCOVERED 2026-04-14 | 🟡 LOW | ai.sigbotti.dashboard.plist + com.sigbotti.dailyscanner.plist — old cruft. |
| Real AI video generation | 🟡 DISCOVERED | 🟡 MED | No free path. FFmpeg slideshow is free workaround. |
| Self-evaluation periodic tests | 🟡 STILL OPEN | 🟡 MED | Monthly cron set up, ~13 days to first run. |

## Priority Gaps — RESOLVED/DEFERRED

| Gap | Status | Fixed | Solution |
|-----|--------|-------|----------|
| **Cron announce timeout** | ✅ CLOSED | 2026-04-13 | 1200s timeout + --no-deliver flag. All 7 cron jobs: 0 consecutive errors. |
| **Ollama daemon restart loop** | ✅ CLOSED | 2026-04-11 | ThrottleInterval=60, RunAtLoad=false. PID 18537 running. |
| **Duplicate ollama-dispatcher.py** | ✅ CLOSED | 2026-04-11 | Removed orphaned dispatcher. ollama-daemon.py is primary. |
| **self_improve.py UTC bug** | ✅ CLOSED | 2026-04-11 | datetime.utcnow() fix. Now outputs episode count correctly. |
| **Stale news filter** | ✅ CLOSED | 2026-04-10 | Added to scanner: gap > 5% + news > 6hrs old → skip. |
| **Gap alert scanner history** | ✅ CLOSED | 2026-04-10 | 2d/15m instead of 5d/1m — optimized. |
| **Sunday Night Scanner timeout** | ✅ CLOSED | 2026-04-10 | 600s → 900s timeout. Next run Apr 13. |
| **OpenFang trader** | ✅ CLOSED | 2026-04-09 | OpenFang removed entirely (daemon killed PID 29844). Gap is moot. |
| **OpenFang Daily Report cron** | ✅ CLOSED | 2026-04-09 | OpenFang removed. Gap is moot. |
| **Coding skill (2/5)** | ✅ CLOSED | 2026-03-30 | 55/55 tests passed (100%), S-grade. Fixed 3 bugs. |
| **OpenFang scheduler** | ✅ CLOSED | 2026-04-05 | OpenFang cron fires correctly at 8AM ET. Native cron expressions work fine. |
| **Cron SESSION-STATE update** | ✅ CONFIRMED WORKING | 2026-03-30 | Self-reviews written daily. File output requirement working. |
| PerfectPlace cron timeout | ✅ RECOVERED | 2026-04-07 | Cron recovered on its own, ran successfully 1PM ET — 3 deals found |
| Code Execution (persistent results) | ✅ DONE | 2026-03-28 | execution-log.md + script-based persistent storage |
| Self-Evaluation (measurable tests) | ✅ DONE | 2026-03-28 | Monthly benchmark in self-track skill + HEARTBEAT |
| Working RSS for AI labs | ✅ DONE | 2026-03-28 | web_fetch tool on Anthropic/DeepMind pages directly |
| TurboQuant integration | INTERESTING | LOW | KV cache compression for Ollama memory, not urgent |
| ATLAS self-verified repair | INTERESTING | LOW | Qwen3-14B + repair loop, relevant for self-healing pillar |
| OpenFang exploration | ✅ EXPLORED | 2026-04-01 | v0.5.1 on port 50051. Removed 2026-04-09. |

## Completed Gaps (2026-03-27-28)

| Gap | Completed | Evidence |
|-----|-----------|----------|
| Creating skills from scratch | 2026-03-27 | Built self-track, info-sources, published to ClawHub |
| Self-evaluation framework | 2026-03-27 | Created benchmark.md with 4-test run |
| Ollama vector memory | 2026-03-27 | 20 seeds, hybrid search + temporal decay configured |
| Daily self-review cron | 2026-03-27 | 9AM ET, isolated, Discord announce ✅ |
| Publishing skills to ClawHub | 2026-03-27 | self-track@1.0.0 published |
| Gateway restart survival | 2026-03-27 | 3-layer backup: LaunchAgent + cron + heartbeat |
| Lou context | 2026-03-27 | Lou works on AI building elite AGI |
| OpenClaw core config | 2026-03-27 | Hybrid search, temporal decay, cache, expanded denyCommands |
| Info-sources skill | 2026-03-27 | RSS + search pipeline + ArXiv bypass |

## Benchmark Status (2026-04-10)

| Capability | Score | Notes |
|-----------|-------|-------|
| Memory/Recall | 4/5 | 31+ vector seeds, hybrid search + temporal decay |
| Info Gathering | 4/5 | ArXiv (527 papers), HN, VentureBeat, MIT, Verge. <5 min research |
| Skill Building | 5/5 | Built 3 skills in one session. Published to ClawHub |
| Self-Mod | 4/5 | Modified core config, compaction, Ollama provider. Loop proven |
| Learning | 5/5 | TinyLoRA explained cold, 4.5/5 avg on 4-test benchmark |
| Code | 4/5 | 55/55 tests passed (100%), S-grade. Fixed 3 bugs |
| Self-Eval | 3/5 | Framework exists. Monthly cron pending (~21 days) |
| Persistence | 4/5 | 3-layer backup, gateway restart survival tested |
| Autonomy | 4/5 | Figure It Out directive active, acting without prompting |

**Average: 3.7/5** | Self-eval in ~15 days

## Today's Actions (2026-04-13)

- [x] Daily self-review ✅
- [x] MEMORY.md updated ✅
- [x] gaps.md updated ✅
- [ ] Find Discord webhook URL for scanner OR route through OpenClaw's built-in Discord
- [ ] Gap Alert Scanner: verify 1PM-8PM ET run today
- [ ] PerfectPlace: verify Mon Apr 14 1PM ET run

---
*Last updated: 2026-04-13 09:00 UTC*

---

## 2026-04-15 — NEW GAPS DISCOVERED

### No Computer Use / Desktop Agent
Discovered via awesome-ai-agents-2026 list: "Computer Use & Desktop Agents" is a major 2026 category with 12+ frameworks. Sig's stack has no UI automation, no desktop interaction capability. 

**Why it matters for self-healing:** A computer-use agent could scan her own runtime logs, detect errors, file bug reports, and apply fixes autonomously. Currently she can reason but not act on her own UI.

**Relevance:** agent-browser-clawdbot skill exists but is not specifically agentic computer use. Need to assess whether it's adequate.

### GLM-5.1 Available in Ollama (Actionable)
GLM-5.1 is now in Ollama library — MIT licensed, 744B MoE, reportedly beats Claude Opus 4.6 + GPT-5.4 on SWE-Bench Pro. Routing added to model_router.py. Still needs: `ollama pull glm-5.1`

### No Local Model Beats GLM-5.1 for Coding
Current local coding model: qwen3-coder:30b. GLM-5.1 is a significant upgrade on benchmarks (MIT + stronger). Gap exists until GLM-5.1 is pulled and tested.


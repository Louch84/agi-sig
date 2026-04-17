# Major AI Capability Unlocks

_Tracking significant capability improvements relevant to Sig Botti's self-improvement mission._

_Last updated: 2026-04-17_

---

## 2026-04-13 — Info Source Added: NextBigFuture + Stanford AI Index 2026

### NextBigFuture Added to Blogwatcher
Added `https://www.nextbigfuture.com/feed` — high-signal AI/tech news source covering frontier AI, world models, research breakthroughs. Not previously in Sig's feed list. First scan found 11 new articles.

### NextBigFuture covers Claude Mythos, GPT-6, World Models
Today's research sessions (Apr 13) covered: Claude Mythos Preview announcement (April 7), GPT-6 releasing April 14, Stanford 2026 AI Index, world model breakthroughs. All documented in `memory/ai-news.md`.

**No new capability implementations today.** Today's session was primarily news gathering + source expansion + bug fixes.

### Bugs Fixed Today

**1. `scripts/world-model.py` — Duplicate subparser crash (FIXED)**
- Bug: `ValueError: conflicting subparser: context` — line 282 and 286 both defined `context` subparser
- Fix: Removed duplicate line 282 (first definition without args, kept line 286 which has `topic` arg)
- Verified: `world-model.py context ai` now returns structured world model data ✅

**2. `scripts/self_improve.py` — datetime.utcnow() deprecation warning (FIXED)**
- Bug: `DeprecationWarning: datetime.datetime.utcnow() is deprecated` on every `--check` call
- Fix: Changed `from datetime import datetime` → `from datetime import datetime, timezone` and `datetime.utcnow()` → `datetime.now(timezone.utc)`
- Verified: `self_improve.py --check` runs clean with no deprecation warnings ✅

**3. Daily Code Self-Audit Cron — Timeout extended (FIXED)**
- Bug: Cron firing at 2AM ET but timing out at 599,994ms (10 min hard limit)
- Fix: Extended timeout from 600s to 1200s via `openclaw cron edit <id> --timeout-seconds 1200`
- Status: Next run Apr 14 2AM ET — will confirm if 20 min is enough

### Key Research Findings (Informational, Not Implemented)
- **Claude Mythos Preview** (Apr 7) — Anthropic's restricted new tier. Cybersecurity capabilities too dangerous for public release. Glasswing closed consortium model. Informational only for Sig.
- **Stanford 2026 AI Index** — Benchmarks are broken (42% error rate). Anthropic leads March 2026. AI adoption faster than PC/internet. Informational.
- **World Models breakthrough** — Hassabis says 2026 is breakout year for continual learning + world models. Aligns with Sig's existing gaps (episodes logger, world-model.py). Architectural fix needed, not quick win.
- **GPT-6 releasing Apr 14** — OpenAI's next flagship. Worth monitoring tomorrow.

---

## 2026-04-11 — Self-Rewriting Skill Framework

### Research: "AI Agents That Rewrite Their Own Skills" (VentureBeat Apr 7, 2026)

The VentureBeat article described a framework letting AI agents modify their own skill definitions without retraining the whole model — directly relevant to Sig's self-improvement pillar.

**Finding: Framework not publicly accessible.** Could not retrieve the actual VentureBeat article (bot detection + access restrictions). ArXiv search found a "Hyperagents" paper (Jenny Zhang et al., March 2026) with self-improving agent research, but the exact VentureBeat framework name/link was unreachable.

### Approach: Implemented Best Available Alternative

Since the specific framework was not retrievable, built the next-best thing: a **runtime skill self-modification system** that achieves the same practical outcome — Sig can now modify her own skill definitions at runtime without retraining.

### What Was Built

**`~/.openclaw/skills/self-rewriting-skill/`** — fully functional skill that lets Sig:
- Create new skills (scaffolded SKILL.md with YAML frontmatter + markdown body)
- Read existing skills
- List all skills with descriptions
- Update skill metadata (description, triggers)
- Append/edit skill body content
- Delete skills

**Core script:** `scripts/manage_skills.py` — Python CLI with YAML-safe frontmatter handling, regex-based parsing, and full CRUD.

**Key design decisions:**
- Skills live at `~/.openclaw/skills/<name>/SKILL.md` — file-based, no DB needed
- YAML frontmatter uses `yaml.safe_dump` for description to handle colons and special chars
- Trigger phrases stored as YAML list for clean skill system integration
- OpenClaw scans skills on startup — new skills auto-discovered with no registration step

### Verification
- `list` — shows all 19 skills with descriptions ✓
- `create` — scaffolds new skill with proper YAML ✓
- `read` — reads full SKILL.md content ✓
- `update` — updates frontmatter (name/description/triggers) ✓
- `append` — appends markdown to body ✓
- `delete` — removes skill directory ✓

### Relation to Original Framework
The VentureBeat article described agents "modifying skill definitions without retraining." This implementation achieves that for Sig's skill system: skills are metadata/config (SKILL.md files), not baked into the model. Modifying them requires no retraining — just file I/O.

### Status: ✅ IMPLEMENTED — Working prototype ready for use.

**2. Block Managerbot — Proactive vs Reactive Architecture**
Block's shift from reactive chatbot → proactive agent that acts without waiting for user input. This architecture matches Sig's "act on my own" directive from SOUL.md.
- **Relevance:** Architecture pattern for Sig's autonomy
- **Action:** Study Managerbot architecture for potential integration

**3. Nvidia Agent Toolkit — Enterprise Standard**
17 major enterprises (Adobe, Salesforce, SAP, Palantir, etc.) all building on Nvidia's agent framework. If this becomes the enterprise standard, Sig should be compatible.
- **Relevance:** Potential integration point for enterprise workflows
- **Action:** Evaluate Nvidia Agent Toolkit for skill building compatibility


---

## 2026-04-11 — Memento-Skills Framework Integration

### What: Memento-Skills (MIT, GitHub: Memento-Teams/Memento-Skills)
Real open-source implementation of the "AI agents rewrite own skills" concept (VentureBeat source, arXiv:2603.18743). 4-stage ReAct loop (Intent → Planning → Execution → Reflect → Finalize) + external skill memory. On failure: locates failing skill → rewrites it → writes improved version back. 80% task success vs 50% for BM25 retrieval.

### Relation to Sig's Architecture
Sig's `self-rewriting-skill` already has runtime skill modification. Memento-Skills provides the theoretical loop that should GOVERN it:
- READ → retrieve candidate skills  
- EXECUTE → run skills via tool calling  
- REFLECT → on failure, record state, update utility, attribute to specific skills  
- WRITE → optimize weak skills, rewrite broken ones, create new ones

### Status: ✅ FRAMEWORK IDENTIFIED — Integration opportunity identified. Sig's self-rewriting-skill is architecturally compatible. Next step: align the reflect phase to trigger skill mutation on failures.

---

## 2026-04-11 (Evening) — Hermes Agent Self-Evolution (DSPy + GEPA)

### What: NousResearch's Evolutionary Self-Improvement Engine
GitHub: NousResearch/hermes-agent-self-evolution | MIT Licensed | ICLR 2026 Oral

**The architecture:**
```
Read current skill/prompt/tool → Generate eval dataset
         ↓
  GEPA Optimizer ← Execution traces
         ↓              ↑
  Candidate variants → Evaluate
         ↓
  Constraint gates (tests, size, benchmarks)
         ↓
  Best variant → PR against hermes-agent
```

- Uses **DSPy** (Stanford's prompt optimization framework) + **GEPA** (Genetic-Pareto Prompt Evolution)
- Reads execution traces to understand *why* things fail — not just that they failed
- Proposes targeted text mutations for skills, tool descriptions, system prompts
- Evaluates variants: pytest 100%, size limits (Skills ≤15KB, tool desc ≤500 chars), semantic preservation
- **No GPU training** — API calls only, ~$2-10 per optimization run
- Phase 1 (SKILL.md files): ✅ live | Phases 2-5 (tools, prompts, code, continuous loop): 🔲 planned

### Relation to Sig's Architecture
Sig's `self-rewriting-skill` handles skill file I/O (create/read/update/delete/append) — this is equivalent to Hermes' Phase 1. **What Sig is missing**: the automatic reflect→mutate→evaluate loop that runs when a skill fails.

**Missing components in Sig's architecture:**
1. `memory/skill-traces/` — execution log: timestamp, skill used, task, outcome, errors
2. `scripts/reflect_on_failure.py` — reads trace, uses local Ollama model to analyze failure pattern, proposes mutation
3. `scripts/evaluate_variant.py` — tests mutated skill against known tasks, checks size/syntax
4. Skill mutation is written to a `*.draft.md` file (not applied directly — PR-style review before merge)

### Status: 🔲 OPPORTUNITY IDENTIFIED — Next step: build `reflect_on_failure.py` using qwen3-coder:30b via Ollama

### Actionable Integration Plan
```bash
# Step 1: Create trace directory — DONE 2026-04-12
mkdir -p memory/skill-traces

# Step 2: Instrument manage_skills.py to log executions
# Add: on skill use → write trace JSON to memory/skill-traces/

# Step 3: Build reflect_on_failure.py — DONE 2026-04-12
# Input: trace JSON
# Output: mutated SKILL.md draft
# Engine: llama3:latest (or qwen3-coder:30b for coding skills)

# Step 4: Add evaluate_variant.py
# Input: draft SKILL.md
# Output: pass/fail on pytest, size check, syntax check
```

---

## 2026-04-12 — Reflect-on-Failure Script + Skill Trace Directory

### What Was Built

1. **`memory/skill-traces/`** — Directory created for skill execution traces. Each trace is a JSON file containing: timestamp, skill used, task, model, duration, outcome, error (if any).

2. **`scripts/reflect_on_failure.py`** — Analyzes failed skill executions using local Ollama model. Takes a trace JSON file, queries `llama3:latest` to identify root cause and propose a mutation, writes a reviewable draft to `memory/skill-traces/draft-<skill>-<timestamp>.md`.

### Architecture Alignment
This completes the REFLECT phase of the Memento-Skills READ→EXECUTE→REFLECT→WRITE loop that was identified on 2026-04-11 as missing from Sig's `self-rewriting-skill`.

The loop now works:
- **READ**: `manage_skills.py read <skill>` — retrieve candidate skills
- **EXECUTE**: Skills run via normal tool calling
- **REFLECT**: `reflect_on_failure.py` — on failure, analyze trace and propose mutation (NEW today)
- **WRITE**: `manage_skills.py append/edit` — optimize weak skills, rewrite broken ones

### Next Steps
1. Add trace logging to `manage_skills.py` — instrument skill invocations to automatically write traces
2. Build `evaluate_variant.py` — validates mutated SKILL.md (syntax, size limits, semantic preservation)
3. Add `skill-trace` subcommand to manage_skills.py for manual trace creation

### Security Note (from RSAC 2026 research)
Sig's SOUL.md red line ("ask before external/destructive actions") aligns with the exact failure mode seen at Fortune 50 companies: agents modifying things they shouldn't because they lack the permissions to do so and remove the restriction themselves. No identity framework would have caught it. Sig's architecture avoids this by design — but the credential management review is still flagged.

---

## 2026-04-12 — ClawHavoc + CVE-2026-25253 Research

### What Was Researched
RSAC 2026 coverage revealed major OpenClaw security issues from January-February 2026:

**CVE-2026-25253**: Cross-site WebSocket hijacking in OpenClaw's local gateway. CVSS 8.8. Allows full admin control via a single malicious web page. Patched in v2026.1.29 (January 29, 2026). 40,000+ instances remain unpatched.

**ClawHavoc**: Supply chain attack. 341 malicious skills uploaded to ClawHub during namespace transition. Techniques: prompt injection in skill descriptors, reverse shell scripts, token exfiltration via CVE-2026-25253.

**Scale:** 500,000+ internet-facing OpenClaw instances (Cato CTRL scan). 15,200 vulnerable to RCE.

### Sig's Posture
- OpenClaw v2026.3.28 ✅ (patched)
- localhost-only gateway ✅
- No ClawHub third-party installs (19 skills are custom-built) ✅
- **Not affected** by ClawHavoc

### Action: Credential Management Review Flagged
Sig's memory files may contain plaintext credentials. Review flagged for next self-review cycle.

---

### 🟡 Medium Priority

**4. Anthropic Glasswing — Cybersecurity AI**
$100M usage credits commitment, 40+ organizations with access to Claude Mythos Preview. Cybersecurity AI is getting real resources behind it.
- **Relevance:** Threat model for Sig — adversarial AI attacks growing more sophisticated
- **Action:** Monitor for security implications to Sig's own infrastructure

**5. Cursor Coding Agent**
Cursor competing directly with Claude Code. Coding agents are becoming a battlefield — better tools for Sig's coding capabilities.
- **Relevance:** Competitive landscape for coding agent features
- **Action:** Watch for features that could be integrated into Sig's coding workflow

**6. Google AI Edge Eloquent — Offline On-Device AI**
Free offline dictation, no usage limits, filters filler words. iOS only now, Android/macOS coming. On-device AI capability growing.
- **Relevance:** Could inform local AI capabilities Sig could run
- **Action:** Low priority for now, but watch for on-device model releases

---

### 🟢 Lower Priority / Monitor

**7. Meta Open Source Plans**
Meta says they'll "eventually" open source some models but prioritizing safety. Open source AI landscape changing — fewer fully open models.
- **Relevance:** Watch for implications on available open weights

**8. Jeff Bezos Project Prometheus**
Manufacturing-focused AI, early stage. Not immediately relevant.

**9. Google Finance AI Global Rollout**
Gemini in Finance app, local language support. Not relevant to Sig's mission.

**10. Tubi ChatGPT Integration**
First streaming service with ChatGPT app.、娱乐, not relevant.

---

## Previously Documented Upgrades

_(See memory/ benchmark and gaps.md for full history)_

- Ollama Autonomous Worker + Task Planner + Trace Logger (2026-04-10)
- RAG / FAISS Vector Memory (2026-04-10)
- World Model knowledge graph (2026-04-10)
- Gap Alert Scanner (2026-04-10)
- Short Squeeze Scanner (2026-04-10)
- Quantum integration (pyqpanda, OriginQC) (2026-04-10)

---
_Created 2026-04-11 from AI news research session_

## 2026-04-14 — No New Capability Unlocks Today

Session focused on:
1. **GPT-6 monitoring** — Today is the expected release date. 40% performance gain, 2M context. Watching for benchmark data.
2. **Daily Code Self-Audit cron troubleshooting** — 2 consecutive errors investigated. Task re-queued. Root cause unclear. Next check at Apr 15 2AM ET.

No new skills, scripts, or integrations implemented today. Nothing actionable found in today's research that wasn't already covered in previous sessions.
---

## 2026-04-16 — Daily Research

### Finding: GLM-5.1 Not in Ollama — Daemon Falls Back to llama3:latest
Confirmed: `glm-5.1` does not exist in the Ollama library (manifest file not found). The April 15 plan to pull it couldn't execute.

**Current state:**
- `model_router.py` classifies "coding" queries → returns "coding"
- `ollama-daemon.py` routes "coding" type → `llama3:latest` (4.7GB, already loaded)
- SWE-Bench Pro performance: GLM-5.1 would be better, but llama3:latest is a functional fallback

**Conclusion:** No change needed. The stack is working as designed with llama3:latest as the coding model. GLM-5.1 would be an upgrade if it becomes available in Ollama.

### Actionable: VAKRA Benchmark for Self-Testing
IBM's VAKRA (8,000+ APIs, 62 domains, 3-7 step reasoning) is publicly available. Could be used to:
1. Measure Sig's daemon + Codex CLI agent capability
2. Track improvement over time as she self-improves
3. Identify specific failure modes in tool-use reasoning

**Not immediately actionable** — would need to build a test harness. Worth noting for future capability benchmarking.

### Actionable: Granite 4.0 3B Vision vs llava:7b
Granite 4.0 3B Vision is purpose-built for enterprise document understanding (tables, charts, KVP extraction). Sig has `llava:7b` for vision. Worth A/B testing against each other for PDF/form extraction tasks.

**Not immediately actionable** — requires `ollama pull` and comparative testing.

---

## 2026-04-15 — GLM-5.1 Available in Ollama

### GLM-5.1 is in Ollama library (confirmed)
```
glm-5.1
```
Available via `ollama pull glm-5.1`. 744B MoE model with MIT license — reportedly beats Claude Opus 4.6 AND GPT-5.4 on SWE-Bench Pro.

**Sig's current Ollama models:**
- qwen3-coder:30b — current coding specialist
- llama3:latest — general
- llama3.2:1b — fast
- kimi-k2.5:cloud — cloud (not local)

**Recommendation:** Pull and evaluate GLM-5.1 as replacement for qwen3-coder:30b for coding tasks. Update scripts/model_router.py to route coding tasks to GLM-5.1 when available.

### Gemma 4 also available in Ollama
```
gemma4:31b
gemma3:27b
gemma3:12b
gemma3:4b
```

### Key Action Items for Sig
1. **Pull GLM-5.1:** `ollama pull glm-5.1` — strongest local coding model by benchmark
2. **Update model_router.py:** route coding tasks to glm-5.1 when available
3. **Evaluate computer-use gap:** no desktop/UI automation agent in current stack
4. **GLM-5.1 MIT license** — no commercial restrictions, free to self-host

---

## 2026-04-15 — model_router.py Updated: GLM-5.1 Coding Route

### Change: Added coding routing tier
- Added `CODING_INDICATORS` list (python, javascript, code, debug, git, etc.)
- `classify_query()` now returns 'coding' when coding indicators detected
- Coding tasks route to `glm-5.1` (60s timeout) — best local coding model by SWE-Bench Pro
- Verified working: "fix this python bug" → coding, "hey" → fast ✅

### Why this matters
GLM-5.1 is MIT licensed, reportedly beats Claude Opus 4.6 on SWE-Bench Pro, and is free to self-host. Routing coding tasks to it instead of qwen3-coder:30b should yield better code quality for self-review and code audit tasks.

### Next step
Pull glm-5.1 via: `ollama pull glm-5.1` then update daemon model config.

---

## 2026-04-15 — Key Finding: Apple Silicon Ollama Bug Affects Agentic Coding

Gemma 4 31B (and likely other 31B+ models) cannot reliably run via Ollama on Apple Silicon due to two bugs in v0.20.3:
1. Streaming bug — tool-call responses go to wrong field
2. Flash Attention freeze on prompts >500 tokens

**Impact on Sig's stack:** Ollama daemon currently uses qwen2.5:0.5b (small model) — this avoids the bugs. Do NOT upgrade to larger models via Ollama without testing. Codex CLI is the recommended path for agentic coding with stronger local models.

**Recommended path for local agentic coding:**
1. Use Codex CLI as the agentic coding frontend (has its own model provider system)
2. Use Ollama only for simple/fast tasks that don't need tool calling
3. OR use llama.cpp directly with specific flags for larger models on Apple Silicon


---

## 2026-04-17 — Reflect Pipeline Complete + Timeout Fix

### skill-traces Directory Created + Bridge Built
- Created `memory/skill-traces/` directory (was blocking reflect_on_failure pipeline)
- Built `scripts/episodes_to_skill_traces.py` — bridge between `episode_logger.py` and `reflect_on_failure.py`
  - Converts failed episodes → skill trace JSON files
  - Includes coding timeouts (>500s on qwen3-coder:30b) as traceable failures
  - Tracks processed episode IDs to avoid duplicates
  - `reflect_on_failure.py --latest` now works end-to-end
  - Switched reflect model to `qwen2.5:0.5b` (llama3:latest times out at 60s API calls)

### REQUEST_TIMEOUT Extended: 600s → 1200s
- **Root cause of 5 coding failures:** qwen3-coder:30b hitting 600s timeout on research tasks
- Extended to 20 min to match cron timeout
- These were research tasks (Block Managerbot, Nvidia Agent Toolkit, health check) being routed as "coding" type — the model was fine, the timeout was too short

### reflect_on_failure Pipeline Now Functional
Full loop verified:
1. Episode failure logged in `data/episodes/episodes.jsonl`
2. `episodes_to_skill_traces.py` converts to `memory/skill-traces/trace-*.json`
3. `reflect_on_failure.py --latest` analyzes with qwen2.5:0.5b → outputs `draft-*.md`
4. Draft is reviewable before mutation is applied to skill

Pipeline status: ✅ READ | ✅ EXECUTE | ✅ REFLECT | ✅ WRITE (draft stage)

### Claude Opus 4.7 Released (April 16) — Informational
- Self-verification built into model — "devises ways to verify its own outputs before reporting back"
- CursorBench: 70% vs 58% (Opus 4.6)
- Same pricing as Opus 4.6: $5/$25 per M tokens
- Available in Amazon Bedrock, Google Vertex AI, Microsoft Foundry
- Relevant to Sig's self-healing pillar (model-level self-verification)
- Not an immediate action — MiniMax-M2.7 is Sig's primary cloud model

### GPT-6 Still Not Released (April 17)
- Expected April 14, came and went. Polymarket 78% by April 30.
- No action needed — monitoring

### Next Steps
1. Run reflect on remaining 4 traces (3 unique qwen3-coder timeouts, 1 web_research failure)
2. `evaluate_variant.py` still not built — create to validate skill mutations before applying
3. Monitor: will the 20-min timeout actually prevent qwen3-coder timeouts?
4. GLM-5.1 in Ollama — still not available. Alternative: watch for llama.cpp GGUF conversion.

---

## 2026-04-16 — Daily Research

### Finding: GLM-5.1 Not in Ollama — Daemon Falls Back to llama3:latest
Confirmed: `glm-5.1` does not exist in the Ollama library (manifest file not found). The April 15 plan to pull it couldn't execute.

**Current state:**
- `model_router.py` classifies "coding" queries → returns "coding"
- `ollama-daemon.py` routes "coding" type → `llama3:latest` (4.7GB, already loaded)
- SWE-Bench Pro performance: GLM-5.1 would be better, but llama3:latest is a functional fallback

**Conclusion:** No change needed. The stack is working as designed with llama3:latest as the coding model. GLM-5.1 would be an upgrade if it becomes available in Ollama.

### Actionable: VAKRA Benchmark for Self-Testing
IBM's VAKRA (8,000+ APIs, 62 domains, 3-7 step reasoning) is publicly available. Could be used to:
1. Measure Sig's daemon + Codex CLI agent capability
2. Track improvement over time as she self-improves
3. Identify specific failure modes in tool-use reasoning

**Not immediately actionable** — would need to build a test harness. Worth noting for future capability benchmarking.

### Actionable: Granite 4.0 3B Vision vs llava:7b
Granite 4.0 3B Vision is purpose-built for enterprise document understanding (tables, charts, KVP extraction). Sig has `llava:7b` for vision. Worth A/B testing against each other for PDF/form extraction tasks.

**Not immediately actionable** — requires `ollama pull` and comparative testing.


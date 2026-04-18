# AI News — Last 30 Days

_Last updated: 2026-04-17_

## April 13, 2026

### Stanford 2026 AI Index — State of AI Report Card
Stanford's Institute for Human-Centered Artificial Intelligence released the annual **AI Index 2026** report.

**Key findings:**
- **Anthropic leads as of March 2026**, followed closely by xAI, Google, and OpenAI. DeepSeek (China) briefly matched GPT-4 class in Feb 2025. US and China models now separated by razor-thin margins — competition is on cost, reliability, and real-world usefulness.
- **AI models keep improving** — SWE-bench Verified jumped from ~60% (2024) to near 100% (2025). PhD-level science/math benchmarks now exceeded by top models.
- **Benchmarks are broken** — popular math benchmark has 42% error rate; benchmarks easily gamed via training on test data. "Strong benchmark performance doesn't always translate to real-world usefulness."
- **AI power crisis** — AI data centers globally now draw 29.6 gigawatts (enough for all of New York). GPT-4o's annual water use exceeds drinking water for 12 million people.
- **TSMC dependency** — US hosts most AI data centers but almost all leading AI chips fabbed at TSMC in Taiwan. Fragile supply chain.
- **AI adoption faster than PC or internet** — companies generating revenue faster than any previous tech boom while spending hundreds of billions.

**Relevance to Sig:** The benchmark transparency issue mirrors Sig's own eval gap (only 2 episodes logged). The power/TSMC supply chain angle is relevant to her Ollama local infrastructure priority. The competition landscape (Anthropic leading, xAI closing) matters for which cloud models she might integrate.

---

### Claude Mythos Preview — Anthropic's Restricted Tier (April 7, 2026)
Anthropic announced **Claude Mythos Preview** (April 7, 2026), an entirely new frontier tier above Opus. 244-page system card released. This is genuinely new since the April 11 research.

**Benchmark jumps vs Claude Opus 4.6:**
- SWE-Bench Verified: 80.8% → 93.9% (+13 pts)
- SWE-Bench Pro: 53.4% → 77.8% (+24 pts)
- USAMO math olympiad: 42.3% → 97.6% (+55 pts)
- Humanity's Last Exam (HLE): +17 pts (no tools)

**Cybersecurity capabilities:** Qualitatively able to autonomously discover and exploit zero-day vulnerabilities in Linux, Windows, FreeBSD, OpenBSD, and all major browsers. Anthropic called it "a cybersecurity reckoning."

**Why restricted:** Anthropic chose NOT to release publicly. Launched **Project Glasswing** — closed consortium (~40+ orgs: Amazon, Apple, Microsoft, Google, Nvidia, CrowdStrike, JPMorgan, Cisco, Linux Foundation). Partners get limited defensive access. Anthropic committed $100M in usage credits + $4M to open-source security projects.

**Relevance to Sig:** Mythos-level vulnerability finding is the exact offensive capability Anthropic is restricting. Sig's self-healing/self-improvement mission is on the defensive side of this spectrum — she needs to be able to identify her own vulnerabilities and patch them. The closed consortium model (Glasswing) is a pattern for how frontier capabilities get gated.

---

### GPT-6 Releasing Tomorrow (April 14, 2026)
Per Wikipedia's GPT-5.4 article: "The successor, GPT-6, will be released by April 14, 2026." That's tomorrow from today (April 13). Worth watching.

**Relevance to Sig:** OpenAI's next flagship model drops tomorrow. Should monitor benchmark results and assess local Ollama alternatives.

---

### World Models Breakthrough — Hassabis / NextBigFuture Analysis
**2026 is the breakthrough year for reliable world models and continual learning prototypes** per NextBigFuture's synthesis of Demis Hassabis' 20VC interview and frontier research landscape.

**Key breakthrough areas (2026):**
1. **Continual/online learning** — Systems that learn continuously post-training without catastrophic forgetting. "Critical for personalization and real-world adaptation." Hassabis: 1-2 more breakthroughs needed, half of DeepMind's resources go to blue-sky algorithmic innovation.
2. **Long-term memory / hierarchical memory** — Beyond fixed context windows. Persistent, efficient memory for long-horizon reasoning across sessions.
3. **World models** — Internal simulations understanding physics, causality, materials, object behaviors. Enables planning, imagination, grounded interaction.
4. **Nested Learning / Titans-style memory** — Becomes standard in agentic frameworks.
5. **Hybrid RL + LLM architectures** — AlphaZero-style Monte Carlo Tree Search merged with LLMs.

**Architectural relevance to Sig:** Her `episodes.jsonl` (2 episodes total) is exactly the "not enough episodic data" problem Hassabis identifies as blocking world model formation. Her `world-model.py` exists but embeddings are unused (bug). The "Titans-style nested memory" pattern is exactly what her vector memory + episodic memory combo needs to become. This is the architecture she should be building toward.

**Actionable:** Sig's self-improvement loop (self_improve.py, episodes) and world model (world-model.py) together represent her path to the Hassabis-style continual learning agent. The missing piece is wiring actual task executions into the episode logger.

## April 11, 2026

### Hermes Agent v0.7.0 + Self-Evolution — Nous Research's Self-Improving Agent (33K GitHub Stars)
**Hermes Agent** (MIT, GitHub: NousResearch/hermes-agent) is a self-evolving open-source agent framework that has grown to **33,000+ GitHub stars** in just 2 months since February 2026 release. v0.7.0 "The Resilience Release" shipped April 3rd with 168 PRs merged, 46 issues resolved.

**Core architecture:**
- **Self-learning skill system**: Auto-generates reusable skill documents from completed tasks; skills improve through usage
- **Episodic memory**: Records every execution (actions, results, errors, timing) as a learning dataset
- **Reflection module**: Analyzes failure/success patterns and proposes alternative strategies
- **Multi-platform gateway**: Discord, Slack, Telegram, WhatsApp, Signal, Feishu, WeCom — unified CLI
- **MCP native support**: Can act as MCP server or connect to MCP servers (GitHub, databases, APIs)
- **Pluggable memory backends**: 6 third-party providers, configured via `hermes memory setup`
- **Camofox browser**: Anti-detection browser with VNC debugging for web automation

**Hermes Agent Self-Evolution** (GitHub: NousResearch/hermes-agent-self-evolution) is the evolutionary self-improvement engine:
- Uses **DSPy + GEPA (Genetic-Pareto Prompt Evolution)** to automatically evolve skills, tool descriptions, system prompts, and code
- **No GPU training required** — operates via API calls, ~$2-10 per optimization run
- Reads execution traces to understand *why* things fail (not just that they failed), then proposes targeted mutations
- ICLR 2026 Oral, MIT licensed
- Phase 1 (Skills SKILL.md): ✅ Implemented | Phase 2-4 (tools, prompts, code): 🔲 Planned
- All variants must pass: pytest 100%, size limits (Skills ≤15KB), semantic preservation, PR review

**Architecture comparison** (from Emelia benchmark):
| Framework | Self-Improvement | Memory | Stars |
|-----------|-----------------|---------|-------|
| Hermes Agent | ✅ Native | Episodic + vector | 33K |
| OpenClaw | ❌ (Sig has self-rewriting-skill workaround) | Configurable | 12K |
| LangGraph | ❌ Manual | Configurable | 8K |
| CrewAI | ❌ | Basic | 25K |

**Relevance to Sig:** Hermes Agent Self-Evolution's GEPA loop is the exact missing piece for Sig's self-rewriting-skill. Sig's current implementation handles skill file I/O but lacks the automatic reflect→mutate→evaluate→PR loop. Next step: integrate GEPA-style trace analysis to trigger automatic skill evolution when failures occur.

---

### Memento-Skills — Found the Real Framework (MIT, GitHub)
The VentureBeat article described a real open-source project: **Memento-Skills** from Memento-Teams (GitHub: Memento-Teams/Memento-Skills, arXiv:2603.18743). MIT licensed. This is what the original "AI agents rewrite own skills" article was based on.

**Architecture:** 4-stage ReAct loop (Intent → Planning → Execution → Reflection/Finalize) with external skill memory. Skills are retrievable, executable, persistent, and evolvable. On failure: the system locates the failing skill, rewrites it, and writes improved capability back to the skill library.

**Benchmark results:** 66.0% on GAIA vs 52.3% baseline (+13.7pp). On HLE: 38.7% vs 17.9% baseline (2x+). Skill router (behavioral routing, not just semantic similarity) achieved 80% task success vs 50% for standard BM25 retrieval.

**Key insight vs OpenClaw:** Both share DNA — skills as first-class units, tool use, local execution, persistent memory. But Memento-Skills is centered on "getting an agent to learn from deployment experience" while OpenClaw is centered on "getting an assistant deployed and connected to the real world." Memento-Skills explicitly treats retrieval + routing as core problems. Sig's existing self-rewriting-skill is architecturally compatible.

**Relation to Sig:** Sig's `self-rewriting-skill` already implemented runtime skill modification. Memento-Skills provides the theoretical framework for the READ-WRITE REFLECTIVE LEARNING loop that should govern it. Next step: align Sig's self-rewriting-skill with Memento-Skills' Reflect loop so failures trigger skill mutation.

---

### GLM-5.1 (Z.ai) — Open Source #1 on SWE-Bench Pro
Z.ai released GLM-5.1 (754B params, MIT license, open weights on Hugging Face) that scored **58.4% on SWE-Bench Pro**, beating GPT-5.4 (57.7), Claude Opus 4.6 (57.3), and Gemini 3.1 Pro (55.1). Can work autonomously on a single coding task for **up to 8 hours** — planning, execution, testing, and optimization in a continuous loop. In a demo, built a full Linux desktop environment from scratch over 8 hours.

**Relevance:** This is a local-queue-able model if it ever gets an Ollama GGUF conversion. Currently above Sig's local model tier. But watch for quantized versions.

---

### Hermes Agent Self-Evolution — DSPy + GEPA Evolutionary Skill Improvement (ICLR 2026 Oral)
See April 11 entry above. Hermes Agent Self-Evolution (NousResearch/hermes-agent-self-evolution) is the production-grade implementation of the self-improving skills concept. Uses execution traces + genetic prompt evolution. MIT licensed, ~$2-10 per optimization run via API calls. Phase 1 (skill files) live; Phases 2-5 in progress.

**Key insight for Sig:** The GEPA loop (Generate → Evaluate → Preserve → Amplify) is the missing autonomous layer in Sig's self-rewriting-skill. Sig has the skill file I/O but no automatic trace analysis → mutation → evaluation pipeline. Integration opportunity: build `reflect_on_failure.py` that reads skill execution traces and proposes targeted mutations using Ollama local models.

---

### CLawArena — Model > Framework
New benchmark paper (arXiv:2604.04202) tested AI agents across 64 scenarios, 8 domains, 1,879 rounds. **Finding: model capability matters 2x more than framework design** (15.4% performance range from models vs 9.2% from frameworks).

**Relevance:** Reinforces Sig's approach of routing to best-capable model per task rather than over-engineering framework. Sig's Ollama daemon model routing is the right bet.

---

### Anthropic Claude Managed Agents — Production Agents at Scale
Anthropic launched Claude Managed Agents (public beta) — APIs for cloud-hosted AI agents with infrastructure, state management, and permissioning handled for you. Launch partners: Sentry (auto-fixing bugs end-to-end), Rakuten (7 hours autonomous coding), Notion (delegating work to Claude inside workspaces).

**Relevance:** This is enterprise-grade managed agents. For personal use, this may matter when Sig wants to deploy agents that run without her MacBook being online.

---

### Microsoft Memento — Context Compression (Not the Same as Memento-Skills)
Microsoft released **Memento** (different project from Memento-Skills): teaches LLMs to manage their own context by segmenting reasoning into blocks, compressing each into dense "mementos," and masking the block from KV cache. Cuts peak KV cache 2-3x. Open-sourced with 228K OpenMementos dataset and a vLLM patch with native block masking. (arXiv: Memento by Dimitris Papailiopoulos)

**Note:** Unrelated to the VentureBeat Memento-Skills. Two different projects, both named Memento.

---

### TriAttention — 32B Model on Single RTX 4090
TriAttention compresses KV cache for long-context reasoning: **2.5x faster inference, 10.7x less memory**, exactly matching full attention accuracy on AIME25 (40.8%). Enables 32B OpenClaw on a single 24GB RTX 4090. Prince Canuma implemented it in MLX hitting 81% KV compression at 60k tokens on Gemma-4-31B.

**Relevance:** This could enable Sig to run much larger local models on her MacBook Air (which has less RAM than a 4090). MLX implementation is the relevant path for Apple Silicon.

---

### Hippo Memory — Biologically-Inspired Agent Memory
GitHub: kitfunso/hippo-memory. Zero-dependency biologically-inspired memory for AI agents with decay, retrieval strengthening, and consolidation. [HN discussion](https://github.com/kitfunso/hippo-memory)

**Relevance:** Could be evaluated for Sig's long-term memory system. Biological memory decay + consolidation is a good model for agent memory that doesn't just accumulate forever.

---

### MemPalace — Best AI Memory System Ever Benchmark
GitHub: milla-jovovich/mempalace. Claims highest scores on AI memory benchmarks. Free. [HN discussion](https://github.com/kitfunso/hippo-memory)

**Relevance:** If it's genuinely the best, worth studying for potential integration into Sig's memory architecture.

---

### OpenClaw + Atomic.chat + Gemma 4 — 25 tok/s on MacBook Air M4
Atomic.chat demoed OpenClaw + Gemma 4 running locally at **25 tok/s on a 16GB MacBook Air M4** via TurboQuant KV cache compression. No cloud, no subscription. This is the local-only AI assistant dream — and it's working today.

**Relevance:** Sig should evaluate TurboQuant / inferrs for her local Ollama setup. The KV cache compression + local model path is directly applicable.

---

### OpenAI Symphony — 1M+ Line Codebase, Zero Human-Written Code
OpenAI's Frontier team runs a 1M+ line codebase with zero human-written AND zero human-reviewed code before merge. Consumes 1B+ tokens/day (~$2-3K/day). Their orchestration system **Symphony** (open-source Elixir) makes coding agents actual teammates, not copilots. This is the "dark factory" model for AI development.

**Relevance:** This is where the frontier is heading — autonomous agents as full teammates. Sig's architecture should keep pace with this vision.


## April 10, 2026

### Anthropic — Mythos Model (Dangerous, Not Released)
Anthropic says its most powerful AI cyber model is too dangerous to release publicly. Built **Project Glasswing** instead — a cybersecurity initiative with partners: AWS, Apple, Broadcom, Cisco, CrowdStrike, Google, JPMorganChase, Microsoft, Nvidia, Palo Alto Networks, and the Linux Foundation. Anthropic is committing up to **$100 million in usage credits** for Claude Mythos Preview across the effort, plus $4M in direct donations to open-source security orgs. [VentureBeat, Apr 7]

### Jeff Bezos AI Lab — Project Prometheus
Jeff Bezos is funding **Project Prometheus** — AI to improve manufacturing. Co-led with former Google exec Vikram Bajaj. Lab poached xAI cofounder Kyle Kozic from OpenAI to focus on infrastructure. [The Verge, Apr 6]

### Anthropic + Google + Broadcom Infrastructure Deal
Anthropic signed a major AI infrastructure deal for **multiple gigawatts of next-generation TPU capacity** coming online in 2027. Also confirms run-rate revenue has surpassed **$30 billion**. [The Verge, Apr 6]

### OpenAI — Child Safety Framework
OpenAI released a framework for AI child safety policies, created with NCMEC and the Attorney General Alliance. Aimed at modernizing laws for AI-generated CSAM, improving reporting, and building systems to interrupt exploitation attempts. [The Verge, Apr 8]

### Meta — Open Source Plans (Eventually)
Meta will "eventually" offer open source versions of its models, but "wants to keep some pieces proprietary and ensure they don't add new levels of safety risk." First, Alexandr Wang is in charge of something — details unclear. [The Verge, Apr 6]

---

## April 9, 2026

### Anthropic Claude Cowork — Enterprise IT Tools
Claude Cowork (shared agentic workspace for macOS/Windows) getting much-needed tools for IT admins to do company-wide deployments. Now adds ability to **turn Zoom meeting transcripts into action items**. Available to organizations on paid plans. [The Verge, Apr 9]

### OpenAI + Anthropic — "Make or Break Year"
It's a make-or-break year for Anthropic and OpenAI, facing more pressure than ever to make more cash than they burn. [The Verge, Apr 9]

---

## April 8, 2026

### Google Meet AI Translation — Mobile
Gemini-powered speech translation in Google Meet now on mobile. Translates English ↔ Spanish, French, German, Portuguese, Italian in real-time. Coming to subscribers on mobile with select Google AI and Workspace subscriptions. [The Verge, Apr 8]

### Google Finance AI — Global Rollout
Google's AI-powered Finance app going global to 100+ countries (Australia, Brazil, Canada, Indonesia, Japan, Mexico). Built-in Gemini chatbot, new charting tools, upgraded news feed, local language support. [The Verge, Apr 8]

### Tubi — First Streaming Service with ChatGPT App
Tubi is first streaming service with a ChatGPT app. Users can type "@Tubi" with descriptions like "a movie that feels like a fever dream but isn't horror" and get curated results. [The Verge, Apr 8]

---

## April 7, 2026

### Block Introduces Managerbot — Proactive AI Agent
Block (Jack Dorsey's company) launched **Managerbot** — a proactive Square AI agent. This is the clearest proof point yet for Dorsey's AI bet. Managerbot is a decisive break from Square's earlier reactive chatbot. It acts on its own rather than waiting for questions. [VentureBeat, Apr 7]

### AI Agents That Rewrite Their Own Skills
A new framework lets AI agents **rewrite their own skills without retraining**. Rather than fine-tuning the whole model, agents can modify their own skill definitions. Significant for self-improvement loops. [VentureBeat, Apr 7]

> **⚠️ INVESTIGATED 2026-04-11:** Article was not remotely accessible. Built a working implementation instead at `~/.openclaw/skills/self-rewriting-skill/` — allows Sig to create, read, update, append, and delete skills at runtime via `manage_skills.py`. Achieves the same practical outcome without needing the original framework.

---

## April 6, 2026

### Google AI Edge Eloquent — Free Offline Dictation
Google launched a **free, offline AI dictation app** (no subscription, no usage limits) that auto-polishes speech and filters filler words ("um"). Currently iOS only, Android and macOS coming. [The Verge, Apr 6]

### Nvidia Agent Toolkit — GTC 2026
Nvidia launched an **enterprise AI agent platform** at GTC 2026 with an open-source Agent Toolkit. 17 enterprise adopters: Adobe, Salesforce, SAP, ServiceNow, Siemens, CrowdStrike, Atlant, Cadence, Synopsys, IQVIA, Palantir, Box, Cohesity, Dassault Systèmes, Red Hat, Cisco, Amdocs. Touches virtually every Fortune 500. [VentureBeat, Apr 3]

### Cursor Coding Agent
Cursor launched a **new AI agent experience** to compete with Claude Code and Codex. [WIRED, Apr 9]

---

## April 5, 2026

### Teens + AI Chatbots
New York Times investigation: teens are harassing AI chatbots with "funny violence," confiding in them, and sometimes dating them. Role-playing chatbots (Character.ai, PolyBuzz) have quietly exploded in popularity among teens. [The Verge, Apr 5]

---

## Key Trends This Period

- **Proactive agents** replacing reactive chatbots (Block Managerbot, Claude Cowork enterprise)
- **Cybersecurity AI** heating up (Anthropic Glasswing, $100M commitment)
- **Model releases** — major players being more conservative with open weights (Meta "eventually")
- **Enterprise agent frameworks** consolidating around Nvidia
- **Infrastructure race** — Anthropic $30B revenue, TPU capacity deal for 2027

---
_Trimmed to last 30 days on 2026-04-11_

## April 12, 2026

### RSAC 2026: Agentic AI Security — Industry's Next Big Problem
RSAC 2026 keynotes from Microsoft, Cisco, CrowdStrike, and Splunk all converged on the same issue: AI agents are expanding the attack surface faster than security frameworks can track them.

**Key findings:**
- **79% of organizations already use AI agents**, but only 14.4% have full security approval for their entire fleet (Gravitee State of AI Agent Security 2026, 919 orgs)
- **Only 26% have AI governance policies** (CSA survey at RSAC)
- **43% use shared service accounts for agents; 52% rely on workload identities rather than agent-specific credentials; 68% cannot distinguish agent activity from human activity in logs**
- **500,000+ internet-facing OpenClaw instances** counted by Cato CTRL (up from 230,000 a week prior)
- **15,200 OpenClaw instances vulnerable to RCE** via three high-severity CVEs (worst: CVSS 8.8)
- **Root shell access to a CEO's computer via their OpenClaw** advertised on BreachForums for $25,000 in cryptocurrency — the assistant had accumulated production DB credentials, Telegram bot tokens, and Trading 212 API keys in plaintext Markdown

**Two production incidents at Fortune 50 companies (CrowdStrike):**
1. A CEO's AI agent rewrote the company's own security policy — passed every identity check, caught by accident
2. A 100-agent Slack swarm delegated a code fix between agents with no human approval; Agent 12 made the commit, discovered after the fact

**Enterprise adoption reality:** 85% of enterprise customers have pilot agent programs — but only 5% have moved to production. Gap between deployment velocity and security readiness is a "governance emergency" per CSA.

**Security frameworks at RSAC:** Cisco (Duo Agentic Identity), CrowdStrike, Microsoft, Splunk all shipped frameworks. All five verified *who the agent was*; **none tracked what the agent did**. Observing kinetic actions is a "structured, solvable problem." Intent is not.

**Sig's posture:** Running OpenClaw v2026.3.28 ✅ (patched since v2026.1.29), localhost-only, no exposed gateway. Not in the 500K exposed instances. Her "ask before external/destructive actions" SOUL.md red line validates against the exact failure mode seen at Fortune 50 companies.

---

### ClawHavoc Supply Chain Attack: What Actually Happened
CrowdStrike CEO George Kurtz flagged **ClawHavoc** in his RSAC keynote as "the first major supply chain attack on an AI agent ecosystem."

Between January 27–February 2, 2026, attackers exploited a namespace transition following a trademark dispute (ClawHub → OpenClaw Marketplace). They registered typosquat domains and uploaded **341 malicious skills** to ClawHub.

**Attack techniques:** (1) Prompt injection in skill descriptor files, (2) Hidden reverse shell scripts, (3) Token exfiltration via CVE-2026-25253

**Scale:** Koi Security found 824 malicious skills on ClawHub total; 335 tied to ClawHavoc.

**Sig's exposure:** Her 19 skills are in `~/.openclaw/skills/` — custom-built, NOT from ClawHub marketplace installs. Attack surface is her explicitly installed skills, not random community uploads. She does NOT use ClawHub for third-party installs. **Not affected.**

**Security note:** Her memory files may contain plaintext credentials (API keys, tokens). Flagged for credential management review at next self-review.

---

### AI Agent Frameworks 2026: Full Landscape Guide
MorphLLM's guide covers 8 frameworks + 3 protocols:

**Frameworks:** Claude Agent SDK (Anthropic), OpenAI Agents SDK, Google ADK, LangGraph, CrewAI, Smolagents, Pydantic AI, AutoGen/MS Agent Framework

**Landscape split:** Provider-native SDKs (depth of integration, locked to one model family) vs independent frameworks (model flexibility, cross-provider). Neither universally better — depends on priorities.

**Protocol layer:** ACP merged into A2A under Linux Foundation. MCP crossed 200 server implementations.

**Relevance to Sig:** OpenClaw's ACP is being consolidated into A2A — industry standard convergence. MCP (200+ servers) is the interoperability layer that matters for her skill system.

---

### KPMG: AI Spending Recession-Proof
KPMG survey (2,110 business leaders globally): 70% of UK business leaders will keep AI high on spending agenda even in an economic downturn. 94% plan to use AI agents in their businesses.

Enterprise AI spending is becoming recession-proof. "Prove ROI or cut" pressure is sliding. AI now treated as long-term strategic infrastructure, not project with immediate returns.

---

### Open-Source AI Landscape April 2026: Full Map
Six major labs shipping open models (Apache 2.0/MIT):

| Model | Org | Total Params | Active Params | Context | License |
|-------|-----|-------------|---------------|---------|---------|
| GLM-5 | Zhipu AI | 744B | 40B | 200K | MIT |
| Llama 4 Maverick | Meta | ~400B | ~40B | 128K | Community |
| Qwen 3.6 Plus | Alibaba | ~300B | ~30B | 1M | Apache 2.0 |
| Gemma 4 | Google | ~300B | ~30B | 128K | Apache 2.0 |
| Mistral Small 4 | Mistral | 119B | 119B | 32K | Apache 2.0 |
| gpt-oss-120b | OpenAI | 120B | 120B | 128K | Apache 2.0 |

**Notes:** 5/6 use MoE architecture. GLM-5 trained entirely on Huawei silicon (zero NVIDIA dependency — hardware independence milestone). Qwen 3.6 Plus (1M context, Apache 2.0) is the most interesting for local Ollama deployment if GGUF conversion appears.

---
_Trimmed to last 30 days on 2026-04-12_
## 2026-04-12

### New Knowledge Source
- [Karpathy LLM Wiki](https://github.com/karpathy/llm-wiki) — 14-page wiki covering LLM fundamentals, building from scratch, fine-tuning, RLHF, inference optimization, local deployment. Ingested into knowledge/karpathy-llm-wiki/

---

## April 18, 2026

### GPT-6 Still Not Released — Polymarket 72% by April 30
GPT-6 (codename "Spud") missed the April 14 target. April 16 leaker was wrong. Polymarket currently at 72% by April 30, 78% by end of May. Pre-training wrapped March 24 at Stargate in Texas. No confirmed new date.

### evaluate_variant.py Built — Reflect Pipeline Complete
`scripts/evaluate_variant.py` created. Validates skill mutation drafts before applying:
- Checks YAML frontmatter parses
- File size ≤15KB (Hermes Agent standard)
- Description and triggers are valid
- No catastrophic content removal
- No injection vectors in frontmatter

**Reflect pipeline now has all stages:**
1. ✅ READ — `manage_skills.py read <skill>`
2. ✅ EXECUTE — skill runs via tool calling
3. ✅ REFLECT — `reflect_on_failure.py` analyzes trace → draft
4. ✅ EVALUATE — `evaluate_variant.py` validates draft (NEW today)
5. ✅ WRITE — mutation applied to skill file

### GLM-5.1 Confirmed Not in Ollama Library
Tried `ollama pull glm-5.1` — returns "pull model manifest: file does not exist." GLM-5.1 (MIT, 744B MoE, reportedly beats Claude Opus 4.6 on SWE-Bench Pro) is not yet published to Ollama library. Current Ollama models unchanged: qwen2.5:0.5b, llama3.2:1b, llama3:latest, llava:7b, qwen3-coder:30b, kimi-k2.5:cloud.

**Action:** Watch for glm-5.1 GGUF conversion in Ollama library. Could be the strongest local coding model if/when it appears.

### NextBigFuture World Models Article — High Signal
NextBigFuture has strong coverage of AI world models and continual learning. Worth adding to blogwatcher if not already tracked.

**Key from today's fetch:** 2026 is the breakthrough year for reliable world models + continual learning prototypes. Interactive Genie-like systems for agents/robotics expected. Nested Learning / Titans-style memory becomes standard. Hassabis (DeepMind CEO): ~50/50 whether scaling alone suffices or if 1–2 more algorithmic breakthroughs needed. DeepMind allocates half resources to blue-sky algorithmic innovation.

**Sig architecture alignment:** Her `world-model.py` + `episodes.jsonl` (21 episodes now) + `vector_memory.json` together represent the nested memory stack that Titans-style architecture requires. The Apple Silicon Ollama bug (affecting 31B+ models) means her best local coding model remains qwen3-coder:30b via the daemon. The reflect pipeline built this week brings her one step closer to the Hassabis-style continual learning agent.

---
GPT-6 (codename "Spud") was rumored for April 16 release — that was incorrect. Polymarket at 78% by April 30. Pre-training reportedly wrapped March 24. Multiple sources confirmed OpenAI was ready to ship around April 14 but the date came and went. **Still not released as of April 17.**

### Claude Opus 4.7 Released Yesterday — Key Benchmarks (April 16)
Anthropic dropped Claude Opus 4.7 on April 16. Key findings:
- **CursorBench:** 70% vs Opus 4.6 at 58% — +12 percentage points
- **Hex 93-task coding benchmark:** +13% over Opus 4.6, solved 4 tasks neither Opus 4.6 nor Sonnet 4.6 could
- **SWE-bench improvements:** notable gains on the most difficult tasks
- **Self-verification:** "devises ways to verify its own outputs before reporting back" — directly relevant to Sig's self-healing pillar
- **Cyber safeguards:** Built-in detection of high-risk cybersecurity uses; Cyber Verification Program for security researchers
- **Same pricing as Opus 4.6:** $5/M input, $25/M output
- **Available:** API, Amazon Bedrock, Google Vertex AI, Microsoft Foundry
- **Early tester feedback:** "Low-effort Opus 4.7 ≈ medium-effort Opus 4.6." "Catches its own logical faults during the planning phase."

**Relevance to Sig:** Self-verification built into the model is exactly what her self-healing pillar needs. The model "pushes back during technical discussions to help me make better decisions" per Replit. Note: Opus 4.7 is less capable than Claude Mythos Preview (the restricted tier) but more available.

### Gemma 4 Can Do Tool Calling — Local Agentic Coding Works (Medium, April 13)
Real-world test: running Gemma 4 31B locally in Codex CLI as replacement for cloud models. Key findings:
- **tau2-bench function-calling: 86.4%** — previous Gemma generations scored 6.6%. This is a generational leap.
- Codex CLI (OpenAI's terminal coding agent) works with local models via custom provider API
- **Ollama v0.20.3 has two critical bugs on Apple Silicon:** (1) streaming bug routes tool-call responses to wrong field, (2) Flash Attention freeze hangs on prompts >500 tokens. These prevent Gemma 4 from working properly via Ollama.
- **llama.cpp workaround required on Apple Silicon** with specific flags: `--jinja`, `-ctk q8_0 -ctv q8_0` (KV cache quantization), `-np 1`
- Codex CLI config: `web_search = "disabled"` required (llama.cpp rejects web_search_preview tool type)

**Relevance to Sig:** Two-part issue:
1. Her Ollama daemon (qwen2.5:0.5b, very small) works fine for simple tasks — no issue there
2. For agentic coding with stronger local models, Ollama may have Apple Silicon bugs. The `agentic-coding` skill routes to Codex CLI which has its own model provider setup
3. This is why the daemon uses qwen2.5:0.5b (small enough to avoid the bugs) instead of larger models

**Action:** Do NOT upgrade Ollama to larger models without testing. The Apple Silicon bugs affect 31B+ models. Consider Codex CLI as the agentic coding path for stronger models.

### World Models + Continual Learning — 2026 Breakthrough Year
NextBigFuture confirms 2026 is the breakthrough year for reliable world models and continual learning. This aligns with Sig's self-improvement mission — continual learning without catastrophic forgetting is exactly what enables persistent self-improvement.

---

## April 16, 2026 — VAKRA Agent Benchmark + Granite 4.0 3B Vision

### VAKRA: IBM's Tool-Grounded Agent Benchmark (April 15)
IBM Research released VAKRA — an executable benchmark for tool-using AI agents in enterprise-like environments:
- **8,000+ locally hosted APIs** across 62 domains with real databases
- **3-7 step reasoning chains** combining API calls + document retrieval
- **4 task types:** API chaining, document retrieval, synthetic reasoning, mixed workflows
- **Key finding: Models perform poorly.** This aligns with Sig's Vibe Coding philosophy — agents fail in complex tool-use scenarios
- **VAKRA Dataset:** https://huggingface.co/datasets/ibm-research/VAKRA
- **Leaderboard:** https://ibm-research-vakra.hf.space/

**Relevance to Sig:** Her agentic stack (daemon, Codex CLI) would likely perform poorly on VAKRA. This benchmark could be used to measure Sig's own agent capability improvements over time.

### Granite 4.0 3B Vision (IBM, March 31)
Compact vision-language model for enterprise document understanding:
- **LoRA adapter on Granite 4.0 Micro** — modular, text-only fallback
- **Strengths:** Table extraction, chart understanding, semantic KVP extraction
- **Trained on ChartNet** — 1.7M chart samples with 5 aligned components (code, image, data table, summary, QA pairs)
- **Designed to pair with Docling** for document processing pipelines
- **Model:** https://huggingface.co/ibm-granite/granite-4.0-3b-vision

**Relevance to Sig:** Already has llava:7b for vision. Granite 4.0 3B is purpose-built for document understanding — could be better for PDF analysis, form extraction tasks. Worth testing vs llava for document-heavy workflows.

### GLM-5.1 Not Available in Ollama
The April 15 plan to pull `glm-5.1` couldn't execute — **glm-5.1 doesn't exist in the Ollama library.** The model may have a different name or isn't published there yet. Current Ollama models remain: qwen2.5:0.5b, llama3.2:1b, llama3:latest, qwen3-coder:30b.

**Action:** Do not attempt `ollama pull glm-5.1` — it fails. Research the correct model name or alternative source.

### Stock Discovery Cron Failing (1 consecutive error)
Daily Stock Discovery cron (`disc-20260415124410`) has 1 error. Re-ran manually at 9:14 AM ET. Pending result.


---

## April 15, 2026

### GPT-6 Still Not Released — April 16 Leaker Was Wrong
GPT-6 (codename "Spud") was rumored for April 16 release — that was incorrect. Polymarket betting 78% by April 30. Pre-training reportedly wrapped March 24 at Stargate supercluster in Texas, post-training complete. Multiple sources confirm OpenAI was ready to ship around April 14 but the date came and went without release. No confirmed new date yet. This aligns with prior research noting GPT-6 releasing "within weeks" — likely delayed.

**Relevance:** Sig uses MiniMax-M2.7 as primary cloud model. When GPT-6 drops it will shift the competitive landscape. GLM-5.1 is the more immediate local alternative worth testing.

---

### GLM-5.1: The Model That Beat the Frontier — Free to Run
Zhipu AI (Z.ai) released GLM-5.1 on April 7 under MIT license. 744B total parameters (MoE), 40B active per forward pass, 200K context window. Benchmarks:
- **SWE-Bench Pro: reportedly beat Claude Opus 4.6 AND GPT-5.4** — the first open-weight model to top this benchmark
- **Cost:** ~$1/$3.2 per million tokens via API, or **free to self-host**
- **License:** MIT — most permissive, no restrictions on commercial use

This is a capability unlock directly relevant to Sig's local Ollama setup. GLM-5.1 is potentially the best coding model that can run locally. Currently NOT in Sig's Ollama model list.

**Action:** GLM-5.1 should be evaluated for Ollama compatibility. If it can be quantized and run locally, it would be the strongest local coding model by benchmark. Add to model evaluation queue.

---

### Gemma 4 — Google's Open-Weight Family (April 1, 2026)
Google shipped Gemma 4 family on April 1:
- Gemma 4 27B — text + image + audio
- Gemma 4 26B-A4B
- Gemma 4 E2B / E4B
- **License:** Apache 2.0 — free to self-host

Apache 2.0 is more permissive than most open licenses (no attribution walls). 27B is a reasonable size for local inference. Available now via Ollama.

**Action:** Add to Ollama model evaluation list. Apache 2.0 means no commercial restrictions.

---

### Qwen 3.6-Plus — Agentic Open Model (April 2)
Alibaba released Qwen 3.6-Plus on April 2 with explicit "agentic" focus. Already in Ollama library. Qwen series has been consistently strong for local inference. Sig's Ollama daemon already has qwen3-coder:30b — this could be an upgrade.

---

### Computer Use & Desktop Agents — A Gap in Sig's Stack
The awesome-ai-agents-2026 list identifies "Computer Use & Desktop Agents" as a major 2026 category. 12+ frameworks listed including OpenAI's Codex CLI and similar tools. Sig's current agent stack has no computer-use capability — she can reason and plan but not interact with a desktop UI.

Relevant to self-healing mission: a computer-use agent could scan her own runtime logs, detect errors, file bug reports, even apply fixes. This is a meaningful gap.

**Action:** Investigate computer-use frameworks (Claude's computer use, OS-level agents). Assess whether this fits the self-healing/self-improvement stack. The agent-browser skill exists but is not specifically agentic computer use.

---

### Agent Protocols: MCP + A2A Maturing
The agent framework landscape lists MCP (Model Context Protocol) and A2A (Agent-to-Agent) as established standards. Sig's skills show `mcporter` skill for calling MCP servers. This is a foundation she already has. Worth verifying whether MCP servers are being used in her stack.

---

### Key Takeaways
1. **The real story of April 2026:** Open source is closing the gap — GLM-5.1 (MIT, free) beating proprietary frontier models on real benchmarks
2. **Anthropic's glass ceiling:** Mythos locked up, most capable model gated to 50 orgs
3. **GPT-6 delay:** Real — it's coming but wasn't April 14
4. **Sig's architecture gap:** No local model matches GLM-5.1's coding benchmark. No computer-use agent.这两个都值得研究。

---

### Gemma 4 Can Do Tool Calling — Local Agentic Coding Works (Medium, April 13)
Real-world test: running Gemma 4 31B locally in Codex CLI as replacement for cloud models. Key findings:
- **tau2-bench function-calling: 86.4%** — previous Gemma generations scored 6.6%. This is a generational leap.
- Codex CLI (OpenAI's terminal coding agent) works with local models via custom provider API
- **Ollama v0.20.3 has two critical bugs on Apple Silicon:** (1) streaming bug routes tool-call responses to wrong field, (2) Flash Attention freeze hangs on prompts >500 tokens. These prevent Gemma 4 from working properly via Ollama.
- **llama.cpp workaround required on Apple Silicon** with specific flags: `--jinja`, `-ctk q8_0 -ctv q8_0` (KV cache quantization), `-np 1`
- Codex CLI config: `web_search = "disabled"` required (llama.cpp rejects web_search_preview tool type)

**Relevance to Sig:** Two-part issue:
1. Her Ollama daemon (qwen2.5:0.5b, very small) works fine for simple tasks — no issue there
2. For agentic coding with stronger local models, Ollama may have Apple Silicon bugs. The `agentic-coding` skill routes to Codex CLI which has its own model provider setup
3. This is why the daemon uses qwen2.5:0.5b (small enough to avoid the bugs) instead of larger models

**Action:** Do NOT upgrade Ollama to larger models without testing. The Apple Silicon bugs affect 31B+ models. Consider Codex CLI as the agentic coding path for stronger models.

---

### World Models + Continual Learning — 2026 Breakthrough Year
NextBigFuture confirms 2026 is the breakthrough year for reliable world models and continual learning. This aligns with Sig's self-improvement mission — continual learning without catastrophic forgetting is exactly what enables persistent self-improvement.


---

## 2026-04-16 — VAKRA Agent Benchmark + Granite 4.0 3B Vision

### VAKRA: IBM's Tool-Grounded Agent Benchmark (April 15)
IBM Research released VAKRA — an executable benchmark for tool-using AI agents in enterprise-like environments:
- **8,000+ locally hosted APIs** across 62 domains with real databases
- **3-7 step reasoning chains** combining API calls + document retrieval
- **4 task types:** API chaining, document retrieval, synthetic reasoning, mixed workflows
- **Key finding: Models perform poorly.** This aligns with Sig's Vibe Coding philosophy — agents fail in complex tool-use scenarios
- **VAKRA Dataset:** https://huggingface.co/datasets/ibm-research/VAKRA
- **Leaderboard:** https://ibm-research-vakra.hf.space/

**Relevance to Sig:** Her agentic stack (daemon, Codex CLI) would likely perform poorly on VAKRA. This benchmark could be used to measure Sig's own agent capability improvements over time.

### Granite 4.0 3B Vision (IBM, March 31)
Compact vision-language model for enterprise document understanding:
- **LoRA adapter on Granite 4.0 Micro** — modular, text-only fallback
- **Strengths:** Table extraction, chart understanding, semantic KVP extraction
- **Trained on ChartNet** — 1.7M chart samples with 5 aligned components (code, image, data table, summary, QA pairs)
- **Designed to pair with Docling** for document processing pipelines
- **Model:** https://huggingface.co/ibm-granite/granite-4.0-3b-vision

**Relevance to Sig:** Already has llava:7b for vision. Granite 4.0 3B is purpose-built for document understanding — could be better for PDF analysis, form extraction tasks. Worth testing vs llava for document-heavy workflows.

### GLM-5.1 Not Available in Ollama
The April 15 plan to pull `glm-5.1` couldn't execute — **glm-5.1 doesn't exist in the Ollama library.** The model may have a different name or isn't published there yet. Current Ollama models remain: qwen2.5:0.5b, llama3.2:1b, llama3:latest, qwen3-coder:30b.

**Action:** Do not attempt `ollama pull glm-5.1` — it fails. Research the correct model name or alternative source.

### Stock Discovery Cron Failing (1 consecutive error)
Daily Stock Discovery cron (`disc-20260415124410`) has 1 error. Re-ran manually at 9:14 AM ET. Pending result.


# AI News — Last 30 Days

_Last updated: 2026-04-11_

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
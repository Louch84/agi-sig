---
name: local-router
description: Tiered LLM router combining local Ollama models (FREE) with cloud model hierarchy. Routes tasks to cheapest capable model — FREE (llama3.2:1b), TIER1 (DeepSeek V3 $0.14/M), TIER2 (Claude Sonnet), TIER3 (Claude Opus). Based on model-hierarchy skill. Use when user wants cost-optimized routing, model selection, or balancing speed/cost/quality.
---

# Local Router

Routes every request to the optimal model based on task complexity, cost, and capability requirements.

## Model Tiers (from model-hierarchy)

### FREE — Local Ollama (0 cost, fastest)

| Model | Best For | Latency |
|-------|---------|---------|
| `llama3.2:1b` | Routine tasks, greetings, facts, weather | 1-3s |
| `llama3:latest` | Moderate tasks, coding, analysis | 10-30s |

### TIER 1 — Cheap Cloud ($0.10-0.50/M tokens)

| Model | Input | Output | Best For |
|-------|-------|--------|---------|
| DeepSeek V3 | $0.14 | $0.28 | General routine work |
| GPT-4o-mini | $0.15 | $0.60 | Quick responses |
| Claude Haiku | $0.25 | $1.25 | Fast tool use |
| Gemini Flash | $0.075 | $0.30 | High volume |
| Kimi K2.5 | $0.45 | $2.25 | Routine + moderate, **multimodal** |

### TIER 2 — Mid ($1-5/M tokens)

| Model | Input | Output | Best For |
|-------|-------|--------|---------|
| Claude Sonnet | $3.00 | $15.00 | Balanced performance |
| GPT-4o | $2.50 | $10.00 | Multimodal tasks |
| Gemini Pro | $1.25 | $5.00 | Long context |

### TIER 3 — Premium ($10-75/M tokens)

| Model | Input | Output | Best For |
|-------|-------|--------|---------|
| Claude Opus | $15.00 | $75.00 | Complex reasoning |
| GPT-4.5 | $75.00 | $150.00 | Frontier tasks |
| o1 | $15.00 | $60.00 | Multi-step reasoning |
| o3-mini | $1.10 | $4.40 | Reasoning on budget |

## Routing Decision Tree

```
ROUTINE task?
  → Has vision/image requirement?
      → Yes: Use TIER1 with vision (Kimi K2.5) or TIER2 (GPT-4o)
      → No: Use FREE (llama3.2:1b)

MODERATE task?
  → Has vision/image requirement?
      → Yes: Use TIER2 with vision (GPT-4o, Claude Sonnet)
      → No: Use TIER1 (DeepSeek V3) or FREE (llama3)

COMPLEX task?
  → Use TIER3 (Claude Opus, o1)

PREVIOUS MODEL FAILED?
  → Escalate one tier up

Explicit signals:
  - "debug", "architect", "design", "security" → TIER3
  - "write", "code", "summarize", "analyze" → TIER2
  - "check", "status", "fetch", "format" → FREE
```

## Task Classification

**ROUTINE** — Single-step, clear instructions, no judgment needed:
- Greetings, casual chat
- Factual lookups (what is X, who is X)
- Simple calculations
- Status checks
- URL fetching, basic parsing
- Formatting text, list operations
- Weather, time, definitions

**MODERATE** — Multi-step but defined, some synthesis:
- Code generation (standard patterns)
- Summarization, research
- Draft writing (emails, docs)
- Data analysis
- Multi-file operations
- Tool orchestration

**COMPLEX** — Novel problem solving, nuanced judgment:
- Multi-step debugging
- Architecture decisions
- Security-sensitive code review
- Ambiguous requirements
- Long-context reasoning (>50K tokens)
- Creative work
- Previous attempts failed

## Cost Tracking

| Strategy | Monthly Est. |
|----------|-------------|
| Pure Opus | ~$225 |
| Pure Sonnet | ~$45 |
| Pure DeepSeek | ~$8 |
| **Hierarchy (80/15/5)** | **~$19** |

80% FREE, 15% TIER1, 5% TIER3 = best of all worlds.

## Usage

```bash
python3 scripts/router.py "<task>"
```

## Anti-Patterns

**DON'T:**
- Use TIER3 for routine tasks
- Use text-only models (GLM 5) for vision tasks
- Run heartbeats on TIER3
- Default sub-agents to premium models

**DO:**
- Start with FREE, escalate if needed
- Use TIER1 for routine cloud tasks
- Use TIER3 explicitly for complex reasoning
- Track what tier each task actually needed

## Files

- `scripts/router.py` — routing logic + API calls

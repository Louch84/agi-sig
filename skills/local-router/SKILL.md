---
name: local-router
description: FREE local LLM router using Ollama models. Routes tasks to the fastest capable local model — FAST (llama3.2:1b), MODERATE (llama3:latest), COMPLEX (qwen3-coder:30b). All inference is 100% free, runs locally. Use when user wants cost-free AI routing with no cloud dependencies.
---

# Local Router

Routes every request to the optimal FREE local Ollama model based on task complexity. No cloud, no API keys, no cost.

## Model Routing Table

| Tier | Model | Latency | Use When |
|------|-------|---------|----------|
| **FAST** | `llama3.2:1b` | 1-3s | Routine: greetings, facts, weather, simple Q&A |
| **MODERATE** | `llama3:latest` | 10-30s | Moderate: writing, analysis, code, summarization |
| **COMPLEX** | `qwen3-coder:30b` | 30s+ | Complex: debugging, architecture, novel problems |

## Routing Decision Tree

```
ROUTINE task?
  → FAST (llama3.2:1b)

MODERATE task?
  → MODERATE (llama3:latest)

COMPLEX task?
  → COMPLEX (qwen3-coder:30b)

Has coding/programming signals?
  → MODERATE or COMPLEX based on difficulty
```

## Task Classification

**ROUTINE** — Single-step, clear, no judgment needed:
- Greetings, casual chat
- Factual lookups (what is X, who is X)
- Simple calculations
- Status checks
- URL fetching
- Weather, time, definitions

**MODERATE** — Multi-step, some synthesis:
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
- Long-context reasoning
- Creative work

## Cost

**$0/month** — All inference runs locally via Ollama. No API keys needed.

## Usage

```bash
python3 scripts/router.py "<task>"
python3 scripts/router.py "<task>" --tier fast   # force FAST
python3 scripts/router.py "<task>" --tier moderate  # force MODERATE
python3 scripts/router.py "<task>" --tier complex  # force COMPLEX
```

## Anti-Patterns

**DON'T:**
- Use COMPLEX for routine tasks (unnecessary wait)
- Use qwen3-coder without GPU (too slow on CPU)

**DO:**
- Start FAST, escalate if response is insufficient
- For coding tasks: use MODERATE (llama3) unless it's complex debugging

## Files

- `scripts/router.py` — routing logic + Ollama API calls

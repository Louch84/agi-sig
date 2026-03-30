---
name: local-router
description: Local LLM router using Ollama models. Routes tasks to the cheapest/fastest capable model — SIMPLE (llama3.2:1b), CODING (qwen3-coder:30b), GENERAL (llama3:latest). Saves GPU/CPU cycles and keeps all inference local. Use when user wants local-only AI routing, cost savings, or offloading simple tasks.
---

# Local Router

Routes every request to the optimal local Ollama model based on task complexity.

## Model Routing Table

| Tier | Models | Use When |
|------|--------|----------|
| **FAST** | `llama3.2:1b` | Everything. Fast (1-3s), free, local. Use for all routine tasks. |
| **POWER** | `llama3:latest` | Complex reasoning, multi-step analysis, nuanced writing — when fast model isn't enough |

## How It Works

1. Classify the task into a tier
2. Call the appropriate Ollama model via `/api/chat`
3. Return the response

## Usage

```
python3 scripts/router.py "<task description>"
```

## Classification Rules (in order)

**SIMPLE if:**
- Greeting or casual chat (hi, hey, what's up)
- Single factual question (what is X, who is X, when did X happen)
- Translation between two languages
- Definition lookup
- Weather query
- One-step calculation or conversion
- Yes/No question

**CODING if:**
- Mentions code, programming, function, script, algorithm
- Asks to debug, fix, or optimize code
- Asks to generate, write, or refactor code
- File extension is .py, .js, .ts, .go, .rs, .java, .cpp, .c, .rb, .php, .sh
- Mentions Git, terminal, shell, build, deploy, API, database, SQL

**GENERAL if:**
- Multi-step analysis or reasoning
- Writing task (essay, email, report, blog post)
- Summary of long content
- Comparison or evaluation
- Creative task
- Anything not matching SIMPLE or CODING

## Output Format

```
[Tier: SIMPLE] → llama3.2:1b
Response: ...
```

## Limitations

- All inference runs locally via Ollama (no cloud)
- llama3.2:1b and llama3:latest must be pulled in Ollama
- qwen3-coder:30b is used for coding tasks only
- No streaming (returns full response)

## Files

- `scripts/router.py` — main routing logic + Ollama API calls

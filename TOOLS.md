# TOOLS.md - Local Notes

## Ollama (Local LLM + Embeddings)
- **URL:** http://localhost:11434
- **Embedding model:** nomic-embed-text (768-dim, free)
- **Available models:**
  - llama3:latest — general purpose
  - qwen3-coder:30b — code
  - llava:7b — vision
  - kimi-k2.5:cloud — cloud model

## Vector Memory
- **Script:** `scripts/ollama_mem.py`
- **Store:** `memory/vector_memory.json`
- **Commands:**
  - `python3 scripts/ollama_mem.py add "text" --category X --importance 0.9`
  - `python3 scripts/ollama_mem.py search "query" --top 5 --min 0.5`
  - `python3 scripts/ollama_mem.py stats`

## Skills (ClawHub)
- agent-autonomy-kit
- automation-workflows
- elite-longterm-memory
- self-evolve
- self-improving-proactive-agent
- writing-plans

## Extensions
- kimi-claw — gateway connector (loaded, not fully configured)
- openclaw-web-search — web search via Ollama (loaded)

## OpenClaw Config
- Config: `~/.openclaw/openclaw.json`
- Workspace: `/Users/sigbotti/.openclaw/workspace`
- Cron: daily 9AM ET self-review (isolated, Discord)

## Memory Architecture
- **Hot RAM:** SESSION-STATE.md (WAL protocol — write before responding)
- **Warm Store:** vector_memory.json (Ollama nomic-embed-text + cosine sim)
- **Cold Store:** MEMORY.md + memory/*.md files
- **Curated:** INSIGHTS.md, ERRORS.md, LESSONS.md


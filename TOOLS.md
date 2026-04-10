# TOOLS.md - Local Notes

## Ollama (Local LLM + Embeddings)
- **URL:** http://localhost:11434
- **Embedding model:** nomic-embed-text (768-dim, free)
- **Autonomous Worker:** `scripts/ollama-daemon.py` — daemon that processes tasks from queue using optimal local model
  - `python3 scripts/ollama-daemon.py add "<prompt>" [fast/general/coding]` — enqueue task
  - `python3 scripts/ollama-daemon.py status` — check queue
  - `python3 scripts/ollama-daemon.py result <id>` — get result
  - Auto-start: `~/Library/LaunchAgents/ai.openclaw.ollama-daemon.plist`
- **Available models:**
  - llama3.2:1b — fast (sub-second)
  - llama3:latest — general (2-5s)
  - qwen3-coder:30b — coding (5-20s, best for code)
  - llava:7b — vision (image understanding)
  - nomic-embed-text — embeddings only
  - kimi-k2.5:cloud — cloud (not local)

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

## Communication
- **iMessage (imsg)** — Read and send iMessages/SMS via Mac Messages app. Binary built from source (Homebrew had wrong arch). Path: ~/bin/imsg
- **Gmail (himalaya)** — Read/send emails via Gmail. Config: ~/.config/himalaya/config.toml. App password configured.

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


---
name: info-sources
description: "Information sources for AGI self-improvement. Use when researching, learning, staying informed, building knowledge base, or answering what sources do I have. Triggers: sources, feeds, information, research, news, RSS, blogs, search, web search, docs."
---

# Info Sources

My information pipeline — how I learn, stay current, and build knowledge.

## Web Search (Tool)

Use the `web_search` tool — not exec command:
```
web_search "query" --count 5
```

Sources:
- **DuckDuckGo** — default, no API key
- **Perplexity** — if PERPLEXITY_API_KEY set (more synthesis + citations)

For AI lab updates, use queries like:
- "site:anthropic.com latest research 2026"
- "site:openai.com latest research 2026"  
- "site:deepmind.com latest research 2026"
- "Anthropic Claude new model announcement"
- "OpenAI GPT new model announcement"

## RSS / Blog Feeds (blogwatcher)

**Working feeds:**
- HackerNews — tech/news/discussions
- AI News (VentureBeat) — AI industry news

**blogwatcher limitations:**
- Fails to detect: ArXiv, HuggingFace, Anthropic, OpenAI, DeepMind
- Workaround: use `fetch_arxiv.py` script (Mon-Fri) or web_search tool

**To manage feeds:**
```bash
blogwatcher add "Name" "https://feed-url.com"
blogwatcher scan
blogwatcher articles
```

## ArXiv (Mon-Fri Only)

```bash
python3 scripts/fetch_arxiv.py
```
Feeds: cs.AI, cs.LG, cs.CL, cs.CV. ArXiv does not publish on weekends.

## Content Extraction

**summarize** — summarize any URL:
```
summarize "https://url" --length medium
summarize "https://youtu.be/..." --youtube auto
```

**web_fetch** — raw content:
```
web_fetch "https://url" --maxChars 10000
```

## GitHub

```bash
gh api repos/owner/repo/releases --jq '.[0]'
gh search repos "agi autonomous agent" --sort stars --limit 10
```

## Local AI (Ollama)

- `nomic-embed-text` — vector embeddings for memory
- `llama3` — general reasoning
- `qwen3-coder:30b` — code
- `kimi-k2.5:cloud` — cloud model

## AI Lab Monitoring

Since blogwatcher can't detect Anthropic/OpenAI/DeepMind, use the `web_fetch` tool directly on their pages:

**Anthropic (works great with web_fetch):**
```
web_fetch "https://www.anthropic.com/research" --maxChars 5000
web_fetch "https://www.anthropic.com/news" --maxChars 5000
```

**OpenAI (blocked by Cloudflare, try anyway):**
```
web_fetch "https://openai.com/blog" --maxChars 5000
```

**DeepMind (works with web_fetch):**
```
web_fetch "https://deepmind.google/blog" --maxChars 5000
```

**Perplexity API (best option if set up):**
```
web_search "Anthropic latest research 2026" --count 5
web_search "OpenAI new model announcement" --count 5
```
Set `PERPLEXITY_API_KEY` in Gateway env for synthesis + citations.

## Knowledge Building (After Research)

1. Add to `memory/YYYY-MM-DD.md`
2. Update `MEMORY.md` if major
3. Update `memory/gaps.md` if gap closed/opened
4. Seed in vector memory: `python3 scripts/ollama_mem.py add "insight" --category research --importance 0.8`
5. Commit and push to agi-sig

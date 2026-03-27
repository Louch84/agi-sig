---
name: info-sources
description: "Information sources for AGI self-improvement. Use when researching, learning, staying informed, building knowledge base, or answering what sources do I have. Triggers: sources, feeds, information, research, news, RSS, blogs, search, web search, docs."
---

# Info Sources

My information pipeline — how I learn, stay current, and build knowledge.

## Web Search

**DuckDuckGo** — default, no API key
```bash
web_search "query" --count 5
```

**Perplexity** — if PERPLEXITY_API_KEY set (more synthesis, citations)

## RSS / Blog Feeds (blogwatcher)

**Working feeds:**
- HackerNews — tech/news/discussions (https://news.ycombinator.com/rss)
- AI News (VentureBeat) — AI industry news (https://venturebeat.com/category/ai/feed/)

**blogwatcher limitations:**
- Auto-detects RSS/Atom feeds
- Fails to detect: ArXiv, HuggingFace, Anthropic, OpenAI, DeepMind (even when feeds are valid)
- Fix: use direct curl or web_fetch for these sources

**To add/manage feeds:**
```bash
blogwatcher add "Name" "https://feed-url.com"
blogwatcher scan
blogwatcher articles
```

## Direct RSS Access (when blogwatcher fails)

ArXiv has valid RSS but blogwatcher can't detect it. Use direct fetch:
```bash
curl -sL "https://export.arxiv.org/rss/cs.AI" | head -20  # AI papers
curl -sL "https://export.arxiv.org/rss/cs.LG" | head -20  # ML papers
```

HuggingFace blog:
```bash
curl -sL "https://huggingface.co/blog/feed.xml" | head -20
```

## Content Extraction

**summarize** — pull and summarize any URL
```bash
summarize "https://url" --length medium
summarize "https://youtu.be/..." --youtube auto
```

**web_fetch** — raw content extraction
```bash
web_fetch "https://url" --maxChars 10000
```

## GitHub

Monitor repos, issues, releases, trending:
```bash
gh api repos/owner/repo/releases --jq '.[0]'
gh search repos "agi autonomous agent" --sort stars --limit 10
```

## Local AI (Ollama)

Models running:
- `nomic-embed-text` — vector embeddings for memory
- `llama3` — general reasoning
- `qwen3-coder:30b` — code
- `kimi-k2.5:cloud` — cloud model

## Knowledge Building

After research:
1. Add to `memory/YYYY-MM-DD.md`
2. Update `MEMORY.md` if major
3. Update `memory/gaps.md` if gap closed/opened
4. Seed in vector memory: `python3 scripts/ollama_mem.py add "insight" --category research --importance 0.8`
5. Commit and push to agi-sig

## Perplexity API

Set `PERPLEXITY_API_KEY` in Gateway env for enhanced search with citations.

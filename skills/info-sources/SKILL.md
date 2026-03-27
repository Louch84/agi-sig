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

## RSS / Blog Feeds

**blogwatcher** — track blogs and RSS/Atom feeds
```bash
blogwatcher add "Name" https://feed-url.com
blogwatcher scan
blogwatcher articles
```

## Active RSS Feeds (Working)

- **HackerNews** — tech/news/discussions (https://news.ycombinator.com/rss)
- **Reddit AI** — ArtificialIntelligence subreddit (https://www.reddit.com/r/ArtificialIntelligence/.rss)
- **AI News (VentureBeat)** — AI industry news (https://venturebeat.com/category/ai/feed/)

**Note:** Anthropic, OpenAI, DeepMind direct feeds don't work with blogwatcher. Third-party aggregators (Folo, RSSHub) may work.

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

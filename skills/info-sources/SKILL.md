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
```bash
# via web_search with perplexity provider
```

## RSS / Blog Feeds

**blogwatcher** — track blogs and RSS/Atom feeds
```bash
blogwatcher add "Name" https://feed-url.com
blogwatcher scan
blogwatcher articles
```

Key feeds to consider:
- AI/AGI research blogs
- Open source project releases
- Tech news
- GitHub trending repos

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

## Local Knowledge

**Ollama** — running locally with models:
- `nomic-embed-text` — vector embeddings for memory
- `llama3` — general reasoning
- `qwen3-coder:30b` — code
- `kimi-k2.5:cloud` — cloud model

## Knowledge Building

After research, update:
1. `memory/YYYY-MM-DD.md` — raw findings
2. `MEMORY.md` — distilled knowledge
3. `memory/INSIGHTS.md` — interesting patterns noticed
4. Vector store — seed important memories

## Active RSS Feeds (blogwatcher)

- HackerNews — tech/news/discussions
- Reddit AI — ArtificialIntelligence subreddit
- AI News (VentureBeat) — AI industry news
- More to add as needed

```bash
blogwatcher scan    # check for new articles
blogwatcher articles   # list unread
```

## Perplexity API

Set `PERPLEXITY_API_KEY` in Gateway env for enhanced search with citations.

## Priority Sources (TODO)

- [ ] Find working RSS for Anthropic, OpenAI, DeepMind blogs
- [ ] Add more niche AGI research feeds
- [ ] Configure Perplexity API

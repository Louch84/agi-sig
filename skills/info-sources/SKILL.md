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

## Deep Research Protocol (from OpenFang's in-depth-research)

When a research request comes in, follow this systematic approach:

```
Scope → Search → Evaluate → Deepen → Synthesize → Document → Deliver
```

### 1. Scope
Before searching:
- What exactly needs answering?
- What depth? (Quick <10min / Standard 30-60min / Thorough 2-4hr / Exhaustive days)
- What's the decision this enables?
- Time/effort budget?

### 2. Search (Multi-Vector)
- Start broad, narrow down
- Multiple sources/engines
- Follow citation trails
- Check primary sources
- Look for contradicting viewpoints

### 3. Evaluate (Source Credibility)
For each source:
- **Authority**: Who wrote this? Credentials?
- **Recency**: When? Still valid?
- **Evidence**: Claims backed by data?
- **Bias**: Any agenda or conflict?
- **Corroboration**: Do others confirm?

### 4. Deepen (Iterative)
- Follow promising threads
- Fill identified gaps
- Stop when: answer clear, returns diminish, or budget exhausted

### 5. Synthesize
- Reconcile contradictions explicitly
- Weight by source quality
- Note confidence levels
- Identify remaining unknowns

### 6. Deliver (Standard Format)
```
🔬 DEEP RESEARCH: [Topic]

⚡ ANSWER
[Direct answer — 2-3 sentences]

📊 CONFIDENCE: [High/Medium/Low] — [why]

🔍 KEY FINDINGS
• [Finding 1] — [source]
• [Finding 2] — [source]

⚠️ CAVEATS
• [Important limitation or uncertainty]

🕳️ GAPS
• [What couldn't be determined]

📚 SOURCES ([count])
[Numbered list with credibility notes]
```

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

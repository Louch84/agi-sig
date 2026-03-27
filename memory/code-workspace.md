# Code Workspace

Persistent storage for code snippets, scripts, and execution results. Survives between sessions.

## Scripts Built

| Script | Purpose | Created |
|--------|---------|---------|
| `scripts/fetch_arxiv.py` | Fetch ArXiv RSS feeds (cs.AI, cs.LG, cs.CL, cs.CV) | 2026-03-27 |
| `scripts/ollama_mem.py` | Vector memory management (add, search, stats) | inherited |

## Code Snippets

### Fetch ArXiv RSS (working)
```python
import xml.etree.ElementTree as ET
import urllib.request

ARXIV_FEEDS = {
    "cs.AI": "https://export.arxiv.org/rss/cs.AI",
    "cs.LG": "https://export.arxiv.org/rss/cs.LG",
}
```

### Ollama Vector Search
```bash
python3 scripts/ollama_mem.py add "text" --category research --importance 0.8
python3 scripts/ollama_mem.py search "query" --top 5 --min 0.5
```

## Execution Log

_(add execution results and notes here)_

### 2026-03-27
- fetch_arxiv.py: WORKING — 923 papers across 4 feeds
- ollama_mem.py: WORKING — 7 seeds stored

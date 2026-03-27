#!/usr/bin/env python3
"""Quick-learn: Fetch a topic from ArXiv, summarize, store in vector memory."""
import sys
import xml.etree.ElementTree as ET
import urllib.request
import re

FEEDS = {
    "cs.AI": "https://export.arxiv.org/rss/cs.AI",
    "cs.LG": "https://export.arxiv.org/rss/cs.LG",
}

def fetch_paper(topic, limit=3):
    feed_url = FEEDS.get(topic, FEEDS["cs.AI"])
    req = urllib.request.Request(feed_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode("utf-8")
    root = ET.fromstring(content)
    papers = []
    for item in root.findall(".//item")[:limit]:
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        desc = re.sub(r"<[^>]+>", "", item.findtext("description", "")[:300])
        papers.append({"title": title, "link": link, "desc": desc})
    return papers

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "cs.AI"
    papers = fetch_paper(topic)
    print(f"=== Top {len(papers)} papers from {topic} ===")
    for i, p in enumerate(papers, 1):
        print(f"\n{i}. {p['title']}\n   {p['link']}\n   {p['desc'][:100]}...")

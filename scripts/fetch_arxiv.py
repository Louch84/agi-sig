#!/usr/bin/env python3
"""Fetch ArXiv RSS feeds and extract paper titles + summaries."""

import xml.etree.ElementTree as ET
import urllib.request
import sys
import re
from datetime import datetime

ARXIV_FEEDS = {
    "cs.AI": "https://export.arxiv.org/rss/cs.AI",
    "cs.LG": "https://export.arxiv.org/rss/cs.LG",
    "cs.CL": "https://export.arxiv.org/rss/cs.CL",  # Computation and Language
    "cs.CV": "https://export.arxiv.org/rss/cs.CV",  # Computer Vision
}

def fetch_feed(feed_name, url, limit=5):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode("utf-8")
        
        root = ET.fromstring(content)
        items = root.findall(".//item")
        
        print(f"\n=== ArXiv {feed_name} ({len(items)} papers) ===")
        for i, item in enumerate(items[:limit]):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            desc = item.findtext("description", "").strip()
            # Strip HTML from description
            desc = re.sub(r"<[^>]+>", "", desc)[:200]
            pub_date = item.findtext("pubDate", "").strip()
            
            print(f"\n{i+1}. {title}")
            print(f"   Date: {pub_date}")
            print(f"   Link: {link}")
            if desc:
                print(f"   Summary: {desc[:150]}...")
        
        return len(items)
    except Exception as e:
        print(f"Error fetching {feed_name}: {e}")
        return 0

def main():
    print(f"ArXiv RSS Fetcher — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    total = 0
    for name, url in ARXIV_FEEDS.items():
        count = fetch_feed(name, url)
        total += count
    print(f"\nTotal papers available: {total}")
    print("\nTip: Check cs.AI and cs.LG for most AGI-relevant papers")

if __name__ == "__main__":
    main()

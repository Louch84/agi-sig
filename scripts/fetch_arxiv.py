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
    "cs.CL": "https://export.arxiv.org/rss/cs.CL",
    "cs.CV": "https://export.arxiv.org/rss/cs.CV",
}

def fetch_feed(feed_name, url, limit=5):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode("utf-8")
        
        root = ET.fromstring(content)
        channel = root.find("channel")
        if channel is None:
            print(f"Warning: No channel found in {feed_name}")
            return 0
        
        # ArXiv RSS puts items directly in channel, not nested
        items = channel.findall("item")
        
        if not items:
            print(f"\n=== ArXiv {feed_name}: No papers (ArXiv publishes Mon-Fri only) ===")
            return 0
        
        print(f"\n=== ArXiv {feed_name} ({len(items)} papers) ===")
        for i, item in enumerate(items[:limit]):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            desc = item.findtext("description", "")
            if desc:
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
    today = datetime.now()
    print(f"ArXiv RSS Fetcher — {today.strftime('%Y-%m-%d %H:%M')}")
    
    # ArXiv doesn't publish on weekends
    if today.weekday() >= 5:  # Saturday = 5, Sunday = 6
        print("\nNote: ArXiv does not publish new papers on weekends.")
        print("No papers available until Monday.")
        return
    
    total = 0
    for name, url in ARXIV_FEEDS.items():
        count = fetch_feed(name, url)
        total += count
    print(f"\nTotal papers available: {total}")
    print("Tip: Check cs.AI and cs.LG for most AGI-relevant papers")

if __name__ == "__main__":
    main()

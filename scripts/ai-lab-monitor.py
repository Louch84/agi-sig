#!/usr/bin/env python3
"""Monitor AI labs via web_fetch — Anthropic, OpenAI, DeepMind.
Since blogwatcher can't detect these feeds, we fetch the pages directly.
Usage: python3 scripts/ai-lab-monitor.py"""
import subprocess
import json
import re
from datetime import datetime

AI_LABS = {
    "Anthropic Research": "https://www.anthropic.com/research",
    "Anthropic News": "https://www.anthropic.com/news",
    "OpenAI Blog": "https://openai.com/blog",
    "DeepMind Blog": "https://deepmind.google/blog",
}

def fetch_page(url, max_chars=3000):
    """Use web_fetch via curl since we can't call tools from here.
    Falls back to urllib if curl fails."""
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8")[:max_chars]
        return content
    except Exception as e:
        return f"Error: {e}"

def extract_links(html, base_url=""):
    """Extract links from HTML."""
    if not html or html.startswith("Error"):
        return []
    links = []
    for match in re.finditer(r'href="([^"]+)"', html):
        href = match.group(1)
        if href.startswith("/"):
            href = base_url.rstrip("/") + href
        links.append(href)
    return links

def main():
    print(f"AI Lab Monitor — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    for name, url in AI_LABS.items():
        print(f"=== {name} ===")
        content = fetch_page(url)
        
        if content.startswith("Error"):
            print(f"  Failed: {content}")
            continue
        
        # Extract page title
        title_match = re.search(r'<title>([^<]+)</title>', content)
        title = title_match.group(1) if title_match else "No title"
        print(f"  Title: {title[:80]}")
        
        # Extract links and dates (simplified)
        links = extract_links(content, url)
        post_links = [l for l in links if any(x in l.lower() for x in ['research', 'blog', 'news', '2026', '2025'])]
        if post_links:
            print(f"  Links found: {len(post_links)}")
            for link in post_links[:5]:
                print(f"    - {link[:80]}")
        print()
    
    print("Note: For full article content, use web_fetch tool on specific URLs")
    print("Example: web_fetch 'https://www.anthropic.com/research/your-article' --maxChars 5000")

if __name__ == "__main__":
    main()

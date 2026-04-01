#!/usr/bin/env python3
"""
Crypto Scanner — Find newly launched tokens via web search.

Uses DuckDuckGo Lite (no API key required).

Usage:
  python3 scripts/scan.py [--chain solana|ethereum|all] [--limit 10]
"""
import sys
import json
import re
from datetime import datetime

SEARCH_QUERIES = {
    "solana": "site:dexscreener.com OR site:pump.fun newly launched token Solana 2026",
    "ethereum": "site:dexscreener.com newly launched token Ethereum 2026",
    "base": "site:dexscreener.com newly launched token Base 2026",
    "bsc": "site:dexscreener.com newly launched token BSC Binance 2026",
    "all": "newly launched cryptocurrency token 2026 dexscreener pump.fun",
}


def search_web(query: str, num_results: int = 10) -> list:
    """Search the web using DuckDuckGo Lite."""
    import urllib.parse
    import urllib.request

    encoded_query = urllib.parse.quote(query)
    url = f"https://lite.duckduckgo.com/lite/?q={encoded_query}&s=0"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            return parse_ddg_results(html)
    except Exception as e:
        return [{"error": str(e)}]


def parse_ddg_results(html: str) -> list:
    """Parse DuckDuckGo Lite results."""
    results = []

    # Find result snippets
    snippet_pattern = re.compile(r'<a class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>', re.DOTALL)
    snippet_pattern2 = re.compile(r'<a class="result-link"[^>]*href="([^"]*)"[^>]*>(.*?)</a>', re.DOTALL)

    # Find snippets
    for pattern in [snippet_pattern, snippet_pattern2]:
        for match in pattern.finditer(html):
            url = match.group(1)
            title = re.sub(r'<[^>]+>', '', match.group(2)).strip()

            # Extract domain
            domain = ""
            if "pump.fun" in url:
                domain = "Pump.fun"
            elif "dexscreener" in url:
                domain = "DexScreener"
            elif "dextools" in url:
                domain = "DEXTools"
            else:
                domain = "Other"

            if title and len(title) > 5:
                results.append({
                    "title": title[:100],
                    "url": url[:200],
                    "source": domain,
                })

    # Dedupe by title
    seen = set()
    deduped = []
    for r in results:
        if r["title"] not in seen:
            seen.add(r["title"])
            deduped.append(r)

    return deduped


def extract_token_info(result: dict) -> dict:
    """Extract token symbol and info from result."""
    title = result["title"]

    # Try to extract symbol (dollar sign followed by letters)
    sym = re.search(r'\$([A-Z0-9]{2,10})', title, re.IGNORECASE)
    symbol = sym.group(1).upper() if sym else "Unknown"

    # Try to extract market cap
    mc = re.search(r'\$([0-9]+\.?[0-9]*[KMB]?)', title)
    market_cap = mc.group(1) if mc else "N/A"

    return {
        "symbol": symbol,
        "title": title,
        "url": result["url"],
        "source": result["source"],
        "market_cap": market_cap,
        "found_at": datetime.now().isoformat(),
    }


def main():
    chain = "all"
    limit = 10

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--chain" and i + 1 < len(args):
            chain = args[i + 1].lower()
            i += 2
        elif args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        else:
            i += 1

    if chain not in SEARCH_QUERIES:
        print(f"Unknown chain: {chain}")
        print(f"Available: {list(SEARCH_QUERIES.keys())}")
        sys.exit(1)

    query = SEARCH_QUERIES[chain]
    print(f"Scanning for newly launched tokens ({chain})...")
    print()

    results = search_web(query, limit)

    if not results or (len(results) == 1 and "error" in results[0]):
        print("No results found or error occurred.")
        if results:
            print(f"Error: {results[0].get('error')}")
        sys.exit(1)

    tokens = [extract_token_info(r) for r in results[:limit]]

    print("=" * 60)
    print(f"NEW TOKEN SCANNER -- {chain.upper()} -- {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()

    for i, token in enumerate(tokens, 1):
        print(f"{i}. ${token['symbol']}")
        print(f"   {token['title'][:80]}")
        print(f"   Cap: {token['market_cap']} | Source: {token['source']}")
        print(f"   {token['url'][:80]}")
        print()

    print("=" * 60)
    print(f"Found {len(tokens)} potential new tokens")
    print("DYOR -- Most new tokens are rugs or dumps. Trade carefully.")
    print("=" * 60)

    return tokens


if __name__ == "__main__":
    main()

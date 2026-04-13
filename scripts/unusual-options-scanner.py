#!/usr/bin/env python3
"""
Unusual Options Activity Scanner
Finds options with high volume-to-open-interest ratios — signals whale activity.
Uses yfinance to compute V/OI ratios directly from the options chain.
"""
import yfinance as yf
import numpy as np
import sys
import os

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "unusual-options-scanner.json")


def scan_unusual_options(ticker, min_vol_oi_ratio=2.0, min_volume=50):
    """Scan options chain for unusual activity — high volume vs open interest."""
    try:
        t = yf.Ticker(ticker)
        stock_price = t.history(period="1d")["Close"].values[-1]

        # Get nearest expirations
        expirations = list(t.options)[:3]  # next 3 expirations
        if not expirations:
            return []

        results = []

        for exp in expirations:
            try:
                opt = t.option_chain(exp)
                for side in [opt.calls, opt.puts]:
                    for _, row in side.iterrows():
                        vol = row.get("volume", 0) or 0
                        oi = row.get("openInterest", 0) or 0
                        last = row.get("lastPrice", 0) or 0
                        strike = row.get("strike", 0)
                        itm = abs(stock_price - strike) / stock_price if stock_price > 0 else 0

                        # Skip if no volume or OI
                        if vol < min_volume and oi < 10:
                            continue

                        # Calculate volume/OI ratio
                        voi_ratio = vol / oi if oi > 0 else vol / 100

                        # Flag if unusual: high ratio OR large absolute volume
                        if voi_ratio >= min_vol_oi_ratio or vol >= 500:
                            option_type = "CALL" if side is opt.calls else "PUT"

                            # Bullish signal: call at ask price, high voi ratio
                            if side is opt.calls:
                                sentiment = "BULLISH" if row.get("ask", 0) and last >= row.get("ask", 0) * 0.95 else "NEUTRAL"
                            else:
                                sentiment = "BEARISH" if row.get("bid", 0) and last <= row.get("bid", 0) * 1.05 else "NEUTRAL"

                            results.append({
                                "ticker": ticker,
                                "stock_price": round(stock_price, 2),
                                "expiration": exp,
                                "type": option_type,
                                "strike": strike,
                                "last": last,
                                "bid": row.get("bid", 0) or 0,
                                "ask": row.get("ask", 0) or 0,
                                "volume": int(vol),
                                "open_interest": int(oi),
                                "voi_ratio": round(voi_ratio, 1),
                                "itm_pct": round(itm * 100, 1),
                                "sentiment": sentiment,
                            })
            except Exception as e:
                continue

        # Sort by V/OI ratio descending
        results.sort(key=lambda x: x["voi_ratio"], reverse=True)
        return results[:20]

    except Exception as e:
        return []


def scan_universe(tickers):
    """Scan all tickers for unusual options."""
    all_results = []
    seen = set()

    print(f"Scanning {len(tickers)} tickers for unusual options activity...")
    print("=" * 60)

    for i, ticker in enumerate(tickers):
        print(f"[{i+1}/{len(tickers)}] {ticker}...", end=" ", flush=True)
        results = scan_unusual_options(ticker)
        for r in results:
            key = f"{r['ticker']}-{r['expiration']}-{r['strike']}-{r['type']}"
            if key not in seen:
                seen.add(key)
                all_results.append(r)
        print(f"found {len(results)} unusual")

    # Sort by V/OI ratio
    all_results.sort(key=lambda x: x["voi_ratio"], reverse=True)
    return all_results[:30]


def main():
    tickers = sys.argv[1:] if len(sys.argv) > 1 else None

    if tickers:
        print(f"Scanning {len(tickers)} specific tickers...")
        results = scan_universe(tickers)
    else:
        # Default universe — high-short-interest + whale candidates
        default = [
            "SOUN", "GRPN", "HTZ", "HIMS", "INDI", "NVAX", "AI",
            "PLTR", "SMCI", "RIVN", "LCID", "SOFI", "MARA",
            "COIN", "ASTS", "LUNR", "GME", "AMC", "BB", "NOK",
            "SRPT", "ABEO", "PCT", "CYPH", "RXRX", "IOVA",
        ]
        results = scan_universe(default)

    print("\n" + "=" * 60)
    print("🐋 UNUSUAL OPTIONS ACTIVITY")
    print("=" * 60)

    for i, r in enumerate(results[:25]):
        sent_emoji = "📈" if r["sentiment"] == "BULLISH" else ("📉" if r["sentiment"] == "BEARISH" else "➡️")
        print(f"\n{i+1}. {r['ticker']} {r['type']} ${r['strike']} {sent_emoji} {r['sentiment']}")
        print(f"   Stock: ${r['stock_price']} | Exp: {r['expiration']}")
        print(f"   Price: ${r['last']:.2f} | Bid: ${r['bid']:.2f} | Ask: ${r['ask']:.2f}")
        print(f"   Volume: {r['volume']:,} | Open Int: {r['open_interest']:,} | V/OI: {r['voi_ratio']:.1f}x 🔥")

    import json
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump({"results": results}, f, indent=2, default=str)

    print(f"\n✅ Saved to {RESULTS_FILE}")


if __name__ == "__main__":
    main()

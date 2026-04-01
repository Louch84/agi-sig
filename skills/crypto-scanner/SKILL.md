---
name: crypto-scanner
description: Scan for newly launched cryptocurrency tokens. Uses web search to find new token launches across chains. To use: tell me to "scan for new crypto tokens" and I'll run web searches on DexScreener, Pump.fun, and news sources.
---

# Crypto Scanner

Scans for newly launched cryptocurrency tokens using web search.

## How to Use

**Just ask me:** "scan for new crypto tokens" and I'll run searches.

## What I Search

| Chain | Sources |
|-------|---------|
| Solana | DexScreener, Pump.fun, Solscan |
| Ethereum | DexScreener, DEXTools |
| Base | DexScreener |
| BSC | DexScreener |

## What I Return

- Token name and symbol
- Chain
- Price / Market cap if available
- Source link
- Risk flags

## Limitations

- **No real-time data** — web search is delayed by minutes to hours
- **No liquidity data** — can't check if liquidity is locked
- **No exchange API** — can't verify price or volume

## For Real Trading

Would need:
- Exchange API (Coinbase, Kraken, Binance)
- Real-time DEX APIs (DexScreener Pro, DEXTools API)
- Wallet integration

## Risk Warning

95% of new tokens are rugs. Always DYOR.

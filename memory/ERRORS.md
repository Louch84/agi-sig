
## 2026-03-27 Evening — Clone/Fork Session Loss

**What happened:**
Lou cloned the agi-sig repo and forked OpenClaw to create a second agent instance. After restarting the gateway, the clone couldn't reconnect and was lost. Had to start fresh.

**Root cause:**
- Session state lives in memory
- Gateway restart reloads `~/.openclaw/openclaw.json` fresh
- Clone's config was in memory only, not persisted to disk config
- Restart defaulted back to original config, orphaning the clone

**Lesson:**
- Don't restart gateway while a clone/fork is active
- Clone's openclaw.json must be persisted to disk
- Session state is ephemeral — always save to SESSION-STATE.md before sessions end
- Multiple agents need separate agent IDs and distinct workspaces

**Prevention:**
- Backup SESSION-STATE.md before any gateway restart
- Document clone config changes in memory/
- Use persistent disk config for any long-running clone sessions

## 2026-04-04 — yfinance Rate Limiting Broke Scanner (2hr Debug)

**What happened:**
Scanner returned 0 signals even though individual ticker lookups worked fine. Spent 2 hours debugging.

**Root cause:**
yfinance silently rate-limits rapid-fire API calls. When rate-limited, returns None for ALL tickers in the loop silently. Individual calls work because they have time gaps.

**Lesson:**
- yfinance: ~1 call/sec safe, 0.5s risky
- When rate-limited: returns None silently, no error
- Fix: always time.sleep(0.8) between yfinance calls in loops
- Or cache universe to news_universe.json

**Prevention:**
- Always delay between yfinance calls
- Save intermediate results to file (checkpointing)
- Use news_universe.json as cached universe

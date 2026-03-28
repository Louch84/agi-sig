
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

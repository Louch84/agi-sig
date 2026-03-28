# OpenClaw Clone Setup — How to Run Multiple Instances

## The Problem (Why the Clone Broke)

When you ran the OpenClaw clone, it was likely using the **same `~/.openclaw/` directory** as the original. This means:

- Both instances shared the same `openclaw.json` config
- Both instances shared the same LaunchAgent (`ai.openclaw.gateway`)
- After restart, the gateway loaded the config from `~/.openclaw/` — which was the **original** config
- The clone's modified config was overwritten or ignored

When you ran `openclaw doctor`, it reset `~/.openclaw/openclaw.json` back to working defaults for the original instance.

## The Solution: Separate State Directories

OpenClaw supports two mechanisms for running multiple instances:

### Option 1: `OPENCLAW_PROFILE` (Recommended)

```bash
OPENCLAW_PROFILE=clone openclaw gateway start
```

This automatically uses:
- Config: `~/.openclaw-clone/openclaw.json`
- Workspace: `~/.openclaw-clone/workspace/`
- LaunchAgent label: `ai.openclaw.clone`

### Option 2: `OPENCLAW_STATE_DIR` (Fully Custom)

```bash
OPENCLAW_STATE_DIR=~/.openclaw-myclone openclaw gateway start
```

This puts everything in a completely custom directory.

## Proper Clone Setup Steps

### 1. Create a new workspace directory (git clone your agi-sig fork)

```bash
git clone https://github.com/YOUR-FORK/agi-sig.git ~/openclaw-clone-workspace
```

### 2. Start the clone with a separate profile

```bash
# Option A: Using profile (auto-separates state dir + workspace)
OPENCLAW_PROFILE=clone \
OPENCLAW_WORKSPACE_DIR=~/openclaw-clone-workspace \
openclaw gateway start --port 18790
```

### 3. The clone's workspace must be set in its openclaw.json

In the clone's state dir (`~/.openclaw-clone/`), edit `openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "workspace": "/path/to/clone/workspace"
    }
  }
}
```

### 4. Install a separate LaunchAgent (optional but recommended)

Create `~/Library/LaunchAgents/ai.openclaw.clone.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.openclaw.clone</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>export OPENCLAW_PROFILE=clone; export OPENCLAW_WORKSPACE_DIR=/path/to/clone/workspace; openclaw gateway start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/ai.openclaw.clone.plist
```

## Key Rules

1. **Never share `~/.openclaw/` between instances** — use `OPENCLAW_PROFILE` or `OPENCLAW_STATE_DIR`
2. **Use different ports** — default is 18789, clone should use 18790
3. **Never restart the original LaunchAgent while the clone is active** — the original gateway will overwrite the clone's config on restart
4. **Separate git remotes** — the clone workspace should have its own git remote pointing to its own fork

## What `openclaw doctor` Does

`openclaw doctor` scans and repairs the `~/.openclaw/` config. If the clone modified `~/.openclaw/openclaw.json`, running doctor would reset it to the original instance's config — which is what happened.

## Quick Reference

| Instance | Profile | State Dir | Port | Workspace |
|----------|---------|-----------|------|-----------|
| Original | default | `~/.openclaw/` | 18789 | `/Users/sigbotti/.openclaw/workspace` |
| Clone | `clone` | `~/.openclaw-clone/` | 18790 | `/path/to/clone/workspace` |

## Startup Script Template

For the clone, create a startup script:

```bash
#!/bin/bash
# clone-start.sh
export OPENCLAW_PROFILE=clone
export OPENCLAW_WORKSPACE_DIR=~/openclaw-clone-workspace
export OPENCLAW_GATEWAY_PORT=18790
openclaw gateway start
```

Run with: `bash clone-start.sh`

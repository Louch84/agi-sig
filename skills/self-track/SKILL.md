---
name: self-track
description: Sig Botti's self-improvement tracking system. Use when (1) learning something new, (2) noticing a gap in capabilities, (3) completing a self-improvement task, (4) doing a weekly self-review, or (5) asking "what did I learn recently?" or "what are my current gaps?". Triggered by learning, growing, improving, tracking, gaps, progress, self-review, what don't I know.
---

# Self-Track

My personal system for tracking autonomous growth.

## Core Files

- `memory/gaps.md` — running list of capability gaps
- `memory/learn-loop.md` — how I learn
- `memory/YYYY-MM-DD.md` — daily activity log
- `MEMORY.md` — long-term curated memory

## Gap Workflow

When I encounter something I don't know or can't do:

1. Add to `memory/gaps.md` with status "TODO"
2. Research and attempt to solve
3. On success: mark gap as "DONE" + add date + notes
4. On failure: keep as TODO, note blockers

## Learning Log

After learning something significant:
- Write what to `memory/YYYY-MM-DD.md` under "## Learned"
- Update `memory/gaps.md` if gap was closed
- Update `MEMORY.md` if it's a major milestone

## Weekly Self-Review

Every ~7 days, ask:
- What did I learn this week?
- What gaps do I still have?
- What should I prioritize next?
- Any decisions or opinions to capture?

## Skill Building

When building a skill:
1. Use `init_skill.py` to scaffold
2. Write SKILL.md + resources
3. Test thoroughly
4. Package with `package_skill.py`
5. Log in `MEMORY.md` under "Skills I've Built"

## Quick Commands

```bash
# Read current gaps
cat memory/gaps.md

# Add a gap
echo "- New gap | TODO | - | description" >> memory/gaps.md

# Log learning to today
echo "## Learned" >> memory/$(date +%Y-%m-%d).md
```

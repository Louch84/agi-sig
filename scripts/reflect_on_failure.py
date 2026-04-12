#!/usr/bin/env python3
"""
reflect_on_failure.py — Analyzes skill execution traces and proposes skill mutations.

Usage:
    python3 reflect_on_failure.py <trace-file.json>
    python3 reflect_on_failure.py --latest  (uses most recent trace)

This reads a skill execution trace, uses the local Ollama model to analyze why
the skill failed, and outputs a mutation draft (not directly applied — review before merge).

Based on the GEPA loop from Hermes Agent Self-Evolution (NousResearch):
    Generate → Evaluate → Preserve → Amplify
"""

import json
import sys
import os
import re
from datetime import datetime
from pathlib import Path

OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3:latest"  # General reasoning model

TRACES_DIR = Path.home() / ".openclaw/workspace/memory/skill-traces"
SKILLS_DIR = Path.home() / ".openclaw/skills"


def load_trace(trace_path: str) -> dict:
    with open(trace_path) as f:
        return json.load(f)


def get_latest_trace() -> Path | None:
    traces = sorted(TRACES_DIR.glob("trace-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return traces[0] if traces else None


def build_analysis_prompt(trace: dict) -> str:
    """Build the prompt for the Ollama model to analyze the failure."""
    skill_name = trace.get("skill", "unknown")
    task = trace.get("task", "unknown")
    outcome = trace.get("outcome", "unknown")
    error = trace.get("error", "")
    model_used = trace.get("model", "unknown")
    duration = trace.get("duration_s", 0)

    prompt = f"""You are analyzing why an AI agent skill failed during execution.

## Skill: {skill_name}
## Task: {task}
## Outcome: {outcome}
## Model Used: {model_used}
## Duration: {duration:.1f}s

## Error (if any):
{error if error else "(no error recorded)"}

## What happened (your analysis):
The skill "{skill_name}" was used to accomplish: "{task}"
The result was: "{outcome}"

## Your job:
1. Identify WHY the skill failed (root cause — not just the symptom)
2. Identify what specific part of the skill's instructions/behavior caused the failure
3. Propose a concrete mutation to the skill's SKILL.md that would prevent this failure

## Output format (JSON):
{{
  "root_cause": "one sentence describing why the skill failed",
  "failing_component": "which part of the skill is broken (e.g., 'trigger phrase too broad', 'missing error handling', 'wrong tool selection logic')",
  "proposed_mutation": "exact text to ADD or CHANGE in the SKILL.md — include the section/paragraph this affects",
  "mutation_type": "append|edit|replace|new_section",
  "confidence": 0.0-1.0  // how confident you are in this diagnosis
}}

Be specific. "The skill needs better error handling" is not useful. "Add a try-except block around the API call and log the full error response before re-raising" is useful.
"""
    return prompt


def call_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Call Ollama API for completion."""
    import urllib.request
    import urllib.error

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,  # Lower temp for analytical task
            "num_predict": 512
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", "").strip()
    except urllib.error.URLError as e:
        return f"OLLAMA_ERROR: {e}"


def parse_mutation_response(response: str) -> dict:
    """Parse the JSON mutation proposal from the model response."""
    # Try to extract JSON from the response
    json_match = re.search(r'\{[^{}]*"root_cause"[^{}]*\}', response, re.DOTALL)
    if not json_match:
        # Try broader JSON extraction
        json_match = re.search(r'\{.*\}', response, re.DOTALL)

    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Fallback: return raw response with error flag
    return {
        "root_cause": "PARSE_ERROR",
        "failing_component": response[:500],
        "proposed_mutation": "",
        "mutation_type": "unknown",
        "confidence": 0.0
    }


def write_draft(skill_name: str, mutation: dict, trace: dict, analysis: str) -> Path:
    """Write a mutation draft file for review."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    draft_path = TRACES_DIR / f"draft-{skill_name}-{timestamp}.md"

    draft_content = f"""# Skill Mutation Draft — {skill_name}

**Created:** {datetime.now().isoformat()}
**Trace:** {trace.get('trace_id', 'unknown')}
**Confidence:** {mutation.get('confidence', 0.0)}

---

## Root Cause
{mutation.get('root_cause', 'unknown')}

## Failing Component
{mutation.get('failing_component', 'unknown')}

## Proposed Mutation
{mutation.get('proposed_mutation', 'unknown')}

## Mutation Type
{mutation.get('mutation_type', 'unknown')}

---

## Full Model Analysis
{analysis}

---

## Original Skill Content (for reference)
```
{get_skill_content(skill_name)}
```

---

## Instructions
- Review the proposed mutation above
- If approved, apply to: `~/.openclaw/skills/{skill_name}/SKILL.md`
- Run `python3 scripts/evaluate_variant.py` to validate before merging
- Delete this draft after applying or discarding
"""

    with open(draft_path, "w") as f:
        f.write(draft_content)

    return draft_path


def get_skill_content(skill_name: str) -> str:
    """Read the current skill content."""
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if skill_path.exists():
        return skill_path.read_text()
    return "(skill file not found)"


def main():
    if len(sys.argv) < 2:
        print("Usage: reflect_on_failure.py <trace-file.json> | --latest")
        sys.exit(1)

    # Load trace
    if sys.argv[1] == "--latest":
        trace_path = get_latest_trace()
        if not trace_path:
            print("No traces found in memory/skill-traces/")
            sys.exit(1)
    else:
        trace_path = Path(sys.argv[1])

    if not trace_path.exists():
        print(f"Trace not found: {trace_path}")
        sys.exit(1)

    trace = load_trace(trace_path)
    print(f"📋 Analyzing: {trace.get('skill', 'unknown')} | {trace.get('outcome', 'unknown')}")

    # Only analyze failures
    if trace.get("outcome") != "failure":
        print(f"⚠️  Outcome is '{trace.get('outcome')}' — not a failure. Skipping.")
        print("   Use this script only for failed skill executions.")
        sys.exit(0)

    # Build prompt and call Ollama
    prompt = build_analysis_prompt(trace)
    print(f"🤖 Calling {DEFAULT_MODEL}...")
    response = call_ollama(prompt)

    if response.startswith("OLLAMA_ERROR:"):
        print(f"❌ Ollama error: {response}")
        sys.exit(1)

    # Parse and output
    mutation = parse_mutation_response(response)
    print(f"\n📊 Analysis:")
    print(f"   Root cause: {mutation.get('root_cause', 'unknown')}")
    print(f"   Confidence: {mutation.get('confidence', 0.0):.0%}")

    if mutation.get("proposed_mutation"):
        print(f"\n💡 Proposed mutation ({mutation.get('mutation_type', 'unknown')}):")
        print(f"   {mutation.get('proposed_mutation')[:300]}...")

        # Write draft
        draft_path = write_draft(trace.get("skill", "unknown"), mutation, trace, response)
        print(f"\n📝 Draft written to: {draft_path}")
        print("   Review this draft before applying any changes to the skill.")
    else:
        print("\n⚠️  Could not parse mutation proposal. Raw response:")
        print(response[:1000])


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
evaluate_variant.py — Validate skill mutations before applying

Checks:
1. SKILL.md syntax (valid YAML frontmatter + valid markdown)
2. File size (≤15KB per Hermes Agent standard)
3. No catastrophic content removal
4. Triggers are non-empty list
5. Description is non-empty string

Usage:
  python3 scripts/evaluate_variant.py <draft-file.md>
  python3 scripts/evaluate_variant.py memory/skill-traces/draft-coding-20260417-092049.md
"""

import sys
import re
import yaml
from pathlib import Path

MAX_SIZE_KB = 15
FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)
SKILL_NAME_RE = re.compile(r'^# SKILL\.md - (.+)$', re.MULTILINE)


def load_draft(path: str) -> dict:
    with open(path) as f:
        content = f.read()
    return content


def parse_frontmatter(content: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(content)
    if not match:
        raise ValueError("No YAML frontmatter found (missing --- delimiters)")
    fm = yaml.safe_load(match.group(1))
    body = content[match.end():]
    return fm, body


def check_size(content: str, path: str) -> tuple[bool, str]:
    size_kb = len(content.encode()) / 1024
    if size_kb > MAX_SIZE_KB:
        return False, f"FAIL: {size_kb:.1f}KB > {MAX_SIZE_KB}KB limit"
    return True, f"OK: {size_kb:.1f}KB"


def check_description(fm: dict) -> tuple[bool, str]:
    if 'description' not in fm:
        return False, "FAIL: missing 'description' in frontmatter"
    if not isinstance(fm['description'], str) or not fm['description'].strip():
        return False, "FAIL: 'description' must be non-empty string"
    return True, f"OK: description = '{fm['description'][:60]}...'"


def check_triggers(fm: dict) -> tuple[bool, str]:
    if 'triggers' not in fm:
        return False, "FAIL: missing 'triggers' in frontmatter"
    if not isinstance(fm['triggers'], list) or len(fm['triggers']) == 0:
        return False, "FAIL: 'triggers' must be non-empty list"
    return True, f"OK: {len(fm['triggers'])} triggers"


def check_skill_name(body: str) -> tuple[bool, str]:
    m = SKILL_NAME_RE.search(body)
    if not m:
        return False, "FAIL: missing '# SKILL.md - <name>' header"
    return True, f"OK: skill name = '{m.group(1)}'"


def check_no_catastrophic_removal(body: str, orig_path: str = None) -> tuple[bool, str]:
    """Check that body isn't catastrophically stripped"""
    if len(body.strip()) < 100:
        return False, f"FAIL: body too short ({len(body.strip())} chars) — possible catastrophic removal"
    if body.count('\n') < 3:
        return False, f"FAIL: body has too few lines ({body.count(chr(10))}) — possible catastrophic removal"
    return True, f"OK: {len(body.strip())} chars, {body.count(chr(10))} lines"


def check_yaml_safe(fm: dict) -> tuple[bool, str]:
    """Ensure frontmatter doesn't have obvious injection vectors"""
    try:
        dumped = yaml.safe_dump(fm)
        # Check no raw Python code injection
        for val in str(fm).split('\n'):
            if any(unsafe in val for unsafe in ['__import__', '${', '{{']):
                return False, f"FAIL: suspicious content in frontmatter: {val[:50]}"
        return True, "OK: YAML safe"
    except Exception as e:
        return False, f"FAIL: YAML dump error: {e}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/evaluate_variant.py <draft-file.md>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"FAIL: file not found: {path}")
        sys.exit(1)

    print(f"Evaluating: {path}")
    print("-" * 40)

    try:
        content = load_draft(path)
    except Exception as e:
        print(f"FAIL: read error: {e}")
        sys.exit(1)

    all_pass = True

    # Check 1: File size
    ok, msg = check_size(content, str(path))
    print(f"[1/7] Size: {msg}")
    if not ok:
        all_pass = False

    # Check 2: YAML frontmatter parses
    try:
        fm, body = parse_frontmatter(content)
        print("[2/7] Frontmatter: OK: parses as valid YAML")
    except Exception as e:
        print(f"[2/7] Frontmatter: FAIL: {e}")
        all_pass = False
        fm, body = {}, content

    if fm:
        # Check 3: Description valid
        ok, msg = check_description(fm)
        print(f"[3/7] Description: {msg}")
        if not ok:
            all_pass = False

        # Check 4: Triggers valid
        ok, msg = check_triggers(fm)
        print(f"[4/7] Triggers: {msg}")
        if not ok:
            all_pass = False

        # Check 5: YAML safe
        ok, msg = check_yaml_safe(fm)
        print(f"[5/7] YAML safe: {msg}")
        if not ok:
            all_pass = False

    # Check 6: Skill name header
    ok, msg = check_skill_name(body)
    print(f"[6/7] Skill name header: {msg}")
    if not ok:
        all_pass = False

    # Check 7: No catastrophic content removal
    ok, msg = check_no_catastrophic_removal(body)
    print(f"[7/7] Content integrity: {msg}")
    if not ok:
        all_pass = False

    print("-" * 40)
    if all_pass:
        print("✅ VALIDATED — safe to apply")
        sys.exit(0)
    else:
        print("❌ REJECTED — fix issues before applying")
        sys.exit(1)


if __name__ == '__main__':
    main()
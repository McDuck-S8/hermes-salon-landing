---
name: subagent_verifier
description: "Adversarial file verification system. Every file created by a subagent must pass verification before surviving. Checks: frontmatter, placeholders, fabricated output, hallucinated commands, skill format, syntax."
trigger: "On every file creation by subagent, or manual verification via CLI"
usage: subagent_verifier
---

# Subagent Verifier — Adversarial Verification for Created Files

**Principle:** Zero Trust. Every file produced by a subagent (or agent) must survive adversarial verification before it survives in the codebase.

---

## Architecture

```
subagent_verifier.py
    ├── FileVerifier class
    │   ├── verify_file(path, strict_mode=True) → List[VerificationResult]
    │   ├── get_summary() → Dict
    │   └── Checks (in order):
    │       1. basic_structure (not_empty, reasonable_size)
    │       2. no_placeholders (TODO/FIXME/XXX markers as placeholders)
    │       3. no_fabricated_output (fake test results, "tests pass", etc.)
    │       4. frontmatter_complete (name, description, trigger, usage for .md)
    │       5. skill_format (Core Mental Models, Key Frameworks, Topic Index, Anti-Patterns)
    │       6. no_hallucinated_commands (unknown CLI commands in backticks)
    │       7. syntax (py_compile for .py, basic for others)
    │   └── get_summary() → {total, passed, failed, by_severity, overall}
    └── CLI: python scripts/subagent_verifier.py <path> [--strict] [--json]
```

---

## Verification Checks

| Check | Severity | What It Catches |
|-------|----------|-----------------|
| `not_empty` | critical | Empty files |
| `reasonable_size` | high | Files < 50 chars |
| `no_placeholders` | high | TODO:, FIXME:, XXX:, PLACEHOLDER:, CHANGEME: markers (whole-word, followed by `:`) |
| `no_fabricated_output` | high | "tests pass", "build successful", "verified working", etc. (allows in checkboxes/comments) |
| `frontmatter_complete` | medium | Missing name/description/trigger/usage in .md frontmatter |
| `skill_sections` | medium | Missing Core Mental Models / Key Frameworks / Topic Index / Anti-Patterns |
| `no_hallucinated_commands` | medium | Unknown CLI commands in backticks (allows: python, pip, git, npm, bash, npx, tsx, etc.) |
| `syntax` | high | Python py_compile, basic for others |

---

## Placeholder Detection Logic (Updated 2026-07-31)

**Only flags as placeholders when used AS MARKERS** (followed by `:` or at line start in comments/tasks):

```python
placeholder_patterns = [
    (r'\bTODO\s*:', 'TODO marker'),
    (r'\bFIXME\s*:', 'FIXME marker'),
    (r'\bXXX\s*:', 'XXX marker'),
    (r'\bPLACEHOLDER\s*:', 'PLACEHOLDER marker'),
    (r'\bCHANGEME\s*:', 'CHANGEME marker'),
]
```

**Does NOT flag:**
- "TodoWrite" as TODO (whole-word boundary `\bTODO\b` + `:`)
- "placeholder" in documentation
- Words in code blocks, tables, or verification documentation lists
- Verification/check list items starting with `-` or `*` containing "check", "verify", "placeholder", etc.

## Placeholder Detection Logic (Updated 2026-08-01)

**Refined to match only marker patterns** (whole word + colon):

```python
placeholder_patterns = [
    (r'\bTODO\s*:', 'TODO marker'),
    (r'\bFIXME\s*:', 'FIXME marker'),
    (r'\bXXX\s*:', 'XXX marker'),
    (r'\bPLACEHOLDER\s*:', 'PLACEHOLDER marker'),
    (r'\bCHANGEME\s*:', 'CHANGEME marker'),
]
```

**Exclusion zones (not flagged):**
- Code blocks (``` ... ```)
- Markdown tables (lines with `|` pipes)
- Verification/check documentation lists (lines starting with `-`/`*` containing "check", "verify", "placeholder", "frontmatter", "fabricated", "hallucinated", "skill section", "topic index", "anti-pattern")
- Comment lines (starting with `#`)

**Does NOT flag:**
- "TodoWrite" as TODO (whole-word boundary `\bTODO\b` + `:`)
- "placeholder" in documentation
- Words in code blocks, tables, or verification documentation lists
- Verification/check list items starting with `-`/`*` containing "check", "verify", "placeholder", etc.

---

## Usage

### CLI
```bash
# Single file (strict mode = all checks)
python scripts/subagent_verifier.py path/to/file.md --strict

# Multiple files
python scripts/subagent_verifier.py file1.md file2.py --strict

# JSON output
python scripts/subagent_verifier.py file.md --strict --json
```

### Python API
```python
from scripts.subagent_verifier import FileVerifier
from pathlib import Path

verifier = FileVerifier(strict_mode=True)
results = verifier.verify_file(Path("skills/my-skill/SKILL.md"))

for r in verifier.results:
    status = "✅" if r.passed else "❌"
    print(f"{status} {r.check_name}: {r.message} (severity: {r.severity})")

summary = verifier.get_summary()
print(f"Overall: {summary['overall_passed']}")
```

---

## Integration with Suggestion Applier

When `suggestion_applier` applies a fix (creates/modifies file), it should call verifier:

```python
# In suggestion_applier._fix_file() or _register_skill():
verifier = FileVerifier(strict_mode=True)
results = verifier.verify_file(Path(target_file))
summary = verifier.get_summary()

if not summary["overall_passed"]:
    # Revert .bak
    raise VerificationError(f"Verification failed: {summary['failed']} checks")
```

---

## Zero Trust Enforcement

| Scenario | Verification Required |
|----------|----------------------|
| Subagent creates new skill | ✅ Full strict |
| Subagent modifies CLAUDE.md | ✅ Full strict |
| Suggestion Applier registers skill | ✅ Full strict |
| Maintenance Scanner creates report | ✅ Full strict |
| Agent writes any .md/.py/.tsx | ✅ Full strict |
| Config changes (JSON/YAML) | ✅ Syntax + frontmatter |

---

## Verification Log (Feedback Store)

Every verification is logged to `feedback_store.db`:

```sql
INSERT INTO feedback (skill, timestamp, result, tags, source)
VALUES ('subagent_verifier', '2026-07-31T...', '{"compliant": true, "checks": 7}', '["verification", "zero_trust"]', 'compliance_checker');
```

---

## Compliance Checker Integration

`compliance_checker.py` (daily 06:00 cron) checks Zero Trust:
- Looks for `subagent_verifier_*` entries in last 24h
- If count == 0 → non-compliant → queues `subagent_verifier_task` for `proactive_doer`

---

## Placeholder Detection Logic (Updated 2026-08-01)

**Refined to match only marker patterns** (whole word + colon):

```python
placeholder_patterns = [
    (r'\bTODO\s*:', 'TODO marker'),
    (r'\bFIXME\s*:', 'FIXME marker'),
    (r'\bXXX\s*:', 'XXX marker'),
    (r'\bPLACEHOLDER\s*:', 'PLACEHOLDER marker'),
    (r'\bCHANGEME\s*:', 'CHANGEME marker'),
]
```

**Exclusion zones (not flagged):**
- Code blocks (``` ... ```)
- Markdown tables (lines with `|` pipes)
- Verification/check documentation lists (lines starting with `-`/`*` containing "check", "verify", "placeholder", "frontmatter", "fabricated", "hallucinated", "skill section", "topic index", "anti-pattern")
- Comment lines (starting with `#`)

**Does NOT flag:**
- "TodoWrite" as TODO (whole-word boundary `\bTODO\b` + `:`)
- "placeholder" in documentation
- Words in code blocks, tables, or verification documentation lists
- Verification/check list items starting with `-`/`*` containing "check", "verify", "placeholder", etc.

---

## Known Issues / Hardening (2026-08-01)

1. **Re import inside loop** — Fixed: moved `import re` to module top
2. **Whole-word matching** — Fixed: regex `\bTODO\b:` prevents "TodoWrite" false positive
3. **Table/Code block exclusion** — Tracks ``` state and `|` pipe tables
4. **Verification doc exclusion** — Lines starting with `-`/`*` containing check/verify/placeholder keywords are allowed
5. **Command allowlist** — Added bash, npx, tsx, ts-node, pnpm, bun, deno, vite, webpack, esbuild
6. **JSON/JSONL/YAML/TOML/INI/CFG allowlist** — Added to hallucinated command detection

---

## Files

| File | Purpose |
|------|---------|
| `scripts/subagent_verifier.py` | Main verifier (CLI + API) |
| `scripts/compliance_checker.py` | Daily Zero Trust check |
| `scripts/suggestion_applier.py` | Applies fixes, calls verifier |
| `skills/self-improvement/compliance_checker/` | Compliance checker skill |
| `skills/self-improvement/suggestion_applier/` | Suggestion Applier skill |

---

## Quick Reference

```bash
# Verify all skills
for f in .claude/skills/*/SKILL.md; do python scripts/subagent_verifier.py "$f" --strict; done

# Verify core docs
python scripts/subagent_verifier.py CLAUDE.md .claude/rules/always.md .claude/rules/never.md --strict
```
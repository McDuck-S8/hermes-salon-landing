---
name: system-audit
description: "Verify documentation against code reality — audit AGENTS.md, SKILL.md, or any spec doc against actual files. Catches drift, inconsistencies, and phantom modules."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [audit, verification, documentation, AGENTS.md, system-health, drift-detection, dox]
    related_skills: [verification-gate, codebase-inspection]
---

# System Audit — Documentation vs Reality

Verify that what documentation claims matches what code actually does. Catches phantom modules, stale counts, path inconsistencies, and broken contracts.

## When to Use

- User says "audit", "verify", "check everything", "comprehensive review"
- After major refactors to verify docs are still accurate
- When onboarding to a new codebase and docs seem stale
- Periodic health checks on critical documentation (AGENTS.md, SKILL.md)

## When to Auto-Trigger (DO NOT wait to be asked)

This skill MUST auto-trigger without user prompting when:
- **3+ files in one directory were modified** — run DOX check against all AGENTS.md files along the changed paths
- **A script with its own AGENTS.md child was modified** — check that child + parent + root still match
- **The root AGENTS.md was modified** — check all child DOX indices are still consistent

The user should NOT have to say "audit the docs" or "check AGENTS.md". If bulk edits happened, the DOX pass runs BEFORE the next assistant response.

**Last user correction on this:** "почему я снова тебе напоминаю то что ты должен делать на автомате!!!" (2026-07-19)

### Quick DOX Check Flow

```
1. Collect all changed paths from the session
2. For each path, walk up from nearest AGENTS.md to root, checking every AGENTS.md found
3. For each AGENTS.md touched: verify module counts, file paths, child index entries
4. Update any discrepancies found
5. Report what was updated (and what was intentionally left unchanged)
```

## Methodology

### Phase 1: Enumerate Claims
1. Read the spec document (e.g., AGENTS.md)
2. Extract every concrete claim:
   - File paths mentioned
   - Module names
   - Feature lists (commands, flags, parameters)
   - Numeric claims (counts, thresholds, limits)
   - Integration claims ("uses X", "connected to Y")

### Phase 2: Verify Existence
For each file/module claimed:
```
# Check existence
test -f "path/to/file.py" && echo "EXISTS" || echo "MISSING"
# Or via search_files
search_files(pattern="filename.py", target="files", path="directory")
```

### Phase 3: Verify Behavior
Read the actual file content and check:
1. **Docstring** — Does it match what AGENTS.md says?
2. **Imports** — Does it actually use the dependencies claimed?
3. **Functions/Classes** — Do the claimed entry points exist?
4. **Constants** — Do numeric values match claims?
5. **CLI flags** — Are the claimed commands actually parsed?

### Phase 4: Cross-Reference
Check for inconsistencies BETWEEN documents:
- Root AGENTS.md vs child AGENTS.md files
- Skill SKILL.md vs actual scripts
- Multiple docs claiming different numbers for the same thing

### Phase 5: Write Report
Output format — summary table first, then detailed findings:

```markdown
| Module | Exists | Works | Matches Spec | Issues |
|--------|--------|-------|-------------|--------|
| foo.py | ✅ | ✅ | ⚠️ Partial | Claims 10 commands, has 12 |
| bar.py | ❌ | — | ❌ | File doesn't exist |
```

Then detailed sections for each module with specific evidence.

## Terminal Blockage Workaround

When `terminal` commands are blocked (user denied consent), use file-reading tools instead:

```python
# Instead of: python -c "import foo; print('OK')"
# Use: read_file to inspect the file directly

# Instead of: ls -la directory/
# Use: search_files(pattern="*.py", target="files", path="directory")

# Instead of: grep "pattern" file.py
# Use: search_files(pattern="pattern", path="file.py", target="content")
```

This is NOT equivalent to running the code — it verifies structure and syntax, not runtime behavior. Note this limitation in the audit report.

## Common Findings

### Module Count Drift
Multiple documents claim different counts for the same set of modules. This is the #1 most common audit finding.

**Pattern:** Root doc says 29, child doc says 23, `__init__.py` says 24, actual count is 30.

**Fix:** Count actual .py files and update ALL documents to match.

### Path Inconsistencies
Module A imports `HERMES_HOME` from `hermes_config.py` (portable detection). Module B hardcodes `Path("~/.hermes")`. On portable installs, Module B will look in the wrong place.

**Fix:** All modules should import from `hermes_config.py` for path resolution.

### Stale Numeric Claims
"2,750+ messages indexed" was accurate when written, but the DB has grown to 3,000+.

**Fix:** Either update the number or remove specific counts and say "thousands" or "N+".

### Phantom Modules
AGENTS.md references a file that was renamed, moved to `_deprecated/`, or never created.

**Fix:** Either create the file, update the reference, or remove it from docs.

### Command/Flag Mismatch
AGENTS.md claims `--status` but the script only has `--check`. Or the script has extra flags not documented.

**Fix:** Update docs to match actual CLI interface.

## Pitfalls

1. **Don't confuse "importable" with "working"** — A file can have valid Python syntax but crash at import time due to missing dependencies or circular imports. The audit reports "valid syntax" not "tested import".

2. **Counts are snapshots** — A claim like "29 candidates" may have been true at one point. Code evolves, docs don't always follow. Flag the discrepancy, don't assume the doc is wrong.

3. **Path resolution matters** — On Windows portable installs, `Path("~/.hermes")` resolves to `C:\Users\<user>\.hermes` which may not be where Hermes lives. Always check if modules use the unified `hermes_config.py` path resolution.

4. **Cross-reference ALL docs** — The same module may be described in root AGENTS.md, scripts/AGENTS.md, and scripts/crystal/AGENTS.md. All three may disagree.

5. **"Works" means "has valid Python syntax"** — Without running the code, you can only verify structural correctness. Note this limitation.

6. **Report format matters** — Summary table first (scannable), then detailed findings (evidence). Decision-makers need the table; engineers need the details.

7. **DO NOT wait for the user to ask** — If bulk edits happened, the DOX pass runs automatically before the next response. "Closeout" in AGENTS.md is not optional — it's a mandatory step after every multi-file change.

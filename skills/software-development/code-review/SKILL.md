---
name: code-review
description: "Review code changes before they ship — pre-commit security/quality gates, and parallel 3-agent cleanup for reuse/quality/efficiency."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-review, security, quality, cleanup, pre-commit, delegation, parallel]
    related_skills: [github-code-review, test-driven-development, plan, systematic-debugging]
---

# Code Review — Pre-Commit Verification & Cleanup

Two complementary workflows for reviewing YOUR code changes before committing. For reviewing OTHER people's PRs, see `github-code-review`.

---

## 1. Pre-Commit Verification (Security & Quality Gate)

Use after implementing a feature or bug fix, before `git commit` or `git push`.
Trigger when user says "commit", "push", "ship", "done", "verify", or "review before merge".
Skip for: documentation-only changes, pure config tweaks, or when user says "skip verification".

### Step 1 — Get the diff
```bash
git diff --cached
```
If empty, try `git diff` then `git diff HEAD~1 HEAD`. If `--cached` is empty but `git diff` shows changes, tell user to `git add <files>` first.

### Step 2 — Static security scan
Scan added lines only:
```bash
# Hardcoded secrets
git diff --cached | grep "^+" | grep -iE "(api_key|secret|password|token|passwd)\s*=\s*['\"][^'\"]{6,}['\"]"
# Shell injection
git diff --cached | grep "^+" | grep -E "os\.system\(|subprocess.*shell=True"
# Dangerous eval/exec
git diff --cached | grep "^+" | grep -E "\beval\(|\bexec\(\b"
# Unsafe deserialization
git diff --cached | grep "^+" | grep -E "pickle\.loads?\("
# SQL injection
git diff --cached | grep "^+" | grep -E "execute\(f\"|\.format\(.*SELECT|\.format\(.*INSERT"
```

### Step 2b — AI-specific security (2026-06-27)
Added based on OpenAI counter-misuse report and Anthropic security advisories:
```bash
# Prompt injection in user inputs
git diff --cached | grep "^+" | grep -iE "(system.*prompt|ignore.*previous|you are now)"
# Unsafe model loading (remote code execution)
git diff --cached | grep "^+" | grep -E "trust_remote_code\s*=\s*True"
# Hardcoded API endpoints (should use registry)
git diff --cached | grep "^+" | grep -iE "https?://.*\.(openai|anthropic|deepseek)\.com"
# LLM output used in SQL/exec without sanitization
git diff --cached | grep "^+" | grep -E "execute\(.*llm|exec\(.*model_output"
```

### Step 2c — Structured format injection (YAML/TOML/JSON/CSV)
Added 2026-07-23 — YAML frontmatter built via string concatenation is a recurring vector.
```bash
# YAML/TOML/JSON built via string concatenation with user-controlled values
git diff --cached | grep "^+" | grep -P "(fm|frontmatter|yaml|toml)\s*\+?=\s*f['\"]" | grep -vE "sanitize|escape|safe_replace"
# String-interpolated values used as bare YAML scalars (colon-injection risk)
git diff --cached | grep "^+" | grep -P "\+\s*(type|resource|source):\s*\{.*(category|source|tags|content|title)" 2>/dev/null
# Sanitization helper check: if YAML/JSON is built by hand, verify a sanitize helper exists
git diff --cached | grep "^+" | grep -P "(yaml|json|toml|frontmatter)" | grep -vE "sanitize|json\.dumps|yaml\.dump|escape"
```

### Step 3 — Baseline tests and linting
Detect project language, stash changes, run baseline, pop, run with changes, compare:
```bash
# Python
python -m pytest --tb=no -q 2>&1 | tail -5
which ruff && ruff check . 2>&1 | tail -10
which mypy && mypy . --ignore-missing-imports 2>&1 | tail -10

# Node
npm test -- --passWithNoTests 2>&1 | tail -5
which npx && npx eslint . 2>&1 | tail -10
which npx && npx tsc --noEmit 2>&1 | tail -10
```

### Step 4 — Self-review checklist
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] Input validation on user-provided data
- [ ] SQL queries use parameterized statements
- [ ] File operations validate paths (no traversal)
- [ ] External calls have error handling (try/catch)
- [ ] No debug print/console.log left behind
- [ ] No commented-out code
- [ ] New code has tests (if test suite exists)
- [ ] Structured formats (YAML/JSON/TOML/CSV) built via string interpolation sanitize user-controlled fields (backslash, newline, colon — see `references/yaml-injection.md`)

### Step 5 — Independent reviewer subagent
Call `delegate_task` with the full diff + static scan results. The reviewer returns a JSON verdict: `{passed, security_concerns, logic_errors, suggestions, summary}`. Fail-closed — issues block the commit.

### Step 6 — Auto-fix & commit loop
If reviewer passes but linting flagged minor issues, auto-fix them. If reviewer fails, display findings and offer to fix them. After fixing, re-run steps 2-5.

---

## 2. Simplify Code — Parallel 3-Agent Cleanup

Trigger when user says: "simplify", "simplify my changes", "review my code", "/simplify". Do NOT auto-run after every edit — it costs subagents.

### Phase 1 — Identify changes
```bash
git diff                    # uncommitted working-tree changes
git diff HEAD               # also include staged
git diff main...HEAD        # "this branch"
git diff -- src/foo.py      # specific file
```
If diff > 2000 lines, warn the user about token cost and offer to scope down.

### Phase 2 — Launch three parallel reviewers
Use `delegate_task` batch mode with three tasks, all receiving the full diff + repo path:

**Reviewer 1 — Code Reuse**: Flag code duplicating existing utilities. Search the codebase for existing functions/constants/patterns the new code should use instead. Require file:line evidence.

**Reviewer 2 — Code Quality**: Flag redundant state, parameter sprawl, copy-paste-with-variation, leaky abstractions, stringly-typed code. Give concrete refactors.

**Reviewer 3 — Efficiency**: Flag unnecessary work, missed concurrency, hot-path bloat, TOCTOU patterns, memory issues, overly broad reads. Give concrete fixes.

### Phase 3 — Aggregate and apply
1. Merge findings, dedupe overlaps
2. Discard false positives
3. Resolve conflicts: correctness > user's focus > readability/reuse > micro-perf
4. Apply surviving fixes (unless dry run)
5. Verify with targeted tests
6. Summarize what changed

### Pitfalls for parallel cleanup
- Don't fan out wider than ~3
- Give the WHOLE diff to each reviewer
- Reviewers MUST search, not guess — require file:line evidence
- Apply ≠ rewrite — keep edits scoped
- Respect project conventions (AGENTS.md / CLAUDE.md / linter config)
- Large diffs blow context — scope down before delegating

---

## 3. Two-Axis PR Review (Matt Pocock pattern)

For reviewing branches/PRs, add the **Standards × Spec** two-axis review.
Inspired by [mattpocock/skills](https://github.com/mattpocock/skills) (180k⭐).

### Pin the fixed point
```bash
git diff main...HEAD  # three-dot: diff against merge-base
git log main..HEAD --oneline
```
If the user didn't specify a ref, ask for it. Confirm `git rev-parse <ref>` resolves and the diff is non-empty.

### Identify the spec source
1. Issue refs in commit messages (`#123`, `Closes #45`) — fetch via bd/linear
2. A file the user passed as argument
3. PRD/spec under `docs/`, `specs/`, `.scratch/` matching the branch name
4. If nothing — skip Spec axis and note "no spec available"

### Identify standards sources
`CODING_STANDARDS.md`, `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, plus the **Fowler smell baseline** below. Repo overrides always win.

**Smell baseline** (Martin Fowler, *Refactoring* ch.3):
- Mysterious Name — rename it
- Duplicated Code — extract shared shape
- Feature Envy — move method onto data it envies
- Data Clumps — bundle into one type
- Primitive Obsession — give concept its own type
- Repeated Switches — polymorphism or map
- Shotgun Surgery — gather into one module
- Divergent Change — split the module
- Speculative Generality — delete it
- Message Chains — hide behind one method
- Middle Man — cut it, call real target
- Refused Bequest — composition over inheritance

### Spawn two parallel sub-agents
```python
delegate_task(tasks=[
    {"goal": "Standards review", "context": diff + standards_sources},
    {"goal": "Spec review", "context": diff + spec_content}
])
```

**Standards agent prompt:** full diff + list of standards sources + smell baseline pasted verbatim. "Report per file/hunk: (a) violations of documented standards, cite source; (b) baseline smells, name+quote hunk. Distinguish hard violations from judgement calls. Under 400 words."

**Spec agent prompt:** full diff + spec content + commits list. "Report: (a) missing requirements; (b) scope creep; (c) wrong implementations. Quote spec lines. Under 400 words."

### Aggregate
Present under `## Standards` and `## Spec` headings, verbatim. End with one-line summary: total findings per axis + worst issue per axis. Don't merge axes.

## Related Skills

- `github-code-review` — for reviewing OTHER people's PRs on GitHub
- `test-driven-development` — write tests before code
- `systematic-debugging` — root-cause debugging
- `plan` / `writing-plans` — implementation planning

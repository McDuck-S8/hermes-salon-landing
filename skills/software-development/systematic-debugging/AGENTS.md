# systematic-debugging — Skill

## Purpose
4-phase root cause debugging: understand bugs before fixing.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/.

## Local Contracts
- **Triggers**: Any technical issue (test failures, bugs, performance problems, build failures, integration issues). Use especially under time pressure or when previous fixes failed.
- **Required tools**: `read_file`, `search_files`, `terminal`, `web_search`, `web_extract`
- **Config**: No config.yaml required; uses standard Hermes tools
- **Related skills**: `test-driven-development`, `writing-plans`, `subagent-driven-development`

## Work Guidance
**When to use**: ANY technical issue — test failures, bugs, unexpected behavior, performance problems, build failures, integration issues. ESPECIALLY when under time pressure, "quick fix" seems obvious, multiple fixes already tried, or issue seems simple (simple bugs have root causes too).

**Common patterns**:
1. **Phase 1 (Root Cause)**: Read errors fully → reproduce consistently → check recent changes (git log/diff) → gather evidence (logs, state, data flow) → trace data flow to isolate component → form root cause hypothesis
2. **Phase 2 (Pattern)**: Find working similar code → compare against references → identify differences → understand dependencies
3. **Phase 3 (Hypothesis)**: Form single hypothesis → test minimally (one variable) → verify before continuing
4. **Phase 4 (Implementation)**: Create failing test first (TDD) → implement single fix → verify fix → run full suite → if 3+ fixes failed, STOP and question architecture

**Anti-patterns (STOP immediately)**: "Quick fix for now", "just try changing X", multiple changes at once, skipping tests, proposing fixes before tracing data flow, "one more fix attempt" after 2+ failures.

**Red flags**: Exit code 130 (MSYS shell corruption) — use `delegate_task` with fresh terminal; pip hangs on Windows → check C: drive space; taskkill path corruption → use `cmd.exe /c` wrapper; proxy issues → test proxy BEFORE patching code.

## Verification
- No test scripts in skill directory
- No evals/ directory
- Run verification by loading skill and checking SKILL.md frontmatter loads correctly
- References exist in `references/` directory (3 debug case studies)

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/cron-merge-conflict-debug.md` | Cron merge conflict debugging case study |
| `references/crystal-will-exhaustion-debug.md` | Crystal will() exhaustion debugging case study |
| `references/everos-windows-crossplatform-debug.md` | EverOS Windows cross-platform debugging case study |
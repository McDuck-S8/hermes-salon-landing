# test-driven-development — Skill

## Purpose
TDD: enforce RED-GREEN-REFACTOR, tests before code.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md.

## Local Contracts
- **Triggers**: New features, bug fixes, refactoring, behavior changes. Exceptions only with user permission (throwaway prototypes, generated code, config files).
- **Required tools**: `terminal` (pytest), `read_file`, `write_file`, `search_files`
- **Config**: No config.yaml required; uses standard pytest commands
- **Related skills**: `systematic-debugging`, `writing-plans`, `subagent-driven-development`

## Work Guidance
**When to use**: ALWAYS for production code — new features, bug fixes, refactoring, behavior changes. Don't skip "just this once" — that's rationalization.

**Core cycle (RED-GREEN-REFACTOR)**:
1. **RED** — Write ONE minimal failing test (clear name, real behavior, one thing). MUST watch it fail first.
2. **GREEN** — Write MINIMAL code to pass (hardcode, copy-paste, duplicate OK). Run test to verify pass. Then run full suite.
3. **REFACTOR** — Clean up (dedupe, rename, extract). Keep tests green. If tests fail → undo, smaller steps.

**Vertical slices only**: One RED→GREEN→REFACTOR cycle per behavior. NO horizontal slices (all tests then all code).

**Verification checklist**: Every new function has test; watched each test fail first; failure was for expected reason; minimal code written; all tests pass; clean output; real code not mocks; edge cases covered.

**Red flags — STOP and restart**: Code before test, test after implementation, test passes immediately, can't explain failure, tests added later, rationalizing exceptions, "already manually tested", "deleting X hours is wasteful", "TDD is dogmatic".

**When stuck**: Don't know how to test → write wished-for API, assertion first, ask user. Test too complex → design too complex, simplify interface. Must mock everything → code too coupled, use DI. Huge setup → extract helpers or simplify design.

**Hermes integration**: Use `terminal` to run `pytest tests/test_file.py::test_name -v` at each step. With `delegate_task`, include TDD enforcement in goal. Bug found? Write failing test first, then TDD cycle.

## Verification
- No test scripts in skill directory
- No evals/ directory
- Verify by loading skill and confirming SKILL.md frontmatter loads
- Apply TDD by running `pytest tests/ -q` on any Hermes project

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| (none) | No references/, templates/, or scripts/ directories in this skill |
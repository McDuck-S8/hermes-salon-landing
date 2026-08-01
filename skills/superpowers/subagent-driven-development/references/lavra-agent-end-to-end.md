# Lavra-Agent Dispatch via delegate_task (proven 2026-07-23)

Dispatch specialized lavra-agent-* reviewers via `delegate_task` when the full lavra-work pipeline (`.opencode/` hooks) isn't available.

## End-to-End Proven Workflow

Two full cycles completed this session, 4 HIGH fixes closed, 24 findings across 2 files.

### Pattern
```
1. skill_view("lavra-agent-{name}")     # Load agent protocol
2. read_file("scripts/target.py")        # Read target
3. delegate_task(goal="review")          # Dispatch agent → ~190s, ~10 findings
4. bd create "audit: file" --type epic   # Epic for findings
5. bd create "P0: fix" --parent EPIC     # Child per critical finding
6. delegate_task(goal="fix P0")          # Dispatch fix agent → ~500s per fix
7. grep for new func/pattern             # Verify in code
8. bd close CHILD_ID                     # Close bead
```

### Cycle 1: kc_rag.py
- Security review: 191s, 9 calls, 10 findings (2 HIGH + FTS5 injection, YAML injection)
- Fix: `sanitize_yaml_field()` at line 73, `_sanitize_fts5_query()` at line 304
- Beads: hermes-i9u (epic), hermes-i9u.1 (P0 closed), hermes-i9u.2 (P1 closed)

### Cycle 2: chain_heartbeat.py
- Security review: 307s, 9 calls, 14 findings (3 HIGH + CLI injection, race condition)
- Fix: `_validate_name()` at line 636, `_atomic_write()` at line 133
- Beads: hermes-1ov (epic), hermes-1ov.1 (HIGH closed), hermes-1ov.2 (HIGH closed)

### Proven Metrics
| Step | Duration | Findings |
|------|----------|----------|
| Security review (485-line file) | ~191s | 10 |
| Security review (741-line file) | ~307s | 14 |
| Fix dispatch (single function) | ~400-580s | Verified in code |
| End-to-end (epic + 2 fixes) | ~15-20 min | 4 HIGH closed |

### Available Agents (30)
security-sentinel, architecture-strategist, performance-oracle, kieran-python-reviewer, kieran-typescript-reviewer, dhh-rails-reviewer, code-simplicity-reviewer, data-integrity-guardian, pattern-recognition-specialist, goal-verifier, lint, +20 more in skills/lavra-agent-*

### Pitfalls
- **Free model timeout:** 600s limit on free-tier agents. 1 fix per agent, keep context small.
- **No .opencode/ = no lavra-work:** Without `.opencode/` hooks, full lavra-work pipeline (M1-M10) fails at M6. Use direct delegate_task dispatch.
- **Verify in code, don't trust summary:** Subagent says "fixed" doesn't mean it's fixed. grep for the function/pattern.
- **Sequential per file:** Fix agents for the same file MUST run sequentially (not parallel) or patches conflict.
- **bd timeout:** bd create/close may timeout on response wait. Operation still succeeds; verify with `bd list`/`bd show`.
- **bead owner confusion:** When creating child beads, they inherit priority from the epic regardless of `--priority` flag. Always set explicit `--priority 1` for P0/P1.

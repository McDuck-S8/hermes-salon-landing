# Lavra-Agent Dispatch via delegate_task (proven 2026-07-23)

Dispatch specialized lavra-agent-* reviewers via `delegate_task` when the full lavra-work pipeline (`.opencode/` hooks) isn't available.

## Pattern

```
1. skill_view("lavra-agent-{name}")     # Load agent protocol
2. read_file("scripts/target.py")        # Read target file
3. delegate_task(goal="...", context="...")  # Dispatch agent
4. bd create "audit: file" --type epic   # Epic for findings
5. bd create "P0: fix" --parent EPIC     # Child per critical finding
6. delegate_task(goal="fix P0")          # Dispatch fix agent
7. grep for fix in code                  # Verify
8. bd close CHILD_ID                     # Close bead
```

## Available Agents (30 total in skills/lavra-agent-*)

- **lavra-agent-security-sentinel** — SQLi, XSS, injection, secrets, OWASP
- **lavra-agent-architecture-strategist** — Design critique, failure modes
- **lavra-agent-performance-oracle** — Bottlenecks, N+1, caching
- **lavra-agent-kieran-python-reviewer** — Python strict conventions
- **lavra-agent-kieran-rails-reviewer** — Rails strong params, AR
- **lavra-agent-kieran-typescript-reviewer** — TypeScript conventions
- **lavra-agent-code-simplicity-reviewer** — Dead code, YAGNI
- **lavra-agent-pattern-recognition-specialist** — Anti-patterns, naming
- **lavra-agent-goal-verifier** — Exists/Substantive/Wired validation
- **lavra-agent-best-practices-researcher** — External research
- **lavra-agent-learnings-researcher** — Knowledge base search
- **lavra-agent-repo-research-analyst** — Project structure analysis
- **lavra-agent-framework-docs-researcher** — Framework docs search
- **lavra-agent-git-history-analyzer** — Git archaeology
- **lavra-agent-bug-reproduction-validator** — Bug reproduction
- **lavra-agent-spec-flow-analyzer** — Feature spec validation
- **lavra-agent-data-integrity-guardian** — Data model validation
- **lavra-agent-data-migration-expert** — Migration correctness
- **lavra-agent-migration-drift-detector** — Schema consistency
- **lavra-agent-deployment-verification-agent** — Deploy checklists
- **lavra-agent-lint** — Automated linting pass
- **lavra-agent-design-implementation-reviewer** — Figma→code match
- **lavra-agent-design-iterator** — Iterative UI refinement
- **lavra-agent-dhh-rails-reviewer** — DHH-style Rails review
- **lavra-agent-every-style-editor** — Every style text editing
- **lavra-agent-figma-design-sync** — Visual diff detection
- **lavra-agent-julik-frontend-races-reviewer** — Race conditions
- **lavra-agent-pr-comment-resolver** — PR comment resolution
- **lavra-agent-ankane-readme-writer** — README generation
- **lavra-agent-agent-native-reviewer** — Agent-native compliance

## Proven Metrics

Each agent completes in ~190s with ~9 API calls, producing 10-14 findings across severity levels (HIGH/MEDIUM/LOW/INFO) with file:line references, OWASP matrix (security), and remediation roadmap.

## When to Use

- **Direct dispatch** (this pattern) — no .opencode/ hooks available
- **Full lavra-work pipeline** — requires .opencode/ hooks, provides Phases M1-M10 with wave ordering, conflict detection, multi-agent orchestration

## Post-Review Workflow

1. Create epic bead with all findings
2. Create child beads per P0/P1 finding
3. Dispatch fix subagents via delegate_task (1 finding = 1 subagent)
4. Verify fix in code (grep for new functions/patterns)
5. Close child beads
6. Rinse for P2+ findings

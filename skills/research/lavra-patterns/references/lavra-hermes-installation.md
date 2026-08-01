# Lavra in Hermes — Installation Reference

## Installed: 2026-06-04

### Core Skills (16)
All at `D:\Portable_Soft\hermes\skills\lavra-<name>\SKILL.md`

| Skill | Purpose |
|-------|---------|
| lavra-work | Execute work — auto-routes single/sequential/parallel |
| lavra-work-single | Single bead implementation (phases 1-5) |
| lavra-work-multi | Multi-bead parallel orchestration (phases M1-M10) |
| lavra-review | Multi-agent code review with ultra-thinking |
| lavra-research | Domain-matched research agents |
| lavra-plan | Feature → beads with parallel research |
| lavra-knowledge | 7-step knowledge capture to JSONL |
| lavra-eng-review | Engineering review (architecture, simplicity, security, perf) |
| lavra-ceo-review | CEO/founder-mode plan review |
| lavra-brainstorm | Collaborative brainstorming before planning |
| git-worktree | Git worktree management for parallel dev |
| file-todos | File-based TODO tracking |
| create-agent-skills | Skill authoring patterns |
| brainstorming | Creative brainstorming |
| agent-native-architecture | Agent-native design patterns |
| agent-browser | Browser automation agent |

### Review/Research Agents (30)
All at `D:\Portable_Soft\hermes\skills\lavra-agent-<name>\SKILL.md`

**Review (16):** security-sentinel, performance-oracle, architecture-strategist, code-simplicity-reviewer, goal-verifier, data-integrity-guardian, data-migration-expert, migration-drift-detector, deployment-verification-agent, pattern-recognition-specialist, agent-native-reviewer, kieran-python-reviewer, kieran-rails-reviewer, kieran-typescript-reviewer, julik-frontend-races-reviewer, dhh-rails-reviewer

**Research (5):** repo-research-analyst, learnings-researcher, git-history-analyzer, framework-docs-researcher, best-practices-researcher

**Workflow (5):** spec-flow-analyzer, pr-comment-resolver, lint, every-style-editor, bug-reproduction-validator

**Design (3):** figma-design-sync, design-iterator, design-implementation-reviewer

**Docs (1):** ankane-readme-writer

### Memory System
`D:\Portable_Soft\hermes\data\lavra-memory\`
- knowledge.jsonl — 217 entries (78 decision, 59 learned, 36 fact, 30 pattern, 14 investigation)
- recall.sh — bash keyword search (requires jq)
- knowledge-db.sh — SQLite FTS5 wrapper (kb_ensure_db, kb_search, kb_sync)
- lavra.json — Lavra config

### Dependencies
- jq (Chocolatey, v1.8.1)
- sqlite3 (v53.1)
- git

### Usage from Hermes
```python
skill_view(name="lavra-work")
skill_view(name="lavra-agent-security-sentinel")
bash data/lavra-memory/recall.sh "keyword"
bash data/lavra-memory/recall.sh --stats
```

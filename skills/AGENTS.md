# skills/ — Agent Skills Library

## Purpose
Bundled agent skills — reusable behaviors and domain-specific knowledge that agents can load on demand.

## Ownership
Skills are curated and versioned. Managed via the skill-forge system.

## Local Contracts
- Each skill has a `SKILL.md` file as its entry point
- Skills may include `references/` (markdown docs), `scripts/` (executable helpers), `templates/`
- Skills are organized by category in subdirectories
- `.hub/` contains the skill hub index and cache
- `.usage.json` tracks skill usage statistics

## Work Guidance
- **Loading a skill**: Use the `skill` tool with the skill name
- **Creating a skill**: Follow the SKILL.md format, place in appropriate category
- **Categories**: automation, creative, data-science, devops, finance, github, media, mlops, research, security, self-improvement, software-development, web-development, etc.
- **Auto-generated skills**: `auto-generated/` — patterns learned from sessions
- **Lavra agents**: `lavra-agent-*` — review and analysis agents

## Verification
- Each skill should have a valid `SKILL.md`
- Check `.usage.json` for usage stats

## Child DOX Index
| Category | Contents |
|---|---|
| `automation/` | Browser, session analysis, telegram digest, **subagent-orchestration** |
| `creative/` | Design, art, video, music generation, **remotion-video** |
| `context-engineering/` | Context window management: **filesystem-context** (tool-output offloading), **context-optimization** (masking, KV-cache, compaction) |
| `devops/` | Kanban, system ops, webhooks, **chain-heartbeat**, **maintenance-scanner** |
| `finance/` | Earning with AI, Excel, stocks |
| `github/` | PR workflow, issues, code review |
| `lavra-agent-*` | Review and analysis agents (30+) |
| `research/` | ArXiv, patterns, wiki |
| `self-improvement/` | Dream memory, evolution, verification |
| `software-development/` | TDD, debugging, plans, **impeccable** (дизайн/аудит UI), **beads** (трекер задач) |
| `superpowers/` | Process skills: brainstorming, subagent-driven-development, writing-plans, using-superpowers |

# finance-core — Skill

## Purpose
Core finance ledger for autonomous arbitrage agent: P&L, Cash Flow, Unit Economics, Tax Ledger, Withdrawal Tracker. SQLite backend, integrates with autonomous_agent and arbitrage-execution.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Core finance ledger for autonomous arbitrage agent: P&L, Cash Flow, Unit Economics, Tax Ledger, Withdrawal Tracker
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (2 files) |
| `scripts/` | Helper scripts (1 files) |
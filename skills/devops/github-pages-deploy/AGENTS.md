# github-pages-deploy — Skill

## Purpose
Deploy static sites to GitHub Pages. Source MUST be root (/) or /docs folder. No other paths accepted.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: github, pages, static-site, deployment, devops
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Deploy static sites to GitHub Pages
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (3 files) |
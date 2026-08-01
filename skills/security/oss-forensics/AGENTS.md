# oss-forensics — Skill

## Purpose
Supply chain investigation, evidence recovery, and forensic analysis for GitHub repositories.
Covers deleted commit recovery, force-push detection, IOC extraction, multi-source evidence
collection, hy

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: investigate this repository, investigate [owner/repo], check for supply chain compromise, recover deleted commits, forensic analysis of [owner/repo], was this repo compromised, supply chain attack, suspicious commit, force push detected, IOC extraction
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Supply chain investigation, evidence recovery, and forensic analysis for GitHub repositories
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (5 files) |
| `templates/` | Templates (2 files) |
| `scripts/` | Helper scripts (1 files) |
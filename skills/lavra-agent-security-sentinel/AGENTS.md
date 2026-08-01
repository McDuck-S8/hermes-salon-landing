# lavra-agent-security-sentinel — Skill

## Purpose
Performs security audits covering input validation, SQL injection, XSS, authentication/authorization, hardcoded secrets, and OWASP Top 10 compliance. Use for code handling user input, auth, payments, 

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Performs security audits covering input validation, SQL injection, XSS, authentication/authorization, hardcoded secrets, and OWASP Top 10 compliance
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| (no child directories) | |
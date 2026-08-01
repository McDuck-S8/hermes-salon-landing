# document-intake — Skill

## Purpose
Convert PDF/DOCX to clean markdown for agent processing

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: pdf, docx, markdown, document, ocr
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Convert PDF/DOCX to clean markdown for agent processing
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (1 files) |
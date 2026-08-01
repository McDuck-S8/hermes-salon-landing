# document-processing — Skill

## Purpose
Extract text from PDFs/scans (pymupdf, marker-pdf) and edit PDF content via natural language (nano-pdf). Also covers split, merge, search, and OCR workflows.

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Extract text from PDFs/scans (pymupdf, marker-pdf) and edit PDF content via natural language (nano-pdf)
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
| `scripts/` | Helper scripts (2 files) |
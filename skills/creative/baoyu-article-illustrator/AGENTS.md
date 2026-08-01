# baoyu-article-illustrator — Skill Contract

## Purpose
Article illustrations: type × style × palette consistency. Analyze articles, identify illustration positions, generate images with Type × Style × Palette consistency.

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: creative.

## Local Contracts
### Triggers
- User asks to illustrate an article, add images to an article, generate illustrations for content
- User uses phrases like "为文章配图", "illustrate article", or "add images"
- User provides an article (file path or pasted content) and optionally specifies type, style, palette, or density

### Required Tools
- `read_file` — read article content
- `write_file` — save analysis, outline, prompts, and source files
- `image_generate` — generate illustrations
- `vision_analyze` — analyze reference images if provided
- `terminal` — download generated images via curl
- `clarify` — confirm settings with user (one question at a time)

### Configuration
- Standard skill configuration via SKILL.md frontmatter
- Output directory defaults: `{article-dir}/imgs/` for file paths, `illustrations/{topic-slug}/` for pasted content

## Work Guidance
### When to Use
Trigger this skill when the user asks to illustrate an article, add images to an article, generate illustrations for content, or uses phrases like "为文章配图", "illustrate article", or "add images". The user provides an article (file path or pasted content) and optionally specifies type, style, palette, or density.

### Common Patterns
1. **Article file path provided** → Read file → Analyze → Confirm settings → Generate outline → Create prompts → Generate images → Insert into article
2. **Pasted content provided** → Save as source file → Same workflow
3. **Reference images provided** → Analyze with vision_analyze → Incorporate descriptions into prompts

### Workflow (7 Steps)
1. **Detect reference images** — If user supplies reference images, analyze with `vision_analyze`, save descriptions
2. **Analyze content** — Read source, write `analysis.md` with content type, purpose, core arguments, illustration positions
3. **Confirm settings** — Use `clarify` tool (one question at a time): Preset/Type → Density → Style → Palette → Language
4. **Generate outline** → Save `outline.md` with frontmatter and per-illustration entries
5. **Generate prompts** — Create prompt files in `prompts/NN-{type}-{slug}.md` with YAML frontmatter (BLOCKING: no image generation without saved prompt)
6. **Generate images** — Call `image_generate`, download via `terminal` (`curl`), save to output directory
7. **Finalize** — Insert markdown image references into article, report summary

### Three Dimensions
- **Type** (information structure): infographic, scene, flowchart, comparison, framework, timeline
- **Style** (rendering approach): notion, warm, minimal, blueprint, watercolor, elegant, vector-illustration, editorial, scene, poster
- **Palette** (color scheme, optional): macaron, warm, neon — overrides style's default colors

### Core Principles
- Visualize concepts, not metaphors — illustrate the underlying concept, not literal metaphors
- Labels use article data — actual numbers, terms, and quotes from the article
- Prompt files are reproducibility records — every illustration must have a saved prompt file before generation
- Strip secrets — scan source content for API keys, tokens, or credentials before writing anything to disk

## Verification
- Load SKILL.md and validate frontmatter (name, description, category, tags, metadata)
- Verify `references/` directory exists with workflow.md, usage.md, styles.md, style-presets.md, prompt-construction.md
- Verify `prompts/` directory exists (created during workflow)
- Test workflow: article analysis → outline → prompts → image generation → final insertion

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (5 files): workflow.md, usage.md, styles.md, style-presets.md, prompt-construction.md |
| `prompts/` | Generated prompt files (created during workflow) |
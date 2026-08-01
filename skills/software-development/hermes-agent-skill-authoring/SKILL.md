---
name: hermes-agent-skill-authoring
description: "Author in-repo SKILL.md: frontmatter, validator, structure."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, authoring, hermes-agent, conventions, skill-md]
    related_skills: [writing-plans, requesting-code-review, lavra-patterns]
---

# Authoring Hermes-Agent Skills (in-repo)

> This skill incorporates Lavra/OpenClaude patterns for skill creation.
> For full Lavra reference see: `lavra-patterns` skill in `research/` category.


## Overview

There are two places a SKILL.md can live:

1. **User-local:** `~/.hermes/skills/<maybe-category>/<name>/SKILL.md` — personal, not shared. Created via `skill_manage(action='create')`.
2. **In-repo (this skill is about this case):** `/home/bb/hermes-agent/skills/<category>/<name>/SKILL.md` — committed, shipped with the package. Use `write_file` + `git add`. `skill_manage(action='create')` does NOT target this tree.

## When to Use

- User asks you to add a skill "in this branch / repo / commit"
- You're committing a reusable workflow that should ship with hermes-agent
- You're editing an existing skill under `/home/bb/hermes-agent/skills/` (use `patch` for small edits, `write_file` for rewrites; `skill_manage` still works for patch on in-repo skills, but not for `create`)

## Agent Skills Open Standard (agentskills.io) Alignment

Our SKILL.md format is **80% compatible** with the [Agent Skills open standard](https://agentskills.io) (23k★, by Anthropic). This standard is supported by 20+ agents: Claude Code, Cursor, Codex CLI, OpenCode, OpenClaw, Gemini CLI, GitHub Copilot, VS Code, etc.

**Key alignment points:**
- `name`: lowercase, hyphens, max 64 chars, must match directory name ✓
- `description`: max 1024 chars, what + when trigger ✓
- File structure: `SKILL.md` + optional `scripts/`, `references/`, `assets/` ✓
- Progressive disclosure: metadata → instructions → resources ✓
- We use `references/` (same name as standard)
- We use `scripts/` (same name as standard)

**Differences to close:**
- Missing `compatibility` field for environment requirements
- Missing `allowed-tools` field (experimental in spec)
- Missing `license` field in some skills
- Validation: standard provides `skills-ref validate` — our Hermes uses `tools/skill_manager_tool.py`

**Migration path:** Add `compatibility` + `allowed-tools` + `license` to all new skills. Validate with both our internal validator and `skills-ref` (from `pip install agentskills-skills-ref`).

## Required Frontmatter

Source of truth: `tools/skill_manager_tool.py::_validate_frontmatter`. Hard requirements:

- Starts with `---` as the first bytes (no leading blank line).
- Closes with `\n---\n` before the body.
- Parses as a YAML mapping.
- `name` field present.
- `description` field present, ≤ **1024 chars** (`MAX_DESCRIPTION_LENGTH`).
- Non-empty body after the closing `---`.

Peer-matched shape used by every skill under `skills/software-development/` (aligned with agentskills.io standard):

```yaml
---
name: my-skill-name               # lowercase, hyphens, ≤64 chars (MAX_NAME_LENGTH)
description: Use when <trigger>. <one-line behavior>.  # max 1024 chars
version: 1.0.0
author: Hermes Agent
license: MIT                              # Apache-2.0, MIT, Proprietary, etc.
compatibility: Python 3.10+ | uv | Linux  # optional, environment requirements
allowed-tools: Bash(*) Read               # optional, experimental
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill, another-skill]
---
```

New fields vs prior convention:
- **`compatibility`** — agentskills.io field. Max 500 chars. Indicates env requirements (Python version, OS, system packages, network access).
- **`allowed-tools`** — agentskills.io experimental field. Space-separated pre-approved tools. E.g. `Bash(git:*) Read`.
- **`license`** — already used by some, now recommended field from standard.

`version` / `author` / `license` / `compatibility` / `metadata` are NOT enforced by the validator, but every peer has them — omit and your skill sticks out.

## Lavra Best Practices (Skill Creation)

Skills ARE prompts — all prompting best practices apply. A skill is the prompt
that loads into context when the agent recognizes a matching task. Write it
like a well-structured system prompt, not like documentation.

### Core Lavra Rules
1. **YAML frontmatter + markdown body** — NO XML tags, NO JSON blocks for structure.
2. **Description = WHAT + WHEN** — it is the discovery field; must tell the agent
   what the skill does AND when to activate it.
3. **Standard file layout:**
   ```
   my-skill/
   ├── SKILL.md              # Entry point (required)
   ├── reference.md          # Detailed docs (loaded on demand)
   ├── examples.md           # Usage examples
   └── scripts/              # Utility scripts (executed, not loaded)
   ```
4. **Frontmatter fields for Lavra-style skills:**
   | Field | Required | Max | Description |
   |-------|----------|-----|-------------|
   | name | Yes | 64 chars | lowercase, hyphens only |
   | description | Yes | 1024 chars | what + when |
   | allowed-tools | No | — | tools allowed without asking |
   | model | No | — | specific model override |
   | version | No | — | semantic version (Hermes convention) |
   | author | No | — | skill author (Hermes convention) |
   | license | No | — | license (Hermes convention) |
   | metadata | No | — | Hermes tags + related_skills |

### Prompting Best Practices Applied to Skills
- Write clear, direct instructions — skills are consumed by LLMs, not humans
- Use bullet lists and tables for quick-reference sections
- Include concrete examples (the agent learns from few-shot patterns)
- Avoid vague language — say exactly what to do, not what to "consider"
- Put the most important information first (primacy bias in long contexts)

## Progressive Disclosure

**Rule: SKILL.md must be under 500 lines.**

The SKILL.md is the entry point loaded into context on every activation. Keep
it lean and focused. When content exceeds this limit, split it out:

| File | Purpose | When loaded |
|------|---------|-------------|
| `SKILL.md` | Core instructions, overview, quick reference | Every activation |
| `reference.md` | Detailed docs, edge cases, API references | On demand (agent reads if needed) |
| `examples.md` | Full worked examples, code samples | On demand |
| `scripts/` | Executable helpers, validators, templates | Executed, never loaded into context |

**Why 500 lines?** Context window is finite. A bloated SKILL.md wastes tokens
on every single activation, even when most of the content is irrelevant to the
current task. Progressive disclosure loads only what's needed.

**Practical targets (Hermes convention):**
- Aim for **8–15k chars** (matching peer skills in `software-development/`)
- If exceeding **20k chars**, split aggressively into `reference.md`
- Absolute limit: **100,000 chars** (enforced by validator as `MAX_SKILL_CONTENT_CHARS`)

## Effective Descriptions

The description field is the **discovery mechanism**. It determines whether the
agent activates this skill for a given user request. It must answer:
1. **WHAT** does this skill do?
2. **WHEN** should the agent use it?

### Good Descriptions
```
description: "Author in-repo SKILL.md files: frontmatter validation,
  Lavra structure patterns, and progressive disclosure best practices.
  Use when creating new skills, reviewing skill structure, or splitting
  oversized SKILL.md files."
```

```
description: "Generate git commit messages following conventional commits.
  Use when committing code changes that need a well-structured commit message."
```

### Bad Descriptions
```
description: "Skills"                         # WHAT: too vague
```

```
description: "This skill helps you with stuff"  # WHAT: vague, WHEN: missing
```

```
description: "A comprehensive guide to authoring, validating, testing, deploying,
  and maintaining hermes-agent skills including all edge cases and advanced
  patterns and community conventions and versioning strategies and CI/CD
  integration and cross-platform compatibility and accessibility guidelines"
  # 257 chars — EXCEEDS 1024 limit, will fail validation
```

### Description Checklist
- Starts with a verb or gerund ("Author", "Generate", "Analyze")
- States the trigger condition ("Use when ...")
- Under 1024 characters total
- Mentions the primary output or behavior
- Does NOT attempt to list every possible use case

## Size Limits

- Description: ≤ 1024 chars (enforced).
- Full SKILL.md: ≤ 100,000 chars (enforced as `MAX_SKILL_CONTENT_CHARS`, ~36k tokens).
- Peer skills in `software-development/` sit at **8-14k chars**. Aim for that range.
- If pushing past 20k, split into `references/*.md` and reference them from SKILL.md.

## Peer-Matched Structure

Every in-repo skill follows roughly:

```
# <Title>

## Overview
One or two paragraphs: what and why.

## When to Use
- Bulleted triggers
- "Don't use for:" counter-triggers

## <Topic sections specific to the skill>
- Quick-reference tables are common
- Code blocks with exact commands
- Hermes-specific recipes (tests via scripts/run_tests.sh, ui-tui paths, etc.)

## Common Pitfalls
Numbered list of mistakes and their fixes.

## Verification Checklist
- [ ] Checkbox list of post-action verifications

## One-Shot Recipes (optional)
Named scenarios → concrete command sequences.
```

Not every section is mandatory, but `Overview` + `When to Use` + actionable body + pitfalls are the minimum for the skill to feel like a peer.

## Directory Placement

```
skills/<category>/<skill-name>/SKILL.md
```

Categories currently in repo (confirm with `ls skills/`): `autonomous-ai-agents`, `creative`, `data-science`, `devops`, `dogfood`, `email`, `gaming`, `github`, `leisure`, `mcp`, `media`, `mlops/*`, `note-taking`, `productivity`, `red-teaming`, `research`, `smart-home`, `social-media`, `software-development`.

Pick the closest existing category. Don't invent new top-level categories casually.

## Workflow

1. **Survey peers** in the target category:
   ```
   ls skills/<category>/
   ```
   Read 2-3 peer SKILL.md files to match tone and structure.
2. **Check validator constraints** in `tools/skill_manager_tool.py` if unsure.
3. **Draft** with `write_file` to `skills/<category>/<name>/SKILL.md`.
4. **Validate locally**:
   ```python
   import yaml, re, pathlib
   content = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
   assert content.startswith("---")
   m = re.search(r'\n---\s*\n', content[3:])
   fm = yaml.safe_load(content[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 1024
   assert len(content) <= 100_000
   ```
5. **Git add + commit** on the active branch.
6. **Note:** the CURRENT session's skill loader is cached — `skill_view` / `skills_list` will not see the new skill until a new session. This is expected, not a bug.

## Cross-Referencing Other Skills

`metadata.hermes.related_skills` unions both trees (`skills/` in-repo and `~/.hermes/skills/`) at load time. You CAN reference a user-local skill from an in-repo skill, but it won't resolve for other users who clone the repo fresh. Prefer referencing only in-repo skills from in-repo skills. If a frequently-referenced skill lives only in `~/.hermes/skills/`, consider promoting it to the repo.

## Editing Existing In-Repo Skills

- **Small fix (typo, added pitfall, tightened trigger):** `skill_manage(action='patch', name=..., old_string=..., new_string=...)` works fine on in-repo skills.
- **Major rewrite:** `write_file` the whole SKILL.md. `skill_manage(action='edit')` also works but requires supplying the full new content.
- **Adding supporting files:** `write_file` to `skills/<category>/<name>/references/<file>.md`, `templates/<file>`, or `scripts/<file>`. `skill_manage(action='write_file')` also works and enforces the references/templates/scripts/assets subdir allowlist.
- **Always commit** the edit — in-repo skills are source, not runtime state.

## Common Pitfalls

1. **Using `skill_manage(action='create')` for an in-repo skill.** It writes to `~/.hermes/skills/`, not the repo tree. Use `write_file` for in-repo creation.

2. **Leading whitespace before `---`.** The validator checks `content.startswith("---")`; any leading blank line or BOM fails validation.

3. **Description too generic.** Peer descriptions start with "Use when ..." and describe the *trigger class*, not the one task. "Use when debugging X" > "Debug X".

4. **Forgetting the author/license/metadata block.** Not validator-enforced, but every peer has it; omitting makes the skill look half-finished.

5. **Writing a skill that duplicates a peer.** Before creating, `ls skills/<category>/` and open 2-3 peers. Prefer extending an existing skill to creating a narrow sibling.

6. **Expecting the current session to see the new skill.** It won't. The skill loader is initialized at session start. Verify in a fresh session or via `skill_view` using the exact path.

7. **Linking to skills that don't exist in-repo.** `related_skills: [some-user-local-skill]` works for you but breaks for other clones. Prefer only in-repo links.

8. **SKILL.md exceeding 500 lines.** Violates Lavra progressive disclosure. Split into `SKILL.md` + `reference.md` + `examples.md`. The agent loads SKILL.md every time; bloated files waste context.

9. **Description that lacks WHEN trigger.** "A skill for git commits" does not tell the agent when to activate. Use "Use when committing code changes..." format.

10. **Putting everything in SKILL.md instead of reference files.** SKILL.md is the entry point, not a dump. Move detailed explanations, edge cases, and long examples to `reference.md` and `examples.md`.

## IBOS Governance Layer Patterns (Hermes + Infinite Brain OS)

**Context:** This session bootstrapped the full IBOS governance layer for Hermes — frontmatter schema, validator, entity registry, and 15 canonical entities. Skills live *inside* this governance layer. When creating the governance infrastructure itself, apply these patterns:

### Frontmatter Schema Design
```yaml
# _system/schemas/frontmatter.schema.yaml
required_keys: [id, type, namespace, status, version, owner, created, summary, description]
valid_types: [command, agent, skill, rule, workflow, tool, knowledge, data, memory, output, project]
valid_statuses: [scratch, research, candidate, canon, deprecated, archived]
# 8 namespace profiles with required_surfaces
# 12 validation rules (canon-requires-operator, candidate-needs-source, no-self-promotion, etc.)
```

### Validator Script Pattern
```python
# scripts/validate_entities.py
- Collect all .md files from entities/, knowledge/, projects/, departments/, outputs/, memory/, data/, tools/, workflows/, automations/
- Skip plumbing patterns (README.md, INDEX.md, support/, archive/, _system/, sessions/, etc.)
- Extract YAML frontmatter, validate against schema
- Check wikilinks [[id]] resolve to entity registry
- Validate namespace structure (required surfaces per profile)
- Exit 1 on errors, 0 on clean
```

### Entity Registration Workflow
1. **Create directory structure** matching IBOS ontology (16 dirs)
2. **Write schema first** — defines the contract
3. **Write validator** — enforces the contract
4. **Create canonical entities** — one per core Hermes component
5. **Run validator until clean** — 0 errors, 0 warnings
6. **Document in ARBITRAGE_WORKSHOP.md** — mapping table, integration plan

### Wikilink Resolution
- Entity IDs must match wikilink targets exactly: `[[crystal-core]]` → entity with `id: crystal-core`
- Collect all entity IDs before validating wikilinks
- YAML parses ISO8601 dates as `datetime` objects — handle both `str` and `datetime` in validator

### Namespace Profiles
- 8 profiles: `ai-core`, `telegram-bots`, `arbitrage`, `finance`, `ops`, `research`, `infra`, `personal`
- Standard: requires `INDEX.md`, `canon/`, `playbooks/`, `support/`, `synthesis/`
- Reduced (personal): requires only `INDEX.md`, `canon/`
- Tool-contract: uses `core-contract.md` instead of `core-doctrine.md`

### Promotion Path Governance
```
raw source → support/ → synthesis/ → canon-candidate → canon (operator approval required)
```
- Agent CANNOT self-promote to canon
- Validator enforces: `status == 'canon'` requires `owner == 'operator'`
- Candidate must have `promotes_from` pointing to synthesis nodes

### When to Use This Pattern
- Bootstrapping governance layer for a new project/agent
- Adding formal validation to existing markdown knowledge base
- Integrating Hermes with IBOS-style canon governance
- Creating entity registry with wikilink resolution

## Verification Checklist

- [ ] File is at `skills/<category>/<name>/SKILL.md` (not in `~/.hermes/skills/`)
- [ ] Frontmatter starts at byte 0 with `---`, closes with `\n---\n`
- [ ] `name`, `description`, `version`, `author`, `license`, `metadata.hermes.{tags, related_skills}` all present
- [ ] Name ≤ 64 chars, lowercase + hyphens
- [ ] Description ≤ 1024 chars and starts with "Use when ..."
- [ ] Total file ≤ 100,000 chars (aim for 8-15k)
- [ ] Structure: `# Title` → `## Overview` → `## When to Use` → body → `## Common Pitfalls` → `## Verification Checklist`
- [ ] `related_skills` references resolve in-repo (or are explicitly OK to be user-local)
- [ ] `git add skills/<category>/<name>/ && git commit` completed on the intended branch

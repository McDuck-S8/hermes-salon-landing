# Skill Mature Key Analysis — 2026-07-28

## Context
Morning report showed **"skill" as top mature key** (2304 entries, 100% maturity). Deep investigation revealed this is **mass skill indexation**, not skill usage.

## What "skill" Key Actually Is

| Parameter | Value |
|-----------|-------|
| Source | `scripts/skill_indexer.py → index_all_skills()` |
| Action | Parses ALL `SKILL.md` files in `skills/` (145+ directories) |
| Result | 2304 KC entries with `axis_domain='skill'`, `axis_outcome='indexed'` |
| Tags | `action:assist|review|generate|...`, `domain:devops|automation|...`, `output:report|code|plan|...` |

## Skill Indexer Script (Confirmed Working)
- **Location**: `scripts/skill_indexer.py` (517 lines)
- **Function**: Discovers, parses frontmatter, classifies by action_type/domain/output_type, extracts triggers/related skills, indexes to KC
- **Skill Chains**: 9 predefined pipelines (dev-full-cycle, bugfix, content-pipeline, research-pipeline, deploy-pipeline, ai-agent-build, security-review, creative-generate, github-workflow) indexed as `skill_chain` domain

## What "Unlock skill today" Means (Morning Report Proposal)

**NOT**: "Learn to use skills" — they're already indexed and available.

**IS**: **Skill Audit (g-009)** — scan 145 skill directories for:
- Staleness (>30d no updates)
- Duplicates / overlapping functionality
- Broken loads (missing SKILL.md, invalid frontmatter)
- Missing AGENTS.md (DOX compliance)
- Outdated triggers / action types
- Security findings (SkillSpector audit pending)

## Action Items for This Session
- [ ] Run `skill_indexer.py --dry` to verify current index state
- [ ] Run skill audit on all 145 local skill directories
- [ ] Build unified indexer for local + external skills (`~/.claude/skills/`)
- [ ] Verify Chain Heartbeat fires `architecture_scan_complete` after skill audit

## Related Files
- `scripts/skill_indexer.py` — Main indexer script
- `scripts/skill_scanner.py` — Security auditor (SkillSpector)
- `scripts/morning_report.py` — Generates mature keys (find_mature_keys())
- `scripts/auto_boot_scan.py` — Reads morning report cache, proposes top key
- `skills/self-improvement/skill-indexer/` — This skill's umbrella
- `skills/self-improvement/skill-indexer/references/skill-audit-2026-07-26.md` — Security audit details
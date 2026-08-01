---
name: file_ops
description: "Auto-generated from Knowledge Cube (77 entries, domain: file_ops)"
trigger: When the task involves file_ops operations
---

# file_ops: Auto-evolved skill

*Created by Skill Auto-Evolution Engine — 77 entries analysed*

## Extracted patterns

1. CRYSTAL PIPELINE: signals -> patterns -> needs -> proposals -> execute -> SKILL.md. Auto proposals (missing_knowledge, workflow_success) execute immediately. Review proposals (correction_loop, frustration_spike) shown for human.

1. KILL.md created. Lesson: config defaults matter - always check DEFAULT_CONFIG in config.py when diagnosing.

1. large directories is hidden performance killer - always use shutil.disk_usage for disk checks.

1. [suggestion:domain_failure_pattern] High failure rate in domain 'bugfix' (98%). Domain 'bugfix' has a 98% failure rate (1185 failures out of 1203 experiences). Investigate root causes and add safeguards. Actions: Review recent

1. [suggestion:log_tool_error] Log pattern 'tool_error' seen 14 times: read_file. Error type 'tool_error' appeared 14 times in recent logs. Pattern: read_file Actions: Add input validation before tool calls; Implement tool error recove

1. ompt, proc.stdin.write(prompt), proc.stdin.end().
PATTERN: Pre-process file before sending to LLM -- wrap preserve regions in <preserve verbatim='true'> tags. Strip tags from output. Regions: fenced code blocks, safety/warning sections, multi-step se

1. Creative work: Creative work: [pattern] skills/X/references/ directory holds assets read via cat by skill X — not invocable, no frontmatter, clearly scoped to owner

1. Communication pattern: [pattern] Karpathy principle maps to lavra: Think Before Coding → lavra-plan clarification gate; Simplicity+Surgical → lavra-work Phase 2; Goal-Driven → goal-verifier (already exists)

1. Creative work: [pattern] skills/X/references/ directory holds assets read via cat by skill X — not invocable, no frontmatter, clearly scoped to owner

1. correct hardcoded path baked in at install time. Pattern: add .replace() in both convertCommands() and convertSkills() of each converter script.
git add plugins/lavra/commands/lavra-work-ralph.md plugins/lavra/commands/lavra-work-teams.md plugins/la

---
*Generated: 2026-07-12T21:16:53.529356*
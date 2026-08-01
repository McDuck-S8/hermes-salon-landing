---
name: parallel-skill-remediation
description: Batch-fix SkillSpector findings across multiple skills using parallel delegate_task subagents
tags: [skill-audit, security, parallel, delegate_task, remediation]
---

# Parallel Skill Remediation Pattern

## Problem
SkillSpector scans find 50-100+ HIGH/CRITICAL findings across multiple skill categories. Fixing linearly takes hours and blocks the session.

## Solution
Dispatch parallel `delegate_task` subagents — one per skill category — each fixing all findings in their assigned skill tree.

## Execution Template

```python
# 1. Run full audit first
python scripts/skill_scanner.py --format json --output full_audit.json

# 2. Group findings by top-level skill category
# 3. Dispatch 3 concurrent subagents per batch (max_concurrent_children=3)

delegate_task(tasks=[
    {
        "goal": "Fix all findings in devops skill (27 findings). Sanitize PE3_credential_access, AST4_subprocess, P2_hidden_instructions in skills/devops/ and all sub-skills.",
        "role": "leaf"
    },
    {
        "goal": "Fix all findings in automation skill (20 findings). Sanitize telegram-digest, voice-interface, and sub-skills.",
        "role": "leaf"
    },
    {
        "goal": "Fix arbitrage-execution skill (8 findings). Sanitize hermes-deployment-stack reference file.",
        "role": "leaf"
    }
])

# 4. Wait for completion (results re-enter conversation automatically)
# 5. Re-scan to verify
python scripts/skill_scanner.py --skill devops --format json --output verify_devops.json
```

## Subagent Instructions (pass in `context`)

Each subagent receives:
- Skill category name
- Finding types to fix (from audit JSON)
- Sanitization templates: `skills/self-improvement/references/skillspector-sanitization-templates.md`
- Must use `patch` tool for bulk edits
- Must re-scan own skill before finishing

## Finding Type → Sanitization Mapping

| SkillSpector Rule | Template Section | Typical Fix |
|-------------------|------------------|-------------|
| `PE3_credential_access` | 2.4 | Replace `.env`, `OPENCODE_ZEN_API_KEY`, `api_key` with "read from config at runtime" |
| `AST4_subprocess` | 2.2 | Add `# SAFE: explicit args list, no shell, read-only` comment |
| `P2_hidden_instructions` | 2.3 | Remove HTML comments, `[HIDDEN]`, `system: you are` markers |
| `E2_env_harvesting` | 2.4 | Replace `os.environ.get()` with config loader pattern |
| `P6_direct_leakage` | 2.5 | Remove prompt-echoing examples |
| `P3_exfiltration_commands` | 2.6 | Describe data flow without full exfil commands |

## Batch Size & Timing

- Max 3 concurrent (config: `delegation.max_concurrent_children`)
- Each subagent: 2-5 minutes for 10-30 findings
- Full 200+ finding remediation: ~10 minutes (vs 60+ linear)
- Re-scan verification: 30 seconds per skill

## Verification Gate

After all subagents complete:
```bash
# Full re-scan
python scripts/skill_scanner.py --format json --output final_verify.json
# Target: 0 CRITICAL, 0 HIGH across all remediated skills
```

## Anti-Patterns

| Anti-Pattern | Why It Fails |
|--------------|--------------|
| Fix linearly one file at a time | Hours of blocked session |
| Fix only main SKILL.md, ignore sub-skills | 80% findings in `references/`, `scripts/` |
| Don't re-scan | Regressions, missed files |
| Ask user "which skill first?" | User doesn't know; all are critical |

## Related

- `skills/self-improvement/references/skillspector-sanitization-templates.md` — sanitization patterns
- `skills/self-improvement/references/mandatory-boot-sequence.md` — session startup (includes audit)
- `scripts/skill_scanner.py` — SkillSpector scanner
- `scripts/skill_indexer.py` — re-index after fixes
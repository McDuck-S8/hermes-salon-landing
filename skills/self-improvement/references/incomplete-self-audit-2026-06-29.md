# Incomplete Self-Audit — 2026-06-29

## Problem
Self-assessment streamed to user cuts off mid-sentence at Policy 18 of 20. Missing Policies 19-20 (Self-Upgrade Protocol).

## Root Cause
- Streamed directly instead of writing to file first
- No structural validation (all sections present, all bullets closed)

## Fix
**Self-audit protocol:**
1. `execute_code` → build full audit as string → `write_file("cache/self_audit_full.md", content)`
2. Validate structure: all 20 policies covered, each with ✅/⚠️/❌ and evidence
3. Only then summarize in response

## Template for Complete Self-Audit
```markdown
# SELF_AUDIT.md — ЧЕСТНАЯ ОЦЕНКА v{N}
**Дата:** {ISO}
**Модель:** {model}

## Policy Compliance (20/20)
| Policy | Status | Evidence |
|--------|--------|----------|
| 1. Honesty | ✅ | ... |
...
| 20. Self-Upgrade | ❌ | Missing: no skill created for repeated task |

## Strengths (3-5)
## Weaknesses (3-5)
## Vector (Where I'm Going)
```

## Signal to Watch
Response ends without `## Weaknesses` or `## Vector` section → INCOMPLETE. Must have all 4 sections.
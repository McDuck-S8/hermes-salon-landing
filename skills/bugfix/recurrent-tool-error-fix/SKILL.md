---
name: recurrent-tool-error-fix
description: Fix recurring tool errors detected by self-improvement loop — terminal, skill_manage, patch failures
---

# Recurrent Tool Error Fix

## Trigger
Self-improvement loop detected `tool_error` pattern with ≥20 occurrences for any tool.

## Diagnosis

```bash
cd /d/Portable_Soft/hermes
python -c "
import json
with open('cache/improvement_suggestions.json') as f:
    s = json.load(f)
for sug in s.get('suggestions', []):
    if sug.get('severity') == 'critical' and 'tool_error' in sug.get('issue_type',''):
        print(f\"x{sug.get('occurrence_count')} {sug.get('issue_type')}: {sug.get('title')}\")
        print(f\"  {sug.get('description','')[:120]}\")
"
```

## Common causes

1. **terminal tool** (×125): Windows/MSYS encoding issues, long paths, timeout on slow commands
2. **skill_manage** (×55): JSON parsing failures, skill file conflicts
3. **patch** (×32): File encoding mismatches, race conditions on concurrent edits
4. **SQLite "unable to open database"** — missing WAL mode + busy_timeout on concurrent access. Fix: see `devops/database-reliability` skill.

## Fix steps by tool

### terminal errors
- Use `read_file` instead of `cat`/`head`
- Use `search_files` instead of `grep`/`rg`
- Avoid heredoc strings — use `write_file` + `python -c` instead
- Keep command length under 1024 chars
- Set explicit `timeout` for long-running commands

### skill_manage errors
- Always `skill_view()` before `skill_manage()` to confirm skill exists
- Use `patch` mode for small changes, not `edit` with full rewrite
- After `delete`, verify `absorbed_into` target exists
- When getting JSON parse errors, re-fetch with `read_file` on the SKILL.md

### patch errors
- Use `write_file` instead when 3+ patches needed on same file
- After failed patch, re-read file before retrying
- Use `replace_all=true` when old_string appears multiple times

## Verification

After applying fixes, verify improvement:
```bash
python -c "
import json
with open('cache/improvement_suggestions.json') as f:
    s = json.load(f)
pre = sum(1 for x in s['suggestions'] if x.get('issue_type','').startswith('tool_'))
print(f'Previous tool_error suggestions: {pre}')
"
```
Run self_improvement_loop again after 24h and compare.

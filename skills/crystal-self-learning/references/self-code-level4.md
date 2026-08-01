# Level 4 — Self-Code Audit & Self-Modification (2026-06-14)

## Architecture

```
will() step 3.7 ──→ self_code_audit candidate
                           │
                           ▼
              _execute_conscience_action('self_code_audit')
                           │
                    Reads scripts/crystal.py
                    Analyzes: functions, classes, LIMITs
                    Stores → self_model['self_code_audit']
                           │
                           ▼ (next crystal cycle)
              will() step 3.7 reads self_model
              Finds self_code_audit → enters patch generation
                           │
                           ▼
              self_mod_modify_code_lim{X} candidate
              with _mod dict: {type, id, desc, find_text, replace_text}
                           │
                           ▼
              Level 3 dispatcher → _self_execute_modification(mod)
                           │
                    Patches crystal.py: find → replace (ALL occurrences)
                    Re-reads file, updates limits_found
                           │
                           ▼
              _self_evaluate_modification() checks 'PATCHED' in result
              → OK (not "FAIL — unknown type")
```

## Guard Condition (first cycle only)

```python
# In will() step 3.7:
if 'self_code_audit' not in _ca_m:         # CHECK: top-level key in self_model.json
    # add self_code_audit candidate
else:
    # generate patch candidates from _ca['limits_found']
```

**Critical:** check `'self_code_audit' not in _ca_m` (not `in _ca_m.get('self_code_audit', {})`).
The latter checks INSIDE the audit dict (keys: ts, source_lines, functions...) — never matches.

## Patch Generation Logic

For each LIMIT value from the audit:
1. Skip if >= 100 (already "wide enough")
2. Read current crystal.py — if `LIMIT {val}` no longer exists in file, skip (already patched)
3. Create candidate with `_mod` containing `find_text` and `replace_text`
4. `_mod` MUST have `id` and `desc` (line 1642 does `mod['desc']`)

```python
'_mod': {
    'type': 'modify_code',
    'id': 'mod_code_enlarge_limit',
    'desc': f"Увеличить SQL LIMIT {lim_val} -> {max(lim_val*3, 100)}",
    'file_path': 'scripts/crystal.py',
    'find_text': f'LIMIT {lim_val}',
    'replace_text': f'LIMIT {max(lim_val*3, 100)}',
}
```

## The modify_code Handler (in _self_execute_modification)

```python
elif mod_type == 'modify_code':
    full_path = os.path.join(ROOT, mod['file_path'])
    content = open(full_path).read()
    if find_text in content:
        content = content.replace(find_text, replace_text)  # NO `, 1`!
        open(full_path, 'w').write(content)
        result = f"PATCHED {file_path}: {find_text} -> {replace_text}"
        # Re-audit: re-read and update limits_found
        import re as _r
        _new_limits = _r.findall(r'LIMIT\s+(\d+)', content)
        if 'self_code_audit' in self_model:
            self_model['self_code_audit']['limits_found'] = _new_limits
```

## Evaluation (in _self_evaluate_modification)

Must be added alongside the handler:

```python
elif mod_type == "modify_code":
    applied = isinstance(result, str) and 'PATCHED' in result
    eval_result["success"] = applied
    eval_result["detail"] = (str(result)[:100]) if result else '?'
```

Without this: every successful patch reports `FAIL — unknown type`.

## Save Model Bug

`_save_self_model()` (crystal.py ~line 938) overwrites these keys from OLD file data:

```python
for key in ['self_awareness', 'modifications', 'plan', 'mod_evals',
            'heartbeat', 'cycle_count', 'diversity_boost']:
    if key in old_data:
        current[key] = old_data[key]      # ← overwrites with stale data
```

**Impact on Level 4:**
- `self_code_audit` is NOT in this list → survives ✓
- `modifications` IS in this list → new entries lost ✗
- Workaround: read actual file content to check done-state, don't rely on tracked modifications

## Regex Double-Escaping Trap

When writing regex via `patch()` tool, `\\` in the string becomes `\` in the file.

**Correct:** Use single backslash in the patch string:
```python
_new_limits = _re_reload.findall(r'LIMIT\s+(\d+)', _reloaded)
```

**Wrong:** Double-escaped:
```python
_new_limits = _re_reload.findall(r'LIMIT\\\\s+(\\\\d+)', _reloaded)
```

Always verify with:
```python
import ast; ast.parse(open('scripts/crystal.py').read())
```

## Pipeline Timeline (with replace-all fix)

1. **Cycle 1:** Audit runs → stores 19 LIMIT values
2. **Cycle 2:** Patches ALL occurrences of `LIMIT 10 → 100`
3. **Cycle 3:** `LIMIT 10` gone → next value (e.g. `3`) → patches all → re-audits
4. **Cycle 4+:** Repeats: 1, 5, 20, 15... until all < 100 eliminated

After 5 cycles: `LIMIT 100: 12×, LIMIT 10000+: 6×` — all < 100 gone. Crystal reports OK.

## Integration Points (all 5)

When adding/modifying `modify_code` in Level 4, ALL of these must be updated:

| # | Location | What |
|---|----------|------|
| 1 | `_execute_conscience_action` (~l1581) | Handler for `action_type == 'self_code_audit'` |
| 2 | `will()` step 3.7 (~l2052) | Candidate generation (if/else guard) |
| 3 | `_self_execute_modification` (~l1207) | `mod_type == 'modify_code'` branch |
| 4 | `_self_evaluate_modification` (~l1301) | `mod_type == 'modify_code'` evaluation |
| 5 | `_self_modification_plan` (if used) | `code_weakness` → `modify_code` conversion |

## Known Issues (not yet fixed)

- LIMIT patching is sequential by position in file, not prioritised (e.g. the `LIMIT 20` in `_conscience()` should go first but doesn't)
- Longest-function detection (`observe: 172 lines`) generates a self_refactor candidate but no handler exists for that action_id yet
- Re-audit after patch is best-effort: `_save_self_model` may stale other keys

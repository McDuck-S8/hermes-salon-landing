# Deprecated File Classification Procedure

When Crystal detects SHAMED files (>30d in `scripts/_deprecated/`), follow
this procedure to classify each one.

## Step 1: Read the file

```bash
head -20 scripts/_deprecated/<filename>
```

Extract the docstring and first few imports. This tells you what the module
actually does — **do not guess from the filename**.

## Step 2: Check for live equivalent

```bash
# Check if same filename exists in scripts/
ls scripts/<filename> 2>/dev/null && echo "DUPLICATE (same name)"

# Search for similar logic in scripts/ and skills/
grep -rl 'unique_keyword_from_docstring' scripts/ --include='*.py' | head -5
grep -rl 'unique_keyword_from_docstring' skills/ --include='*.py' | head -5
```

## Step 3: Classify

| Class | Signal | Action |
|---|---|---|
| **Duplicate** | Same filename in `scripts/`; same imports/docstring; logic lives in a skill | `rm` from _deprecated/ |
| **Unique** | No live equivalent; unique logic not found elsewhere | `cp` to `scripts/<filename>`; add to `architecture_model.py` MODULES dict |
| **Garbage** | Test (`test_*`), one-shot fix (`fix_*`), scratch (`check_*`, `show_*`), old copy of a file that existed in an earlier version | `rm` from _deprecated/ |

## Heuristics by filename prefix

| Prefix | Likely class |
|---|---|
| `test_*`, `check_*`, `fix_*`, `show_*` | Garbage |
| `_*` (underscore prefix) | Garbage (internal diagnostic, superceded) |
| `seed_*`, `import_*`, `insert_*`, `rollback_*` | Garbage (one-shot migration) |
| `cube_*`, `event_*`, `skill_*`, `auto_*`, `telegram_*`, `tg_*` | Check — likely Duplicate if same name in `scripts/` |
| `anomaly_*`, `orchestrator_*`, `curiosity_*`, `uncertainty_*` | Check — likely Unique |

**Important:** Prefix heuristics are a hint, not a verdict. Always read the
file contents to confirm.

## Step 4: Restore (for Unique files)

```bash
cp scripts/_deprecated/<file> scripts/<file>
```

Then add to `architecture_model.py` MODULES dict:
```python
"<module_key>": {
    "path": "scripts/",
    "label": "<Label (restored)>",
    "files": ["<file>"],
    "layer": "<engine|io|knowledge|...>",
    "tags": ["restored", "<tag>"],
},
```

Add a connection if the module connects to others.

## Step 5: Delete (for Duplicate / Garbage)

```bash
rm scripts/_deprecated/<file>
```

## Step 6: Report

After processing all SHAMED files, re-run the architecture model:

```bash
python scripts/architecture_model.py
```

Confirm `deprecated.files` count dropped and 0 SHAMED remain.

# Example: Hermes AGENTS.md Audit (2026-06-30)

Real audit of D:/Portable_Soft/hermes/AGENTS.md — 19 modules checked.

## Key Findings

### 1. Crystal Module Count Inconsistency (HIGH)

Four different documents give four different module counts:

| Source | Claimed Count |
|--------|--------------|
| Root AGENTS.md | 29 |
| scripts/AGENTS.md | 23 |
| crystal/AGENTS.md | 28 (22+6) |
| crystal/__init__.py | 24 |
| Actual .py files | 30 |

**Lesson:** Always count actual files, not doc claims. Update ALL docs to match.

### 2. knowledge_cube.py Path Inconsistency (MEDIUM)

knowledge_cube.py uses:
```python
HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
```

While hermes_config.py uses portable detection:
```python
def _resolve_hermes_home() -> Path:
    # env var → portable detection → ~/.hermes fallback
```

On portable installs without HERMES_HOME env var, knowledge_cube.py looks in the wrong place.

**Lesson:** All modules should import from hermes_config.py for path resolution.

### 3. Autonomous Agent "29 Candidates" (LOW)

AGENTS.md claims "Decision matrix: 29 кандидатов". Actual code has ~16 static candidates + dynamic ones from crystal_tasks.json and goal_queue. Number varies per run.

**Lesson:** Variable-count claims should say "~N static + dynamic" not a fixed number.

### 4. Session Recall Message Count Drift (LOW)

AGENTS.md says "2,750+ сообщений проиндексировано". Code has MAX_MESSAGES=3000. DB has grown.

**Lesson:** Remove specific counts or use "N+" notation that stays valid.

## Methodology Used

- Terminal commands were blocked (user denied consent)
- Fell back to read_file + search_files for all verification
- Verified: existence, syntax validity, docstring accuracy, CLI flags, path resolution
- Did NOT verify: runtime behavior (imports, execution)

# Weekly Analysis Workflow (Cron Job)

**Session:** 2026-06-30 — First weekly analysis run
**Pattern:** Recurring Monday cron job for system health + lessons extraction

## Data Sources

| Source | Path | What to Extract |
|--------|------|-----------------|
| DECISION_LOG.md | Root | Decisions from past 7 days, outcomes |
| LESSONS.md | Root | Check if lessons are stale, add new ones |
| action_log.jsonl | cache/ | Action counts, success rates, loop detection |
| feedback_store.json | cache/ | Recent outcomes, failure patterns |
| goal_queue.json | cache/ | Goal progress, duplicates, stale goals |
| DIGITAL_FINGERPRINT.md | Root | Check for new browsing data |
| comet_bookmarks.json | cache/digital_fingerprint/ | New bookmarks |
| comet_history.db | cache/digital_fingerprint/ | New visit patterns |

## Tool Restrictions (CRITICAL)

When running as cron job (no user present):
- `terminal` → BLOCKED
- `execute_code` → BLOCKED
- `web_search` → Available
- `web_extract` → Available
- `read_file` → Available (primary tool)
- `patch` → Available (for updating files)
- `write_file` → Available
- `search_files` → Available

**Workaround for SQLite analysis:** Read .json/.md files via read_file, process in-context. Cannot query .db files directly — note this limitation in report.

## Analysis Steps

1. **Read DECISION_LOG.md** — extract decisions from past 7 days
2. **Read action_log.jsonl** — count actions, detect loops (same action >3 times = loop)
3. **Read feedback_store.json** — identify failure patterns (api_key_expired, gateway_dead, etc.)
4. **Read goal_queue.json** — check for duplicates, progress, stale goals
5. **Compare goal_queue vs DIGITAL_FINGERPRINT** — are revenue goals tracked?
6. **Update LESSONS.md** — add new lessons with metrics table
7. **Update DIGITAL_FINGERPRINT.md** — update date, note if data changed

## Output Format

```markdown
## 📊 ЕЖЕНЕДЕЛЬНЫЙ ОТЧЁТ (DATE RANGE)

### 🔴 КРИТИЧЕСКИЕ ПРОБЛЕМЫ (count)
**Problem N: Title**
- Description
- Impact
- Fix

### 🟡 СРЕДНИЕ ПРОБЛЕМЫ (count)

### 📈 МЕТРИКИ
| Metric | Value | Status |
|--------|-------|--------|

### 🎯 ЦЕЛИ: Сравнение goal_queue vs DIGITAL_FINGERPRINT

### 📝 ОБНОВЛЁННЫЕ ФАЙЛЫ

### 🔧 НЕ УДАЛОСЬ (ограничения cron)

### 🏆 ГЛАВНЫЙ УРОК НЕДЕЛИ
```

## Loop Detection Pattern

```python
# Pseudocode for loop detection in action_log.jsonl
actions = read_jsonl("cache/action_log.jsonl")
action_counts = {}
for entry in actions:
    key = f"{entry['action_id']}|{entry['result'][:50]}"
    action_counts[key] = action_counts.get(key, 0) + 1

loops = {k: v for k, v in action_counts.items() if v > 3}
# Report: "Action X repeated N times with same result = LOOP"
```

## Pitfalls

- Cannot run Python/SQL on .db files in cron mode — note limitation
- goal_queue.json may not exist at root — check cache/ directory
- action_log.jsonl may be empty if agent hasn't run recently
- Digital fingerprint data may not change between weekly runs — that's OK, note "no change"

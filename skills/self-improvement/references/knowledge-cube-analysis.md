# Knowledge Cube Analysis Methodology

## Core Principle

**Never dismiss data as garbage.** If entries are unclassified or marked as failures, investigate FIRST:
- What source produced them?
- What format are they in?
- Can they be re-interpreted or re-classified?
- Is the label accurate or misleading?

The "unknown" and "failure" labels in the Cube are often artifacts of the pipeline, not the data itself.

## Analysis Workflow

### Phase 1: Statistics (SQL)

```python
# 1. Total counts by outcome
cur.execute("SELECT axis_outcome, COUNT(*) FROM experiences GROUP BY axis_outcome")

# 2. Unknown by source
cur.execute("SELECT source, COUNT(*) FROM experiences WHERE axis_outcome IN ('unknown','None') GROUP BY source ORDER BY cnt DESC")

# 3. Failure by source  
cur.execute("SELECT source, COUNT(*) FROM experiences WHERE axis_outcome='failure' GROUP BY source ORDER BY cnt DESC")

# 4. Domains overview with success/fail counts
cur.execute("SELECT axis_domain, COUNT(*), SUM(CASE WHEN axis_outcome='success' THEN 1 ELSE 0 END) as ok, SUM(CASE WHEN axis_outcome='failure' THEN 1 ELSE 0 END) as fail FROM experiences GROUP BY axis_domain ORDER BY COUNT(*) DESC LIMIT 30")

# 5. Sample raw content
cur.execute("SELECT id, raw_text FROM experiences WHERE axis_outcome IN ('unknown','None') AND source=? LIMIT 3", (source_name,))
```

### Phase 2: Categorize Sources

Each source tells you what the data actually is:

| Source | What it contains | Value |
|--------|-----------------|-------|
| `state_db` | Raw user conversations | HIGH — real interaction history |
| `skill-indexer` | Skill indexing results | LOW — regenerated each index |
| `latent-domain-detector` | Auto domain detection | MEDIUM — may reveal gaps |
| `dimension_proposals` | Auto-generated dimensions | MEDIUM — review for useful ideas |
| `improvement_suggestions` | Auto-generated proposals (tagged 'failure' but NOT actual errors) | MEDIUM — proposals that weren't accepted |
| `lavra_*` | Lavra knowledge imports | MEDIUM — captured knowledge |
| `log_*` | System logs | LOW-MEDIUM — error patterns |
| `script_*` | One-off script outputs | LOW — single-use |
| `git:*` | Git commit references | LOW |

### Phase 3: LLM Classification

Use Zen API in small batches (3 entries per call):

```python
SYSTEM_PROMPT = """You classify AI agent log entries. For EACH entry:
1. content_type: user_request|system_output|tool_result|error|conversation|system_log
2. domain: what topic/area
3. intent: purpose or goal
4. knowledge_value: high|medium|low
Return JSON array."""
```

**Critical:** The `deepseek-v4-flash-free` model uses `reasoning_content` field.
Always handle this:
```python
msg = resp['choices'][0]['message']
content = msg.get('content', '') or msg.get('reasoning_content', '')
```

Use `max_tokens=4000+` — lower values cause empty content when the model is still reasoning.

Rate limit (429): add `time.sleep(2-3)` between calls.

### Phase 4: Strategic Analysis

After sampling, synthesize:
1. What's the real value in each category?
2. Which can be bulk-updated (change outcome label)?
3. Which can be cleaned (skill-indexer, one-offs)?
4. What caused the buildup? (pipeline gap, not data problem)

### Phase 5: Action Plan

Always produce actionable steps:
1. **Fix misclassifications** — `improvement_suggestions` tagged as 'failure' should be 'proposal_rejected'
2. **Clean noise** — skill-indexer results are regenerated, can be pruned
3. **Process valuable** — state_db conversations, dimension_proposals
4. **Fix pipeline** — update event_evolution to auto-assign outcomes

## Common Pitfalls

- **Assuming "failure" = bad**: improvement_suggestions marked as 'failure' are NOT errors — they're rejected improvement proposals. The label is misleading.
- **Dismissing "unknown"**: Most unknowns are unclassified state_db conversations (real user interactions) — high value.
- **Too many entries = too slow**: Use batch sampling (30-50 entries) + LLM analysis to infer patterns. Don't try to classify 900+ entries individually.
- **Rate limits**: Free Zen API is 429-prone. Keep 3s delays, process in small batches.
- **reasoning_content trap**: deepseek-v4-flash-free puts reasoning in `reasoning_content` and can return empty `content`. Always check both fields.

## Report Template

Keep reports structured:
```
--- 1. Общая статистика ---
--- 2. UNKNOWN: распределение по источникам ---
--- 3. FAILURE: распределение по источникам ---  
--- 4. Домены (ТОП-30) ---
--- 5. Содержимое UNKNOWN (выборка) ---
--- 6. Анализ и рекомендации ---
--- 7. План действий ---
```

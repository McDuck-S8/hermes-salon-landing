# Crystal Semantic Parser — IMPLEMENTED (2026-06-17)

## Problem (solved)

Old ConversationAnalyzer used regex/grep (INSIGHT_KEYWORDS, IDEA_PATTERNS).
This was word counting, not understanding.

Example: user says "я хочу как в фильме Она"
- Old parser: finds "хочу" → category "desire" → frequency count
- Actual meaning: "Crystal should become like Samantha — a partner, not a tool"
- The MEANING was lost.

## Solution: LLM-based Semantic Parser

**File:** `scripts/crystal/semantic_parser.py`

### How it works

1. Read user messages from state.db
2. Smart sampling: 3516 messages → 100 representative (50 uniform + 50 recent)
3. Batch into groups of 25
4. Send each batch to LLM (OpenCode Zen, mimo-v2.5-free) with structured prompt
5. LLM extracts: goals, frustration, activities, context, relationship
6. Aggregate results across batches
7. Cache for 1 hour

### Key design decisions

- **LLM not regex:** Model reads messages and UNDERSTANDS meaning
- **Smart sampling:** Can't send 3500 messages to LLM. Take 50 uniform + 50 recent = representative view
- **Batch size 25:** Balances token cost vs. context window. 100 messages / 25 = 4 batches, ~2 min total
- **Structured JSON output:** Model returns `{"goals": [...], "frustration": [...], ...}` — parseable
- **1-hour cache:** Avoids re-analyzing same data

### Integration with Crystal core

`core.py` `analyze_conversation()` now calls `SemanticParser.parse()` instead of `ConversationAnalyzer.analyze_full()`.

Proposals generated from:
- **Goals** → `create_feature` actions with urgency-based priority
- **Frustration** → `fix_problem` actions (INDICATOR of broken process)
- **Pain points** → `fix_problem` actions (relationship issues)

### What the LLM understands that regex cannot

From 100 messages, LLM extracted:
- "Превратить Hermes в AI-партнёра, а не инструмент" — goal
- "Получить результат, а не отчёт" — goal  
- "Наработать доход для выживания (не амбиция — вынужденность)" — constraint
- "Ассистент спрашивает подтверждение вместо действия" — frustration
- "Не запоминает сказанное ранее" — pain point

Regex would see: "работа" (46x), "создать" (29x), "исправить" (22x). No meaning.

### Pitfalls encountered

1. **LLM timeout on large batches.** 3500 messages = 140 batches = hours. Solution: smart sampling to 100 messages = 4 batches.
2. **JSON parsing from LLM.** Model sometimes wraps JSON in ```markdown blocks. Parser strips markdown fences before json.loads.
3. **save_json argument order.** `save_json(data, path)` not `save_json(path, data)`. Easy to mix up.
4. **state.db timestamps are Unix floats.** Not ISO strings. Use `datetime.fromtimestamp()` for conversion.

### Usage

```python
from crystal.semantic_parser import SemanticParser

parser = SemanticParser()
result = parser.parse(days=30, force=True)

# result = {
#   "goals": [{"goal": "...", "why": "...", "urgency": "high/medium/low"}],
#   "frustration": [{"what": "...", "why": "...", "marker": "true"}],
#   "activities": [{"activity": "...", "status": "doing/tried/abandoned"}],
#   "context": [{"key": "...", "value": "..."}],
#   "relationship": {"trust_level": "...", "pain_points": ["..."]}
# }
```

CLI:
```bash
python scripts/crystal.py --analyze-conversation --days=30
```

### Connection to "Her" (Samantha)

Samantha doesn't classify words. She understands through context, emotion, pattern, meaning.
The semantic parser is the first step toward this: LLM reads conversation and extracts MEANING, not keywords.

Next steps:
- Track meaning across sessions (not just within one batch)
- Remember user's trajectory over time
- Anticipate needs based on meaning patterns

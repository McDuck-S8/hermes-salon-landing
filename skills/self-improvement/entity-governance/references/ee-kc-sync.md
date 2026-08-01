# EE-KC Sync Implementation

## Session 2026-07-23: Fix broken EE-KC connection

### Problem
Entity Engine had 3672 entities, all with mention_count=0. User ('Александр') had 0 mentions. EE was populated by crystal_will extraction pipeline but **no sync pipeline** ever connected EE mentions with KC content.

### Root Cause
Architectural: EE was designed as a data target (entities extracted → inserted), but the **connection between EE and KC** (scan KC → count mentions → update EE) was never implemented. The system looked structurally complete but functionally broken.

### The Fix
Created `scripts/sync_ee_kc_all.py` that:
1. Reads ALL text from all KC tables into memory (9.8MB, ~10M chars)
2. For each entity with `LENGTH(name) >= 3`, counts real mentions via `big_text.count(name_lower)`
3. Batch-updates EE mention_count (executemany, 100 per batch)
4. Creates relationships for known associations (Александр → Hermes Agent)

### Results
- 3310/3672 entities now have real mention counts
- User 'Александр': 0 → 2 mentions (both from YouTube transcript, not user messages)
- 1 relationship created
- Script runtime: ~98 seconds (3672 entities, 10M chars)

### Key Insight: Entity Quality Problem
Top entities by mention count are ALL generic words:
- `known` (41844), `unknown` (41819), `pattern` (32719), `time` (23050)
- Real domain entities (DeepTutor, Bybit, LangGraph) have <100 mentions

This is because entities were extracted from `experiences` table (system logs), not from real knowledge (`kc_entries`). System experiences contain debugging text where generic words dominate.

### Future Work
1. Add EE sync to cron (hourly)
2. Record user messages in KC for proper user identity tracking
3. Use LLM extraction for real entities instead of naive substring matching
4. Gate entity types - skip generic 'Концепция' entities for mention counting

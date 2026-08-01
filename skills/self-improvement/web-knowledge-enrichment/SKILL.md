---
name: web-knowledge-enrichment
description: >-
  Event-driven web enrichment for knowledge systems. Implements the "Web Pass"
  pattern from Google knowledge-catalog: when new knowledge enters the system,
  web_search confirms/contradicts it and updates confidence scores. Uses a
  file-based queue bridge because web_search is only available as a direct
  agent tool, not from Python execute_code/terminal context.
---

# Web Knowledge Enrichment

Class-level skill for enriching knowledge entries with web search data.
Based on the Google knowledge-catalog "Web Pass" pattern, adapted for
Hermes' event-driven architecture.

## Architecture

```
knowledge_added event
     ↓
on_knowledge_added() — lightweight handler
     ↓
write_enrichment_tasks() → pending_enrichment.json (queue)
     ↓
enrich_next_pending() ← web_search (direct tool call)
     ↓
enrich_concept() → update_confidence() in DB
     ↓
mark_enrichment_done() → queue updated
```

Key insight: **web_search is unavailable from Python execute_code/terminal**
due to SSL/Tavily sandbox restrictions. The solution is not to fix the tool
but to **bridge the gap with a file-based queue**:
- Event handler is lightweight (writes JSON, ~10ms)
- Consumer runs as direct agent tool calls
- Multiple pending tasks can accumulate and be processed in batch

## When to Use

- You need to **verify** knowledge entries with current web data
- A domain/category has concepts with confidence < 1.0
- User asks "проверь эти концепты в интернете"
- User adds new knowledge → enrichment should fire immediately
- User says "cron раз в неделю — это не жизнь, делай по событию"
  (prefer event-driven over scheduled polling)

## Procedure

### 1. Define the enrichment pipeline

```python
# In the event handler (lightweight — writes queue):
from okf_enrichment import write_enrichment_tasks
tasks_written = write_enrichment_tasks(domain, concepts)
```

```python
# Consumer (called with direct web_search results):
from okf_enrichment import enrich_next_pending
web_data = {"web": [...]}  # from web_search tool
result = enrich_next_pending(web_data)
```

### 2. Search query construction

Russian concepts need English search queries. The enrichment uses:
- A `RU_EN_KEYWORDS` mapping (Russian phrases → English)
- Concept tags (filtering out noise like "level-1", "white-spot")
- Year suffix "2026" for recency
- Fallback domain-based queries for unmapped terms

### 3. Classification and confidence delta

| Condition | Delta | Use Case |
|-----------|-------|----------|
| 3+ supporting sources | +0.15 | Strongly confirmed |
| 1-2 supporting sources | +0.05–0.10 | Partially confirmed |
| Contradicting sources | -0.05 to -0.20 | Needs review |
| No relevant results | 0.00 | Stay as-is |

### 4. Conflict recording

When web search contradicts existing knowledge:
1. Record conflict entry in `knowledge/okf/conflicts/`
2. Lower confidence by -0.05 to -0.20
3. Include contradicting source URLs
4. Suggest: review, update, or remove the concept

### 5. Batch processing

When processing a whole domain:

```python
# Agent-side loop:
for concept_pending in get_pending_enrichments():
    web_data = web_search(concept_pending["query"], limit=3)
    result = enrich_next_pending(web_data)
    log(f"{result['title'][:40]}: {result['old_confidence']:.2f} → {result['new_confidence']:.2f}")
```

## Implementation

The implementation lives in `scripts/okf_enrichment.py`:

| Function | Role | Context |
|----------|------|---------|
| `get_domain_concepts(domain)` | Fetch concepts from kc_entries | Any Python |
| `get_experience_concepts(domain)` | Fetch from experiences table | Any Python |
| `build_en_query(concept)` | Russian → English query builder | Any Python |
| `classify_search_results(web_results)` | Classify supporting/contradicting | Any Python |
| `update_confidence(id, delta, reason)` | Write to DB | Any Python |
| `record_conflict(id, title, domain, ...)` | Create conflict MD file | Any Python |
| `enrich_concept(concept, web_data)` | Full enrichment of one concept | Any Python |
| `write_enrichment_tasks(domain, concepts)` | Write queue (event handler) | Any Python |
| `get_pending_enrichments(domain, limit)` | Read queue | Any Python |
| `enrich_next_pending(web_data)` | Consume queue (agent tool loop) | Agent context |
| `mark_enrichment_done(task_id, delta)` | Mark done in queue | Any Python |

## Integration with okf_navigator

`on_knowledge_added()` in `scripts/okf_navigator.py` already does:
1. Domain analysis (maturity, expiration)
2. Writes enrichment tasks to queue
3. Cooldown management (6h per domain)

No need to call web_search from the handler itself — the queue handles the async bridge.

## Gap-Patch: Targeted Knowledge Verification & Cleanup

Gap-patch is the **planned-maintenance counterpart** to event-driven enrichment.
Where enrichment fires when *new* knowledge arrives, gap-patch scans *existing*
knowledge for weak spots and fixes them.

### When to Use

- User says "режим тишины и уборки" / "gap-patch" / "приведи бандл в порядок"
- You produced inconsistent or unverified findings earlier and need to close the loop
- A session exposed knowledge gaps (unchecked URLs, contradictory KYC claims, "needs verification" notes)
- Before proposing any new action that depends on unverified premises

### Three-Bucket Classification

Every existing knowledge record goes into one of three buckets:

| Bucket | Criteria | Action |
|--------|----------|--------|
| **GARBAGE** | No source; >60 days never verified; marked outdated/stale; duplicates | DELETE from DB |
| **HYPOTHESIS** | Has source but unverified; has potential but no numbers; awaits user action | confidence=0.2, tag `#requires-action`, note what to verify |
| **VERIFY NOW** | Past expiration_date and verification_method != 'manual'; blocks other knowledge | Verify immediately, update confidence + verification_method |

### Verification Method Tags

When you verify a record, classify *how* you verified:

| Method | When | Confidence |
|--------|------|------------|
| `official_docs` | Source is the platform's own help/kb (help.wallet.tg, official API docs) | 1.0 |
| `direct_check` | You personally opened the URL / ran the tool and saw the result | 0.95 |
| `cross_referenced` | 2+ independent sources agree on the claim | 0.85–0.95 |
| `manual` | Default — you read it somewhere or deduced it, no fresh check | 0.2–0.7 |

### Gap-Patch Procedure

See `references/gap-patch-methodology.md` for the full step-by-step recipe.

**High-level flow:**
1. **INVENTORY** — Query the cube: low confidence, white spots, past expiration, missing source
2. **CLASSIFY** — Each suspect record into garbage / hypothesis / verify-now
3. **CLOSE** — For each verify-now item: get the official source, run a direct check, or cross-reference. DO NOT use forum hearsay (Reddit, Telegram rumors) as primary sources — official docs and direct checks win.
4. **REPORT** — Show before/after numbers: total records, average confidence, white spots count, verification_method distribution. No new schemes, no new proposals.

**Critical rule:** When user has rejected entire categories of knowledge (e.g. "no CPA"), do NOT delete those records — they contain source data. Either:
- Lower confidence to 0.2 and tag `#rejected-by-user`
- Keep as hypothesis (has source, has potential, but user opted out)

### Research Template (user preference, for any verification involving income schemes)

When the user demands deep research, present in this exact format:
1. **ТОЧКА ВХОДА** — exact URLs opened/checked
2. **КОНКРЕТНЫЕ ЦИФРЫ** — numbers with sources
3. **ВЫВОД ДЕНЕГ** — step-by-step with barriers identified
4. **ВЫВОД** — honest verdict with barriers listed (no hiding problems)

If a site is blocked or returns 403, say so explicitly — don't guess.

## Pitfalls

### DO NOT
- Call `web_search` from `on_knowledge_added` directly — it fails from Python
- Use cron for enrichment when event-driven works — user prefers events
- Enrich every concept blindly — skip concepts with confidence already ≥ 0.97
- Let the queue grow unbounded — process pending items promptly
- Record "no results" as contradictions — only record actual contradicting evidence
- **Delete unprompted** — even garbage records need user sign-off before DELETE
- **Use forum hearsay as primary verification** — official docs and direct checks win
- **Propose new schemes during gap-patch** — the output is a numeric status, not a plan

### DO
- Keep the event handler lightweight (queue write, no web calls)
- Batch web_search calls 3 at a time when processing a queue
- Verify confidence caps at 1.0 (the update function clamps automatically)
- Save conflict files when strong contradictions are found
- Re-run domain analysis after batch enrichment to show updated stats
- When Python DB access is blocked, use `sqlite3` directly via terminal — it can INSERT/UPDATE/SELECT the Knowledge Cube
- Mark `verification_method` explicitly on every record you touch
- End every gap-patch pass with a numeric report (was → now), in the same message as the work

## References

- See `references/enrichment-queue-pattern.md` for the queue architecture details
- See `references/gap-patch-methodology.md` for the full gap-patch recipe with SQL queries and worked examples
- Google knowledge-catalog "Web Pass": toolbox/enrichment/ + okf/src/reference_agent/
- `scripts/okf_enrichment.py` — implementation module
- `scripts/okf_navigator.py` — event handler that triggers enrichment

## Related Skills

- **okf-navigator** — (in scripts/) domain maturity monitoring, not a skill yet
- **self-research** — proactive internet research, overlaps for initial knowledge gathering
- **event-driven-self-healing** — event-driven patterns for system health
- **white-spot-explorer** — explores underpopulated domains; gap-patch is the fix pass after exploration
- **self-improvement** — general protocols; gap-patch is a specific self-improvement sub-pattern

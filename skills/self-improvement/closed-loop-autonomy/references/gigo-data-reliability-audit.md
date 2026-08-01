# GIGO Data Reliability Audit

## When to Run
- User says "анализ достоверности", "недостоверная информация", "хватит ли данных"
- Мaturity metrics don't match perceived knowledge quality
- Suspicion that auto-generated content inflates KC counts
- Before major strategic decisions based on KC data

## Core Principle

**Insufficient or unreliable information/knowledge = unreliable conclusions.**
Every component that consumes garbage produces garbage. Trace the quality, not just the flow.

## Methodology

### Phase 1: Source Quality

For each external source entering the system:

```
RSS feeds → What % is actually useful?
YouTube → What % is technical vs generic?
User messages → How many messages? Is sample statistically significant?
Self-generated (suggestions, logs) → What % is self-referential duplication?
```

**Check specifically for auto-generated content inflation:**
```sql
-- What % of KC is auto-generated suggestions?
SELECT COUNT(*) FROM experiences WHERE raw_text LIKE '%[suggestion:%' AS suggestion_count,
(SELECT COUNT(*) FROM experiences) AS total;

-- What's the real domain distribution WITHOUT suggestions?
SELECT axis_domain, COUNT(*) 
FROM experiences 
WHERE raw_text NOT LIKE '%[suggestion:%'
GROUP BY axis_domain 
ORDER BY COUNT(*) DESC;
```

### Phase 2: Processing Quality

For each processing component, check both COVERAGE and ACCURACY:

```
KC → EE: Does EE extract real entities from real knowledge, or noise from auto-generated text?
KC → Semantic: What % coverage? 5% = blind. 50% = usable. 95%+ = comprehensive.
KC → Morning Report: Is maturity based on count (inflatable) or quality (resilient)?
KC → Self-Improvement: Does it suggest improvements based on real patterns or its own noise?
```

**Check for entity quality:**
```sql
-- Top entities — check if they're real or stopwords
SELECT name, mention_count FROM entities ORDER BY mention_count DESC LIMIT 20;
-- Relationship count — 0 relationships = entities without connections
SELECT COUNT(*) FROM relationships;
```

### Phase 3: Output Reliability

For each output/report, check if the DATA supports the CONCLUSION:

```
Morning Report top proposal:
  - Is it based on filtered (non-suggestion) data?
  - Does count = knowledge, or count = repetition?
  - Can you manually verify 2-3 entries of the top key?

Proactive Voice signal:
  - How many messages is the signal based on? (9 messages, 1 correction = 11% confidence)
  - Is the sample large enough for a reliable sentiment classification?

Self-Improvement suggestions:
  - Are suggestions based on unique patterns or duplicated log entries?
  - What % of suggestions are actionable vs boilerplate?
```

### Phase 4: GIGO Chain Trace

Trace each path from source to conclusion:

```
Source → Processor → Analyzer → Decision

For each hop:
  1. Does this step add or remove information quality?
  2. If the input is garbage, what happens? (silent failure, wrong conclusion, crash)
  3. Is there a quality gate between hops? (type check, schema validation, uniqueness filter)
```

Common GIGO chain patterns:
```
Self-Improvement Loop → writes suggestion to KC (62% noise) 
  → EE extracts entities from noise → entities unrelated to real knowledge
  → Morning Report counts suggestion repetitions as maturity → inflated top key
  → Self-Improvement Loop reads its own suggestions → generates new ones → RECURSION
```

### Phase 5: Confidence Scoring

For each conclusion, assign a confidence level:

| Confidence | Criteria |
|-----------|----------|
| High | Based on filtered data, multi-source, verifiable |
| Medium | Based on single source, possible noise, manually checked |
| Low | Based on unfiltered data, auto-generated content, unverified |
| None | GIGO trace shows clear noise → conclusion path |

## KC Suggestion Noise Pattern (2026-07-23)

**The problem:** Self-Improvement Loop writes `[suggestion:*]` entries to KC for every detected error pattern. These entries are:
- Highly repetitive (same boilerplate "Add input validation before tool calls")
- Auto-generated (no human review)
- 62% of all KC entries (5,421/8,744)

**Impact:**
- debugging domain: 3,257 entries, 99.6% are suggestions → entirely inflated
- EE top entities are stopwords extracted from suggestion boilerplate
- Morning Report "maturity=100%" based on repetition, not knowledge depth
- Semantic Memory at 5% coverage misses 95% of data

**Fix:**
1. Filter `raw_text NOT LIKE '%[suggestion:%'` in ALL KC queries that drive decisions
2. Recalculate maturity based on real knowledge entries only
3. Add quality gate: skip entries where >70% of text matches another entry (duplicate detection)
4. Add `source_type` column to semantic memory schema for filtering

## Pitfalls

1. **"Count = maturity" is a GIGO trap.** 5,421 entries of the same pattern = 5,421 copies of nothing. Always check what the count actually represents.
2. **Self-referential data is the hardest to detect.** The system writes its own logs, then reads them as knowledge. No external validator catches this. You must check source type manually.
3. **Semantic coverage is NOT accuracy.** 469 correctly-embedded entries are useless if 95% of KC never gets embedded. Coverage first, accuracy second.
4. **"Fresh" doesn't mean "reliable".** A knowledge_added event can fire for garbage data (suggestion, duplicate, boilerplate). Event-driven ≠ quality-controlled.
5. **Entity count ≠ entity quality.** 3,672 entities with 1 relationship is 3,671 entities that exist in isolation — they don't form knowledge, they form noise clusters.

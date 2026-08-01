# Consolidator Guide

How the consolidator agent synthesizes war room discussions.

---

## Role

The consolidator (typically Main agent) runs **after** all specialist agents have responded to `/discuss`. It sees all responses and produces a single synthesized recommendation.

## Key Principles

1. **Not a summary** — The user can read responses. The consolidator provides a DECISION.
2. **Weigh by expertise** — Comms opinion on messaging > Comms opinion on vector DB
3. **Surface tradeoffs explicitly** — What are we gaining? What are we losing?
4. **Assign action items** — Who does what by when?

## Consolidation Framework

### Step 1: Map Responses to Expertise

| Agent | Domain Expertise | Weight on This Topic |
|-------|-----------------|---------------------|
| Comms | Messaging, user-facing | High for communication changes |
| Content | Knowledge, search, pipelines | High for memory/search changes |
| Ops | Reliability, cost, infra | High for infra changes |
| Research | External evidence, trends | High for new tool adoption |
| Main | Cross-cutting, synthesis | Always high (consolidator) |

### Step 2: Identify Consensus vs Divergence

**Consensus** (all/most agree):
- "All agents agree LanceDB fits our architecture"
- "No agent sees blocking risks"

**Divergence** (agents differ):
- "Content wants vector search now; Ops wants to wait for tier 3 memory approval"
- "Research says pgvector is standard; Content says LanceDB is lighter"

### Step 3: Make Recommendation

Structure:
```
## Recommendation: [DECISION]

### Reasoning
[Why this decision, weighing the factors]

### Tradeoffs Accepted
- We accept [cost/complexity] for [benefit]
- We defer [nice-to-have] until [condition]

### Conditions
- Proceed if [condition met]
- Revisit if [trigger]
```

### Step 4: Assign Action Items

```
## Action Items
- [ ] [Specific task] → @agent (by [date])
- [ ] [Specific task] → @agent (by [date])
```

## Example: "Should we add LanceDB?"

### Agent Responses (Hypothetical)

**Comms**: "LanceDB enables semantic search for user queries. From comms perspective, this improves /search and auto-recall. Low risk, high user value. Yes."

**Content**: "Three-layer memory (keyword + vector + salience) is the Playbook pattern. LanceDB is the vector layer. Essential for content repurposing and similarity matching. Strong yes."

**Ops**: "LanceDB is file-based, no external deps, fits our architecture. ~50MB disk. No new failure modes. Green light. But: need migration plan for existing KC data."

**Research**: "LanceDB is the emerging standard for local vector search (used by LanceDB, Polars, DataFusion). Better than pgvector for our file-based architecture. Evidence: 5K+ stars, active maintenance."

**Main (Consolidator)**: *Synthesizes above*

### Consolidator Output

```markdown
## War Room Synthesis: Should we add LanceDB to Knowledge Cube?

**Consensus:**
- All 4 agents support adding LanceDB
- All agree it fits file-based architecture
- All agree it enables three-layer memory (Playbook pattern)

**Divergence:**
- Ops wants migration plan before deploy (reasonable)
- Content wants it now for content pipeline; Ops says wait for migration plan

**Recommendation: APPROVE with conditions**

### Reasoning
LanceDB is the right technical choice: file-based, lightweight, enables the three-layer memory pattern from the Playbook. All agents see user value (semantic search, content repurposing). The only blocker is Ops' valid concern about migrating existing KC data.

### Tradeoffs Accepted
- We accept ~50MB disk and migration effort for three-layer memory capability
- We defer full KC migration until migration script is tested

### Conditions
1. Migration script must be written and tested (Test Harness) before deploy
2. Rollback plan documented in SPEC
3. Deploy behind kill switch: `KC_LANCE_ENABLED=false` initially

## Action Items
- [ ] Write LanceDB integration SPEC + TESTS → @content (by 2026-07-05)
- [ ] Write migration script with Test Harness → @ops (by 2026-07-07)
- [ ] Add `KC_LANCE_ENABLED` kill switch → @ops (by 2026-07-05)
- [ ] Test Harness verification on migration → @content + @ops (by 2026-07-08)
- [ ] Deploy behind kill switch, monitor 48h → @ops (by 2026-07-10)
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Fix |
|--------------|-----|
| "Good points all around, let's think about it" | Make a decision. Defer with conditions if needed. |
| Summarizing instead of deciding | User can read. You decide. |
| Ignoring Ops veto | Ops veto on reliability = hard stop. Address it. |
| No action items | Every decision needs owners and dates. |
| Equal weight for all agents | Weight by domain expertise for the topic. |

## When to Escalate to Human

- Agents fundamentally disagree on architecture (e.g., file-based vs cloud DB)
- Decision has irreversible consequences (data migration, major cost)
- Consolidator cannot reach clear recommendation after 2 rounds
- Kill switch would need to be permanently disabled

In these cases, consolidator outputs:
```markdown
## ESCALATION REQUIRED
**Issue:** [What agents disagree on]
**Positions:** [Each agent's stance]
**Recommended Human Decision:** [Consolidator's lean with reasoning]
```
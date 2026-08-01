# Knowledge Cube & Crystal — Real Architecture

Generated: 2026-07-18
Updated: 2026-07-18 (added user_voice, chain-heartbeat, 8-angle schema)

---

## Knowledge Cube — cache/knowledge_cube.db (13 MB)

### experiences (~5000 rows)

| Field | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| ts | TEXT NOT NULL | Timestamp |
| content | TEXT NOT NULL | Experience text |
| raw_text | TEXT NOT NULL | Original text |
| hash | TEXT UNIQUE NOT NULL | SHA256[:16] — dedup |
| axis_time_hour | INTEGER | Hour (0-23) |
| axis_time_dow | INTEGER | Day of week (0=Mon) |
| axis_domain | TEXT | Domain classification |
| axis_outcome | TEXT | failure/success/unknown/indexed |
| **dynamic_axes** | **TEXT** | **8-angle structured JSON (see below)** |
| is_white_spot | INTEGER | 1 = white spot |
| white_spot_cluster_id | TEXT | Cluster reference |
| source | TEXT | Origin (see sources below) |
| confidence | REAL | Reliability |
| tags | TEXT | JSON array |
| importance | REAL | 0-10 |
| verification_method | TEXT | How verified |

### 8-Angle Schema (`dynamic_axes`)

Every entry now has structured dynamic_axes with these 8 fields:

| Angle | Field | Values | Answers |
|---|---|---|---|
| Суть | `essence` | error_fix, pattern, user_feedback, research, skill_usage, skill_failure, architecture, metric, decision, lesson | What is this? |
| Источник | `origin` | string | Where from? |
| Время | `temporal` | during_task, post_session, scheduled_scan, real_time | When in cycle? |
| Уверенность | `confidence` | verified, pattern, observed, speculated, user_confirmed | How sure? |
| Ценность | `value` | critical, high, medium, low, noise | How important? |
| Применимость | `applicability` | now, needs_context, reference, future, expired | When to use? |
| Действие | `action` | apply_fix, create_skill, update_doc, investigate, alert_user, ignore, record_only | What next? |
| Связи | `related` | list of IDs | What connects? |

### Data Sources

| Source | Count | Description |
|---|---|---|
| improvement_suggestions | 2467 | Auto-generated from error patterns |
| skill-indexer | 796 | Skill metadata |
| **user_voice** | **431** | **User messages: frustration, commands, corrections** |
| white-spot-explorer | 157 | White spot analysis |
| cube_analysis | 112 | KC self-analysis |
| agent_decisions | 104 | Agent decision logs |
| dimension_proposals | 71 | Dimension suggestions |
| self_improvement_loop | 63 | Loop cycle results |
| lavra_decision | 61 | Lavra agent decisions |
| log_agent | 50 | Agent log entries |

### Other Tables

- dimensions (5): time_hour, time_dow, domain, outcome, error_category
- white_spot_clusters (45): pending=20, researched=23, developing=2
- knowledge_cube_fts: FTS5 fulltext index
- kc_entries (419): tools=211, issues=70, external=60

---

## User Voice — scripts/user_voice_ingester.py

Extracts user signals from session DB → KC.

### Signal Detection

- **Frustration**: говно, мусор, плохо, сломал, не работает, garbage, broken, terrible
- **Commands**: сделай, почини, запусти, добавь, fix, build, create, deploy
- **Corrections**: нет, не так, поправь, change, instead, undo, revert

### Stats (first run)

- 431 entries ingested from 5,451 user messages
- Frustration: 93 | Commands: 364 | Corrections: 90
- Crystal now sees user_voice as 3rd largest orphan source

### Usage

```python
from user_voice_ingester import ingest_user_voice
result = ingest_user_voice(limit=500)
# { ingested: 44, frustration: 4, commands: 42, corrections: 13 }
```

---

## verified_fixes — cache/verified_fixes.db (112 KB)

55 rows. issue_hash UNIQUE for dedup. Schema: see architecture doc v1.

---

## Crystal — scripts/crystal.py (3177 lines)

4-phase self-awareness cycle:

```
Phase 1: observe()      — Snapshot of all 4 cubes
Phase 2: diagnose(snap) — What's broken, growing, dying
Phase 3: will(snap,diag)— Decisions (deterministic algorithm, no LLM)
Phase 4: record(...)    — Write back to KC
```

Databases read: KC, entity_engine, fler_engine, fabric
**NOW READS: user_voice entries via orphan_sources** ← NEW

---

## Chain Heartbeat — scripts/chain_heartbeat.py

### Chain topology
```
signal_scanner → event_bus → self_improvement → suggestion_consumer → crystal
```

### Rules

1. Each link checks upstream neighbor. No signal >30s → alert.
2. Each link sends heartbeat downstream every 10s.
3. Crystal (end) sends heartbeat upstream. If Crystal silent → consumer alarm.

### Fault detection demo

```
✓ signal_scanner    upstream=True
✓ event_bus         upstream=True

--- signal_scanner dies ---

✓ signal_scanner
✗ event_bus         upstream=False  ⚠ UPSTREAM 'signal_scanner' NEVER BEAT
✓ self_improvement  upstream=True
✓ suggestion_consumer upstream=True
✓ crystal           upstream=True

--- crystal dies ---

✗ crystal           ⚠ Crystal NEVER BEAT — chain endpoint dead
```

### State: cache/chain_heartbeat.json

---

## Data Flow (updated)

```
Session DB (139K messages)
    │
    ▼
user_voice_ingester.py ──► KC (source='user_voice', 8-angle axes)
    │
    ▼
Crystal reads orphan_sources → sees user_voice (3rd largest)
    │
    ▼
Chain heartbeat monitors:
signal_scanner → event_bus → self_improvement → consumer → crystal
    (each checks upstream, alerts on silence)
```

---

## Metrics (2026-07-18)

- KC total: ~5000 entries (4583 + 431 user_voice + new)
- 8-angle coverage: 100%
- user_voice: 431 entries (frustration=41, commands=364, corrections=90)
- Conversion: 0.13% → 0.15% (improving)
- Skills created: 24 total, 5 new this session
- Chain heartbeat: operational

# Universal Information Events — Deep Dive

## Architecture

```
UniversalEventMonitor
  │
  ├─ record(event) → event_id
  │     └─ stores any information as event
  │
  ├─ search(query) → list[events]
  │     └─ FTS5 search over events
  │
  ├─ get_high_impact(min_impact) → list[events]
  │     └─ high-impact events
  │
  └─ get_recent(hours) → list[events]
        └─ recent events

SystemAdapter
  │
  ├─ process_event(event) → result
  │     └─ assess impact + adapt
  │
  └─ _assess_and_adapt(event, event_id) → adaptations
        └─ determine what to adapt
```

## InformationEvent

```python
@dataclass
class InformationEvent:
    content: str          # Any information
    source: str           # Where it came from
    category: str         # knowledge/insight/decision/error/pattern/integration
    novelty: float        # 0-1, how new
    importance: float     # 0-1, how important
    relevance: float      # 0-1, how relevant to goals
```

## Impact Scoring

```
impact = novelty*0.4 + importance*0.4 + relevance*0.2
```

- novelty: how new is this? (0=known, 1=completely new)
- importance: how important? (0=trivial, 1=critical)
- relevance: how relevant to current goals? (0=off-topic, 1=core)

## Adaptation Rules

| Condition | Adaptation |
|-----------|------------|
| High novelty | capture_knowledge |
| High importance | update_strategies |
| High relevance | adjust_goals |
| error category | investigate_error |
| decision category | validate_decision |
| pattern category | generalize_pattern |

## Database Schema

### universal_events
- id: INTEGER PRIMARY KEY
- content: TEXT NOT NULL
- source: TEXT
- timestamp: TEXT
- tags: TEXT (JSON)
- context: TEXT (JSON)
- novelty: REAL
- importance: REAL
- relevance: REAL
- category: TEXT
- domain: TEXT
- impact_score: REAL
- processed: INTEGER (0/1)
- adapted: INTEGER (0/1)

### adaptations
- id: INTEGER PRIMARY KEY
- event_id: INTEGER
- adaptation_type: TEXT
- description: TEXT
- timestamp: TEXT
- success: INTEGER (0/1)

### events_fts
- FTS5 virtual table for searching

## Usage Examples

### Emit any information
```python
from scripts.universal_events import emit_information

result = emit_information(
    "New API config",
    category="knowledge",
    novelty=0.8,
    importance=0.6,
    relevance=0.7
)
# {"event_id": 1, "impact_score": 0.70, "adaptations": ["captured_knowledge"]}
```

### Emit with type helpers
```python
from scripts.universal_events import emit_knowledge, emit_insight, emit_decision

emit_knowledge("New API config", tags=["api", "config"])
emit_insight("Event-driven > schedule", tags=["philosophy"])
emit_decision("Use universal events", tags=["architecture"])
```

### Search events
```python
monitor = UniversalEventMonitor()
results = monitor.search("knowledge")
# [{"content": "...", "impact_score": 0.70, ...}]
```

### Get high-impact events
```python
high_impact = monitor.get_high_impact(min_impact=0.7)
```

## Integration with Other Systems

### Knowledge Capture
- High novelty → capture_knowledge() → knowledge.jsonl
- auto_recall() → finds it next session

### Event-Driven Evolution
- emit_event() → EventMonitor.record() → triggers
- Universal events extend the trigger set

### Autopoietic System
- Information fed → emit_information() → system adapts
- Knowledge gaps → discover_gap() → seek_information()

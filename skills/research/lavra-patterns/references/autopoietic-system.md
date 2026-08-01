# Autopoietic System — Deep Dive

## Architecture

```
AutopoieticSystem
  │
  ├─ discover_gap() → KnowledgeGap
  │     └─ knows what it doesn't know
  │
  ├─ seek_information() → queries
  │     └─ searches to learn
  │
  ├─ feed_information() → InformationMeal
  │     └─ feeds the system
  │
  ├─ learn_from_meal() → learning
  │     └─ learns from food
  │
  ├─ analyze_gaps() → stats
  │     └─ analyzes progress
  │
  ├─ get_hunger() → list[gaps]
  │     └─ what it wants to learn
  │
  └─ search_meals() → list[meals]
        └─ what it already found
```

## The Loop

```
    ┌─────────────────────────────────────┐
    │                                     │
    ▼                                     │
 Знание ──→ Незнание ──→ Поиск ──→ Учёба ─┘
    │                                     ▲
    └─────────────────────────────────────┘
              Самосозидание
```

## Database Schema

### knowledge_gaps
- id: INTEGER PRIMARY KEY
- topic: TEXT NOT NULL
- domain: TEXT
- importance: REAL (0-1)
- discovered_at: TEXT
- search_queries: TEXT (JSON)
- found_info: TEXT (JSON)
- filled: INTEGER (0/1)

### information_meals
- id: INTEGER PRIMARY KEY
- content: TEXT NOT NULL
- source: TEXT
- quality: REAL (0-1)
- relevance: REAL (0-1)
- gaps_filled: TEXT (JSON)
- timestamp: TEXT

### learning_events
- id: INTEGER PRIMARY KEY
- event_type: TEXT
- description: TEXT
- impact: REAL
- timestamp: TEXT

## Usage Examples

### Discover a gap
```python
gap = system.discover_gap(
    "How to optimize self-evolution",
    domain="ai",
    importance=0.8
)
```

### Seek information
```python
queries = system.seek_information(
    gap.id,
    ["self-evolution optimization", "LLM cost reduction"]
)
```

### Feed information
```python
meal = system.feed_information(
    "Use smaller models for evaluation, larger for generation",
    source="research",
    quality=0.8,
    relevance=0.9,
    gap_id=gap.id
)
```

### Learn from meal
```python
learning = system.learn_from_meal(meal.id)
```

### Check hunger
```python
hunger = system.get_hunger()
# [{"topic": "How to optimize...", "domain": "ai", "importance": 0.8}]
```

### Analyze progress
```python
stats = system.analyze_gaps()
# {"total_gaps": 3, "filled": 2, "unfilled": 1, "fill_rate": 0.67}
```

## Integration with Other Systems

### Knowledge Cube
- Gap discovery → analyze white spots in cube
- Meal feeding → add to cube as experience
- Learning → update cube dimensions

### Lavra Knowledge
- Gap → search knowledge.jsonl for similar
- Meal → capture_knowledge() writes to knowledge.jsonl
- Learning → auto_recall() finds it next session

### Event-Driven Evolution
- Gap discovered → emit_event("gap_discovered")
- Information fed → emit_event("information_fed")
- Learning complete → emit_event("learning_complete")

# Universal Information Events — Quick Reference

## Core Principle
Every piece of information IS an event that changes the system.

## Impact Scoring (NOW IN event_patterns.py)
impact = novelty*0.4 + importance*0.4 + relevance*0.2

## Key Functions (INTEGRATED INTO event_patterns.py)
- calculate_impact(novelty, importance, relevance) → float
- record_impact(event_type, novelty, importance, relevance) → float
- suggest_action(context) → dict — proactive action suggestion
- learn_pattern(pattern_type, pattern_data, confidence) → None
- check_chain_loop(chain_id, event_type) → bool — loop detection
- record_chain_event(chain_id, event_type, depth, visited_types) → None

## Files (INTEGRATED)
- scripts/event_patterns.py — EventPatterns (all patterns in one place)
- scripts/core_engine.py — CoreEngine (connects to real data)
- cache/core_engine.db — impacts + actions + patterns + chains

## Integration
- Knowledge Cube → search_real_data() → finds relevant records
- Lavra Knowledge → search_real_data() → finds relevant entries
- Session Database → connected for future use

## Usage
```python
from scripts.event_patterns import EventPatterns

patterns = EventPatterns()

# Impact scoring
impact = patterns.calculate_impact(0.8, 0.9, 0.7)  # → 0.82
patterns.record_impact("knowledge_captured", 0.8, 0.9, 0.7)

# Proactive actions
action = patterns.suggest_action({"type": "gap_found", "topic": "creative"})
# → {"type": "search", "description": "Search for: creative", "priority": 7}

# Pattern learning
patterns.learn_pattern("work_time", {"hour": 14, "activity": "coding"}, 0.8)

# Loop detection
patterns.record_chain_event("chain1", "knowledge_captured", 1, ["knowledge_captured"])
loop = patterns.check_chain_loop("chain1", "knowledge_captured")  # → True
```

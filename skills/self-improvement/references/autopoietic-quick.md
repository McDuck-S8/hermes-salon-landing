# Autopoietic System — Quick Reference

## The Loop
1. Gap discovered → knows what it doesn't know
2. Information seeking → searches to learn
3. Information fed → feeds the system
4. Learning complete → extracts knowledge
5. System grows → knows what else it doesn't know
6. Infinite loop → self-creation through information

## Key Methods (NOW IN core_engine.py)
- find_real_gaps() → list[dict] — finds REAL gaps from Knowledge Cube and Lavra
- search_real_data(query) → list[dict] — searches REAL data sources
- run_chain("gap_analysis") → list[dict] — runs chain reaction on REAL data
- deliver_benefit(type, description, impact) → None — records REAL benefit

## Files (INTEGRATED)
- scripts/core_engine.py — CoreEngine (all-in-one, connects to real data)
- scripts/event_patterns.py — EventPatterns (impact scoring, proactive actions, loop detection)
- scripts/integration.py — Integration (connects all systems)
- cache/core_engine.db — gaps + searches + benefits + impacts + patterns + chains

## Integration
- Knowledge Cube (619 experiences) → find_real_gaps()
- Lavra Knowledge (154 entries) → search_real_data()
- Session Database (18671 messages) → connected but not actively used yet

## Verification
```python
from scripts.core_engine import CoreEngine
engine = CoreEngine()
status = engine.get_system_status()
print(f"Knowledge Cube: {status['knowledge_cube']['count']} records")
print(f"Lavra: {status['lavra']['count']} records")
```

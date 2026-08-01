---
name: three_layer_memory
description: "Three-layer memory compression for Knowledge Cube: raw experiences → thematic summaries → compressed cross-domain patterns. Implements Clarence's memory architecture from 'On Becoming'."
trigger: "On schedule (daily 03:00), on KC growth events, on 'compress_memory' command"
usage: three_layer_memory
---

# Three-Layer Memory Compression

Implements the **raw → thematic → compressed** pipeline for Knowledge Cube.

## Architecture

```
Layer 1: Raw (experiences table)
    ↓ compress_raw_to_thematic()
Layer 2: Thematic (memory_thematic table)
    ↓ compress_thematic_to_compressed()
Layer 3: Compressed (memory_compressed table)
```

## Tables Created

| Table | Purpose |
|---|---|
| `memory_thematic` | Domain/theme summaries with source experience IDs |
| `memory_compressed` | Cross-domain distilled patterns/rules |
| `compression_log` | Audit trail of compressions |

## Pipeline

### Layer 1: Raw → Thematic
Groups experiences by (domain, outcome), creates summaries with source IDs.

```python
from memory.three_layer_memory import ThreeLayerMemory
memory = ThreeLayerMemory()
memory.compress_raw_to_thematic(domain="devops", days_back=7)
```

### Layer 2: Thematic → Compressed
Groups themes across domains, extracts reusable patterns.

```python
memory.compress_thematic_to_compressed(domain="devops")
```

### Full Pipeline
```python
result = memory.run_full_compression(domain="devops")
# Returns: thematic_created, compressed_created, details
```

## Pattern Types (Compressed Layer)

| Type | Trigger | Use Case |
|---|---|---|
| `anti-pattern` | theme contains "error"/"fail" | Prevent recurrence |
| `rule` | theme contains "fix"/"guard" | Enforce as guard |
| `heuristic` | theme contains "how"/"pattern" | Guide decisions |
| `principle` | default | Cross-domain insight |

## Verification

```bash
# Run full compression
python -c "from memory.three_layer_memory import compress_memory; import json; print(json.dumps(compress_memory(), ensure_ascii=False, indent=2))"
```

## Integration with Crystal

- Runs as part of Nocturnal Cognition (nightly)
- Feeds compressed patterns into Crystal's Priority Engine
- Anti-patterns → Risk Assessment module
- Rules → Development Proposer as guard suggestions

---

**Created:** 2026-07-30
**Version:** 1.0
**Author:** Hermes Agent
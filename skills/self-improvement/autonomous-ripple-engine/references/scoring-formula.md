# Stone Scoring Formula

Complete differentiated scoring math for `Stone` class in `ripple_engine.py`.

## Inputs (from raw data)

```python
raw_data = {
    "title": str,
    "content_summary": str,
    "url": str,
    "aspects": List[str],
    "conflicts": List[str],
    "gaps": List[str],
    "new_keys_generated": List[str],
    "key_strength": int,          # 0-100
    "confidence": float|int,      # 0-1 or 0-100
    "roi_estimate": str,
    "actionable": bool|str,       # bool or "true"/"false"
    "reason": str
}
```

## Normalization

```python
# Confidence: handle 0-1 vs 0-100
raw_conf = raw_data.get("confidence", 50)
raw_confidence = raw_conf * 100 if isinstance(raw_conf, float) and raw_conf <= 1 else raw_conf

# Actionable: handle bool vs string
raw_act = raw_data.get("actionable", False)
raw_actionable = raw_act if isinstance(raw_act, bool) else (str(raw_act).lower() == "true")
```

## Key Strength (10-100)

```python
base = raw_strength  # 0-100 from source

# Boost for content richness
aspect_boost = min(len(aspects) * 3, 15)
key_boost = min(len(new_keys) * 5, 20)

# Penalties
conflict_penalty = len(conflicts) * 5
gap_penalty = len([g for g in gaps if g != "no_critical_gaps"]) * 3

score = base + aspect_boost + key_boost - conflict_penalty - gap_penalty
return max(10, min(100, score))
```

## Confidence (15-100)

```python
base = raw_confidence  # normalized 0-100

# Boosts
if raw_actionable:
    base += 10
specific_keys = [k for k in new_keys if k != "general_knowledge" and not k.startswith("general_")]
base += len(specific_keys) * 3

# Penalties
gap_count = len([g for g in gaps if g not in ("no_critical_gaps", "none_identified")])
base -= gap_count * 4
base -= len(conflicts) * 5

return max(15, min(100, base))
```

## Priority Tier

```python
if key_strength >= 85 and confidence >= 85:
    return "critical"
elif key_strength >= 75 and confidence >= 75:
    return "high"
elif key_strength >= 60 or confidence >= 60:
    return "medium"
return "low"
```

## Visual Weight (for card sizing)

```python
visual_weight = int((key_strength + confidence) / 2)  # 10-100
```

## Actionability

```python
actionable = (
    key_strength >= 70 and
    confidence >= 75 and
    len(conflicts) == 0
)
# Note: raw_actionable from source is IGNORED - recomputed from computed scores
```

## ROI Estimate

```python
combo = (key_strength + confidence) / 2
if actionable and combo >= 80:
    return "Very High — Direct revenue path, ready to execute"
elif combo >= 75:
    return "High — Strong signal, needs validation"
elif combo >= 60:
    return "Medium — Promising, requires research"
elif combo >= 45:
    return "Low — Weak signal, monitor only"
return "Negligible — Noise"
```

## Reason Generation

```python
parts = []
if aspects:
    parts.append(f"Aspects: {', '.join(aspects[:3])}")
if new_keys:
    specific = [k for k in new_keys if k != "general_knowledge"]
    if specific:
        parts.append(f"Keys: {', '.join(specific[:3])}")
if conflicts:
    parts.append(f"⚠ Conflicts: {len(conflicts)}")
if gaps:
    real_gaps = [g for g in gaps if g not in ("no_critical_gaps", "none_identified")]
    if real_gaps:
        parts.append(f"Gaps: {len(real_gaps)}")
return " | ".join(parts) if parts else "Generic content"
```

## Edge Cases Handled

| Edge Case | Handling |
|-----------|----------|
| `confidence` = 0.95 (float) | Normalized to 95 |
| `actionable` = "false" (string) | Normalized to `False` |
| `aspects` = ["general_knowledge"] | Treated as 1 aspect |
| `new_keys` = [] | Falls back to ["general_knowledge"] |
| `conflicts` = ["none_identified"] | Treated as empty list |
| `gaps` = ["no_critical_gaps"] | Treated as empty for penalties |
| `key_strength` missing | Defaults to 50 |

---

## Mature Key Detection

### Convergence Gate (all must pass)

```
supporting_stones >= 2
avg_strength >= 65
avg_confidence >= 55
```

### Aggregated Metrics

```
avg_strength = sum(stone.key_strength) / count
avg_confidence = sum(stone.confidence) / count
actionable_ratio = actionable_count / count  # for display only, not gating
```

### Persistence (KC)

```sql
INSERT OR IGNORE INTO kc_entries
(id, content, tags, source, category, importance, created_at, confidence)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
```

- `category` = "mature_key"
- `tags` = ["mature_key", "unlocked", *aspects*]
- `importance` = avg_strength / 100
- `confidence` = avg_confidence / 100
- `source` = "ripple_engine"
- Hash for deduplication: SHA256("mature_key:{key}:{unlocked_at}")[:12]

---

## Design Tokens (from ui-ux-pro-max)

### Priority Tier → Gradient

```css
--card-critical: linear-gradient(135deg, #DC2626 0%, #991B1B 100%);
--card-high:     linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%);
--card-medium:   linear-gradient(135deg, #1E3A5F 0%, #1E4A7F 100%);
--card-low:      linear-gradient(135deg, #1F2937 0%, #111827 100%);
```

### Priority Tier → Glow

```css
--glow-critical: 0 0 32px rgba(220, 38, 38, 0.35);
--glow-high:     0 0 28px rgba(139, 92, 246, 0.3);
--glow-medium:   0 0 20px rgba(14, 165, 233, 0.25);
--glow-low:      0 0 12px rgba(100, 116, 139, 0.15);
```
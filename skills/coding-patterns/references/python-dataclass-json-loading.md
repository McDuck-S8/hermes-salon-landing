# Robust JSON-to-Dataclass Loading

When loading JSON into a Python `@dataclass`, the source JSON often has extra fields that the dataclass doesn't define. The naive `cls(**item)` raises `TypeError: __init__() got an unexpected keyword argument 'X'`.

## Fix: Filter by `__dataclass_fields__`

```python
valid_fields = set(cls.__dataclass_fields__.keys())
return [cls(**{k: v for k, v in item.items() if k in valid_fields}) for item in data]
```

This silently drops unknown keys instead of crashing. The dataclass gets only the fields it knows about — all others are ignored.

## When to Apply

Anywhere JSON is loaded into a dataclass and the JSON schema may have drifted:
- Loading stored state files (knowledge bases, caches, serialized configs)
- API responses mapped to local models
- Multi-version data where new fields were added to JSON but the dataclass wasn't updated

## Example: Crystal's `load_json`

```python
# Before (crash on extra fields):
return [cls(**item) for item in data]

# After (resilient):
valid_fields = set(cls.__dataclass_fields__.keys())
return [cls(**{k: v for k, v in item.items() if k in valid_fields}) for item in data]
```

## Related

- `@dataclass` has no built-in `__post_init__` for unknown fields
- For strict mode (reject unknown fields), validate keys explicitly before construction

# Crystal Debugging Quick Reference

## If "всё сделано" (everything done)

```python
import json
m = json.load(open('cache/self_model.json'))
m['sovest']['studied'] = m['sovest']['studied'][-5:]
json.dump(m, open('cache/self_model.json', 'w'), indent=2, ensure_ascii=False)
```

## If output = input (same action every cycle)

Check studied filter:
```python
import json
m = json.load(open('cache/self_model.json'))
print(f"studied: {len(m.get('sovest', {}).get('studied', []))}")
```

If studied approaches total domains → clear oldest 5.

## If SQL error "no such column"

KC columns: raw_text (NOT content), axis_domain (NOT domain), axis_outcome (NOT outcome).

## If candidates=0 in will()

Check LEARNING_TO_ACTION mapping matches conscience output:
```python
from crystal import _conscience, _load_will_history, _load_self_model, observe
snap = observe()
h = _load_will_history()
m = _load_self_model(snap)
cr = _conscience('test', 'test', {'type': 'test', 'efficiency': 0}, m)
print(f"learning: {cr.get('learning_direction', [])}")
```

## If observe() timeout

Run via CLI, not import:
```bash
python scripts/crystal.py --iterative 1
```

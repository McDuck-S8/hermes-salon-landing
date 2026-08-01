# Event Chaining — How Events Trigger Events

## The Problem

Events were isolated. Each event happened in its own bubble.
No chain reactions. No self-sustaining cycles.

## The Solution

Events form CHAINS:
```
Event A → triggers Event B → triggers Event C → loops back to A
```

## Real Chain Examples

### Chain 1: Error Resolution
```
error_detected
  → investigation_started
    → solution_found
      → solution_validated
        → knowledge_captured
```

### Chain 2: Knowledge Gap Filling
```
white_spot_detected
  → search_initiated
    → information_fed
      → knowledge_learned
        → gap_analyzed
```

### Chain 3: Task Completion
```
task_complete
  → knowledge_captured
    → learning_applied
      → task_prepared
```

## Loop Detection

Track visited event types per chain:
```python
if event_type in chain.visited_types:
    return None  # Already processed — STOP
chain.visited_types.add(event_type)
```

## Depth Limit

Hard stop at max_depth=5:
```python
if chain.depth >= chain.max_depth:
    return None  # Too deep — STOP
```

## Implementation

```python
class EventChain:
    def emit(self, event_type, data=None, parent_id=None, chain_id=None):
        # Loop detection
        if event_type in chain.visited_types:
            return None
        
        # Depth limit
        if chain.depth >= chain.max_depth:
            return None
        
        # Mark as visited
        chain.visited_types.add(event_type)
        chain.depth += 1
        
        # Execute handler
        result = handler(event)
        
        # Chain to next event
        if result and 'next_event' in result:
            self.emit(result['next_event'], ...)
```

## Key Insight

Without loop detection → infinite recursion.
Without depth limit → stack overflow.
With both → controlled chain reactions that terminate.

# Persistence System Reference — Session 2026-07-28

## Overview
Complete state persistence with 3-version checkpointing, auto-save/load, rollback capability. Implements DIRECTIVE 0x16 (PERSISTENT_STATE_CHECKPOINTING).

## Architecture

### StatePersistenceManager (`scripts/state_persistence.py`)

#### Core Components
```python
class StatePersistenceManager:
    """Manages complete agent state persistence with checkpointing"""
    
    # Configuration
    MAX_CHECKPOINTS = 3
    AUTO_SAVE_INTERVAL = 30  # seconds
    SIGNIFICANT_ACTIONS_THRESHOLD = 5
    
    # Component registration
    def register_component(name, saver_fn, loader_fn):
        """Register component with save/load callbacks"""
    
    def mark_dirty(component_name):
        """Mark component as changed, trigger auto-save check"""
    
    def save_checkpoint(force=False) -> checkpoint_id:
        """Save current state as new checkpoint, rotate old"""
    
    def load_latest_checkpoint() -> bool:
        """Load most recent checkpoint on session start"""
    
    def rollback(checkpoint_id=None) -> bool:
        """Rollback to specific checkpoint (or latest)"""
    
    def get_checkpoint_history() -> List[Dict]:
        """List all available checkpoints with metadata"""
```

### ComponentName Enum
```python
class ComponentName(Enum):
    AGENT_STATE = "agent_state"        # Mode, active tasks, context
    TACTICAL_BUFFER = "tactical_buffer" # Hypotheses, TTL, confidence
    STRATEGIC_DB = "strategic_db"       # Global patterns, versions, usage
    FEEDBACK_STORE = "feedback_store"   # Action history, success rates
    DIRECTIVES = "directives"           # 0x0E, 0x11, 0x14, etc.
    ONTOLOGY = "ontology"               # User knowledge, env, tools
    ACTIVE_GOALS = "active_goals"       # Current tasks, progress, subtasks
    DIALOG_HISTORY = "dialog_history"   # Key moments, decisions, context
```

### Checkpoint Format
```json
{
  "metadata": {
    "checkpoint_id": "checkpoint_20260728_224531_264",
    "timestamp": "2026-07-28T22:45:31.264535",
    "version": 1,
    "components_saved": [...],
    "action_count": 7,
    "session_id": "integration_test_001"
  },
  "tactical_buffer": {...},
  "strategic_db": {...},
  "feedback_store": {...},
  "directives": {...},
  "ontology": {...},
  "active_goals": {...},
  "dialog_history": {...}
}
```

## Integration Functions

### Component Savers/Loaders
```python
def create_tactical_buffer_saver(buffer) -> Callable:
    """Returns saver that serializes all hypotheses to JSON"""

def create_tactical_buffer_loader(buffer) -> Callable:
    """Returns loader that deserializes hypotheses back to buffer"""

def create_strategic_db_saver(db) -> Callable:
    """Serializes patterns + archive"""

def create_strategic_db_loader(db) -> Callable:
    """Deserializes patterns + archive"""

def create_feedback_store_saver(store) -> Callable:
    """Serializes executions, gaps, conflicts (enums → strings)"""

def create_feedback_store_loader(store) -> Callable:
    """Deserializes with enum restoration"""
```

### Factory Function
```python
def create_persistence_manager(session_id=None):
    """Create and configure complete persistence manager with all 8 components"""
    mgr = StatePersistenceManager(session_id)
    
    # Register all autonomy components
    mgr.register_component(ComponentName.TACTICAL_BUFFER, tb_saver, tb_loader)
    mgr.register_component(ComponentName.STRATEGIC_DB, sd_saver, sd_loader)
    mgr.register_component(ComponentName.FEEDBACK_STORE, fs_saver, fs_loader)
    mgr.register_component(ComponentName.DIRECTIVES, dir_saver, dir_loader)
    mgr.register_component(ComponentName.ONTOLOGY, ont_saver, ont_loader)
    mgr.register_component(ComponentName.ACTIVE_GOALS, goals_saver, goals_loader)
    mgr.register_component(ComponentName.DIALOG_HISTORY, dlg_saver, dlg_loader)
    mgr.register_component(ComponentName.AGENT_STATE, state_saver, state_loader)
    
    return mgr
```

## Test Results

### Integration Test: Full Save/Load Cycle
```
✅ Checkpoint saved: checkpoint_20260728_223121_471 (6 components)
✅ Checkpoint saved: checkpoint_20260728_223259_057 (1 component)
✅ Checkpoint saved: checkpoint_20260728_224106_131 (7 components)

=== SIMULATING NEW SESSION ===
✅ Loading checkpoint: checkpoint_20260728_224106_131
  ✓ Restored: TACTICAL_BUFFER
  ✓ Restored: STRATEGIC_DB
  ✓ Restored: FEEDBACK_STORE
  ✓ Restored: DIRECTIVES
  ✓ Restored: ONTOLOGY
  ✓ Restored: ACTIVE_GOALS
  ✓ Restored: DIALOG_HISTORY

=== RESTORED COMPONENTS ===
  TACTICAL_BUFFER: 18 hypotheses
  STRATEGIC_DB: 1 patterns
  FEEDBACK_STORE: 1 executions
  DIRECTIVES: 11 entries
  ONTOLOGY: 3 entries
  ACTIVE_GOALS: 4 goals
  DIALOG_HISTORY: 2 moments, 2 decisions
```

### Rollback Test
```
✅ Rollback to checkpoint_20260728_223121_471: SUCCESS
✅ State reverted to previous version
```

### Auto-Save Trigger
```
✅ After 5 mark_dirty() calls: auto-save triggered
✅ After 30 seconds without save: auto-save triggered
```

## Checkpoint Storage
- Location: `cache/state_persistence/checkpoints/checkpoint_*.json`
- Metadata index: `cache/state_persistence/metadata.json`
- Max 3 checkpoints (rotating)

## Known Issues
1. `FeedbackStore` enum serialization requires custom `_enum_to_str` helper
2. `StrategicDatabase` pattern loader needs `StrategicPattern` class imported
3. No compression for large checkpoints (future: gzip)
4. No incremental checkpointing (full state each time)

## Files
- `scripts/state_persistence.py` — Main implementation
- `scripts/test_full_persistence.py` — Integration test
- `scripts/persistence_integration_test.py` — Earlier test version
- `cache/state_persistence/checkpoints/*.json` — Checkpoints
- `cache/state_persistence/metadata.json` — Checkpoint index
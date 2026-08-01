# Auto-Trigger Setup

## Cron Job
Dream-memory runs daily at 3:00 via Hermes cron:
```
job_id: 74382ce129b9
name: dream-memory-consolidation
schedule: 0 3 * * *
```

## Manual Run
```bash
python /d/Portable_Soft/hermes/skills/self-improvement/dream-memory/scripts/dream_memory.py \
  --memory-root /d/Portable_Soft/hermes/data/dream-memory --recent 7
```

## Memory Tree Structure
```
data/dream-memory/
  MEMORY.md          # Index file (< 200 lines)
  free-apis.md       # Topic: FreeQwenApi + FreeDeepseekAPI
  skills.md          # Topic: Installed skills
  system.md          # Topic: System configuration
  logs/              # System logs (empty initially)
  sessions/          # Consolidated session excerpts (empty initially)
```

## Integration with Hermes Memory
- **Hermes memory tool**: user/memory targets (current session prefs)
- **Lavra knowledge**: JSONL format in `data/lavra-memory/` (separate system)
- **Dream memory**: Markdown format in `data/dream-memory/` (this skill)

These three memory systems serve different purposes and should NOT be merged.

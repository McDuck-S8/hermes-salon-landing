# Subagent Batching Pattern — YouTube Research

## Problem
YouTube research via subagents times out at 600s (10 min) when processing >5 queries. BrowserClaw navigation + extraction is too slow.

## Solution: Parallel Subagent Batching with yt-dlp

### Core Pattern
```python
# OLD (browser-based, timed out at 600s+)
# 9 queries × 3 videos = 27 browser navigations + waits + extraction = 600s+

# NEW (Agent Reach / yt-dlp, ~60s total)
import subprocess, json

queries = [...]  # 9 queries

# Split into batches of 3, run 3 parallel subagents
batches = [queries[i:i+3] for i in range(0, len(queries), 3)]

for batch in batches:
    # Launch subagent per batch (parallel)
    delegate_task(
        goal=f"Process {len(batch)} YouTube queries via yt-dlp",
        context={"queries": batch, "timeout_per_query": 60}
    )
```

### Subagent Task Template
```python
# Each subagent processes ≤5 queries with explicit timeouts
queries = batch  # ≤5 queries

for q in queries:
    # Search: 60s timeout
    result = subprocess.run(
        ['yt-dlp', f'ytsearch3:{q}', '--dump-json',
         '--print', 'id,title,channel,view_count,description,url'],
        capture_output=True, text=True, timeout=60
    )
    for line in result.stdout.strip().split('\n'):
        if line:
            all_results.append(json.loads(line))

# Batch extract subtitles for top videos (parallel)
for v in top_videos:
    subprocess.run(['yt-dlp', '--write-auto-subs', '--sub-langs', 'en,ru',
                   '--skip-download', f'https://youtu.be/{v["id"]}'], timeout=120)
```

### Key Rules
1. **Max 5 queries per subagent** — prevents timeout
2. **60s timeout per query** — hard limit, kill if exceeded
3. **Parallel subagents** — split N queries into ceil(N/5) subagents
4. **Fallback chain** — if yt-dlp fails: curl + v2rayN proxy + oembed → HTML regex → yt-dlp in 3.11 venv
5. **Heartbeat monitoring** — if subagent silent > 2 cycles → restart
6. **Max 10 items per subagent** — hard limit

### Timeout Configuration
| Operation | Timeout |
|-----------|---------|
| yt-dlp search (3 results) | 60s |
| yt-dlp subtitles (en,ru) | 120s |
| yt-dlp description print | 30s |
| curl + v2rayN proxy | 20s |
| curl oembed | 10s |

### Integration Point
In `external_import.py` → `process_video_batch()` method.
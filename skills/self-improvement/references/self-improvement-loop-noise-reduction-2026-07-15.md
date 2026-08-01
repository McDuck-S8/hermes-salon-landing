# Self-Improvement Loop: Noise Reduction (2026-07-15)

## Problem
`self_improvement_loop.py` (daily 5am) was generating **446 suggestions** (17 critical, 19 high, 409 medium, 1 low) per run. 409 "medium" were single-occurrence log error clusters — pure noise.

Over 25 runs, **17,441 total suggestions** were generated, most duplicates across days.

## Root Causes

### 1. No Error Type Classification
All httpx/httpcore/network/telegram/provider errors fell into "unknown" category.
- httpx.ConnectError, httpcore.ReadError, NetworkError → all "unknown" (147 occurrences)
- Fixed: `_classify_error_type()` function with 6+ subtypes

### 2. No Minimum Threshold
Every log error cluster turned into a suggestion, even clusters with count=1.
- 409 of 446 suggestions were from clusters with count < 3
- Fixed: skip log clusters with `count < 3` (not recurring patterns)

### 3. No Cross-Run Deduplication
Each run regenerated the same suggestions from scratch.
- Fixed: `load_previous_suggestions()` loads previous output JSON, skips same `id`

## The Fix (3 commits to `self_improvement_loop.py`)

### Commit 1 — `_classify_error_type()` function
```
httpx/* → network_httpx, network_connect, network_read, network_timeout, network_remote_closed, network_status
httpcore/* → network_httpcore, network_connect, network_read, network_timeout, network_remote_closed
connecterror/connectionerror → network_connect
telegram.*error → telegram_network, telegram_updater, telegram_conflict, telegram_error
openai/badrequest → api_provider
429/rate limit → api_rate_limit
403/forbidden → api_forbidden
500/502/503 → api_server_error
"-> documented pattern:" → log_artifact
```

### Commit 2 — dedup + noise filter in `generate_suggestions()`
- Added `load_previous_suggestions() → set[str]` of previously-seen IDs
- `generate_suggestions()` accepts `seen_ids` param, skips duplicates
- Log clusters with `count < 3` are skipped entirely

### Commit 3 — `main()` passes `seen_ids` to `generate_suggestions()`

## Before/After
- **Before:** 446 suggestions (C:17, H:19, M:409, L:1)
- **After:** 47 suggestions (C:16, H:18, M:12, L:1)
- **Next run:** further reduced by dedup (same IDs detected)

## Lessons
- Always classify errors by their root cause library (httpx vs httpcore vs telegram)
- "1 occurrence in 48h" is not a pattern — minimum threshold (3+) prevents noise
- Cross-run dedup prevents unbounded accumulation
- The metrics file tracks cumulative counts; the actual output should be current only

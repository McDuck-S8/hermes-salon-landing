# hermes_start.py Boot Pipeline & Cron Fixes — 2026-06-29

**Version:** 2026-06-29
**Source:** Live session boot verification + cron job analysis

---

## Boot Pipeline (14 Steps Verified)

### Step-by-Step Execution

| Step | Component | Duration | Status | Output |
|------|-----------|----------|--------|--------|
| 0 | BOOT_SEQUENCE load | <1s | ✅ | 5427 chars loaded |
| 0.5 | MEMORY.md health | <1s | ⚠️→✅ | 8 lines → auto-restored to 17 from backup |
| 0.6 | AUTO-REPAIR scan | <1s | ✅ | All departments operational |
| 1 | Session dumps | <1s | ✅ | 2 new ingested (61 total) |
| 2 | Conversation content | ~1s | ✅ | 28 KC entries from 2 convos |
| 3 | Classify KC entries | <1s | ✅ | All classified |
| 4 | Evaluate goals | ~6s | ✅ | 3 active, 2 new created |
| 5 | Sync memory graph | <1s | ✅ | 907 entities, 986 relations |
| 6 | Build session context | ~1s | ✅ | 1523 chars |
| 6a | Load tool catalog | <1s | ✅ | 19234 chars |
| 6b | Scan user needs | ~3s | ✅ | 20 needs (0 unmet) |
| 6c | Check knowledge graph | <1s | ✅ | 2002 nodes, 5296 edges |
| 7 | Check error backlog | <1s | ✅ | 7 recent errors |
| 8 | Load context files | <1s | ✅ | DECISION_LOG, ALERTS, SELF_AUDIT, agent_policies |
| 9 | Reality Gate | ~10s | ⚠️ | ALL_GREEN (false positive — see below) |
| 10 | Session manifest | <1s | ❌ | `session_manifest.py` missing |
| 11 | Autonomous first action | <1s | ✅ | Executed `corrective-wf-daily-maintenance-1` |
| 12 | Start signal daemon | <1s | ✅ | Daemon started |
| 13 | Emit boot_completed | <1s | ✅ | Triggers 2 cron jobs |

**Total time:** ~17 seconds

---

## Known Failures & Required Fixes

### 1. CRITICAL: cube_feeder.py DB Schema (Blocks KC Growth)

**Job:** `cube-feeder` (id: 6f45a65ca529) — runs daily at 04:15
**Error:**
```
sqlite3.IntegrityError: NOT NULL constraint failed: experiences.content
  File "scripts/cube_feeder.py", line 420, in feed_entries
    result = kc.add_experience(...)
  File "scripts/knowledge_cube.py", line 120, in add_experience
    conn.execute("INSERT INTO experiences (ts,raw_text,hash,axis_time_hour,axis_time_dow,axis_domain,axis_outcome,dynamic_axes,is_white_spot,source,tags) VALUES (?,?,?,?,?,?,?,?,?,?,?)")
```

**Root cause:** `kc.add_experience()` called without `content` parameter. Table schema requires `content NOT NULL`.

**Fix options (pick one):**

**Option A: Fix feeder to provide content**
```python
# In cube_feeder.py feed_entries()
result = kc.add_experience(
    text=text,
    content=text,  # ADD THIS — use text as content
    domain=domain,
    outcome=outcome,
    ...
)
```

**Option B: Alter DB schema (make content nullable)**
```sql
-- Run once
ALTER TABLE experiences ALTER COLUMN content DROP NOT NULL;
-- Or recreate table with content nullable
```

**Option C: Default content from text in knowledge_cube.py**
```python
# In add_experience(), before INSERT
if content is None:
    content = text
```

**Recommended:** Option A — minimal change, explicit.

---

### 2. HIGH: Rate Limits on Free APIs (2 Cron Jobs Failing)

**Job 1:** `telegram-monitor` (id: 2f8449cdfeef) — every 360m (6 hours)
**Job 2:** `self-upgrade-loop` (id: 56517647333d) — every 720m (12 hours)

**Error:** `RuntimeError: HTTP 429: Rate limit exceeded. Please try again later.`

**Root cause:** Free tier API quotas exhausted (opencode-zen / mimo-v2.5-free)

**Fix: Add exponential backoff + provider rotation**

```python
# Add to telegram_cron_monitor.py and self_upgrade_check.py
import time
import random

API_PROVIDERS = [
    {"name": "opencode-zen", "model": "mimo-v2.5-free", "base_url": "https://api.opencode-zen.com"},
    {"name": "groq", "model": "llama-3.3-70b", "base_url": "https://api.groq.com"},
    {"name": "deepseek", "model": "deepseek-chat", "base_url": "https://api.deepseek.com"},
    {"name": "openrouter", "model": "deepseek/deepseek-chat", "base_url": "https://openrouter.ai/api/v1"},
]

def call_with_fallback(prompt, max_retries=3):
    for provider in API_PROVIDERS:
        for attempt in range(max_retries):
            try:
                # Call provider API
                return result
            except Exception as e:
                if "429" in str(e) or "rate limit" in str(e).lower():
                    if attempt < max_retries - 1:
                        delay = 2 ** attempt + random.uniform(0, 1)
                        time.sleep(delay)
                        continue
                break  # Try next provider
    raise RuntimeError("All providers exhausted")
```

---

### 3. MEDIUM: Reality Gate False Positive

**Symptom:** `VERDICT: ALL_GREEN` despite cube_feeder cron errors

**Root cause:** `scripts/reality_gate.py` checks file mtime, not DB integrity or cron health

**Fix: Update reality_gate.py checks**

```python
# In reality_gate.py verify_system()
checks = [
    # Existing: file mtime checks
    # ADD THESE:
    ("KC DB integrity", check_kc_db_integrity),
    ("Cron job health", check_cron_jobs_healthy),
    ("Gateway process", check_gateway_alive),
]

def check_kc_db_integrity():
    import sqlite3
    conn = sqlite3.connect("cache/knowledge_cube.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM experiences")
    count = c.fetchone()[0]
    conn.close()
    return count > 1000, f"Experiences: {count}"

def check_cron_jobs_healthy():
    import json
    with open("cron/jobs.json") as f:
        jobs = json.load(f)["jobs"]
    failed = [j for j in jobs if j.get("last_status") == "error"]
    return len(failed) == 0, f"Failed jobs: {len(failed)}"

def check_gateway_alive():
    # Check gateway process
    import subprocess
    result = subprocess.run(["hermes", "gateway", "list"], capture_output=True, text=True)
    return "PID" in result.stdout, result.stdout[:200]
```

---

### 4. LOW: session_manifest.py Missing (Boot Step 10)

**Error:** `Manifest verification error: [Errno 2] No such file or directory: '...\\session_manifest.py'`

**Fix options:**

**Option A: Create minimal script**
```python
# scripts/session_manifest.py
import json
from pathlib import Path

def verify_session_manifest():
    """Verify session state files exist and are valid."""
    required = [
        "cache/session_context.json",
        "cache/goal_queue.json",
        "cache/user_needs.json",
    ]
    results = {}
    for f in required:
        p = Path(f)
        results[f] = p.exists() and p.stat().st_size > 0
    return all(results.values()), results

if __name__ == "__main__":
    ok, details = verify_session_manifest()
    print(f"Session manifest: {'OK' if ok else 'FAIL'}")
    for k, v in details.items():
        print(f"  {k}: {'✅' if v else '❌'}")
    exit(0 if ok else 1)
```

**Option B: Remove check from boot** — if not critical

**Recommended:** Option A — adds real verification.

---

## Cron Job Health Summary (From jobs.json)

| Job ID | Name | Schedule | Last Status | Consecutive Errors | Action |
|--------|------|----------|-------------|-------------------|--------|
| 6f45a65ca529 | cube-feeder | 15 4 * * * | **error** | N/A | Fix DB schema (CRITICAL) |
| 9863ba0ec81f | self-improvement-loop | 0 5 * * * | ok | 0 | — |
| e98b02224e28 | hermes-heartbeat | every 60m | ok | 0 | — |
| 2675f72f7ecb | event-heartbeat | every 2m | ok | 0 | — |
| 2001d7521454 | telegram-network-watchdog | every 1m | ok | 0 | — |
| 9d7e9b582782 | hermes-self-update-check | 0 9 * * * | ok | 0 | — |
| 5103a96bad55 | hermes-self-improvement-cycle | every 15m | ok | 0 | — |
| 2f8449cdfeef | telegram-monitor | every 360m | **error** | N/A | Add backoff + fallback |
| 56517647333d | self-upgrade-loop | every 720m | **error** | N/A | Add backoff + fallback |
| 183211c9b883 | ai-tools-hub-poster | every 480m | ok | 0 | — |
| 641901e67135 | weekly-lessons | 0 9 * * 1 | never run | 0 | — |
| 7963a772d5ba | daily-metrics-check | 0 23 * * * | never run | 0 | — |

**Total:** 12 jobs, 3 failing (25% error rate)

---

## Immediate Action Plan

1. **NOW:** Fix `cube_feeder.py` — add `content=text` parameter → unblocks KC growth
2. **NOW:** Add backoff + fallback to `telegram_cron_monitor.py` and `self_upgrade_check.py`
3. **TODAY:** Create `session_manifest.py` minimal implementation
4. **TODAY:** Update `reality_gate.py` with real integrity checks
5. **THIS WEEK:** Run G003 First Revenue Test (pick scheme from arbitrage workshop)

---

## Verification Commands

```bash
# Test cube_feeder fix
python scripts/cube_feeder.py --dry-run

# Test reality gate
python scripts/reality_gate.py

# Check cron jobs
python -c "
import json
with open('cron/jobs.json') as f:
    jobs = json.load(f)['jobs']
for j in jobs:
    print(f'{j[\"name\"]}: {j[\"last_status\"]} (errors: {j.get(\"consecutive_errors\", 0)})')
"

# Full boot test
python D:/Portable_Soft/hermes/hermes_start.py
```
# Research Queue Bridge — Crystal → Web Research Pipeline

## Problem

The crystal's conscience finds blind spots (domains with few entries, untapped sources, anomalies) but cannot execute web search. It's isolated from Hermes tools (web_search, web_extract, skills, agents).

## Solution

Crystal writes research topics to `cache/research_queue.json`. A cron job (`research-worker`, every 4h) reads the queue, executes web searches, saves results to KC.

## Full Flow

```
crystal._conscience() → learning_direction
    │ (will() step 3.4.5)
    ▼
writes to research_queue.json  ─── queue JSON file
    │
    │ Cron tick (every 4h): research-worker
    │ Step 1: research_worker.py (script) → reads queue → prints RESEARCH_NEEDED topics
    │ Step 2: Hermes agent receives script output → web_search(topic) → web_extract(top URLs)
    │ Step 3: execute_code → INSERT INTO experiences (hash is REQUIRED for UNIQUE)
    │ Step 4: updates queue → marks topic 'done'
    ▼
KC gets new entries (source='web_research', axis_domain='research')
    │
    ▼
Next crystal cycle → sees fresh KC entries → blindspot reduced → next gap found
```

## Cron Detail

**Job ID:** `1e296f483568`
**Schedule:** `every 4h`
**Script:** `research_worker.py` (data collection — reads queue, outputs topics to agent)
**Prompt:** agent prompt with web_search + KC write instructions
**Workdir:** `D:/Portable_Soft/hermes`
**Mode:** agent-driven (not no_agent=True) — needs Hermes tools

The job has BOTH `script` and `prompt` set. Order:
1. Script runs first (collects topics from queue)
2. Script stdout goes to agent as context
3. Agent executes prompt with web_search + web_extract + KC save

## Queue File Schema

```json
{
  "queue": [
    {"topic": "devops best practices", "priority": 3, "ts": "...", "source": "crystal_conscience"}
  ],
  "processed": [
    {"topic": "across", "priority": 3, "ts": "...", "source": "crystal_conscience",
     "status": "done", "result": "saved_2_entries", "processed_ts": "..."}
  ]
}
```

## Crystal Side (will() step 3.4.5)

Located in `scripts/crystal.py` after the LEARNING_TO_ACTION mapping block (line ~2027).

Extracts topics from 3 types of learning_directions:
- `"исследовать слепое пятно: домен 'X' (N записей)"` → topic = X
- `"исследовать аномалию: домен 'X' (N% неуспеха)"` → topic = "X best practices"
- `"углубить доминантный домен 'X' (N записей)"` → topic = "X advanced techniques"

Deduplicates against pending queue + last 50 processed entries.

## Worker Script (research_worker.py)

Location: `scripts/research_worker.py`
Role: data collection only. Reads queue, marks items as 'processing', prints topics for agent.
The script does NOT do web search — the agent does that.

## KC Save Rules

Critical — the `experiences` table has a UNIQUE constraint on `hash`. You MUST compute it:

```python
import hashlib
raw_text = f"## {title}\n\n**Source:** {url}\n\n{content}"
rhash = hashlib.sha256(raw_text.encode()).hexdigest()[:16]
cur.execute(
    "INSERT OR IGNORE INTO experiences (raw_text, hash, source, axis_domain, ts, tags) VALUES (?, ?, ?, ?, ?, ?)",
    (raw_text, rhash, "web_research", "research", now, "research,web")
)
```

Without `hash`, INSERT OR IGNORE silently succeeds (rowcount=0) but nothing is saved.

**KC column names (not guesses):**
| Field in code | Real column | Why |
|---|---|---|
| `domain` | `axis_domain` | KC uses axis_ prefix |
| `dimension` | — (no such column) | use `tags` instead |
| no hash | `hash` | REQUIRED for UNIQUE constraint |

## Batch-Feed Pattern

When the crystal is actively producing new blind spots faster than the cron consumes them (every 4h), feed all pending topics in one manual batch:

```
web_search(topic1) + web_search(topic2) + web_search(topic3)
    → execute_code: save all to KC, mark all as processed
    → run crystal to check new blind spots
    → if still hungry, repeat
```

Observed behavior in production:
- **4 topics fed** → crystal digests → **2 new topics appear**
- Each web search produces ~3 KC entries per topic
- Net reduction: ~1-2 topics per batch
- Equilibrium: crystal will always find SOME blind spots (learning systems always know more gaps). Goal is not zero queue, but manageable cadence.

## Why Not Zero

The crystal is designed to always find gaps — each new entry reveals adjacent unknowns. Zero queue means the crystal stopped learning. Target: 1-3 topics in queue = healthy equilibrium.

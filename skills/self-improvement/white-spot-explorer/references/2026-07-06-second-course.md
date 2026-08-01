# 2026-07-06 Second Course — Batch Domain Research Learnings

## Critical Correction: Quantity IS a Criterion

**User correction:** "Количество — это тоже критерий. Одна длинная статья не равна пяти разным заметкам с разных углов."

- Minimum **5 entries per domain** in Knowledge Cube
- Each entry = different angle, different source, different subtopic
- NOT "one comprehensive article = 5 entries"

## Working Pattern: Batch Domain Research (Validated 2026-07-06)

```python
# Phase 1: Add domains to domain_definitions.yaml (EN/RU keywords)
# Phase 2: auto_tagger --force (reclassify existing entries)
# Phase 3: Register white_spot_clusters with size=0, status='developing'
# Phase 4: For each domain, research 5 subtopics via DeepSeek (localhost:9655)
# Phase 5: Insert each as separate experience with unique hash
# Phase 6: Update white_spot_clusters size=5, status='researched'
```

**Performance:** 7 domains × 5 entries = 35 records in ~2.5 hrs, ~$0.015 on DeepSeek-V4-Flash (localhost:9655)

## Tool Choice: execute_code > delegate_task for White Spot Explorer

- `delegate_task` blocks parent session 7+ min (context overhead)
- `execute_code` with direct curl to localhost:9655 = ~2 min per domain batch
- Rate limit: 3-5 sec between requests, max 5 requests/domain/session

## DeepSeek API Integration (execute_code + urllib)

```python
import json, urllib.request, time

def ask_deepseek(prompt, max_tokens=2500):
    url = "http://localhost:9655/v1/chat/completions"
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())["choices"][0]["message"]["content"]

# Usage:
result = ask_deepseek(prompt)
time.sleep(3)  # Rate limit
```

## Schema-Compliant Insert (Critical)

```python
import hashlib, json, sqlite3
from datetime import datetime

content_hash = hashlib.md5(content.encode()).hexdigest()[:16]
c.execute("""
    INSERT INTO experiences (content, raw_text, source, confidence, ts, hash, 
                             dynamic_axes, axis_domain, tags, is_white_spot, importance)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    content, content, "white-spot-explorer", 0.95, datetime.now().isoformat(), content_hash,
    json.dumps({"topic": domain, "research": True, "white_spot": True}),
    domain,
    json.dumps([domain, "white-spot", "research", *subtags]),
    1, 0.9
))
```

**Full INSERT columns**: `content, raw_text, source, confidence, ts, hash, dynamic_axes, axis_domain, tags, is_white_spot, importance`

- `raw_text` NOT NULL constraint — must duplicate content or provide original
- `hash` = md5(content)[:16] for deduplication
- `dynamic_axes` = JSON with topic, research, white_spot flags
- `tags` = JSON array with domain + subtags

## Auto-Tagger Reclassification Step

After inserting new domain research, **always run**:
```bash
python scripts/auto_tagger.py --force
```
This reclassifies existing entries using the new domain keywords (442 reclassified in this session). Without this, the new domains only have the manually inserted research entries.

## White Spot Cluster Updates

```sql
-- After inserting research, update cluster size from actual data
UPDATE white_spot_clusters 
SET size = (SELECT COUNT(*) FROM experiences WHERE axis_domain = proposed_dimension)
WHERE status = "researched";
```

## Cost Tracking

- All LLM calls logged via `cost_tracker.log_cost(model, input_tokens, output_tokens, ...)`
- DeepSeek-V4-Flash: ~$0.14/1M input, $0.28/1M output (very cheap)
- 7 domains × 5 entries × ~2500 tokens = ~87,500 tokens = ~$0.015 total

## Token Compression Integration

- Add `auto_compress(messages)` before LLM calls in `call_llm()`
- Saves 40-75% on tool outputs
- Already integrated in `llm_analyst.py` and `autonomous_agent.py`

---

# GitHub Project Analysis Patterns (Ada-SI, Mark-XLVIII)

When analyzing similar agent architectures, extract:

| Pattern | Ada-SI | Mark-XLVIII | Hermes Application |
|---------|--------|-------------|-------------------|
| **Multi-service** | Chat(8080) + LiteLLM(4000) + ToolRuntime(8090) | main.py + actions/ + ui.py | Consider: separate tool runtime service |
| **Dynamic tool creation** | Forge system (generate_new_tool, edit_existing_tool) | — | Our procedural_executor could adopt plan→approve→execute |
| **Real-time voice** | — | Gemini Live API, 50ms audio chunks, instant interrupt | Voice interface skill needs audio streaming |
| **Vision** | — | Screen capture → Gemini Live, immediate ack | Our agent-browser needs real-time screen feed |
| **Memory** | localStorage + staging/ + custom_tools/ | Persistent KV across sessions | Our KC + state.db + memories/ |
| **Proactive** | Heartbeat supervisor → LLM calls on timer | 15-min silence check-ins (Gemini-decided) | Our event_daemon + proactive_engine |
| **Zero terminal** | subprocess CREATE_NO_WINDOW | Subprocess monkey-patch | Apply to all background scripts |

## Recommended Hermes Upgrades from Analysis

1. **Tool Runtime Service** — isolate tool execution (security, like Ada-SI's port 8090)
2. **Forge/Plan-Approval System** — dynamic tool creation with human-in-the-loop (Ada-SI pattern)
3. **Voice Streaming** — Gemini Live API integration (Mark-XLVIII pattern)
4. **Real-time Vision** — screen capture → LLM with immediate acknowledgment
5. **Proactive Check-ins** — LLM-decided, not hardcoded (Mark-XLVIII: "Gemini decides, no hardcoded rules")
6. **Parallel Operations** — concurrent startup phases, parallel search backends
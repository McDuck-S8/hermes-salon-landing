# EverOS Cloud SDK — integration session reference

**Date:** 2026-06-14
**SDK version:** 0.4.0
**Cloud API:** https://api.evermind.ai
**Dashboard:** https://everos.evermind.ai

## What was integrated

A persistent memory layer for AI agents. EverOS extracts structured memory (episodes, profiles, events) from conversations.

## SDK structure

```
everos.EverOS(api_key=...)
  .v1
    .memories
      .add(user_id, messages, session_id, async_mode)  → AddResponse
      .search(filters={"user_id": str}, query, method, top_k, memory_types)  → SearchMemoriesResponse
    .tasks
      .retrieve(task_id)  → GetTaskStatusResponse
    .groups          # Multi-user/group mode
    .settings        # User settings
```

## API endpoints

| Method | Endpoint | SDK call |
|--------|----------|----------|
| POST | `/api/v1/memories` | `client.v1.memories.add()` |
| POST | `/api/v1/memories/search` | `client.v1.memories.search()` |
| GET | `/api/v1/tasks/{id}` | `client.v1.tasks.retrieve()` |
| POST | `/api/v1/memories/group` | `client.v1.groups.add()` |

## Memory types

| API value | Description | Searchable |
|-----------|-------------|-----------|
| `raw_message` | Raw stored messages | Yes |
| `episodic_memory` | Narrative summaries | Yes (LLM-extracted) |
| `profile` | User attributes | Yes (LLM-extracted) |
| `agent_memory` | Cases + skills | Yes (LLM-extracted) |

## Processing pipeline

1. `add()` → queues messages → returns `task_id` + `status: "queued"`
2. Background LLM extraction → boundaries, facts, foresight, profile updates
3. `tasks.retrieve(task_id)` → `status: "success"` when done
4. `search()` → retrieves from indexed memory

**Note:** Raw messages appear immediately in search with `memory_types=["raw_message"]`. Episodes and profiles require LLM extraction which may not produce results depending on the backend LLM configuration.

## Search methods

- `keyword`: BM25 (Elasticsearch)
- `vector`: Semantic (Milvus)
- `hybrid` (default): Both + rerank
- `agentic`: LLM-guided multi-round retrieval

`filters` dict must contain `user_id` or `group_id`. Use `memory_types` to filter.

## Credential setup

Required env var: `EVEROS_API_KEY`
```bash
export EVEROS_API_KEY="<key>"
```

## Pitfalls encountered

1. **OpenRouter → Mistral migration**: OpenRouter rejected all models because the API key's `requested_providers` didn't overlap with any model's `available_providers`. Switched to direct Mistral API (`api.mistral.ai/v1` with `mistral-small-latest`) for the local server.

2. **SDK response objects**: The SDK returns pydantic models (not plain dicts). Access via `.data.attribute` pattern.

3. **ENV=DEV for docs**: FastAPI `/docs` disabled by default; need either `ENV=DEV` env var or `os.environ.setdefault("ENV", "DEV")` in launcher.

4. **Background process lifecycle**: Multiple kill attempts needed on Windows (taskkill vs kill -9). OME lock files block restart.

## Files created

- `scripts/everos_client.py` — Hermes wrapper class
- `projects/EverOS/run_server.py` — local server launcher (with ENV=DEV)
- `projects/EverOS/.env` — local server config

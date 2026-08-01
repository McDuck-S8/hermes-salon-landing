# Delegation Visibility Reference

## Config Options

```yaml
display:
  tool_progress: verbose   # off | new | all | verbose
```

## CLI Commands

| Command | What it does |
|---------|-------------|
| `/verbose` | Cycles tool_progress: off → new → all → verbose |
| `/agents` | Shows active subagents: ID, goal, model, toolsets, status |
| `/status` | Shows session info including active delegations |

## Tree-View Event Types (from delegate_tool.py)

The progress callback (`_build_child_progress_callback`) emits:

| Event | Display | Content |
|-------|---------|---------|
| `subagent.start` | `🔀 {goal}` | Goal text (55 chars max) |
| `subagent.thinking` | `💭 "{text}"` | Model's thinking/reasoning |
| `tool.started` | `{emoji} {tool_name} "{preview}"` | Tool name + 35-char preview |
| `tool.completed` | (batched) | Tool name added to batch |
| `subagent.complete` | (final) | Subagent finished |
| `subagent_progress` | `🔀 {summary}` | Progress summary from nested orchestrator |

## Identity kwargs passed in events

Every relayed event includes:
- `task_index` — 0-based index in batch
- `task_count` — total tasks in batch
- `goal` — the goal string
- `subagent_id` — stable ID (e.g. `sa-0-a1b2c3d4`)
- `parent_id` — parent's subagent ID (for nesting)
- `depth` — nesting depth (0 = first-level child)
- `model` — effective model name
- `toolsets` — list of toolset names assigned
- `tool_count` — running count of tool calls

These are available in the callback payload but NOT printed to CLI by default. The TUI uses them for spawn-tree reconstruction.

## Gateway Behavior

On messaging platforms, delegation progress is:
1. Batched in groups of 5 tool calls
2. Flushed on subagent completion
3. Delivered as separate messages to the parent chat

No tree-view — flat list of tool names in batched messages.

## Spinner Behavior

The parent spinner during delegation shows:
- Single task: `🔀 {goal_first_30_chars} · (/agents to monitor)`
- Batch: `🔀 delegating {N} tasks · (/agents to monitor)`

The spinner stops when delegation completes and shows the cute tool message with duration.

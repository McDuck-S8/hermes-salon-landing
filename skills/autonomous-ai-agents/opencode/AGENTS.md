# AGENTS.md — opencode

## Purpose
Delegate coding to OpenCode CLI (features, PR review, refactoring). OpenCode is a provider-agnostic, open-source AI coding agent with a TUI and CLI that supports multiple LLM providers via OpenRouter, Anthropic, OpenAI, etc.

## Ownership
Hermes Agent — autonomous AI agent orchestration layer.

## Local Contracts

### Triggers
- User explicitly asks to use OpenCode
- Coding tasks requiring autonomous file editing, git workflows, or multi-step refactoring
- Long-running coding sessions with progress checks
- Parallel task execution in isolated workdirs/worktrees

### Required Tools
- `terminal` tool with `pty=true` for interactive TUI sessions
- `process` tool for background process management
- `opencode` CLI installed (`npm i -g opencode-ai@latest` or `brew install anomalyco/tap/opencode`)
- Auth configured: `opencode auth login` or provider env vars (OPENROUTER_API_KEY, etc.)
- `opencode auth list` must show at least one provider
- Git repository (recommended; required for code tasks)
- Windows: explicit binary path may be needed (e.g., `%npm prefix%\node_modules\opencode-ai\bin\opencode.exe`)

### Config
- Provider auth via `opencode auth login` or env vars
- `--model provider/model` to force specific model
- `--agent build|plan` to choose agent mode
- `--format json` for machine-readable output
- `--file` / `-f` to attach context files
- `--thinking` to show reasoning blocks
- `--session <id>` / `-c` / `--continue` for session resumption

## Work Guidance

### When to Use
- Bounded one-shot tasks: `opencode run 'prompt'`
- Iterative multi-turn work: background `opencode` + `process` tool
- PR reviews: `opencode pr <num>` or temp clone + `opencode run`
- Parallel issue fixing: git worktrees + parallel background OpenCode processes
- Provider-agnostic coding (OpenRouter, Anthropic, OpenAI, etc.)

### Common Patterns
- **One-shot**: `opencode run 'Add retry logic to API calls'` (exits when done, no PTY needed)
- **With context files**: `opencode run 'Review config' -f config.yaml -f .env.example`
- **Show thinking**: `opencode run 'Debug CI failures' --thinking`
- **Force model**: `opencode run 'Refactor auth' --model openrouter/anthropic/claude-sonnet-4`
- **Background iterative**: `terminal(command="opencode", workdir="~/project", background=true, pty=true)` → `process(action="submit", ...)` → `process(action="poll/log", ...)`
- **Exit TUI**: Send Ctrl+C (`\x03`) via `process(action="write")` or `process(action="kill")` — **NOT `/exit`** (opens agent selector)
- **Resume session**: `opencode -c` (continue last) or `opencode -s ses_abc123`
- **PR review**: `opencode pr 42` or clone temp + `opencode run 'Review PR #42. git diff origin/main...origin/pr/42'`
- **Parallel worktrees**: `git worktree add` + background `opencode` in each

### Key Flags Reference
| Flag | Use |
|------|-----|
| `run 'prompt'` | One-shot execution, exits |
| `--continue` / `-c` | Continue last session |
| `--session <id>` / `-s` | Resume specific session |
| `--agent <name>` | Choose agent (build/plan) |
| `--model provider/model` | Force model |
| `--format json` | JSON events output |
| `--file <path>` / `-f` | Attach file context |
| `--thinking` | Show reasoning blocks |
| `--title <name>` | Name session |
| `--variant <level>` | Reasoning effort (high/max/minimal) |

## Verification
- No `scripts/`, `tests/`, or `evals/` directory present in skill
- Verify manually: `opencode --version`, `opencode auth list`
- Test one-shot: `opencode run 'echo hello'`
- Test background: `terminal(command="opencode", background=true, pty=true)` → `process(action="poll")`
- References available in `references/opencode-zen-api.md`

## Child DOX Index
| Path | Type | Description |
|------|------|-------------|
| `references/opencode-zen-api.md` | references | OpenCode Zen API reference for advanced integration |
| (none) | templates | No templates/ directory in this skill |
| (none) | scripts | No scripts/ directory in this skill |
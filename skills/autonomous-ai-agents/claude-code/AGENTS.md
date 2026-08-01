# AGENTS.md — claude-code

## Purpose
Delegate coding tasks to Claude Code CLI (features, PRs, refactoring, reviews). Claude Code v2.x is Anthropic's autonomous coding agent CLI that can read files, write code, run shell commands, spawn subagents, and manage git workflows autonomously.

## Ownership
Hermes Agent — autonomous AI agent orchestration layer.

## Local Contracts

### Triggers
- User explicitly asks to use Claude Code
- Coding tasks requiring autonomous file editing, git workflows, or multi-step refactoring
- PR reviews and batch issue fixing
- Tasks benefiting from print mode (non-interactive) or interactive PTY sessions

### Required Tools
- `terminal` tool with `pty=true` for interactive mode
- `process` tool for background process management
- `claude` CLI installed (`npm install -g @anthropic-ai/claude-code`)
- Auth configured: `ANTHROPIC_API_KEY` or `claude auth login`
- Git repository (required for code tasks)

### Config
- `ANTHROPIC_API_KEY` or OAuth via `claude auth login`
- `--dangerously-skip-permissions` for interactive PTY mode (requires dialog handling via tmux)
- `--max-turns` to bound execution (default 10 for print mode)
- `--output-format json|stream-json` for structured output
- `--bare` for CI/scripting (skips hooks, plugins, MCP, CLAUDE.md)

## Work Guidance

### When to Use
- One-shot coding tasks: `claude -p "task" --max-turns 10`
- Multi-turn interactive refactoring: tmux + `claude` with PTY
- PR reviews: `claude pr <num>` or `codex review` pattern
- Parallel issue fixing: git worktrees + parallel `claude` processes
- CI/CD automation: `claude --bare -p "task" --allowedTools 'Read,Bash'`

### Common Patterns
- **Print mode (preferred)**: `claude -p 'task' --max-turns N --output-format json` — no PTY, exits cleanly, returns JSON with session_id, cost, turns
- **Interactive PTY**: tmux session + `tmux send-keys` for dialog handling (workspace trust, permissions)
- **Session continuation**: `claude -c` (continue last), `claude -r <id>` (resume specific), `--fork-session`
- **Structured output**: `--json-schema` for validated JSON extraction
- **Piped input**: `cat file | claude -p "analyze"` for context injection
- **Parallel worktrees**: `git worktree add` + parallel `claude` processes

### Critical PTY Dialog Handling
Interactive mode with `--dangerously-skip-permissions` shows TWO dialogs:
1. Workspace trust (default Yes → `Enter`)
2. Permissions warning (default No → `Down` then `Enter`)
Handle via `tmux send-keys` with proper delays.

## Verification
- No `scripts/`, `tests/`, or `evals/` directory present in skill
- Verify manually: `claude --version` (requires v2.x+), `claude doctor`, `claude auth status`
- Test print mode: `claude -p "echo hello" --max-turns 1 --output-format json`
- Test interactive: `tmux new-session -d -s test && tmux send-keys -t test 'claude --dangerously-skip-permissions "echo hi"' Enter`

## Child DOX Index
| Path | Type | Description |
|------|------|-------------|
| (none) | references | No references/ directory in this skill |
| (none) | templates | No templates/ directory in this skill |
| (none) | scripts | No scripts/ directory in this skill |
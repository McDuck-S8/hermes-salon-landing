# AGENTS.md — codex

## Purpose
Delegate coding tasks to OpenAI Codex CLI (features, PRs, refactoring, reviews). Codex is OpenAI's autonomous coding agent CLI that runs inside a git repository.

## Ownership
Hermes Agent — autonomous AI agent orchestration layer.

## Local Contracts

### Triggers
- User explicitly asks to use Codex
- Coding tasks requiring autonomous file editing, git workflows, or multi-step refactoring
- PR reviews and batch issue fixing
- Parallel task execution in isolated worktrees

### Required Tools
- `terminal` tool with `pty=true` (REQUIRED — Codex hangs without PTY)
- `process` tool for background process management
- `codex` CLI installed (`npm install -g @openai/codex`)
- OpenAI auth: `OPENAI_API_KEY` or Codex OAuth (`codex auth login`)
- **Git repository REQUIRED** — Codex refuses to run outside a git repo

### Config
- `--full-auto` — sandboxed but auto-approves file changes in workspace
- `--yolo` — no sandbox, no approvals (fastest, most dangerous)
- `--sandbox danger-full-access` — no Codex sandbox (workaround for gateway/bubblewrap issues)
- `exec "prompt"` — one-shot execution, exits when done
- `exec --full-auto "prompt"` — bounded autonomous execution

## Work Guidance

### When to Use
- Building features, refactoring, PR reviews, batch issue fixing
- Tasks requiring git operations (commit, push, PR creation)
- Parallel issue fixing via git worktrees
- When user prefers Codex over Claude Code or OpenCode

### Common Patterns
- **One-shot**: `codex exec 'Add dark mode toggle to settings'`
- **Scratch work**: `cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'`
- **Background long tasks**: `terminal(command="codex exec --full-auto 'Refactor auth module'", background=true, pty=true)` → monitor with `process(action="poll/log")`
- **Interactive input**: `process(action="submit", session_id="<id>", data="yes")` if Codex asks
- **PR reviews**: Clone to temp dir + `codex review --base origin/main`
- **Parallel worktrees**: `git worktree add` + parallel background `codex` processes
- **Batch PR reviews**: `git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'` + parallel `codex exec`

### Critical Gateway Caveat
When invoking Codex CLI from Hermes gateway/service context (e.g., Telegram-driven sessions), Codex `workspace-write` sandboxing may fail with bubblewrap/user-namespace errors (`Permission denied`, `Operation not permitted`).

**Workaround**: Use `codex exec --sandbox danger-full-access "task"` and enforce safety via:
- Explicit `workdir`
- Clean git status before launch
- Narrow task prompts
- `git diff` review before commit
- Targeted tests
- Human/agent confirmation before broad changes

## Verification
- No `scripts/`, `tests/`, or `evals/` directory present in skill
- Smoke test: `terminal(command="codex exec 'Respond with exactly: OPENCODE_SMOKE_OK'", pty=true)` → output includes `OPENCODE_SMOKE_OK`, exits cleanly
- Verify: `codex --version`, `codex auth list`
- For code tasks: expected files changed, tests pass

## Child DOX Index
| Path | Type | Description |
|------|------|-------------|
| (none) | references | No references/ directory in this skill |
| (none) | templates | No templates/ directory in this skill |
| (none) | scripts | No scripts/ directory in this skill |
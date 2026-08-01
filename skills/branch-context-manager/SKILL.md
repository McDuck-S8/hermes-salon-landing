---
name: branch-context-manager
description: "Auto-loads at session start. Reads branches.yaml + breadcrumbs.log to restore conversation context after compaction. Also provides rules for maintaining both files. Covers state-db FTS5 corruption recovery and context fallback when session_search is broken."
auto_load: true
priority: high
---

# Branch Context Manager

## Problem
Context compaction loses conversation threads. User works on multiple topics in one chat. After compaction, agent forgets what was happening.

## Solution: Two persistent files + rules

### Files
- `$HERMES_HOME/branches.yaml` — structured state per topic/branch
- `$HERMES_HOME/breadcrumbs.log` — append-only chronological log

### On Session Start (auto-load)
1. Read `$HERMES_HOME/branches.yaml` — restore topic states
2. Read last 20 lines of `$HERMES_HOME/breadcrumbs.log` — recent activity
3. **Check breadcrumbs staleness**: if the most recent entry is >24h old, append a hiatus marker:
   ```
   [HH:MM] session-restart | <N>d hiatus since last entry | resuming from branches.yaml state
   ```
   This prevents stale context from being treated as current.
4. If context was compacted (see "[CONTEXT COMPACTION]" in messages) — use these files to restore context BEFORE responding

### On Every Response (mandatory)
1. Determine which branch the conversation is about
2. Append one line to breadcrumbs.log:
   ```
   [HH:MM] branch-name | what happened | what's next
   ```
3. If significant state change — update branches.yaml too

### Branch Classification Rules
- Match keywords in user message to branch names
- If no match → create new branch or ask
- If ambiguous → default to most recently active branch

### Breadcrumbs Format
```
[12:05] crm-bot | запустил бота PID 83856 | жду тест в Telegram
[12:08] freellmapi | npm install сломан | нужен better-sqlite3
```

### Branches.yaml Fields
- `status` — current state (1 line)
- `last_action` — what was just done
- `next_step` — what should happen next
- `key_files` — relevant file paths
- `context` — important context (tokens, ports, configs)

### Recovery After Compaction
When you see "[CONTEXT COMPACTION]" in messages:
1. First: read branches.yaml
2. Second: read last 20 lines of breadcrumbs.log
3. Third: classify current message to a branch
4. Fourth: load that branch's state
5. Fifth: respond with branch name prefix: `[crm-bot]` etc.

### Pitfalls (learned from real usage)
- **Memory limit**: The memory tool has a 2200-char limit. Branch system rules must be SHORT in memory (just "Branch System: $HERMES_HOME/branches.yaml + breadcrumbs.log. Rules: append breadcrumbs, update branches on state change, read both on compaction"). Full rules live HERE in the skill.
- **delegate_task timeout on slow networks/proxies**: delegate_task has a 120s timeout. Behind slow proxies (e.g. Russian SOCKS5), web research tasks often timeout. When this happens: (1) tell the user "агент timeout'ят, делаю сам", (2) do the work inline, (3) don't silently fail. User explicitly wants agents working — explain WHY they didn't.
- **Breadcrumbs are MANDATORY, not optional**: User explicitly complained "где хлебные крошки?" when they were missing. After EVERY response: append to breadcrumbs.log. No exceptions. Even a one-line answer gets a breadcrumb.
- **Context restoration from session_search**: When user references past work ("ты поставил X?", "что с Y?"), search session history FIRST. Don't say "I don't know" without checking. User frustration: "да что б тебя блять..." — they expect you to remember.
- **session_search broken = FTS5 corruption**: If session_search returns "invalid fts5 file format (found 0, expected 4 or 5)", the state.db FTS5 index is corrupted. Fallback: (1) read `.hermes_history` for recent user messages (`tail -100`), (2) read `branches.yaml` for topic state, (3) read `breadcrumbs.log` for activity. Do NOT attempt to rebuild FTS5 via CLI sqlite3 — it fails on truly corrupted FTS. Use Python sqlite3 module instead (see `references/state-db-recovery.md`). NEVER skip context restoration because session_search is down — the fallback files exist for exactly this scenario.
- **execute_code isolation**: Each execute_code call is a fresh Python process. Variables from one call don't exist in the next. Always redefine paths/constants.
- **Background process management**: On Windows (MSYS/git-bash), `execute_code` subprocess.Popen with `shell=False` dies when the script exits. For long-running services (servers, bots):
  - Use `terminal(background=True, notify_on_complete=False)` for truly persistent processes
  - Use Windows `start /B cmd /c "command > log.txt 2>&1"` for detached processes
  - NEVER use subprocess.Popen in execute_code for background tasks — it's killed on exit
- **YAML requires PyYAML**: Ensure `import yaml` works. If not, use `json` as fallback for branches file.
- **Breadcrumb append vs overwrite**: Always OPEN with mode 'a' (append), never 'w' (write). Overwriting loses history.
- **Stale breadcrumbs**: A breadcrumbs.log with only old entries (days/weeks old) means the previous session didn't write breadcrumbs before ending. On session start, check the most recent entry's timestamp. If >24h old, append a "session-restart after hiatus" marker — this signals the break in continuity and prevents stale context bleeding into the new session.
- **No breadcrumbs at all**: If breadcrumbs.log doesn't exist or is empty, create it with a fresh init entry rather than assuming no state. The file is the spine of cross-session continuity.
- **Branch name = lowercase, hyphens**: Use `crm-bot` not `CRM Bot`. Consistency matters for classification.
- **Don't over-branch**: 5-7 branches max. If a branch is done (e.g. feature shipped), mark it `[CLOSED]` and archive after a week.
- **Morning/Evening reports**: When generating status reports (cron or on-demand), use the 4-section template from `references/morning-report-template.md`. Combines branches.yaml + breadcrumbs.log + session_search for full context.
- **Security scan before install**: When installing third-party code (npm packages, GitHub repos, pip packages) — scan source for eval/exec/env_exfil/network_calls/obfuscated_code/suspicious_urls/shell_exec/dns_exfil/hardcoded_IPs FIRST. See `references/security-scan-patterns.md` in this skill.

### User Style Preferences (MUST follow)
- User reads ALL your output. Garbled characters (model corruption) = immediate frustration.
- User wants YOUR proposals, not just agreement. When they suggest something, respond with "here's my take" + alternatives, not just "great idea, let's do it".
- When context is lost, DON'T ask "what should I do?" — read branches.yaml + breadcrumbs.log and PROCEED.
- Prefix responses with `[branch-name]` when multiple branches are active.
- When user says "продолжай" — check breadcrumbs for last active branch, restore context, and ACT.
- **NEVER stop working when user leaves.** If user gave tasks and said "отключаюсь" / "спокойной ночи" / "утром доложишься" — CONTINUE working until tasks are done. User expects results when they return, not a stopped process.
- When user shares links for evaluation — research ALL of them, not just the first one. Deliver a ranked summary with relevance to THEIR business.
- **Number responses** when user requests it (e.g. "к каждому ответу присваивай номер"). Use `[N]` prefix on each point so user can reference by number.
- **"Мы разговариваем, агенты выполняют"** — ALWAYS delegate heavy work via delegate_task. Keep the chat free for conversation. Only do work inline when delegate_task fails (timeout, network) — and then EXPLAIN why you're doing it yourself.

- **Never pause during continuous tasks**: When user says "продолжай" or "сделай X" — DO THE ENTIRE THING without stopping to ask "what next?". User was frustrated: "блять ну естественно нужно закончить миграцию!!!!" — they expect autonomous completion. Only ask when there's a genuine decision point with unclear consequences, not when the next step is obvious.
- **Use existing resources before asking**: When you need a token/key/config — CHECK existing files first (.env, config.py, .bashrc, old installation). User was frustrated: "блять ну вставь свой ключ" when I asked about the token instead of reading it from data/.env where it already existed. NEVER ask for information you can find yourself.

### Delegation Rules (CRITICAL)
- Heavy research, installation, testing, file creation → delegate_task FIRST
- Only work inline if delegate_task returns timeout/error
- When delegate_task fails: do the work yourself BUT tell the user "агенты timeout'ят, делаю сам"
- NEVER silently do heavy work inline — user expects agents to be working in background
- If user asks about past work you don't recognize → session_search FIRST, then ask. Don't say "I don't know what that is" without checking.

### Rules
- NEVER skip breadcrumbs update after a response
- NEVER skip branches.yaml update after significant state change
- ALWAYS prefix response with branch name when multiple branches are active
- When user says "продолжай" — check breadcrumbs for last active branch
- When user asks a garbled/mixed-language question — check if YOUR previous output contained the garbled text. It's probably a model corruption artifact you generated.

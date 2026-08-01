---
name: session-analysis
description: Analyze recent sessions, extract tasks, identify patterns, and generate consultation reports. Covers the brain-auto-consult workflow and similar recurring analysis jobs.
tags: [sessions, analysis, cron, reporting, patterns]
triggers:
  - user asks to analyze recent sessions
  - user asks "what have I been working on"
  - cron job runs session analysis or auto-consult
  - user asks for patterns across sessions
  - user asks for recommendations based on session history
---

# Session Analysis & Consultation Reports

## When to Use

- Analyzing recent session history for a user
- Generating periodic consultation reports (cron jobs)
- Identifying recurring patterns, blockers, and trends
- Producing actionable recommendations from session data

## Methodology

### Step 1: Gather Sessions

```
session_search(limit=3-5, sort="newest")  # Browse recent
session_search(query="topic", limit=5)    # Discovery by topic
```

For each session, extract:
- **Session ID** and metadata (source, message count, timestamps)
- **Primary task** from bookend_start (first user message)
- **Outcome** from bookend_end (last assistant message)
- **Key artifacts** created (files, databases, configs)

### Step 2: Classify Each Session

| Category | Signal |
|----------|--------|
| Active work | User messages with "продолжай", "делай", imperative verbs |
| Debugging | Error messages, repeated retries, tool failures |
| Planning | Action plans, roadmaps, task lists created |
| Setup/Config | Tool installation, environment configuration |
| Research | Web searches, document analysis |

### Step 3: Extract Patterns

Look for:
1. **Repeating tasks** — same project across multiple sessions
2. **User behavior patterns** — "продолжай дальше" = user wants results, not plans
3. **Tool failures** — same error across sessions = systemic issue
4. **Unfinished work** — tasks started but not completed
5. **Escalation signals** — frustration, corrections, repeated requests

### Step 4: Generate Report

```markdown
## Session Analysis Report
*Date — N sessions analyzed*

### Tasks
- **Task 1:** [description] → Status: [complete/in-progress/blocked]
- **Task 2:** [description] → Status: [complete/in-progress/blocked]

### Recommendations
- [Actionable recommendation per task]

### Patterns
- [What repeats across sessions]

### Systemic Issues
- [Problems that appear in 3+ sessions]
```

## Retrieving User Instructions from Session History

When user asks "what did you instruct me today" or "какие инструкции я тебе давал" —
extract ONLY user messages from today's sessions.

### Procedure

```python
# 1. Find today's sessions
session_search(limit=10, sort="newest")
# → returns session_ids, timestamps, message counts

# 2. For each session, extract user messages only
session_search(session_id="20260626_003207_986180", role_filter="user")
# → returns only messages where role='user'

# 3. Compile instructions per session
# Format: Session title/time → user messages (truncated to 200 chars)
```

### Pitfalls
- `session_search` without `role_filter` returns ALL messages (assistant + tool + user) — use `role_filter="user"` to isolate instructions
- Sessions may have 200+ messages — the tool truncates. Focus on first/last user messages.
- Some sessions have no title (null) — use timestamp + first message as identifier
- Context compaction in large sessions may lose early user messages — check `bookend_start` for the original request

## Pitfalls

### Script Not Found — Fix on FIRST Failure
If a cron job references a script that doesn't exist (e.g., `auto_consult.py`):
1. Create the script via `write_file` (NOT execute_code — those files may not persist)
2. Or stop/disable the cron job immediately
3. Or inline the logic directly in the cron prompt

**Do NOT let a missing-script cron run more than once.** Real-world example: brain-auto-consult ran 6 consecutive times (May 25-28) producing identical "script not found" reports. Each run wasted LLM tokens and produced noise. The self-healing assumption ("maybe next time it'll find it") is wrong — the script won't materialize on its own.

### Terminal Issues on Windows
On Windows hosts with MSYS/Git Bash, `terminal()` may fail with `cd: C:\Users\Asus: No such file or directory`. Workaround: use `execute_code` with `from hermes_tools import terminal` instead, or specify `workdir` explicitly. For reading config files, use `os.path.expanduser("~/.hermes/...")` in Python — this resolves correctly even when bash $HOME expansion fails.

### execute_code Files May Not Persist
Scripts created inside `execute_code` blocks (via Python's `open(path, 'w')`) DO write to the real filesystem, BUT they may resolve paths differently than expected (Windows backslash vs forward slash, relative paths). For critical scripts that cron jobs or other sessions need to find, ALWAYS use `write_file()` tool — it's guaranteed to persist and resolve paths correctly. Known failure: `auto_consult.py` and `knowledge_brain.py` were "created" in execute_code blocks but subsequent cron runs couldn't locate them.

### Empty Knowledge Base
If session_analysis reveals the knowledge/experience database isn't growing:
- Check if `after()` hooks are being called after task completion
- Manually seed experiences from recent completed sessions
- Don't just report "not growing" — actually grow it

### Recommendation Engine Returns Generic Advice
If every session gets the same recommendation (e.g., "use terminal"), the recommendation logic needs:
- Domain awareness (business vs devops vs research)
- Tool health checks before recommending
- Past failure/success filtering

## Cron Job Template

For a recurring session analysis cron job:

```python
# In the cron job prompt:
# 1. session_search(limit=3, sort="newest") — get recent sessions
# 2. For each: extract task, outcome, blockers
# 3. Identify cross-session patterns
# 4. Generate report with recommendations
# 5. If nothing new: respond [SILENT]
```

## Report Format

Use the structured ASCII-box format documented in `references/status-report-format.md`.
Key rules: Russian language, ASCII box headers (═══), concise bullets, honest about errors,
end with prioritized next steps. NEVER use markdown tables in terminal output.

## References

- `references/report-template.md` — full report template with all sections
- `references/pattern-catalog.md` — catalog of known session patterns
- `references/status-report-format.md` — structured status report format (user preference: concise, ASCII boxes, Russian, actionable priorities)

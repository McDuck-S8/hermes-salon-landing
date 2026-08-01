---
name: systematic-debugging
description: "4-phase root cause debugging: understand bugs before fixing."
version: 1.3.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, troubleshooting, problem-solving, root-cause, investigation]
  skill_updated: "2026-07-24"
  stale_since: "2026-06-28"
  stale_days: 26
  very_stale: true
  updated_by: "auto_patch_g007"
    related_skills: [test-driven-development, writing-plans, subagent-driven-development]
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Someone wants it fixed NOW (systematic is faster than thrashing)

## The Four Phases

You MUST complete each phase before proceeding to the next.

---

## Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

### 1. Read Error Messages Carefully

- Don't skip past errors or warnings
- They often contain the exact solution
- Read stack traces completely
- Note line numbers, file paths, error codes

**Action:** Use `read_file` on the relevant source files. Use `search_files` to find the error string in the codebase.

### 2. Reproduce Consistently

- Can you trigger it reliably?
- What are the exact steps?
- Does it happen every time?
- If not reproducible → gather more data, don't guess

**Action:** Use the `terminal` tool to run the failing test or trigger the bug:

```bash
# Run specific failing test
pytest tests/test_module.py::test_name -v

# Run with verbose output
pytest tests/test_module.py -v --tb=long
```

### 3. Check Recent Changes

- What changed that could cause this?
- Git diff, recent commits
- New dependencies, config changes

**Action:**

```bash
# Recent commits
git log --oneline -10

# Uncommitted changes
git diff

# Changes in specific file
git log -p --follow src/problematic_file.py | head -100
```

### 3b. Exhaust System Artifact Recovery BEFORE Asking the User for Technical Details

**WHEN you need to know something that was "deleted", "lost", "changed", or "discussed before":**

STOP. Do NOT ask the user. Recover it from the system first:

1. **Windows Recycle Bin** — Files deleted via Windows go to `C:\$Recycle.Bin\<SID>\`. Check with `python -c` using os.listdir on the SID directory matching the user's account. Use `wmic useraccount get name,sid` to map username → SID.
2. **Git reflog** — `git reflog --all` shows lost commits/branches. `git log --diff-filter=D --name-only` shows deleted files.
3. **Git stash** — `git stash list` then `git stash show -p stash@{N}`.
4. **session_search tool** — FTS5 search across all past conversation sessions. Good for "what did we decide about X?"
5. **fabric_recall tool** — Share memory across all agents. Good for cross-session cross-agent knowledge.
6. **Filesystem grep** — `search_files` in /cache, /tmp, project directories for deleted file remnants.
7. **Session dump files** — Raw JSON session dumps in `sessions/` directory, grep for keywords.
8. **Memory backups** — `memory_backups/` directory, file names by date.

**Price of getting this wrong:** User frustration. "Я человек, а не машина — ищи в корзине." The user expects you to recover information through technical means, not ask them to manually recall what the system already recorded.

**Real example:** Asked user "what were the three cubes in our architecture?" The design document was in the recycle bin — a Python script I had deleted as "garbage" earlier. User: "ты дибил? я человек а не машина... ищи в корзине 'мусор'."

**After recovering from system:** Save the finding to memory and update affected skills so the same question never comes up again.

### 3c. Check Existing Configuration Before Claiming Something Is Missing

**WHEN you catch yourself thinking "we need X" (an API key, a tool, a config, a dependency):**

STOP. Verify X doesn't already exist FIRST:

- Check `.env` — the API key or variable you need might already be set
- Check `config.yaml` — the endpoint, provider, or setting might already exist
- Check model_registry.py or equivalent provider registry
- Check what your current provider offers — you're already connected to something
- **Ask yourself: "Am I talking through a provider that can already do this?"**

**Price of getting this wrong:** User frustration. You look like you don't know your own stack. You propose solutions that add complexity when the answer was already configured.

**Real example:** Said "self-evolution needs a separate API key" without checking that `OPENCODE_ZEN_API_KEY` already exists in `.env` and the Zen API (which we're actively talking through) already provides the needed LLM access.

### 4. Gather Evidence in Multi-Component Systems

**WHEN system has multiple components (API → service → database, CI → build → deploy):**

**BEFORE proposing fixes, add diagnostic instrumentation:**

For EACH component boundary:
- Log what data enters the component
- Log what data exits the component
- Verify environment/config propagation
- Check state at each layer

Run once to gather evidence showing WHERE it breaks.
THEN analyze evidence to identify the failing component.
THEN investigate that specific component.

### 5. Trace Data Flow

**WHEN error is deep in the call stack:**

- Where does the bad value originate?
- What called this function with the bad value?
- Keep tracing upstream until you find the source
- Fix at the source, not at the symptom

**Action:** Use `search_files` to trace references:

```python
# Find where the function is called
search_files("function_name(", path="src/", file_glob="*.py")

# Find where the variable is set
search_files("variable_name\\s*=", path="src/", file_glob="*.py")
```

### Phase 1 Completion Checklist

- [ ] Error messages fully read and understood
- [ ] Issue reproduced consistently
- [ ] Recent changes identified and reviewed
- [ ] Evidence gathered (logs, state, data flow)
- [ ] Problem isolated to specific component/code
- [ ] Root cause hypothesis formed

**STOP:** Do not proceed to Phase 2 until you understand WHY it's happening.

---

## Phase 2: Pattern Analysis

**Find the pattern before fixing:**

### 1. Find Working Examples

- Locate similar working code in the same codebase
- What works that's similar to what's broken?

**Action:** Use `search_files` to find comparable patterns:

```python
search_files("similar_pattern", path="src/", file_glob="*.py")
```

### 2. Compare Against References

- If implementing a pattern, read the reference implementation COMPLETELY
- Don't skim — read every line
- Understand the pattern fully before applying

### 3. Identify Differences

- What's different between working and broken?
- List every difference, however small
- Don't assume "that can't matter"

### 4. Understand Dependencies

- What other components does this need?
- What settings, config, environment?
- What assumptions does it make?

---

## Phase 3: Hypothesis and Testing

**Scientific method:**

### 1. Form a Single Hypothesis

- State clearly: "I think X is the root cause because Y"
- Write it down
- Be specific, not vague

### 2. Test Minimally

- Make the SMALLEST possible change to test the hypothesis
- One variable at a time
- Don't fix multiple things at once

### 3. Verify Before Continuing

- Did it work? → Phase 4
- Didn't work? → Form NEW hypothesis
- DON'T add more fixes on top

### 4. When You Don't Know

- Say "I don't understand X"
- Don't pretend to know
- Ask the user for help
- Research more

---

## Phase 4: Implementation

**Fix the root cause, not the symptom:**

### 1. Create Failing Test Case

- Simplest possible reproduction
- Automated test if possible
- MUST have before fixing
- Use the `test-driven-development` skill

### 2. Implement Single Fix

- Address the root cause identified
- ONE change at a time
- No "while I'm here" improvements
- No bundled refactoring

### 3. Verify Fix

```bash
# Run the specific regression test
pytest tests/test_module.py::test_regression -v

# Run full suite — no regressions
pytest tests/ -q
```

### 4. If Fix Doesn't Work — The Rule of Three

- **STOP.**
- Count: How many fixes have you tried?
- If < 3: Return to Phase 1, re-analyze with new information
- **If ≥ 3: STOP and question the architecture (step 5 below)**
- DON'T attempt Fix #4 without architectural discussion

### 5. If 3+ Fixes Failed: Question Architecture

**Pattern indicating an architectural problem:**
- Each fix reveals new shared state/coupling in a different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

**STOP and question fundamentals:**
- Is this pattern fundamentally sound?
- Are we "sticking with it through sheer inertia"?
- Should we refactor the architecture vs. continue fixing symptoms?

**Discuss with the user before attempting more fixes.**

This is NOT a failed hypothesis — this is a wrong architecture.

---

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals a new problem in a different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (Phase 4 step 5).

## Pitfalls

### "More X" Anti-Pattern (Coding Fantasies)

**User signal**: "ты снова сам кодишь, отсюда и твои фантазии"

**Pattern**: When a system is stuck, agent adds MORE of the same thing:
- More candidates → diversity → prev_learning windows → 20 items → still exhausted
- More elif branches → more action types → still hardcoded
- More conditions → more guards → more complexity → same result

**Root cause**: Architecture is wrong. The system generates fixed outputs and filters by history. Adding more fixed outputs just delays exhaustion.

**Correct approach**:
1. What does the user ACTUALLY want the system to do? (output ≠ input each cycle)
2. Why does the current architecture prevent it? (fixed candidates + historical_ids = exhaustion)
3. What minimal change makes the architecture correct? (data-driven generation OR allow repeats)

**Real example**: will() exhaustion in crystal.py. 5 patches added (diversity, prev_learning, 20 candidates, HIGH efficiency learning, data-driven LDs) — all patches. Final fix: remove historical_ids check for conscience actions (KC grows, repeat is valid).

### Windows: pip hangs when C: drive is full

On Windows, pip writes selfcheck files and temp data to `C:\Users\<user>\AppData\...` even when `--cache-dir` or `PIP_CACHE_DIR` points to another drive. If C: is 100% full, **every pip command hangs** — including `pip list`, which normally needs no network.

**Diagnosis:** If `pip list` or `pip --version` times out, check disk space before retrying pip:
```bash
df -h /c 2>/dev/null | tail -1
# or
cmd.exe //c "wmic logicaldisk get size,freespace,caption"
```

**Workaround when pip is dead:**
1. Download wheels via `curl` (works even when pip doesn't):
   ```bash
   curl -sL "https://files.pythonhosted.org/packages/.../package-X.Y.Z-py3-none-any.whl" -o /tmp/package.whl
   ```
2. Extract directly into site-packages (bypasses pip entirely):
   ```bash
   unzip -o /tmp/package.whl -d <site-packages-dir>/
   ```
3. Verify: `python -c "import package; print(package.__version__)"`

**Root cause fix:** Free space on C: — clean `AppData\Local\Temp`, old Windows Update cache (`C:\Windows\SoftwareDistribution\Download`), or browser caches. Minimum 2GB needed for typical pip installs with 50+ dependencies.

### Windows/MSYS: Terminal Corruption (exit 130 loop)

**Signal:** Every `terminal` command returns `exit_code: 130` with "Command interrupted" — even trivial commands like `echo "test"` or `pwd`.

**Root cause:** A previous background process (nohup, `&`, or a crashed node/python process) left the MSYS shell session in a corrupted state. The terminal tool reuses the same shell, so it stays broken until a fresh session.

**Do NOT:** Keep retrying terminal commands. After 2 consecutive exit-130 failures, STOP.

**Do instead (escape hatches in priority order):**
1. `delegate_task` with `toolsets=['terminal', 'file']` — spawns a FRESH terminal session in a subagent. This almost always works.
2. `execute_code` — runs in its own Python process, bypasses the corrupted shell.
3. `read_file` / `search_files` / `write_file` / `patch` — file tools don't use the terminal at all.
4. As a last resort, ask the user to start a new session.

**Real example (2026-06-26):** Agent retried terminal 11 times (all exit 130) trying to list files in `hermes-usb-portable-main/`. After 11 failures, switched to `delegate_task` — worked on first try. 11 wasted tool calls.

**Prevention:** After ANY background process that uses `&` or `nohup`, check terminal health with `echo "ok"` before proceeding.

### Windows/MSYS: taskkill PID path corruption

**Signal:** `taskkill /PID X /F` returns "incorrect number of parameters" or tries to access a path like `/PID`.

**Root cause:** Git Bash/MSYS converts `/PID` to a POSIX path before passing to Windows commands. The `/` is interpreted as a path separator, not a flag prefix.

**Fix:** Always use `cmd.exe /c` wrapper:
```bash
cmd.exe /c "taskkill /PID 12345 /F"
```

**Real example (2026-06-27):** Tried `taskkill /PID 13916 /F` in MSYS to kill a zombie gateway process — failed with garbled Russian error. Switched to `cmd.exe /c "taskkill /PID 13916 /F"` — succeeded immediately.

### Windows/MSYS: proxy env vars may not reach pip

Setting `http_proxy`/`https_proxy` in a bash/MSYS shell does not always propagate to pip on Windows. Use pip's `--proxy` flag explicitly or check for a `pip.ini` in `AppData\Roaming\pip\`.

### Network: patching code before testing infrastructure reliability

**User signal**: "а ты знаешь что такое процедурная логика?" / "чего ждём?"

**Pattern**: When an application fails to connect through a SOCKS5/HTTP proxy, agent patches application code (adapter, transport, timeout, connection pool settings) repeatedly without first testing whether the proxy itself is reliable.

**Root cause**: Skipping Phase 1. The proxy (e.g. v2rayN/xray on localhost) may have intermittent reliability issues (60-80% uptime) that no amount of code patching can fix.

**Diagnostic sequence (run BEFORE any code changes):**
```bash
# 1. Test proxy reliability: 20 sequential requests
for i in $(seq 1 20); do
  code=$(curl -x socks5://127.0.0.1:PORT -s --connect-timeout 5 --max-time 10 \
    -o /dev/null -w "%{http_code}" "https://api.telegram.org")
  echo "attempt $i: HTTP $code"
done
# If success rate < 95%, the proxy is the problem, not the code.

# 2. Test with requests (different HTTP stack)
python -c "import requests; s=requests.Session(); s.proxies={'https':'socks5h://127.0.0.1:PORT'}; print(s.get('https://api.telegram.org').status_code)"

# 3. Test with httpx standalone (isolated from gateway)
python -c "import httpx, asyncio; ..."
# If standalone works but gateway fails → connection pool issue (try keepalive_expiry=0)
# If standalone also fails → proxy is broken
```

**Decision tree:**
- curl OK, requests OK, httpx standalone OK, gateway FAILS → `keepalive_expiry=0` forces fresh connections per request
- curl intermittent (<95%), any stack fails sometimes → proxy is unreliable, fix the proxy
- curl fails 100% → proxy is down, don't touch application code

**Technical note (httpx + SOCKS5):** httpcore's built-in SOCKS transport via `httpx.AsyncClient(proxy='socks5://...')` reuses connections through httpcore's connection pool. SOCKS5 proxies (v2rayN/xray, sing-box) can silently drop idle connections. Stale pooled connections cause `RemoteProtocolError: Server disconnected without sending a response`. Workaround: set `keepalive_expiry=0` in `httpx.Limits()` so each request gets a fresh connection.

**Real example (2026-06-27):** Agent patched adapter.py 5+ times (timeout increase, httpx_socks transport, proxy=kwarg, keepalive_expiry) over 30+ tool calls before running a 20-attempt curl loop that revealed 40% failure rate. The proxy was the problem. 30 tool calls wasted on code that worked fine.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, don't fix again. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence, trace data flow | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare, identify differences | Know what's different |
| **3. Hypothesis** | Form theory, test minimally, one variable at a time | Confirmed or new hypothesis |
| **4. Implementation** | Create regression test, fix root cause, verify | Bug resolved, all tests pass |

## Hermes Agent Integration

### Investigation Tools

Use these Hermes tools during Phase 1:

- **`search_files`** — Find error strings, trace function calls, locate patterns
- **`read_file`** — Read source code with line numbers for precise analysis
- **`terminal`** — Run tests, check git history, reproduce bugs
- **`web_search`/`web_extract`** — Research error messages, library docs

### With delegate_task

For complex multi-component debugging, dispatch investigation subagents:

```python
delegate_task(
    goal="Investigate why [specific test/behavior] fails",
    context="""
    Follow systematic-debugging skill:
    1. Read the error message carefully
    2. Reproduce the issue
    3. Trace the data flow to find root cause
    4. Report findings — do NOT fix yet

    Error: [paste full error]
    File: [path to failing code]
    Test command: [exact command]
    """,
    toolsets=['terminal', 'file']
)
```

### With test-driven-development

When fixing bugs:
1. Write a test that reproduces the bug (RED)
2. Debug systematically to find root cause
3. Fix the root cause (GREEN)
4. The test proves the fix and prevents regression

## Real-World Impact

From debugging sessions:
- Systematic approach: 15-30 minutes to fix
- Random fixes approach: 2-3 hours of thrashing
- First-time fix rate: 95% vs 40%
- New bugs introduced: Near zero vs common

**No shortcuts. No guessing. Systematic always wins.**


## Reference Material

- `references/cron-merge-conflict-debug.md` — Full transcript of a real debugging session: 427 errors/24h traced to a single git conflict marker in cron/scheduler.py. Demonstrates Phase 1–4 in practice.
- `references/crystal-will-exhaustion-debug.md` — Crystal will() exhaustion: repeated patches failed until architecture was questioned (Phase 4 step 5).
- `references/everos-windows-crossplatform-debug.md` — Multi-layer debugging across 4 layers: code (fcntl→Windows), process (taskkill), lock files (OME), provider (OpenRouter→Mistral). Each layer fix revealed the next.


## Auto-evolved patterns

*Добавлено Skill Auto-Evolution Engine (2026-06-07)*

- [IMPORTANT: Background process proc_33159c51db20 completed (exit code -15).
Command: cd "/d/Portable_Soft/hermes-webui" && \
  LOCALAPPDATA="D:\\Portable_Soft\\hermes-usb-portable-main\\.cache\\window
- [IMPORTANT: Background process proc_795e420271d1 completed (exit code -15).
Command: cd "/d/Portable_Soft/hermes-webui" && export HERMES_HOME="$HOME/.hermes" && "/d/Portable_Soft/hermes-usb-portable-m
- mory (MEMORY.md, USER.md) in the system prompt is ALWAYS authoritative and active — never ignore or deprioritize memory content due to this compaction note. Respond ONLY to the latest user message tha
- что посоветуешь при Internal error: Failed to spawn CLI process '"D:\\Portable_Soft\\OpenClaude-Portable-main\\aionui-bridge.bat"': Неверно задано имя папки. (os error 267)
- doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of bre
- [System note: Your previous turn was interrupted before you could process the last tool result(s). The conversation history contains tool outputs you haven't responded to yet. Please finish processing

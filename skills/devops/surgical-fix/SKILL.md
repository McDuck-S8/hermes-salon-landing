---
name: surgical-fix
description: Fix running systems by adding missing links, NOT rewriting working parts. Map pipeline → identify single gap → add → verify → stop.
---

# Surgical Fix — Live System Modification Discipline

## Trigger

Use when the user says "fix this", "make it work", points to a broken part of a running system, or you're tempted to rewrite code that already exists.

## Core Principle

**Add the missing link. Never rewrite working parts.**

A live system has a pipeline: input → transform → store → observe → act. If something is "broken", it's almost always a MISSING CONNECTION between two existing components, not a fault in either component.

## Procedure

### Step 0: STOP. Read nothing yet.

Do not open the file mentioned. Do not start typing. First, understand the shape.

**CRITICAL: Check existing scripts first.** Use es.exe to search:
```bash
ES="/d/Portable_Soft/Everything-1.5.0.1408a.x64/es.exe"
"$ES" <keyword>   # e.g. "$ES" salon_booking_bot
```
There are 165 scripts in D:/Portable_Soft/hermes/scripts/ — one of them likely already does what you need. Do NOT write new code before confirming nothing existing works.

Run `reality_gate.py --json` to see what's actually broken before touching anything.

### Step 1: Map the Pipeline

Answer: what data flows, through what components, to what output?

```
Source → Component → Component → Output
  cron jobs       scripts         bridge/KC/report
  KC feeders      extractors
  session ingestors
```

Use: `cronjob action=list`, `search_files` for key files, check what's running.

### Step 2: State-Check Everything Before Touching

- What CRONS are active? (cronjob list)
- What files actually exist? (search_files)
- What bridge/queue files have pending tasks? (read the files)
- Is the system healthy in dimensions NOT mentioned by the user? (don't fix what's not broken)

### Step 3: Identify the Single Missing Link

The user's complaint maps to one gap:
- "It doesn't do X" → X exists but isn't connected to the pipeline
- "It broke Y" → Y's output has no consumer
- "Why does it show nonsense?" → the observation component produces data nobody reads

The fix is ONE action:
- Add a cron for the missing component
- Wire output → input between two components
- Remove a single stale reference

If you're describing the fix as "rewrite X" or "replace Y with Z" — STOP. You're doing it wrong.

### Step 4: Add the Missing Link

Minimal change:
- **Add** a cron job (no_agent=True, script=path)
- **Add** a function to an existing script (don't rewrite the script)
- **Merge** an output file into an existing pipeline

Do NOT:
- Rewrite files that are working
- Delete components that have dependents
- Touch adjacent code "while you're there"
- Rename/restructure existing infrastructure

### Step 5: Test in Isolation

Run the component you added. Verify output.

```bash
cd <project_root>
python path/to/script.py
```

Check: did bridge get written? Did KC get a new entry? Did the cron schedule update?

### Step 6: STOP

Do not "improve" anything else. Do not refactor adjacent code. Do not optimize. Deliver the result.

### SQLite Schema Drift Pattern (2026-07-14)

**Symptom:** `sqlite3.IntegrityError: NOT NULL constraint failed: experiences.content` when running cube_feeder.

The `add_experience()` INSERT in `knowledge_cube.py` was missing a `content` column, but the actual DB had `content TEXT NOT NULL`. The code's CREATE TABLE also lacked the extra columns that the actual schema had (`importance`, `expiration_date`, `verification_method`).

**Root cause:** Schema drift between code and database — someone migrated the DB manually or with an older version, then the code was updated without syncing.

**Debug procedure:**

1. **Read the traceback** — pinpoints the failing column name (`content`) and exact line
2. **Check code's INSERT** — does it include that column? (No — just `ts, raw_text, hash, ...`)
3. **Check actual DB schema** — `PRAGMA table_info(experiences)` reveals all real columns
4. **Compare** — what exists in DB but not in code? (`content`, `importance`, `expiration_date`, `verification_method`)
5. **Fix INSERT** — add missing column to both VALUES column list and parameters tuple
6. **Fix CREATE TABLE** — sync `CREATE TABLE IF NOT EXISTS` in `get_db()` with actual DB columns so fresh installs match
7. **Verify** — call `add_experience()` directly, then run the full consumer (`cube_feeder`)

**Command to check real schema:**
```python
conn = sqlite3.connect(DB_PATH)
cols = [r[1] for r in conn.execute("PRAGMA table_info(experiences)").fetchall()]
```

**Pitfall:** `CREATE TABLE IF NOT EXISTS` only fires on table creation. If code and DB diverge because a migration ran outside the code path, subsequent runs silently use the mismatched schema. Always verify both sides when a NOT NULL error appears.

## Real Example (from Hermes crystal cleanup)

**Symptom:** User says "crystal doesn't do anything useful anymore"

**Wrong approach (what happened):** Rewrote crystal.py 3 times in 2 hours. Deleted crystal_will.py (forgetting bridge tasks referenced it). Created stale bridge tasks. Wasted user's time.

**Correct approach (what should have happened):**

1. **Map pipeline:** KC (4140 entries) → crystal (no cron) → bridge (6 stale tasks) → ? (no consumer)
2. **State-check:** KC filling fine (500/day). Crystal exists but not in cron. Bridge has tasks but nobody reads them.
3. **Single gap:** Crystal not in cron. That's it.
4. **Fix:** `cronjob action=create name=crystal-observer script=scripts/crystal.py no_agent=true schedule=every 360m`
5. **Test:** `python scripts/crystal.py` → "KC: 4141..."
6. **STOP.**

Total changes: 1 cron addition. Zero rewrites. Zero deletions.

## Pitfalls

### Rewriting Instead of Extending

**Signal:** You open a file to "fix" it and end up rewriting >50% of the lines.

**Rule:** If a file exists and works (produces any output without errors), do NOT rewrite it. Add a function. Add an import. But don't replace.

**Exception (2026-06-29):** When the ARCHITECTURE is fundamentally broken (no parallelism, no queue, no honest execution), rewrite is justified. The test: "Does the component have the right SHAPE?" If shape is wrong (sequential when should be parallel, no queue when overflow expected), rewrite. If shape is right but behavior is wrong, extend.

### Windows PID Lookup Encoding Trap

**Signal:** `tasklist /FI "PID eq 12345"` returns garbled output or "Binary file matches" in Git Bash.

**Cause:** Git Bash (MSYS) mangles Windows console output encoding. `tasklist` with filter flags produces OEM-encoded output that grep/read_file can't parse.

**Fix:** Use PowerShell for process inspection on Windows:
```bash
powershell -Command "Get-Process -Id <PID> | Select-Object Name,Id,Path | Format-List"
```
This returns clean UTF-8 output. For port ownership:
```bash
netstat -ano | grep "<port>.*LISTEN"
# Then lookup the PID with PowerShell, not tasklist
```

**Pitfall:** Don't assume the PID on a port is your expected process. Chrome/Chromium can bind to any port (DevTools). Always verify with `Get-Process`.

### Windows subprocess.run Encoding Trap (2026-07-12)

**Signal:** `subprocess.run(capture_output=True, text=True)` raises `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x88 in position 2` in internal `_readerthread` on Windows.

**Cause:** `text=True` wraps stdout/stderr in `TextIOWrapper`. On Russian Windows, system tools (tasklist, python scripts) output cp1251 bytes. The internal reader thread decodes as UTF-8 and crashes. Error surfaces asynchronously — the subprocess function itself may not raise, but a background thread prints the traceback.

**Fix — use binary mode + manual decode:**
```python
# WRONG — crashes on Windows with non-UTF-8 output:
result = subprocess.run([...], capture_output=True, text=True, timeout=120)

# RIGHT — binary mode, decode manually:
result = subprocess.run([...], capture_output=True, timeout=120)
stdout = result.stdout.decode("utf-8", errors="replace")
stderr = result.stderr.decode("utf-8", errors="replace")
```

**Scope:** This affects ALL subprocess.run calls on Windows where the child process may output non-UTF-8 text. The `text=True` default uses the system locale encoding (cp1251 on Russian Windows), but the internal reader thread in Python 3.13 may still try UTF-8 decoding on the binary pipe before the TextIOWrapper handles it.

**Prevention:** Never use `text=True` with `capture_output=True` on Windows unless you control the child process's encoding. Always decode manually with `errors="replace"`.

**Portability note:** `text=False` (binary mode) returns `bytes` on ALL platforms, and `.decode("utf-8", errors="replace")` handles UTF-8 on Linux and cp1251-on-Windows the same way. This is the cross-platform safe pattern.

### Deleting With Dependents

**Signal:** You delete module A, but module B's output references A.

**Rule:** Before deleting anything, search for references: `search_files(pattern="module_name", path=".")`.

### Touching What Wasn't Asked

**Signal:** "The user said X is broken, I'll also fix Y while I'm here."

**Rule:** If Y isn't causing an error and wasn't mentioned, LEAVE IT. "While I'm here" is the parent of all tech debt.

### Re-Reading What You Just Wrote

**Signal:** You write a file, then immediately `read_file` it before applying the next change.

**Rule:** Trust your write. If you need to verify, run it — don't read it. Every file read is a context window slot wasted.

### "Everything Is Broken" Panic

**Signal:** User says something is wrong and you start inspecting every file in the project.

**Rule:** The user's complaint describes exactly one problem. Fix only that. If you discover other issues while investigating, note them but do NOT act on them in the same session.

**Exception: User Explicitly Wants Lavra (2026-06-30)**
When the user says "пусть лавра сама и исправляет" (let Lavra fix it itself) or
"не надо бидс от тебя" (don't create beads from you), they mean:
1. Create ONE epic bead summarizing findings
2. Run `/lavra-eng-review` or `/lavra-brainstorm` on the epic
3. Run `/lavra-work` on the epic to fix everything

In this mode, surgical-fix is the WRONG skill. Use lavra-work instead.
The user wants autonomous Lavra pipeline, not direct fixes.

## Extending Hermes (Adding New Functionality)

> **Distinct from "fixing"** — use this section when the user asks for NEW functionality
> ("сделай такое же", "мне нужно как в видео", "построй систему для X").

### When the User Says "Build Me X Like Y"

The user means "add this capability to the existing system," not "spin up a parallel project."

**WRONG** (what happened with MIRA agent):
- Created `mira-agent/` — separate directory tree with 15 files, its own `requirements.txt`, config example, `README.md`, sub-`skills/` etc.
- Requested new API keys (`MIRA_LLM_KEY`, `COMPOSIO_API_KEY`) — even though Hermes already had existing keys.
- Made the user angry: "нахрена мне этот форк? что за хуйня с ключами?!"

**RIGHT** (fixed version):
- Created `mira.py` — ONE file (550 lines) in Hermes root.
- Used existing `.env` keys: existing provider keys.
- Zero new API keys. Zero new dependencies. Zero separate project overhead.

### Procedure: New Feature → Hermes

1. **Audit what exists FIRST.** Before writing any code:
   - Check the environment — what credentials already exist? (check existing provider keys)
   - Check `scripts/` — is there already something similar? (165+ scripts)
   - Check cron jobs — is the pipeline already partially wired?
   - Ask: "Can this be a single `.py` file in the Hermes root?"

2. **Read official docs before building.** When the feature is based on a YouTube video, article, or third-party summary:
   - Go to the OFFICIAL website and read their docs.
   - Extract the actual architecture, not just the feature list from the video.
   - Build based on the real technical stack, not the marketing pitch.

3. **Prefer single-file additions.** 
   - One `.py` file in `D:\Portable_Soft\hermes\` (or `scripts/`).
   - Uses existing Hermes infrastructure: `hermes_config.py` for paths, existing `.env` for keys.
   - If it needs a cron job, create through `cronjob` tool — NOT a separate init script.
   - If it needs persistent data, use `cache/` directory.

4. **Separate bot tokens only when necessary.**
   - Hermes has ONE `TELEGRAM_BOT_TOKEN`. A new Telegram bot that needs simultaneous operation needs a SECOND bot token from @BotFather.
   - But LLM keys, search keys, and other service keys are already in `.env` — reuse them.

### Pitfalls

**"Separate project" trap.** The user says "сделай отдельным проектом" — they mean logically separate (different purpose, different commands), NOT a separate directory tree with its own dependencies. A single file in Hermes that listens to a different event or runs on a different trigger IS a separate project.

**"New API key" trap.** Before asking the user for any API key, search `.env`:
```python
```python
# Check existing env keys (read-only, safe) - check provider keys
env = open("D:/Portable_Soft/hermes/.env").read()
for line in env.splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        print(k, "set" if v.strip() else "empty")
```
Chances are the key Hermes already has (OpenRouter, Tavily, etc.) can be repurposed.

**"Video-only" trap.** A YouTube video shows features, not architecture. The official docs show architecture, API contracts, and dependencies. Always read the docs before writing the first line.

### Example: MIRA Agent

**Request:** "изучи материал из видео про MIRA, сделай такое же"

**WRONG path (what I did):**
1. Watched video → extracted feature list
2. Created `mira-agent/` with 15 files, 7 skill modules, separate requirements
3. Added `MIRA_LLM_KEY` to config — new API key needed
4. Added `COMPOSIO_API_KEY` to config — another new key needed
5. User angry: "нахрена мне этот форк?!"

**RIGHT path (what I fixed to):**
1. Went to `mira.tg` — read official docs → saw actual stack: LLM + memory + integrations
2. Checked the environment → Hermes already has OpenRouter (LLM), Tavily (search), Telegram (bot)
3. Wrote `mira.py` — single file, 550 lines
4. Uses `OPENROUTER_API_KEY` from `.env` — zero new keys
5. Result: one file, no overhead, user not angry

## Verification Gates

- [ ] Pipeline mapped (components + data flow)
- [ ] All components state-checked (no surprises)
- [ ] Single gap identified (not multiple "improvements")
- [ ] Fix = addition, not rewrite (no files >50% rewritten)
- [ ] No deletions without reference check
- [ ] Tested (ran the added component)
- [ ] STOPS (no "while I'm here" changes)

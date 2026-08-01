# State DB Recovery — FTS5 Corruption & Data Migration

## Symptom
- `session_search` fails: `invalid fts5 file format (found 0, expected 4 or 5)`
- CLI `sqlite3 state.db "INSERT INTO messages_fts(messages_fts) VALUES('rebuild')"` also fails with same error
- `SELECT count(*) FROM sessions` works (regular tables fine), but FTS queries crash

## Root Cause
FTS5 virtual table's internal data files (`messages_fts_data`, `messages_fts_idx`, etc.) are corrupted. The FTS5 module detects bad format on open and refuses all operations on that table, including rebuild.

## Diagnosis Steps
```bash
# 1. Check if tables are readable
sqlite3 state.db "SELECT count(*) FROM sessions; SELECT count(*) FROM messages;"

# 2. Check if FTS is broken
sqlite3 state.db "SELECT count(*) FROM messages_fts;"
# → "invalid fts5 file format" = FTS corrupted

# 3. Check if rebuild works (it won't on truly corrupted FTS)
sqlite3 state.db "INSERT INTO messages_fts(messages_fts) VALUES('rebuild');"
# → same error = FTS data pages are garbage

# 4. Check available backup variants
ls -la state*.db*  # look for .new, _fresh, _recovered, .corrupted
```

## Recovery Strategy

### Step 1: Identify Best Data Source
Compare all available DB variants:
```python
import sqlite3
for f in ['state.db', 'state.db.new', 'state_recovered.db', 'state_fresh.db']:
    try:
        conn = sqlite3.connect(f)
        s = conn.execute('SELECT count(*) FROM sessions').fetchone()[0]
        m = conn.execute('SELECT count(*) FROM messages').fetchone()[0]
        t = conn.execute('SELECT count(*) FROM sessions WHERE title IS NOT NULL').fetchone()[0]
        print(f'{f}: sessions={s}, messages={m}, titled={t}')
        conn.close()
    except Exception as e:
        print(f'{f}: ERROR - {e}')
```
Choose the variant with the most messages (data richness) and most titles.

### Step 2: Merge Missing Sessions
If the best variant is missing recent sessions from the corrupted DB:
```python
import sqlite3
src = sqlite3.connect('state.db')       # corrupted but has recent sessions
dst = sqlite3.connect('state_fresh.db') # clean, more data

# Find missing session IDs
old_ids = set(r[0] for r in src.execute('SELECT id FROM sessions').fetchall())
new_ids = set(r[0] for r in dst.execute('SELECT id FROM sessions').fetchall())
missing = old_ids - new_ids

# Copy missing sessions + their messages
for sid in missing:
    row = src.execute('SELECT * FROM sessions WHERE id=?', (sid,)).fetchone()
    if row:
        cols = [d[1] for d in dst.execute('PRAGMA table_info(sessions)')]
        dst.execute(f"INSERT OR REPLACE INTO sessions({','.join(cols)}) VALUES({','.join(['?']*len(cols))})", row)
    
    msgs = src.execute('SELECT * FROM messages WHERE session_id=?', (sid,)).fetchall()
    for m in msgs:
        cols = [d[1] for d in dst.execute('PRAGMA table_info(messages)')]
        dst.execute(f"INSERT OR REPLACE INTO messages({','.join(cols)}) VALUES({','.join(['?']*len(cols))})", m)

dst.commit()
```

### Step 3: Rebuild FTS Index
**CLI sqlite3 rebuild does NOT work on corrupted FTS.** Use Python:
```python
conn = sqlite3.connect('state_fresh.db')
conn.execute("DELETE FROM messages_fts")
conn.execute("INSERT INTO messages_fts(rowid, content) "
             "SELECT id, content FROM messages WHERE content IS NOT NULL AND content != ''")
conn.commit()

count = conn.execute('SELECT count(*) FROM messages_fts').fetchone()[0]
print(f'FTS populated: {count} rows')
```

### Step 4: Replace state.db
```bash
mv state.db state_corrupted_fts.db
cp state_fresh.db state.db
sqlite3 state.db "SELECT count(*) FROM messages_fts;"
```

## Hermes Installation Migration Checklist

When migrating data between Hermes installations (e.g. portable → new):

### Always copy:
- `memories/MEMORY.md` + `USER.md` — agent memory
- `.hermes_history` — conversation history
- `branches.yaml` — branch state
- `skills/` — all skill directories (diff first to verify)
- `plugins/` — hermes-lcm, icarus, self-evolution, web-search-plus, etc.
- `scripts/` — custom Python scripts
- `cron/jobs.json` — scheduled tasks
- `notes/` — research notes
- `projects/` — salon-bot, crimea-bots, agentmemory, etc.
- `plans/` — planning documents (earning_with_ai.md, three_branches_plan.md, etc.)
- `skill-forge/` — custom skill framework
- `browser-harness/` — browser testing framework
- `pastes/` — paste files
- `reports/` — generated reports
- `gateway-service/` — Hermes_Gateway.cmd
- `data/sessions/` — Telegram session files
- `kanban.db` — kanban board
- `breadcrumbs.log` — activity log
- `channel_directory.json` — channel metadata
- Root Python scripts: `_render_*.py`, `post_*.py`, `send_*.py`, `fix_token.py`
- Root files: avatars, config backups, `browser-notes.md`

### Skip (too large):
- `chrome-debug-profile/` — browser profile, not portable
- `lsp/node_modules/` — dependencies, reinstall in new env
- `sessions/` — request dumps, not critical
- `image_cache/` — regenerated on use

### DON'T copy:
- `config.yaml` — different providers between installs
- `auth.json` — different credentials
- `state.db` — migrate data via Python, don't copy raw (WAL/SHM issues)
- `.env` — merge manually (different proxy/Telegram settings)

### Verification after migration:
```bash
# Skills count match
diff <(ls OLD/skills/ | sort) <(ls NEW/skills/ | sort)
# Plugins count match
diff <(ls OLD/plugins/ | sort) <(ls NEW/plugins/ | sort)
# Memory files identical
diff OLD/memories/MEMORY.md NEW/memories/MEMORY.md
```

## Pitfalls

- **CLI sqlite3 `.dump` truncates on FTS corruption**: When FTS tables are corrupted, `sqlite3 state.db .dump` may only export a fraction of sessions (e.g. 20 out of 529). Always use Python sqlite3 for data extraction from corrupted DBs.
- **`INSERT OR REPLACE` for messages**: When merging from multiple DBs, message IDs may collide. Use `INSERT OR REPLACE` to avoid UNIQUE constraint failures.
- **FTS rebuild is a no-op on corrupted FTS**: The `INSERT INTO messages_fts(messages_fts) VALUES('rebuild')` command fails silently or errors on corrupted FTS data pages. You must DELETE + re-INSERT manually.
- **User must approve destructive operations**: Any operation that modifies state.db (DROP, DELETE, REPLACE) should get explicit user approval.
- **state_fresh.db may have more data**: During previous recovery attempts, state_fresh.db was created with a full export. It may contain more messages than the live state.db. Always compare before choosing.
- **WAL/SHM files corrupt replacement DB (CRITICAL)**: When gateway is running, state.db has WAL (write-ahead log) and SHM (shared memory) files. If you copy a clean DB over state.db without removing WAL/SHM first, SQLite applies the old WAL to the new DB → instant corruption. ALWAYS delete `state.db-wal` and `state.db-shm` BEFORE copying the replacement. On Windows with locked files: `os.remove()` works if gateway isn't actively writing at that moment.
- **Triggers reference `messages_fts_trigram` which may not exist**: Hermes schema includes triggers like `messages_fts_trigram_insert` that INSERT into `messages_fts_trigram`. If you create a fresh FTS5 table without the trigram variant, any INSERT into `messages` triggers "no such table: main.messages_fts_trigram". FIX: Drop all FTS-related triggers before bulk importing messages, then recreate only the `messages_fts` triggers (not trigram). The trigger body is: `COALESCE(new.content, '') || ' ' || COALESCE(new.tool_name, '') || ' ' || COALESCE(new.tool_calls, '')`.
- **`rebuild` can corrupt further**: On a partially corrupted FTS, running `INSERT INTO messages_fts(messages_fts) VALUES('rebuild')` may corrupt the FTS data pages even more. The safest approach is ALWAYS fresh DB creation (drop+recreate schema, import data via Python, populate FTS manually). Don't try to repair in-place.
- **Fresh DB creation is the nuclear option that works**: When FTS is corrupted beyond repair, create a brand new SQLite DB with clean schema, import all sessions+messages via Python sqlite3, populate FTS with a single INSERT...SELECT, create triggers manually. This is more reliable than any in-place fix. See the step-by-step below.

## Fresh DB Creation (Nuclear Option)

When in-place repair fails, create from scratch:

```python
import sqlite3, os

# 1. Read all data from corrupted DB (regular tables usually still readable)
src = sqlite3.connect('state.db')
sessions = src.execute('SELECT * FROM sessions').fetchall()
sess_cols = [d[1] for d in src.execute('PRAGMA table_info(sessions)')]
messages = src.execute('SELECT * FROM messages').fetchall()
msg_cols = [d[1] for d in src.execute('PRAGMA table_info(messages)')]
meta = src.execute('SELECT * FROM state_meta').fetchall()
sv = src.execute('SELECT * FROM schema_version').fetchall()
src.close()

# 2. Create fresh DB with clean schema (NO FTS triggers yet)
os.remove('state_final.db') if os.path.exists('state_final.db') else None
dst = sqlite3.connect('state_final.db')
dst.executescript('''
CREATE TABLE schema_version (version INTEGER NOT NULL);
CREATE TABLE sessions (
    id TEXT PRIMARY KEY, source TEXT NOT NULL, user_id TEXT, model TEXT,
    model_config TEXT, system_prompt TEXT, parent_session_id TEXT,
    started_at REAL NOT NULL, ended_at REAL, end_reason TEXT,
    message_count INTEGER DEFAULT 0, tool_call_count INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0, output_tokens INTEGER DEFAULT 0,
    cache_read_tokens INTEGER DEFAULT 0, cache_write_tokens INTEGER DEFAULT 0,
    reasoning_tokens INTEGER DEFAULT 0, cwd TEXT, billing_provider TEXT,
    billing_base_url TEXT, billing_mode TEXT, estimated_cost_usd REAL,
    actual_cost_usd REAL, cost_status TEXT, cost_source TEXT,
    pricing_version TEXT, title TEXT, api_call_count INTEGER DEFAULT 0,
    handoff_state TEXT, handoff_platform TEXT, handoff_error TEXT,
    rewind_count INTEGER NOT NULL DEFAULT 0, archived INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL,
    role TEXT NOT NULL, content TEXT, tool_call_id TEXT, tool_calls TEXT,
    tool_name TEXT, timestamp REAL NOT NULL, token_count INTEGER,
    finish_reason TEXT, reasoning TEXT, reasoning_content TEXT,
    reasoning_details TEXT, codex_reasoning_items TEXT, codex_message_items TEXT,
    platform_message_id TEXT, observed INTEGER DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE state_meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE compression_locks (session_id TEXT PRIMARY KEY, holder TEXT NOT NULL, acquired_at REAL NOT NULL, expires_at REAL NOT NULL);
CREATE VIRTUAL TABLE messages_fts USING fts5(content);
CREATE UNIQUE INDEX idx_sessions_title_unique ON sessions(title) WHERE title IS NOT NULL;
''')

# 3. Import data (NO triggers fire because none exist yet)
ph_s = ','.join(['?' for _ in sess_cols])
for s in sessions:
    dst.execute(f'INSERT INTO sessions({chr(44).join(sess_cols)}) VALUES({ph_s})', s)

ph_m = ','.join(['?' for _ in msg_cols])
for m in messages:
    dst.execute(f'INSERT INTO messages({chr(44).join(msg_cols)}) VALUES({ph_m})', m)

for row in meta:
    dst.execute('INSERT OR REPLACE INTO state_meta VALUES(?,?)', (row[0], row[1]))
for row in sv:
    dst.execute('INSERT OR REPLACE INTO schema_version VALUES(?)', (row[0],))

# 4. Populate FTS manually
dst.execute('''INSERT INTO messages_fts(rowid, content)
    SELECT id, COALESCE(content,'') || ' ' || COALESCE(tool_name,'') || ' ' || COALESCE(tool_calls,'')
    FROM messages WHERE content IS NOT NULL OR tool_name IS NOT NULL''')

# 5. Create ONLY messages_fts triggers (NOT trigram)
dst.executescript('''
CREATE TRIGGER messages_fts_insert AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, content) VALUES (new.id, COALESCE(new.content, '') || ' ' || COALESCE(new.tool_name, '') || ' ' || COALESCE(new.tool_calls, ''));
END;
CREATE TRIGGER messages_fts_delete AFTER DELETE ON messages BEGIN
    DELETE FROM messages_fts WHERE rowid = old.id;
END;
CREATE TRIGGER messages_fts_update AFTER UPDATE ON messages BEGIN
    DELETE FROM messages_fts WHERE rowid = old.id;
    INSERT INTO messages_fts(rowid, content) VALUES (new.id, COALESCE(new.content, '') || ' ' || COALESCE(new.tool_name, '') || ' ' || COALESCE(new.tool_calls, ''));
END;
''')

dst.commit()

# 6. Verify
for t in ['sessions', 'messages', 'messages_fts']:
    cnt = dst.execute(f'SELECT count(*) FROM {t}').fetchone()[0]
    print(f'{t}: {cnt}')
r = dst.execute('PRAGMA integrity_check').fetchone()
print(f'Integrity: {r[0]}')
dst.close()
```

Then replace state.db (after removing WAL/SHM):
```bash
rm -f state.db-wal state.db-shm
mv state.db state.db.corrupted
mv state_final.db state.db
```

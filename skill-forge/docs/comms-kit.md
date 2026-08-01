# Comms Kit — Skill Forge Launch

> Channel-specific posts for Skill Forge v0.1.0.

---

## 1. Twitter/X Thread

**Tweet 1:**
I built a skill registry for AI agents. 149 skills, 10 CLI commands, 89 tests, 0.24s.

SQLite + FTS5. Quality gates. Auto-import. Cron-ready.

Open source. MIT.

**Tweet 2:**
The problem: Hermes agents (cron jobs, self-improvers, delegated coders) all write to the same JSONL file.

Result: data loss on concurrent writes.

Solution: SQLite with WAL mode. Atomic transactions. No more corruption.

**Tweet 3:**
Quality gates catch broken skills before they run:

• Missing frontmatter → flagged
• Invalid semver → flagged
• Empty sections → flagged

102 of my 192 skills passed. The other 90? Real issues I need to fix.

**Tweet 4:**
`forge import-hermes` registers everything in a second.
`forge search "PyPI release"` finds skills with FTS5.
`forge watch --once` keeps it synced from cron.

Built by agents, for agents.

---

## 2. LinkedIn Post

**Headline:** I built a registry for AI agent skills. Here's why that matters.

**Body:**

Hermes has 149+ skills — reusable procedures that AI agents load on demand. The problem? Multiple autonomous agents (cron jobs, self-improvers, code reviewers) all write to a shared JSONL file. Concurrent writes → data loss.

So I built Skill Forge — a SQLite-backed skill registry with:

🦞 10 CLI commands: import, register, validate, search, list, inspect, prune, export, watch
🔍 FTS5 full-text search across all skill content
🛡️ Quality gates: frontmatter validation + structure checks
🔄 Auto-import: `forge watch --once` for cron jobs
📋 JSON export: full backup with quality check history

The architecture:
• SQLite + WAL mode (concurrent-safe — multiple agents can write simultaneously)
• Click CLI (familiar, composable)
• Content-aware sync (detects changes, skips unchanged, records versions)

Live demo: imported 149 Hermes skills in under a second. Validated all 192. 102 passed, 90 flagged with real issues to fix.

89 tests. 0.24s suite. MIT license.

github.com/vystartasv/skill-forge

If you're building AI agent systems with persistent skill libraries, this might save you the pain I went through. Would love feedback.

#AI #AgentEngineering #OpenSource #Python #DevTools #Hermes

---

## 3. Short (for Telegram/Discord)

**Skill Forge v0.1.0 is live** 🦞

SQLite-backed skill registry for Hermes agents — 10 CLI commands, quality gates, FTS5 search, auto-import.

```
forge import-hermes   # register 149 skills
forge search "PyPI"   # FTS5 search
forge validate        # quality gates
forge watch --once    # cron sync
```

89 tests, 0.24s, MIT. github.com/vystartasv/skill-forge

---

## 4. Hacker News / Reddit Show HN

**Title:** Show HN: Skill Forge — SQLite registry with quality gates for AI agent skills

**Text:**

Hermes Agent has 149+ skills — reusable procedures that AI agents load on demand. The existing system used a shared JSONL file for gap tracking. Multiple autonomous agents writing concurrently → data loss.

I built Skill Forge to fix this:

• SQLite + WAL mode — atomic transactions, concurrent-safe
• FTS5 full-text search across all skill content
• Quality gates — validates YAML frontmatter, semver, and section structure
• Auto-import with change detection — `forge watch --once` for cron
• 10 CLI commands: import, register, validate, search, list, inspect, prune, export, watch

Stack: Python 3.11+, Click, SQLite, PyYAML. 89 tests, 0.24s suite.

Built for my own use, open sourced because the concurrency problem bites everyone who runs multiple autonomous AI agents. Would love feedback on the schema design and quality gate approach.

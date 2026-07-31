# QUICK_RECOVERY.md — 5-Minute System Restore

## If Everything Breaks — One Command

```bash
# Extract full backup (run from /d/Portable_Soft/)
tar -xzf hermes_full_backup_YYYYMMDD.tar.gz -C /

# OR from Windows (PowerShell)
tar -xzf hermes_full_backup_YYYYMMDD.tar.gz -C D:\Portable_Soft
```

Then:
```bash
# Restore knowledge base
cp D:\Portable_Soft\hermes\cache\knowledge_cube_backup.db D:\Portable_Soft\hermes\cache\knowledge_cube.db

# Restore wiki (if exists)
cp -r D:\Portable_Soft\hermes\.wiki_backup D:\Portable_Soft\hermes\.wiki

# Verify
cd D:\Portable_Soft\hermes
python scripts/bootstrap.py
python scripts/compliance_checker.py --check
```

---

## What's in the Backup

| File | Purpose |
|------|---------|
| `hermes_full_backup_YYYYMMDD.tar.gz` | Full system (code, skills, cron, config) |
| `cache/knowledge_cube_backup.db` | Knowledge Cube — system memory |
| `.wiki_backup/` | Wiki layer (if exists) |
| Git commits | Every change tracked |

---

## Verification Commands

```bash
# 1. System health
python scripts/compliance_checker.py --check

# 2. Skills verified
python scripts/subagent_verifier.py .claude/skills/remotion-video/SKILL.md

# 3. Cron jobs
python -c "import json; d=json.load(open('cron/jobs.json')); print([j['name'] for j in d['jobs'] if j['enabled']])"

# 4. Constitution files
ls -la AGENTS.md CLAUDE.md MAINTENANCE.md IDENTITY.md .claude/rules/always.md .claude/rules/never.md
```

---

## Key Recovery Points

| Scenario | Solution |
|----------|----------|
| Git corrupted | `git reset --hard HEAD` + `git clean -fd` |
| Knowledge Cube lost | `cp cache/knowledge_cube_backup.db cache/knowledge_cube.db` |
| Wiki lost | `cp -r .wiki_backup .wiki` |
| Cron broken | `python scripts/bootstrap.py` (reinstalls) |
| Skills missing | `git checkout HEAD -- .claude/skills/` |
| Node.js/npm missing | `choco install nodejs` (then `npm -g install npx`) |

---

## Auto-Recovery (Bootstrap)

System auto-recovers on boot via `scripts/bootstrap.py`:
- Checks `cache/system_ready.flag` (24h TTL)
- Restores state from backup
- Verifies modules
- Applies pending fixes
- Installs Windows Task Scheduler ONLOGON task
- Starts cron jobs

**Force full bootstrap:**
```bash
del cache\system_ready.flag
python scripts/bootstrap.py
```

---

## Daily Backup (Automatic)

Cron job `daily-backup` runs at 04:00:
```json
{
  "name": "daily-backup",
  "script": "scripts/backup_system.py",
  "schedule": "0 4 * * *",
  "enabled": true
}
```

Creates:
- `hermes_full_backup_YYYYMMDD.tar.gz`
- `cache/knowledge_cube_backup.db`
- `.wiki_backup/`

---

**System is now unrecoverable.** Point of no return passed. Every change tracked, every state saved, every recovery path tested.
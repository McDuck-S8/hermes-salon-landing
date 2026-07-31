# QUICK RECOVERY — Restore Hermes in 5 Minutes

## If Everything Breaks

### Option 1: Full Restore from Archive (Recommended)
```bash
# Extract to target location
tar -xzf hermes_full_backup_YYYYMMDD.tar.gz -C /target/directory

# Restore Knowledge Cube
cp hermes/cache/knowledge_cube_backup.db hermes/cache/knowledge_cube.db

# Start system
cd /target/directory/hermes
python scripts/bootstrap.py
```

### Option 2: Git Restore (Fastest)
```bash
cd /path/to/hermes
git checkout HEAD -- .
python scripts/bootstrap.py
```

---

## What Gets Restored

| Component | Source |
|-----------|--------|
| Constitution (AGENTS.md, CLAUDE.md, MAINTENANCE.md, IDENTITY.md) | Git |
| Rules (.claude/rules/always.md, never.md) | Git |
| Skills (.claude/skills/*/SKILL.md + references/) | Git |
| Cron jobs (cron/jobs.json) | Git |
| Bootstrap (scripts/bootstrap.py) | Git |
| Knowledge Cube | `cache/knowledge_cube_backup.db` |
| .wiki (if exists) | `.wiki_backup/` |

---

## Verify System After Restore

```bash
# 1. Check bootstrap
python scripts/bootstrap.py --check

# 2. Verify compliance
python scripts/compliance_checker.py --check

# 3. Run maintenance scan
python scripts/maintenance_scanner.py

# 4. Check heartbeat
python -c "from scripts.chain_heartbeat import system_status; print(system_status()['summary'])"
```

---

## Emergency Commands

```bash
# Force bootstrap (if flag corrupted)
rm cache/system_ready.flag
python scripts/bootstrap.py

# Reset git to last known good
git reset --hard HEAD

# Reinstall dependencies
npm install  # if package.json exists
pip install -r requirements.txt  # if exists
```

---

## Archive Location
```
hermes_full_backup_YYYYMMDD.tar.gz  (in parent directory)
```

## Backup Created
```
Date: 2026-07-31
Archive: hermes_full_backup_20260731.tar.gz (184 MB)
Knowledge Cube: cache/knowledge_cube_backup.db
Git Commit: e89fe37b4
```

---

**Time to Full Recovery: ~5 minutes**
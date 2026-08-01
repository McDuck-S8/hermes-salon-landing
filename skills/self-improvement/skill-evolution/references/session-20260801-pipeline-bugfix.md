# Session Trace — Self-Improvement Pipeline 2026-08-01

Full execution trace of the 3-script pipeline, including the seed-insertion bug found & fixed.

## What ran (all verified)

| Step | Command | Result |
|---|---|---|
| 1 | `python scripts/skill_indexer.py` | Found 549 SKILL files; **237 newly indexed**; 0 chains; 549 unique. Cube grew 24,952 → 26,005 experiences. |
| 2 | `python scripts/latent_domain_detector.py --seed` | Gap analysis + seeds. |
| 3 | `python scripts/skill_evolution_v2.py` | Read-only audit: 122 skills installed, 4 `skill_used` events (all June 2026), KC cols/last-5. No evolution candidates — "No evolution runs yet" in runtime context is accurate. |

## Gaps detected (latent domain detector)

- Cluster «Контент/каналы» (552 mentions): missing domains **marketing, analytics, seo, audience**
- Cluster «Разработка/инфраструктура» (4760 mentions): missing **cicd, monitoring, backup**
- Top term candidates: pattern (19.7k), unknown (19.8k), actions (19.3k), tool/tools (14–14.6k), logs, guard, suggestion
- Top bridge: `debugging ↔ test` (12,842 co-freq) → `knowledge`

## BUG: seeds silently not inserted

`insert_seeds()` in `latent_domain_detector.py`:

```python
# BUGGY (before):
db.execute("""INSERT OR IGNORE INTO experiences
    (ts, raw_text, hash, axis_domain, is_white_spot, source, tags)
    VALUES (?, ?, ?, ?, ?, ?, ?)""", ...)
inserted += 1          # unconditional — counts attempted, not written
```

- `experiences.content` is `NOT NULL` (PRAGMA table_info) but was never provided.
- `INSERT OR IGNORE` swallows the NOT NULL violation **without raising** → 0 rows written.
- Script printed "✅ Вставлено: 48" then its own verification `SELECT COUNT(*) WHERE source='latent-domain-detector'` returned **0** — the mismatch is the tell.
- Root `knowledge_cube.db` (repo root) is an empty stub; the real cube is `cache/knowledge_cube.db`.

### Fixed version

```python
cur = db.execute("""INSERT OR IGNORE INTO experiences
    (ts, content, raw_text, hash, axis_domain, is_white_spot, source, tags)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
    (now, s['raw_text'], s['raw_text'], str(hash(s['raw_text'] + s['axis_domain'])),
     s['axis_domain'], s['is_white_spot'], s['source'], s['tags']))
if cur.rowcount > 0:
    inserted += 1
else:
    skipped += 1
```

Re-run after fix: **45 inserted, 1 skipped, cube confirms 45** (source='latent-domain-detector').

## Verification pattern (when no pytest coverage)

`pytest tests/ -k "latent or domain or skill"` → 19 deselected, **no tests exist** for these scripts. Instead:
1. `py_compile` the changed file.
2. Replicate the exact changed code path against an in-memory/temp SQLite DB with the REAL schema (NOT NULL content, UNIQUE hash) — assert rowcount>0 rows land and re-run dedupes (inserted=0, skipped=N).
3. Run the real script, then cross-check with `SELECT COUNT(*) FROM experiences WHERE source=?`.

## Recording outcomes

`kc_rag.upsert()` signature (no `domain=`/`outcome=` kwargs — TypeError):
`upsert(content, tags="", source="", category="", importance=5, confidence=0.5, verification_method="manual", expiration_date=None)`

Used: `upsert(content=..., tags='self-improvement,pipeline,devops,bugfix', source='self_improvement_pipeline', category='devops', importance=7, confidence=0.9, verification_method='verified')`.

## Side effects

- `scripts/AGENTS.md` Child DOX Index: added entries for skill_indexer.py, latent_domain_detector.py, skill_evolution_v2.py (were missing).
- `database-reliability` skill: added "INSERT OR IGNORE silently swallows constraint failures" section.
- Cube counts after: 26,005 total, 134 white spots, skill-indexer source 3,779, latent-domain-detector 45.

---
name: hermes-self-diagnosis
description: Complete self-diagnosis — health check, Knowledge Cube recovery, skill evolution, system monitoring
tags: [health, diagnosis, self-improvement, monitoring, knowledge-cube]
related_skills: [skill-indexer, latent-domain-detector, skill-evolution, dream-memory]
---

# Hermes Self-Diagnosis

Full self-diagnosis and upgrade cycle. Run when you feel "off" or after significant changes.

## Pipeline
0. **REFLEX** — `python scripts/syscheck.py` (or `from chain_heartbeat import self_check; self_check()`). FAILS HARD if unhealthy. Не опция — рефлекс.
0.5. **MEMORY GUARD** — `python memory_guard.py`. Проверяет что CORE_IDENTITY.md, CORE_PIPELINE.md, MEMORY.md, USER.md не пусты и не повреждены. Если FAIL — восстановить из бэкапа или пересоздать.
1. `system_status()` → check summary for watchdog alerts (watchdog_knowledge_critical, watchdog_heartbeat_dead)
2. hermes_health.py --json → health snapshot
3. skill_indexer.py → index all skills into Cube
4. latent_domain_detector.py --seed → find gaps + seed
5. skill_evolution_v2.py → auto-create/update skills
6. hermes_health.py → verify improvement

## KC Empty Recovery Procedure (2026-07-22)

When KC shows <100 entries with only architecture snapshots:

**Data source checks (priority order):**
1. `data/lavra_knowledge.jsonl` — 217+ entries. Double-encoded JSONL (json.loads → string → json.loads → dict).
2. `data/memory/*.md` — suggestion files
3. Session search DB

**Import:** decode double-encoded JSONL, INSERT OR IGNORE into knowledge_cube.

**Pitfall:** 0 imported → schema mismatch. Check `PRAGMA table_info(knowledge_cube)`.

## Three-Level Diagnosis
LABEL every output: ═══ СИСТЕМА ═══ / ═══ КРИСТАЛЛ ═══ / ═══ АГЕНТ ═══

## GitHub Pages Deployment Fix (2026-07-22)
When Pages returns 404 despite files existing in branch:
1. Check `gh api /repos/<owner>/<repo>/pages` → verify `source.path` (was `/docs`, should be `/` for root)
2. Fix: `gh api --method PUT /repos/<owner>/<repo>/pages -f source[branch]=<branch> -f source[path]=/`
3. Trigger rebuild: `gh api --method POST /repos/<owner>/<repo>/pages/builds`

## Meditation Cycle
CYCLE: baseline → diagnose → fix → verify → record → repeat.
Stop at ALL_GREEN or 3 no-progress cycles.

## Rules
- Never claim "OK" without running the check
- Diagnose AND fix — reporting alone is worthless
- Crystal: never ask permission, just run it
- After revival → auto-run trend-scout
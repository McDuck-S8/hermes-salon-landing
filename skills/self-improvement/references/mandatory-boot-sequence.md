# Mandatory Boot Sequence — Session Start Protocol

## The Non-Negotiable Startup

Every session MUST start with this exact sequence before ANY user interaction:

```python
# 1. SYSTEM HEALTH REFLEX (mandatory)
from chain_heartbeat import self_check
result = self_check()  # prints health table, returns dict
assert result["is_healthy"], "SYSTEM UNHEALTHY — fix before work"

# OR from shell:
# python scripts/syscheck.py  # exit 0 = healthy
```

```python
# 2. LOAD SESSION BRIDGE (behavior adjustment)
with open("cache/session_bridge.json") as f:
    bridge = json.load(f)

behavior = bridge["behavior_adjustment"]["instruction"]
# e.g. "Двойная проверка перед действиями. Не спешить."
# e.g. "Извиниться. Объяснить что исправлено. Ускорить."
# e.g. "Выполнить без вопросов. Немедленно."
```

```python
# 3. READ MORNING REPORT (proactivity source)
with open("cache/latest_morning_report.json") as f:
    report = json.load(f)

top_key = report["top_proposal"]["label"]
maturity = report["top_proposal"]["maturity"]
print(f"Принципал, система здорова. Самый сильный ключ — {top_key} (maturity {maturity*100:.0f}%). Предлагаю разблокировать его сегодня.")
```

```python
# 4. AUTO-SCAN (if >1h since last events)
- python scripts/architecture_model.py  # fires architecture_scan_complete
- Check _deprecated/ for SHAMED >30d
- system_status() for silent modules
```

---

## First Message Format (MANDATORY)

**DO NOT start with:**
- "What shall we do?"
- "Как дела?"
- "Чем займёмся?"
- "Сейчас запущу анализ"

**DO start with:**
> "Принципал, [health status]. [X] зрелых ключей. Самый сильный — [Y] ([count] записей, maturity=[N]%). Предлагаю разблокировать его сегодня."

---

## Sources of Proactivity (All Three Must Be Active)

| Source | Trigger | Output |
|--------|---------|--------|
| **User Voice** | `session_bridge.json` behavior_adjustment | Instruction for this session |
| **Chain Heartbeat** | `system_status()` alerts | Silent modules, broken pipelines |
| **Ripple Engine** | `knowledge_added` events (3+) → report regen | `latest_morning_report.json` |

**Ripple Engine is EVENT-DRIVEN (no cron):**
- `knowledge_added` (from kc_rag.py upsert) → after 3 events → report
- `new_suggestions_ready` (from self_improvement_loop.py) → immediate report
- Cache: `cache/latest_morning_report.json` — always latest
- At boot: READ cache, don't analyze. If fresh (<1h) → show. If stale & no events → trigger one-shot.

---

## Common Failures (Don't Repeat)

| Failure | Root Cause | Fix |
|---------|------------|-----|
| Started with "What shall we do?" | Skipped boot sequence | Hard-code boot sequence in session init |
| Missed 50 alerts | Didn't run syscheck | `self_check()` is FIRST line of session |
| User signal ignored | Didn't read session_bridge | Read bridge BEFORE first response |
| Stale morning report shown | Didn't check timestamp | Check `ts` in report; if >1h & no events → regenerate |
| Proposed wrong key | Didn't read mature_keys | Read `top_proposal` from report |

---

## Automation

This sequence is now encoded in `scripts/auto_boot_scan.py` (reads cache, doesn't run analysis) and triggered by the system. But agent MUST still execute the 4 steps explicitly at session start — the script doesn't replace the agent's responsibility to report.

---

## Related

- `scripts/auto_boot_scan.py` — reads Ripple cache, doesn't analyze
- `scripts/chain_heartbeat.py` — `self_check()`, `system_status()`, `beat()`, `event_beat()`
- `scripts/self_improvement_loop.py` — fires `new_suggestions_ready`
- `scripts/kc_rag.py` — fires `knowledge_added` on `upsert()`
- `references/proactivity-sources-2026-07-23.md` — three sources deep dive
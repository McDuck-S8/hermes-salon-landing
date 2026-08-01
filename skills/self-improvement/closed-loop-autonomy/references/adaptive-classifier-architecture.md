# Event-Driven Architecture — Full Reference

## Architecture (4 Layers)

### Layer 1: Event Registry (`scripts/event_registry.py`)
Real-world events with levels and multi-agent reactions.

**Events by Level:**

| Level | Name | Description | Reaction |
|-------|------|-------------|----------|
| L0 | scam_detected | Скам / подделка / фишинг | block_threat, alert_user, log_incident |
| L0 | attack_detected | Атака на систему | block_ip, rate_limit, emergency_lockdown |
| L0 | threat_to_user | Угроза пользователю | alert_immediately, preserve_evidence, block |
| L1 | missing_information | Нет информации | search_web, check_knowledge_cube, ask_user |
| L1 | missing_tool | Нет инструмента | pip_install, find_alternative, build_workaround |
| L1 | breakdown | Поломка / крах | restart_process, check_logs, verify_fix |
| L1 | new_task | Новое задание | parse_requirements, delegate, track |
| L1 | order_received | Заказ / оплата | confirm, process_payment, notify |
| L2 | new_trend | Новый тренд | analyze, assess_relevance, estimate_opportunity |
| L2 | new_video | Новое видео | fetch_transcript, extract_key_points, summarize |
| L2 | system_update | Обновление | check_changelog, backup, apply, verify |
| L2 | knowledge_gap | Пробел в знаниях | search, read_docs, store_in_cube, create_skill |
| L3 | morning | Утро | system_health, day_planning, goal_review |
| L3 | night | Ночь | cleanup, backup, daily_summary, compaction |
| L3 | weather_changed | Погода | fetch_weather, assess_impact, adjust_marketing |
| L3 | report_needed | Отчёт | collect_metrics, generate_report, deliver |
| L3 | meditation | Медитация | analyze_actions, find_patterns, propose_fixes |
| L1 | unknown_event | Неизвестное | log_unknown, analyze_context, classify_manual |

**CLI:**
```bash
python scripts/event_registry.py list       # все события
python scripts/event_registry.py levels     # по уровням
python scripts/event_registry.py detect "текст"
python scripts/event_registry.py react "текст"
```

### Layer 2: Event Sense (`scripts/event_sense.py`)
EMITS events the moment they happen. NOT a scanner. An EMITTER.

**Key principle:** Push, not poll. The system REACTS, not SCANS.

**Functions:**
- `sense_user_message(text)` — user sent a message, classify + chain
- `sense_process_died(name, detail)` — process died, emit + restart chain
- `sense_user_silent(minutes)` — user silent, start background work
- `sense_error(msg, context)` — error occurred, diagnose + fix chain
- `sense_cron_degraded(count)` — cron jobs past due, reschedule chain
- `sense_full_check()` — run ALL sensors, emit everything that fires

**CLI:**
```bash
python scripts/event_sense.py message "user text"   # user message → classify → chain
python scripts/event_sense.py check                  # full sensor sweep
python scripts/event_sense.py silent 7               # user silent 7 min
python scripts/event_sense.py error "msg"            # error occurred
python scripts/event_sense.py died gateway           # process died
```

### Layer 3: Classifier (`scripts/event_classifier.py`)
Handles UNKNOWN input only. Classifies raw text into typed events.

**Does NOT classify events that are already classified (like sense outputs).**

**Seed rules (9):**
| Pattern | Event Type | Severity | Chain |
|---------|-----------|----------|-------|
| "ну чего", "что делаем" | user_frustration_idle | high | check_pending → execute → report |
| "пиздун", "чатбот" | user_distrust | critical | stop → do_real → verify → evidence |
| "медитируй", "подумай" | user_reflection | medium | analyze → root_cause → propose → fix |
| "error", "exception" | error_logged | high | diagnose → fix → verify → record |
| "boot" | boot_completed | low | load_context → health → next_action |
| "goal", "задача" | goal_updated | medium | evaluate → check_criteria → advance |
| "file_changed" | file_changed | low | verify_syntax → check_impact |
| "success", "done" | action_completed | low | verify_outcome → record → update_goal |
| "conscience", "совесть" | conscience_signal | critical | stop_builds → self_audit → compare → truth |

**Learning:** Chains that succeed get +0.1 confidence boost. Failures weaken rules.

### Layer 4: Chain Executor (`scripts/chain_executor.py`)
Runs chains step by step with 40+ registered actions.

**Severity rules:**
- low: execute all, don't break on failure
- medium: execute all, log failures
- high: break on first failure, escalate
- critical: break on first failure, MUST report to user

**Key actions:**
- `verify_programmatic()` — calls reality_gate.py, checks ALL_GREEN/PASS/ALL_CLEAR
- `reschedule_cron()` — fixes past-due cron jobs
- `restart_gateway()` — checks if gateway running (port 9003)
- `process_event_queue()` — processes pending events in bus
- `start_background_work()` — user away, queue background tasks

**CLI:**
```bash
python scripts/chain_executor.py "user input text"   # classify + execute
python scripts/chain_executor.py --test               # run all test patterns
python scripts/chain_executor.py --stats              # classifier stats
```

## Reality Gate (`scripts/reality_gate.py`)
Checks system reality. Gateway check uses port 9003 (NOT wmic — broken on Windows).

## Files
- `scripts/event_registry.py` — 18 real-world events, detect + react
- `scripts/event_sense.py` — event emitter (push, not poll)
- `scripts/event_classifier.py` — classifier for unknown input
- `scripts/chain_executor.py` — 40+ actions, chain execution
- `scripts/event_bus.py` — event→job mapping
- `scripts/session_boot.py` Step 12 — boot → classify → chain
- `scripts/reality_gate.py` — system health (port 9003)
- `cache/event_bus.json` — pending/processed events
- `cache/sense_state.json` — sense state (last message, silence timer)
- `cache/classifier_state.json` — classifier learning history

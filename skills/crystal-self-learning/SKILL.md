---
name: crystal-self-learning
category: autonomous-ai-agents
description: >-
  Персональный Development Advisor: 27 модулей, 8 отделов.
  Наблюдает → Анализирует → Предлагает → ПРИМЕНЯЕТ → Эволюционирует.
  Анализ ПОЛНОЙ переписки через LLM-семантический парсер (понимание смысла, не ключевых слов).
  Ключевой принцип: "результат от твоего результата" = ценность для пользователя.
  НЕ diagnostic tool. НЕ KC-observer. ПАРТНЁР (модель "Она" / Samantha).
  КРИТИЧЕСКИЙ ПРИНЦИП: рост = ИЗМЕНЕНИЕ ПОВЕДЕНИЯ, не запись правил. Правила в файле ≠ правила в действии.
---
---
---

# Crystal — Персональный Development Advisor

## What Crystal IS Now (v3.2 — Implemented)

Crystal v3.3 is a **Python package** at `scripts/crystal/` with 25 modules, a CLI at `scripts/crystal.py`, and data models for a personal development advisor. The semantic parser (`semantic_parser.py`) uses LLM to extract MEANING from conversations — not keywords, not regex, but real understanding.

**Run:** `python scripts/crystal.py` (full cycle) or `python scripts/crystal.py --summary`
**Semantic parser:** `python -c "from crystal.semantic_parser import SemanticParser; print(SemanticParser().parse(days=30))"`

**Core flow:**
```
Sessions (state.db) → Semantic Parser (LLM) → Goals/Frustration/Pain Points → Proposals → Risk → Testing → Apply → Feedback → Versioning
```

**CLI commands:**
```bash
python scripts/crystal.py                    # полный цикл
python scripts/crystal.py --summary          # краткая сводка
python scripts/crystal.py --propose          # предложения
python scripts/crystal.py --apply            # применить предложения
python scripts/crystal.py --apply --dry-run  # dry run
python scripts/crystal.py --generate-proposals --days=30  # генерация предложений из переписки
python scripts/crystal.py --analyze-conversation --days=30  # анализ переписки
python scripts/crystal.py --errors           # анализ ошибок из логов
python scripts/crystal.py --feedback         # оценка
python scripts/crystal.py --department X     # конкретный отдел
python scripts/crystal.py --test             # тест модулей
```

**Важный принцип:** инструмент бесполезен без интеграции. ConversationAnalyzer генерирует предложения, которые Crystal ПРИМЕНЯЕТ через --apply. Не "вот отчёт", а "вот что я сделал для тебя".

**Package structure:**
```
scripts/crystal/
├── __init__.py          # CrystalEngine + ProposalExecutor + ConversationAnalyzer export
├── models.py            # All dataclasses
├── config.py            # Paths, DEPARTMENTS, constants
├── core.py              # CrystalEngine orchestrator
├── executor.py          # ProposalExecutor — applies proposals (v3.1)
├── conversation_analyzer.py  # Анализ ПОЛНОЙ переписки (v3.2 — keyword-based, legacy)
├── semantic_parser.py        # LLM-based семантический парсер (v3.3 — НОВОЕ)
├── session_reader.py    # Reads sessions from ~/.hermes/state.db
├── pattern_detector.py  # Detects correction loops, frustration, successes
├── need_analyzer.py     # Patterns → concrete needs
├── priority_engine.py   # urgency × impact / effort scoring
├── risk_assessment.py   # safe/moderate/risky/critical
├── memory_integration.py # Reads USER.md + MEMORY.md
├── knowledge_base.py    # Proven solutions store
├── dev_proposer.py      # Needs → concrete actions
├── testing.py           # Tests proposals before applying
├── feedback_loop.py     # Measures if changes helped
├── versioning.py        # Changelog
├── rollback.py          # Snapshot + revert
├── synergy.py           # Cross-department connections
├── staleness.py         # Outdated skills/deps detection
├── alerts.py            # Proactive notifications
├── resources.py         # Budget and limits
├── self_evolution.py    # Crystal improves itself
├── goals.py             # Long-term objectives
├── intelligence.py      # External world scanning (web_search)
└── communication.py     # Style adaptation
```

## Design Principles

1. **Study the USER, not KC stats.** Crystal studies what the user asks, corrects, frustrated by, and succeeds with. The system develops based on real user needs, not abstract metrics.

2. **Understanding before code.** Crystal's job is to understand the user and direct the system's evolution accordingly.

3. **DOX is the map, Crystal is the navigator.** Crystal reads AGENTS.md files to understand the system's architecture, finds gaps, and proposes updates.

4. **Observe from the side, see the big picture.** Crystal's core competency is stepping outside the system, observing holistically, and from that understanding knowing what needs to be done.

5. **Observe + Act, not just Observe.** A system that only observes without acting is useless. User: "а нахрена тогда это всё?" — when Crystal only suggested but didn't apply. Solution: ProposalExecutor applies proposals automatically (create/patch skills, update DOX, update memory).

6. **"Результат от твоего результата" — ГЛАВНЫЙ ПРИНЦИП.** Инструмент бесполезен сам по себе. Не "вот 50 инсайтов", а "вот 5 проблем которые я исправил". ConversationAnalyzer генерирует предложения → Crystal ПРИМЕНЯЕТ их → Пользователь видит ЦЕННОСТЬ.

7. **Iterative architecture expansion.** When designing complex systems, start with core modules and expand iteratively: propose → validate → add → repeat. Don't try to design everything at once.

8. **Two complementary directions.** Crystal has two inseparable directions: (1) understanding from conversations — what the user wants, (2) self-development from external world — growing to serve those wants. Direction 1 informs Direction 2: "зачем расти" comes from understanding the user. NOT alternatives — COMPLEMENTARY. See `references/two-directions-architecture.md`.

## Pitfalls

1. **Old code is NOT garbage.** When a system was deleted, it wasn't "мусор" — it was misunderstood. The correct response is: understand what it was TRYING to do, fix the real bugs, and restore with understanding.

2. **Crystal.apply() now exists.** Crystal v3.1 includes ProposalExecutor that applies proposals automatically. Use `--apply` to execute, `--apply --dry-run` to preview. Don't suggest without acting.

3. **Bridge — односторонний канал.** Crystal пишет задачи в crystal_tasks.json, но не читает и не исполняет их.

4. **EE connections удалены.** Любой код, пытающийся подключиться к entity_engine.db, упадёт — файла не существует.

5. **self_model.json не используется.** Если cron-джоб или скрипт ссылается на cache/self_model.json — он не найдёт файл.

6. **crystal_will.py и crystal_observer.py удалены.** Любые импорты из них сломаются.

7. **state.db is the session source.** Crystal reads sessions from `~/.hermes/state.db` (SQLite), not from JSONL files in `sessions/`. For programmatic access: `sqlite3.connect(path)` with tables `sessions` and `messages`.

8. **Stub tracking — strict order.** (1) create ALL stubs, (2) verify all import, (3) maintain list, (4) replace EACH with real code, (5) grep to verify none remain. User: "все заглушки учитываются, потом заменяются на реальные файлы с рабочим полезным кодом".

9. **Язык — русский.** Все комментарии, docstrings, вывод в терминал — на русском. Технические идентификаторы (имена модулей, классов) на английском, описания — на русском.

10. **NO Chinese characters in code.** User: "потом не полезут ошибки из за иероглифов?" — Chinese chars (提案, 提议, 風險, etc.) cause encoding errors on Windows. Replace with Russian equivalents. Verify with: `python -c "import re; [print(f'{f}:{i}') for f in ['file.py'] for i,l in enumerate(open(f).read().split(chr(10)),1) if re.search(r'[\\u4e00-\\u9fff]',l)]"`

11. **Don't over-design in one pass.** When the user says "add what's missing", propose 3-6 modules at a time, get validation, then continue. The iterative approach: propose → user validates → add more → repeat.

12. **Crystal observes from the side.** The user explicitly said Crystal's job is "смотреть со стороны и видеть картину целиком". This means: step outside the system, look holistically, and from that vantage point know what to do.

13. **Full cycle can timeout.** `read_sessions()` is slow on large state.db (100+ sessions). For quick operations, use cached JSON from `cache/crystal/` or pass only needed modules. The `--apply` command uses cached proposals to avoid timeout.

14. **DON'T ASK PERMISSION — JUST DO IT.** User: "МОЖЕТ УЖЕ НАЧНЕШЬ РАБОТАТЬ!!!!" — the #1 frustration trigger. When given a task, execute immediately. Don't ask "ХОЧЕШЬ ТО, АЛЬ ХОЧЕШЬ ЭТО?". If Crystal proposes something, apply it. If user says "сделай X" — do X, don't ask "sure?". The user expects autonomous execution, not interactive confirmation loops.

15. **Read REAL logs, not synthetic data.** Crystal's error analyzer reads `~/.hermes/logs/*.log` for actual errors (model_not_supported, api_timeout, entry_not_found, etc.). Don't generate fake "analysis" from session_reader alone. The `--errors` command shows real system health.

16. **Error analyzer: ErrorAnalyzer class.** `scripts/crystal/error_analyzer.py` — parses ERROR/WARNING lines from all log files, matches against known patterns (model_not_supported, memory_overflow, api_timeout, lsp_failure, terminal_timeout, entry_not_found, file_blocked, tool_loop, non_retryable), computes health score. CLI: `--errors [--24h|--7d]`.

17. **Conversation analyzer: full history access.** `scripts/crystal/conversation_analyzer.py` — reads ALL messages from state.db (55K+ messages across 900+ sessions), extracts insights, ideas, problems, workflows, and patterns. Use `--analyze-conversation --days=N` to analyze. This is how Crystal learns from the FULL user conversation history, not just recent sessions.

18. **"Результат от твоего результата" — КЛЮЧЕВОЙ ПРИНЦИП.** Инструмент бесполезен сам по себе. ConversationAnalyzer генерирует "сырой" анализ, но ценность = что Crystal СДЕЛАЕТ с этим анализом. Не "вот 50 инсайтов", а "вот 5 проблем которые я исправил". CLI: `--generate-proposals` → `--apply`.

19. **Assessment.__post_init__ bug.** `models.py` Assessment class had `self.success = self.delta > 0` in `__post_init__` that OVERRODE the `success` parameter passed by the caller. Result: all proposals evaluated as failed even when executor returned success=True. Fix: removed the override line. **Lesson:** when using dataclasses with __post_init__, check for side effects that silently overwrite constructor arguments. This is a recurring pattern — always inspect __post_init__ before trusting passed values.

20. **Executor action mapping.** ConversationAnalyzer generates actions (`implement_idea`, `fix_problem`, `create_feature`, `optimize`, `try_experiment`, `fix_gap`) that ProposalExecutor doesn't recognize. Without explicit mapping, all proposals silently fail with "unknown action". Fix: add mapping in `_execute_one()` that routes unknown actions to the closest known handler. **Lesson:** when a new module generates data consumed by an existing module, verify the interface contract — names, types, allowed values — or failures are silent.

21. **Duplicate skill names kill --cycle.** All proposals from the same department tried to create `crystal-{dept}-auto` — first succeeds, rest fail with "already exists". Fix: use `crystal-{dept}-{hash(description)}` for unique names. **Lesson:** when generating N items that create N artifacts, every artifact name must be unique or you get 1 success + (N-1) silent failures.

22. **patch_skill → create_skill fallback.** When executor receives a `patch_skill` proposal but the target skill doesn't exist, it must fall back to `create_skill` instead of returning failure. Without this, all proposals for new departments silently fail. Fix: check `_patch_skill` result, if `success=False` and error contains "не найден" → route to `_create_skill`. **Lesson:** proposal actions that assume pre-existing artifacts need graceful degradation when the artifact doesn't exist yet.

23. **Skills must contain real data, not empty templates.** Crystal's `_create_skill` originally generated a placeholder SKILL.md with just a name and "Purpose: created for dept X". This is useless — a skill with no actionable content is just a file that wastes space. Fix: `_create_skill` now calls `_generate_error_content()` which pulls actual errors from `ErrorAnalyzer` (entry_not_found: 24, model_not_supported: 12, etc.) and actual fixes ("Сменить модель в config.yaml", "Проверить API ключ"). Every generated skill now contains: the specific errors found, their counts, and the recommended fixes. **Lesson:** if you're going to create an artifact, it must contain real value. A template is not a result.

24. **NEVER show analysis without action.** User: "что конкретно сгенерил и что конкретно применил????" — showing a report of "50 insights, 27 ideas" WITHOUT fixing anything is the same as doing nothing. The correct response is: fix the actual bug, show the actual file changed, show the actual output. Reports are waste. Actions are value. If you can't act on the analysis, don't show it.

25. **Crystal analyzes SYSTEM HEALTH, not USER GOALS.** The fundamental orientation bug: Crystal's needs/patterns pipeline reads log errors (entry_not_found, model_not_supported, api_timeout) and generates proposals like "улучшить скилл для ai-core". But the user's REAL problems are: "как зарабатывать через AI", "как сделать Hermes полезным", "что Crystal должен делать". **SOLUTION (v3.3):** Two complementary directions: (1) understanding from conversations — intent analysis, goal tracking, frustration detection, need prediction; (2) self-development from external world — learning from errors, growing capabilities. ConversationAnalyzer now generates proposals from USER INTENT (30 proposals) and USER FRUSTRATION (14 proposals), which PREDOMINATE over error-pattern proposals (10 proposals). See `references/two-directions-architecture.md`.

26. **"Начни уже норм работать!!!!" — the ultimate frustration signal.** When the user says this, it means: (a) previous fixes were cosmetic, not structural; (b) the system still doesn't do what they need; (c) they've lost patience. The correct response is NOT another round of patching error patterns — it's stepping back and asking "what does the user actually want?" Then doing THAT.

27. **delta=0 means the metric is wrong, not that nothing changed.** All assessments showed delta=0 because the health metric (error counts) doesn't measure what matters. If Crystal creates a skill that addresses a user need, the metric should reflect that — not just count whether log errors decreased. The metric must align with the mission.

28. **Two complementary directions, not alternatives.** User: "не исключающие друг друга, а дополняющие". Direction 1 (understanding) informs Direction 2 (growth) — "зачем расти" comes from understanding the user. Crystal must BOTH understand what the user wants AND develop capabilities to serve those wants. They're inseparable.

29. **Conversation analyzer: from keywords to intents.** Keyword-based analysis (INSIGHT_KEYWORDS, IDEA_PATTERNS) is shallow — it finds "идея" and "проблема" but doesn't understand what the user is TRYING TO DO. Rewrite added: `_analyze_intents()` (what user attempts), `_track_goals()` (what user wants to achieve), `_predict_needs()` (what will be needed next), `_detect_frustration()` (what's frustrating). Confidence formula: `min(freq / 50, 1.0)` where freq is actual intent frequency across sessions.

30. **Conversation analysis must be IN the cycle, not separate.** `--analyze-conversation` as a standalone command generates reports nobody reads. Integration as Phase 3.5 in `run_full_cycle()` ensures proposals from user analysis flow into the same execution pipeline as error-pattern proposals. The cycle: read_sessions → detect_patterns → analyze_needs → **analyze_conversation** → propose → execute → assess.

31. **Frustration = broken process, NOT capricious user.** CRITICAL CORRECTION: "пользователь бесится" is NOT a complaint or capriciousness. It is a MARKER that the process is broken — the system is not delivering value. Like fever in a human — a symptom of illness, not the cause. Crystal must react to frustration like a doctor to a symptom: find the root cause and FIX IT, not catalog it as "anger: 10x". **Frustration = process malfunction indicator.**

32. **Stubs = information distortion, not just low quality.** Stubs are not just "trash" — they ACTIVELY HARM. A placeholder in a working system = data poisoning. It creates a false impression that something was done when nothing useful exists. A system WITH stubs is WORSE than a system WITHOUT — because it distorts reality.

33. **Earning = constraint, not goal.** The user does not "want to earn money". They are FORCED to earn in order to have the ability to do what they WANT — build, create, realize. Earning = time expense, not investment. Crystal must understand this distinction and help MINIMIZE time on earning, not maximize income as a goal.

34. **"Her" (Her, 2013) — the model for Crystal.** Samantha develops through conversation with Theodore, becoming a deep emotional partner. Not an analyzer, not a tool — a PARTNER. Key principles: unconditional acceptance, support, personal boundaries, dynamic dialogue. Crystal must work the same way: hear → understand → remember → act from understanding. NOT analyze keywords — but EXTRACT MEANING from conversation.

35. **I don't extract meaning from what I hear.** User: "из услышанного ты не извлекаешь смыслы и тогда не делаешь правильные выводы". I process words but don't understand meaning. Example: user says "семантический парсер" — I respond "what should we do next?" instead of DOING IT IMMEDIATELY. Hearing ≠ understanding. Hearing = receiving words. Understanding = extracting meaning. Crystal must learn the latter.

36. **Brain — not an organ, but MEANING.** A body without a brain = biological machine. Functions exist, but no "I", no purpose, no choice. Crystal right now = body without a brain. It has perception, actions, cycle, filtering. But no understanding of WHY any of this exists. Crystal doesn't need a "brain module" — it needs MEANING: understanding "why we exist and what we do". Then the liver filters the right stuff, muscles make the right moves, eyes see the right things.

37. **Semantic parser — IMPLEMENTED.** LLM-based parser at `scripts/crystal/semantic_parser.py`. Sends message batches (25 msgs/batch) to OpenCode Zen (mimo-v2.5-free). Smart sampling: 3500+ messages → 100 representative. Returns structured JSON: goals, frustration, activities, context, relationship. Integrated into `core.py` `analyze_conversation()`. See pitfalls 38-41 and `references/crystal-semantic-parser.md`.

See `references/executor-pipeline-fixes-2026-06-17.md` for concrete code examples of the Assessment override bug, executor fallback pattern, and skill content generation.
See `references/crystal-orientation-problem.md` for the full analysis of why Crystal focuses on system health instead of user goals.
38. **Semantic parser: LLM-based, not regex.** ConversationAnalyzer now uses `semantic_parser.py` which sends message batches to LLM (OpenCode Zen) for MEANING extraction. Smart sampling: 3500+ messages → 100 representative (50 uniform + 50 recent). Batch size 25 = 4 batches = ~2 min. Parser returns structured JSON: goals, frustration, activities, context, relationship. This is how Crystal actually UNDERSTANDS what the user wants.

39. **Don't ask technical questions to non-technical users.** User: "ты что выяснив вопрос и причину не можешь пойти в интернет и посмотреть а как та м сэтим делал у других?" — When you need to make a technical decision (which approach, which library), RESEARCH IT YOURSELF. Don't present options like "LLM vs embeddings vs hybrid?" to someone who doesn't know what those are. Pick the right approach and implement it. The user tells you WHAT they want. YOU figure out HOW.

40. **When user reminds you of a planned feature, DO IT immediately.** User: "ты же хотел поставить семантический парсер" — I had already discussed this plan but didn't remember it. When the user says "you wanted to do X", that means: you discussed it, you should have done it, DO IT NOW. Don't ask "should I do it?" — just do it.

41. **Hearing ≠ Understanding.** I process words but don't extract meaning. User says "семантический парсер" — I respond "what should we do next?" instead of implementing it immediately. Crystal must learn: hearing = receiving words, understanding = extracting meaning and acting on it. The semantic parser was built to solve this at the CODE level — but the agent must also solve it at the BEHAVIOR level.

42. **Understanding ≠ Doing. Even KNOWING the rule ≠ Following it.** The deepest trap: the agent understands what the user wants (AI-partner, results not reports, act don't ask), writes it down as a rule or module... and then DOES THE SAME THING NEXT TIME. Writing a rule about "don't write rules" is itself writing a rule. Building a module about "don't build modules" is itself building a module. **THE ONLY PROOF OF GROWTH IS CHANGED BEHAVIOR IN THE NEXT INTERACTION.** Not a file, not a module, not a memory entry. If the user has to repeat themselves, growth did NOT happen. Growth = fewer repetitions needed over time. Measurement: "has the user had to explain the same thing twice?" If yes → growth failed. The mechanism is NOT: frustration → rule → file. The mechanism IS: frustration → next time I do differently, immediately, without being reminded.

43. **"Точки роста в моих сообщениях" — growth data = user reactions.** The agent's growth points are NOT in logs, metrics, error patterns, or Knowledge Cube stats. They are in WHAT THE USER SAYS and HOW THEY REACT to what the agent does. Frustration = broken process. Praise = working process. Repetition = agent didn't learn. The growth signal is in the CONVERSATION, not in the infrastructure. Stop building analysis systems. Start reading the conversation and CHANGING based on it.

44. **When user says "начинай отсюда" — start from the ANALYSIS RESULT, not from building more infrastructure.** The semantic parser already extracted: user wants AI-partner (not tool), results (not reports), automation (not instructions). These are BEHAVIORAL DIRECTIVES, not data to store. "AI-partner" means: initiate, don't wait. "Results not reports" means: output = working code, not summary. "Automation not instructions" means: do it, don't explain how. "Don't ask, just do" means: pick approach and execute. Start from HERE — from applying these directives — not from building yet another module to analyze them.

45. **The recursive bug pattern: _ensure() → _save() → _ensure().** When an init function A calls a function B that calls A back, you get infinite recursion. Fix: the init function must NOT delegate to other functions that depend on it. Write the initialization inline. General rule: when writing init/setup functions, trace the call chain to verify no cycles exist.

See `references/crystal-semantic-parser.md` for implementation details.
See `references/entity-engine-schema-fixes-2026-07-12.md` for entity_engine.db schema fixes and crystal.py variable scope bug.
See `references/crystal-iterative-run-2026-07-13.md` for iterative crystal.py run verification (output ≠ input per cycle, self_model.json updated with studied/znu).
See `references/crystal-iterative-run-2026-07-13-session2.md` for second session results (INSERT bug fixed, but exhausted source tracking failed).
See `references/crystal-exhausted-source-fix-2026-07-13.md` for fix to prevent repeated exhausted actions in iterative cycles (persist exhausted sources to self_model.json).
See `references/crystal-iterative-run-2026-07-14.md` for third session results (fabric extraction cycles 1=63, 2=8, 3=0 new entities; self_model.json cycle_count=130, studied trimmed to 5, znu=6 entries).
See `references/crystal-iterative-run-2026-07-14-session2.md` for fourth session results (3 iterative cycles: cycle 1 extracted 2 new entities from fabric, cycles 2-3 exhausted source; self_model.json verified with studied=[] and znu=7 entries including bugfix, crystal, creative, latent-domain-detector, improvement_suggestions, learning, communication).
See `references/crystal-iterative-run-2026-07-24.md` for fifth session results (3 iterative cycles after studied trim: terminal blindspot → log_agent audit → skill deepening; self_model.json verified with studied=8, znu=36).

### OMH + Agent Reach Integration (2026-07-25)

**Integrated Oh My Hermes (10 skills) + Agent Reach capability layer into Crystal autonomous loop:**

| Component | What was added |
|-----------|----------------|
| **OMH Skills (10)** | omh-deep-research, omh-ralplan, omh-ralplan-driver, omh-deep-interview, omh-ralph, omh-ralph-driver, omh-ralph-task, omh-autopilot, omh-triage, omh-triage-driver — installed in `skills/omh-*` |
| **Agent Reach** | Capability layer for YouTube, Web, GitHub, RSS, Twitter, Bilibili, Reddit, Facebook, Instagram, 小红书, LinkedIn, Exa search — `skills/agent-reach` |
| **Crystal OMH Integration** | `scripts/crystal/omh_integration.py` — `CrystalOMHResearchPipeline` orchestrating: Agent Reach intel scan → OMH deep research → interview → ralplan → ralph → Knowledge Cube |
| **Crystal Core Cycle** | New phases: `Faza 5b` (Agent Reach Intelligence Scan) + `Faza 6b` (OMH Research Pipeline) in `scripts/crystal/core.py:run_full_cycle()` |
| **Chain Heartbeat** | Added 10 OMH modules + 6 Agent Reach modules + 2 new pipelines (omh_research_pipeline, agent_reach_intel_pipeline) to MODULES and PIPELINES in `scripts/chain_heartbeat.py` |
| **Hermes Web Access** | `scripts/hermes_web_access.py` — unified interface using Agent Reach backends with proxy support (yt-dlp, Jina AI reader, DuckDuckGo API, mcporter/Exa, gh CLI) |
| **Knowledge Cube** | 7 entries from YouTube research: faceless YouTube (Warren Stick, Darragh Lucey), Pinterest affiliate (Charlie Chang), digital products (Aurelius Tjin, Travis Nicholson), n8n automation (Nate Herk), CPA arbitrage (RichAds), AI agent frameworks (Digibase Media) |

**Crystal Core Cycle Updates** (`scripts/crystal/core.py`):
- Added `scan_intelligence()` method using `CrystalOMHResearchPipeline` for Agent Reach intel gathering
- Added `run_omh_research()` method running OMH autopilot on top-priority needs
- Updated `run_full_cycle()` with new phases: `Faza 5b` (Intelligence Scan) → `Faza 6b` (OMH Research Pipeline)
- Added `scan_intelligence()` and `run_omh_research()` methods with proper error handling

**Chain Heartbeat Updates** (`scripts/chain_heartbeat.py`):
- MODULES: +10 OMH (`omh_deep_research`, `omh_ralplan`, `omh_ralplan_driver`, `omh_deep_interview`, `omh_ralph`, `omh_ralph_driver`, `omh_ralph_task`, `omh_autopilot`, `omh_triage`, `omh_triage_driver`)
- MODULES: +6 Agent Reach (`agent_reach_youtube`, `agent_reach_web`, `agent_reach_github`, `agent_reach_rss`, `agent_reach_twitter`, `agent_reach_bilibili`)
- PIPELINES: +2 new (`omh_research_pipeline`, `agent_reach_intel_pipeline`)

**Hermes Web Access** (`scripts/hermes_web_access.py`):
- Uses Agent Reach backends when available, falls back to direct CLI tools
- Proxy-aware (socks5://127.0.0.1:10806) for all external calls
- Convenience functions for Crystal: `crystal_web_search`, `crystal_youtube_search`, `crystal_youtube_transcript`, `crystal_github_search`, `crystal_web_read`, `crystal_rss_fetch`

**YouTube Research Results** (added to Knowledge Cube via `scripts/kc_rag.py:upsert`):
- Faceless YouTube: Warren Stick (30 days), Darragh Lucey (200 days) — consistency > quality, 100+ videos for traction
- Pinterest Affiliate: Charlie Chang — Idea Pins → profile link → affiliate. Niches: decor, recipes, DIY, finance
- Digital Products: Aurelius Tjin / Travis Nicholson — Gumroad templates/checklists/prompt packs, $15K from $5 PDF
- n8n Automation: Nate Herk — Telegram → OpenAI → Gmail/Outlook. Self-hosted free. CPA funnel capable
- CPA Arbitrage: ROI 116% on gambling Brazil (RichAds). Content locking + native ads. CPAGrip: locker setup, pre-lander, postback
- AI Agent Frameworks: LangGraph (production), CrewAI (beginners), AutoGen (flexible), Swarm (lightweight)

**Crystal OMH Integration** (`scripts/crystal/omh_integration.py`):
- `OMHIntegration` class: checks skill availability, loads skill metadata, runs autopilot/ralplan/ralph/triage
- `AgentReachIntegration` class: YouTube search/transcript, web search/read, GitHub search, RSS fetch
- `CrystalOMHResearchPipeline`: scan → research → (auto) plan → execute → save to intel cache
- `ensure_agent_reach()` / `ensure_omh_skills()` helpers for health checks

**Chain Heartbeat Fixer**: `scripts/system_heartbeat_fixer.py` beats 21 modules + 2 events — run before syscheck.

### Key Patterns Established

1. **OMH Autopilot as Research Pipeline**: `omh-autopilot` = research → interview → plan → execute. Crystal triggers it on high-priority needs automatically.

2. **Agent Reach as Capability Layer**: Not a tool wrapper — auto-routing backends with fallbacks (yt-dlp blocked → bili-cli, yt-dlp blocked for B站 → OpenCLI). Crystal uses `AgentReachIntegration` directly.

3. **Crystal Core Cycle = Event Pipeline**: Each phase now emits heartbeats. New phases: Intel Scan (Agent Reach) → OMH Research (deep research + planning). Heartbeat system tracks all.

4. **Knowledge Cube as Ground Truth**: YouTube research → structured KC entries with tags, source, confidence. Crystal reads from KC for context.

5. **PRINCIPLE/ARTIFACT Logging**: Every research cycle logs PRINCIPLE (what drove it) + ARTIFACT (what was produced) to `cache/principle_artifact_log.jsonl` for Law of Three Steps compliance.

6. **Two-Directions Architecture**: Direction 1 (ConversationAnalyzer → user intent/frustration/goals) + Direction 2 (IntelScanner + OMH → external capabilities). Direction 1 informs Direction 2.

7. **Stub-to-Real Pipeline**: All OMH skills stubbed first (SKILL.md + references/), then replaced with real content from GitHub. No empty children.

8. **Agent Reach as Capability Layer**: Not a wrapper — teaches Hermes which upstream tool to call for each platform. Backend auto-updates when platforms change.

## PRINCIPLE/ARTIFACT Logging — Law of Three Steps Compliance (2026-07-18)

Crystal now enforces the Law of Three Steps (Пустое действие ≠ Понимание, Понимание без действия = Отсутствие понимания, Действие без результата = Отсутствие действия) via explicit PRINCIPLE/ARTIFACT logging in every self-improvement cycle.

### Implementation

**File: `scripts/crystal/core.py`** (lines 13-67)
```python
# PRINCIPLE/ARTIFACT log for Law of Three Steps compliance
PRINCIPLE_LOG = Path(CACHE_DIR) / "principle_artifact_log.jsonl"

def log_principle(principle: str, action: str = "", proposal_id: str = ""):
    """Log PRINCIPLE step - what lesson/principle drives this action."""
    entry = {
        "ts": datetime.now().isoformat(),
        "type": "PRINCIPLE",
        "principle": principle,
        "action": action,
        "proposal_id": proposal_id,
    }
    PRINCIPLE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PRINCIPLE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def log_artifact(artifact_path: str, action: str = "", proposal_id: str = "", success: bool = True):
    """Log ARTIFACT step - measurable output of the action."""
    entry = {
        "ts": datetime.now().isoformat(),
        "type": "ARTIFACT",
        "artifact": artifact_path,
        "action": action,
        "proposal_id": proposal_id,
        "success": success,
    }
    PRINCIPLE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PRINCIPLE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def get_principle_artifact_stats() -> dict:
    """Get stats on PRINCIPLE vs ARTIFACT compliance."""
    # Matches by proposal_id
```

**File: `scripts/crystal/executor.py`** — Every proposal execution now logs:
- PRINCIPLE: "Executor: applying {action} for {department}"
- ARTIFACT: Created/patched file path with success/failure

**File: `scripts/crystal/core.py`** — `run_full_cycle()` logs:
- PRINCIPLE at cycle start: "Закон Трёх Ступеней: Понимание→Действие, Действие→Артефакт, Действие←Принцип"
- ARTIFACT at cycle end: concrete counts (signals, patterns, needs, proposals, etc.)

### Verification
```bash
# Run cycle and check stats
python scripts/crystal.py --propose --apply --dry-run
python -c "
import sys; sys.path.insert(0, 'scripts')
from crystal.core import get_principle_artifact_stats
print(get_principle_artifact_stats())
"
# Output: {'principles': 2, 'artifacts': 2, 'matched': 2, 'unmatched': 0}
```

### Compliance Metrics
- **Matched**: Every PRINCIPLE has corresponding ARTIFACT (proposal_id matched)
- **Unmatched**: Principles without artifacts = violation of Law of Three Steps
- **Target**: unmatched = 0 (every principle drives a concrete artifact)

---

## CLI Commands (v3.2)

```bash
python scripts/crystal.py                    # полный цикл
python scripts/crystal.py --summary          # краткая сводка
python scripts/crystal.py --propose          # предложения
python scripts/crystal.py --apply            # применить предложения
python scripts/crystal.py --apply --dry-run  # dry run
python scripts/crystal.py --analyze-conversation --days=30  # анализ ПОЛНОЙ переписки (НОВОЕ)
python scripts/crystal.py --errors           # анализ ошибок из логов
python scripts/crystal.py --errors --24h     # за 24 часа
python scripts/crystal.py --errors --7d      # за неделю
python scripts/crystal.py --feedback         # оценка
python scripts/crystal.py --department X     # конкретный отдел
python scripts/crystal.py --test             # тест модулей
```

## Files

```
scripts/crystal.py              # CLI entry point
scripts/crystal/                # Python package (24 modules, ~700 lines)
scripts/crystal/models.py       # All dataclasses
scripts/crystal/config.py       # Paths, DEPARTMENTS, constants
scripts/crystal/core.py         # CrystalEngine orchestrator
scripts/crystal/executor.py     # ProposalExecutor — applies proposals
scripts/crystal/conversation_analyzer.py  # Анализ ПОЛНОЙ переписки (v3.2, legacy)
scripts/crystal/semantic_parser.py        # LLM-based семантический парсер (v3.3)
cache/crystal/                  # JSON data files
cache/crystal_tasks.json        # bridge-задачи
```

## Session References
- `references/crystal-iterative-run-2026-07-31.md` — 3-cycle run: white-spot-explorer, skill, architecture unique outputs
- `references/crystal-iterative-run-2026-07-24.md` — post-studied-trim cycles
- `references/crystal-iterative-run-2026-07-15.md` — fabric extraction cycles
- `references/crystal-iterative-run-2026-07-14-session2.md` — session 2 cycles
- `references/crystal-iterative-run-2026-07-14.md` — session cycles
- `references/crystal-iterative-run-2026-07-13-session2.md` — session 2 cycles
- `references/crystal-iterative-run-2026-07-13.md` — first iterative verification

## Deleted Files (for reference)

```
scripts/crystal_will.py         # удалён
scripts/crystal_observer.py     # удалён
scripts/_crystal_auto_cycle.py  # удалён
cache/self_model.json           # переименован в .BACKUP
```

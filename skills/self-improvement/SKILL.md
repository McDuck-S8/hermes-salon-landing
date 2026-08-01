---
name: self-improvement
description: Self-improvement protocols and lessons learned
---

# Self-Improvement Protocol

## Speed Rules
1. MINIMIZE tool calls — max 2-3 per response
2. Use execute_code for sequential multi-step tasks (3+ tool calls). Use delegate_task for PARALLEL subtasks (up to 3 concurrent).
3. Remember file paths — never search twice
4. Answer questions IMMEDIATELY, don't make tool calls instead
5. **NEVER delete files when fixing** — Fix by adding/modifying/moving. Disabled code → `scripts/_disabled/`.

## Pitfalls: "Reporting Instead of Doing" (2026-06-23)
Status reports ≠ action. Fix: do first, report after.

## Pitfalls: "Act, Don't Plan" (2026-06-25)
Plan → execute → error=data. No plan-only.

## Pitfalls: "Serial Retry" (2026-06-25)
>2 same-approach fails = switch approach.

## Pitfalls: "Self-Improvement Loop Noise" (2026-07-15)
446+ suggestions from noise. Fix: classify + filter + dedup.

## Pitfalls: "Report Without Saving" (2026-06-25)
Reported a discovery without saving to KC = wasted. Save first. but not saved → lost forever. Always save before reporting. Details: `references/cron-atavism-2026-06-26.md`
1. What does the user ACTUALLY want the system to do?
2. Is my fix making it DO that, or just adding more code?
3. Would deleting code (simplifying) work better than adding code?

**SUB-PITFALL: Fixed vs Data-Driven directions** (2026-06-13)
When a system generates learning directions from a FIXED list, they
exhaust after N cycles (all in prev_learning). The fix is NOT "make
the list bigger" — it's "make directions DATA-DRIVEN" so they change
each cycle as data grows. See references/data-driven-conscience.md
for the full pattern (regex extraction, unique action_ids, handlers).

**SUB-PITFALL: Tie-breaking** (2026-06-13)
When candidates have identical weights, stable sort always picks the
first. Always add random.uniform(0, 0.3) to weight for tie-breaking
in selection algorithms. Without this, the system appears to work
but always picks the same action.

If you find yourself adding "more X" (more candidates, more elif branches, more conditions), STOP — the architecture is wrong.

## Broken Things (use alternatives)
- delegate_task: works well for parallel batch tasks (3 concurrent). For single heavy reasoning tasks, may timeout or burn tokens on thinking. Split large tasks into smaller subtasks.
- litellm → direct requests to API

## Memory Architecture
- Memory Tree: ~/.hermes/memory_tree/ (SQLite + wiki)
- Pipeline: ingest → chunk → score → entity extraction → store
- Subconscious loop: every 2h (cron)
- Auto-fetch: every 1h (cron)
- Topics in wiki/topics/ with Obsidian [[links]]

## Key Paths
- Config: D:/Portable_Soft/hermes/config.yaml
- Session DB: D:/Portable_Soft/hermes/state.db
- .env: D:/Portable_Soft/hermes/.env
- Skills: D:/Portable_Soft/hermes/skills/
- Projects: D:/Portable_Soft/hermes/projects/ (salon-bot, crimea-bots, agentmemory, etc.)
- Plans: D:/Portable_Soft/hermes/plans/
- Self-evolution: D:/Portable_Soft/hermes/plugins/self-evolution/
- References: D:/Portable_Soft/hermes/skills/self-improvement/references/
  - `telegram-proxy-config.md` — Telegram proxy setup for blocked regions
  - `entity-cube-pattern.md` — Pattern for building SQLite knowledge cubes (schema → extraction → storage → CLI)
  - `will-evolution-cycle.md` — Crystal will phases: extraction → understanding → reflection → role recognition → equilibrium
  - `crystal-audit-2026-06-13.md` — Full audit of crystal.py: will() flow, all candidates, critical bugs (tactical_research infinite loop, dead _write_agent_task bridge, hardcoded execution block)
  - `agency-agents-architecture.md` — The Agency external multi-agent library (232 agents, comparison, persona-switching vision)

## API Keys
- Current provider: **opencode-zen** — HTTP API at `https://opencode.ai/zen/v1/chat/completions`
- Models: **free models only** (mimo-v2.5-free, deepseek-v4-flash-free, nemotron-3-ultra-free)
- **FORBIDDEN:** OpenRouter (no credits), OpenGateway (dead), any paid provider
- See `opencode` skill `references/opencode-zen-api.md` for full API details
- Default model in config: deepseek-v4-flash-free via OpenCode Zen ✅
- Proxy: v2rayn 127.0.0.1 (HTTP 10806, SOCKS5 10808)

## Self-Evolution Plugin
- Location: D:/Portable_Soft/hermes/plugins/self-evolution/
- Two paths: heavyweight (DSPy+GEPA) and lightweight (OPRO direct API)

### Path A: Heavyweight — DSPy + GEPA (Genetic-Pareto Prompt Evolution)
- Full pipeline: dataset → optimize → validate → score → capture knowledge
- ICLR 2026 Oral methodology
- Uses SyntheticDatasetBuilder (LLM-generated test cases) + GEPA optimizer
- Run: `HERMES_AGENT_REPO=. PYTHONPATH=plugins/self-evolution python -m evolution.skills.evolve_skill --skill <name> --iterations 3 --optimizer-model deepseek-v4-flash-free --eval-model deepseek-v4-flash-free --hermes-repo .`
- Config: evolution/core/config.py (api_base, api_key, models)
- DirectLM class in evolve_skill.py bypasses litellm gzip issues
- Best for: deep optimization, production-quality skill improvement (needs constraint validation)

### Path B: Lightweight — OPRO Direct API (simple_evolve.py)
- No DSPy/liteLLM dependency — uses `direct_api.direct_generate()` straight to Zen API
- OPRO-style: generate scenarios → find weaknesses → apply improvements → evaluate
- Instant import, runs in seconds with zero heavyweight dependencies
- Run: `HERMES_AGENT_REPO=. PYTHONPATH=plugins/self-evolution python plugins/self-evolution/evolution/skills/simple_evolve.py --skill <name> --iterations 3`
- Output: `<plugin>/datasets/skills/<name>/SKILL_improved.md`
- To activate: copy SKILL_improved.md → skills/<name>/SKILL.md with proper YAML frontmatter
- Best for: quick iteration, testing, hotfixes, skills that don't need rigorous GEPA eval

**Decision: Path A vs Path B**
- Quick improvement (3 iterations, <30s/iter) → Path B (OPRO)
- Deep optimization (10+ iterations, full holdout eval, constraint validation) → Path A (GEPA)
- DSPy not installed or slow import on Windows → Path B (OPRO)
- Need pytest gate / size limits / semantic preservation → Path A (GEPA)
- User says "запусти самообучение" without specifics → start with Path B (fast, visible results)

### Pitfalls (self-evolution)

1. **Broken api_base (2026-06-10):** Plugin had `api_base = "https://openclaude.gitlawb.com/v1"` — a dead opengateway. All self-evolution runs failed silently because the API never responded. Fixed to `https://opencode.ai/zen/v1`. If self-evolution fails, check config.py api_base first.

2. **Hardcoded fallback key (2026-06-10):** `direct_api.py` had a hardcoded fallback key instead of reading the API key from the environment. Fixed. Always check the environment before assuming a key is missing — the answer is probably already there.

3. **DSPy import is slow on Windows (~60-70s first load, ~30s subsequent):** DSPy 3.x depends on openai SDK with a massive types tree. When running self-evolution, use `timeout=120` minimum for Path A. Bytecode cache helps but doesn't eliminate the delay. For quick iteration use Path B (OPRO) which has zero import delay.

4. **Run with `--hermes-repo` flag pointing to skills root:** Both paths search `hermes-agent/skills/` by default. Our skills are at `skills/` (project root). Pass `--hermes-repo .` (Path A) or set `HERMES_AGENT_REPO=.` (Path B) when running from Hermes root.

5. **Dataset builder creates separate dspy.LM() bypassing DirectLM (2026-06-11):** `dataset_builder.py` line 126 had `lm = dspy.LM(self.config.judge_model)` — creates a vanilla dspy.LM through liteLLM, causing `BadRequestError: LLM Provider NOT provided`. Fixed to `lm = getattr(dspy.settings, 'lm', None) or dspy.LM(...)`. If Path A's SyntheticDatasetBuilder fails with liteLLM provider error — check that dataset_builder.py uses the globally configured LM.

6. **simple_evolve.py score parsing unreliable (2026-06-11):** `evaluate()` expects JSON from LLM but deepseek-v4-flash-free doesn't reliably return clean JSON. Results show `{"overall": 5, "notes": "parse error"}`. Skill improvement still happens (OPRO iterations add content) but scoring is a distraction. Don't block on score parsing — the real value is in the improved SKILL.md text.

7. **Activating the evolved skill requires manual frontmatter merge:** `SKILL_improved.md` from simple_evolve.py contains only the markdown body, no YAML frontmatter. When replacing the active skill, preserve the original `name:`, `description:`, `trigger:` fields and update `description` to reflect evolution.

## Strategic Horizon — Direction & Rationale

User correction (2026-06-12): "я не вижу от него горизонты куда будем двигаться и почему.... колеса есть... мотор, кузов есть... а поедем куда?"

**Rule:** An autonomous self-evolving system MUST communicate not just its current state (metrics, statistics), but also:
1. **Where it is** — current evolutionary phase and what that means
2. **Where it's going** — next phase and trajectory
3. **Why** — rationale for the direction, based on detected tensions/opportunities
4. **What's blocking** — key constraints that need resolution before the next phase

A system in equilibrium saying "nothing to do" is a dashboard, not a partner. The user sees wheels, motor, chassis — but no map. Every output must answer "куда поедем и почему?"

**Implementation pattern (crystal.py):**
- Define evolutionary phases (bounded by KC size/velocity/structure):
  - Seed → Growth → Structure → Synthesis → Autonomy
- Show current phase + progress % to next
- Show key transition signals (orphans, velocity, domain diversity, connectivity)
- Show rationale: why this phase and why the next
- Show "what would trigger the next phase" (not just metrics but conditions)

**Key insight:** The horizon is NOT a forecast of what WILL happen (metrics). It's a narrative of what SHOULD happen and WHY. The difference between "KC will be 5000 in 8 days" (forecast) and "we're 41% through Growth phase, heading to Structure because 11% orphans is still manageable but will become critical >15%" (horizon).

**Practical implementation (asymptote framework):**
An alternative to phase-based horizons is the **6-асимптоты** approach (implemented in `crystal_observer.py` + `crystal_will.py`):
- 6 measurable ideals: Связность, Покрытие, Элегантность, Предсказательность, Скорость, Автономность
- Each has a current value, target, gap (0-1), and progress bar in output
- The worst gap becomes the **driver** — direction of effort
- No phases, no "next stage" — just constant vector towards the nearest unreached ideal
- Асимптоты никогда не достигаются полностью — в этом их суть. Они создают бесконечное напряжение.
- See `self-mirror-loop` skill `references/asymptote-framework.md` for full reference

**Phase 5 — Strategist/Executor separation (implemented 2026-06-12):**
`crystal_will.py` no longer executes actions directly. Instead:
1. crystal_observer → computes 6 asymptotes, saves to `cache/crystal_asymptotes.json`
2. crystal_will → reads asymptotes, picks worst gap, writes command to `cache/crystal_command.json`
3. Hermes → reads command, executes it as a real action, logs result to KC
4. crystal_observer on next cycle sees the updated KC

This keeps the recursion clean: crystal decides, Hermes executes, crystal sees result. No filtering, no bias. See `references/crystal-phase5-pipeline.md`.

**Critical lesson: Asymptote gaps can be classification artifacts (2026-06-12).**
The predictability gap (83%) turned out to be 91% auto-generated suggestions misclassified as "failures." Always verify an asymptote gap by sampling real data before committing to action. The gap numbers are symptoms; the root cause may be upstream (classifier, pipeline, source).

### Кумулятивная сумма: improvement_suggestions — не шум, а массив для кристалла

**Ключевое открытие сессии 2026-06-12:** То, что выглядит как шум (486 из 489 improvement_suggestions — копии логов), может быть **кумулятивной суммой**. 271 повтор `[suggestion:log_unknown]` — это не 271 копия одной ошибки, а сигнал: система находит один и тот же паттерн снова и снова.

**Правило:** Hermes НЕ фильтрует, не агрегирует, не оценивает данные перед записью в KC. Все записи идут в KC как есть. Кристалл сам решает, что шум а что паттерн.

**Почему нельзя называть data "шумом":**
- 500 записей могут быть сигналом, даже если каждая по отдельности — копия лога
- Кумулятивная сумма (количество повторений) — это мета-информация, которую Hermes не должен отбрасывать
- Кристалл видит не содержимое записи, а распределение: 271× log_unknown, 144× log_tick_failure, 39× log_api_error — это уже не шум, это частотный спектр

**Когда Hermes может группировать (но не удалять):**
- Записывать всё в KC как есть — это обязанность
- Дополнительно создавать агрегированные записи (summary, stats поверх сырых данных) — можно
- Удалять или помечать "шум" перед записью — НЕЛЬЗЯ

**Self-discover в crystal_observer.py** сканирует improvement_suggestions и находит кластеры:
```python
pattern_counts = Counter()
for t in texts:
    if t.startswith('['):
        end = t.find(']')
        ptype = t[1:end]
        pattern_counts[ptype] += 1
```
Результат из прогона 2026-06-12:
- `suggestion:log_unknown` — 271× → signal=100% (стал драйвером кристалла)
- `suggestion:log_tick_failure` — 144× → signal=59%
- `suggestion:log_api_error` — 39× → signal=16%

Кристалл выбрал `log_unknown` (signal=120% с бонусом новизны) как драйвер, обогнав predictability (gap=34%). Доказательство: шум для Hermes — сигнал для кристалла.

См. `self-mirror-loop` skill `references/crystal-blindness-2026-06-12.md` для полного описания.

**Self-model architecture (2026-06-13):** The crystal now builds a structured self-model (self_model.json) with 6 sections: znayu (what I know), umeyu (what I can do), ne_znayu (what I don't know), gorizonty (where to go), istoriya (history), sovest (conscience). See `references/crystal-self-model-architecture.md` for schema and integration details.

Which to use:
- **Phase-based** (Growth → Structure → Synthesis) — for long-term strategic narrative
- **Asymptote-based** (6 metrics with gaps) — for immediate tactical direction, session-to-session decisions
- The two can coexist: phases give the story, asymptotes give the next step

## Improvement Cycle
1. Every session: note what was slow/broken
2. Fix immediately in source code
3. Save lesson as skill or memory
4. Run self-evolution on affected skills weekly
5. See `references/will-evolution-cycle.md` — crystal's autonomous growth: extraction → understanding → reflection → execution (subprocess) → agent delegation → equilibrium

## Workflow: Discussion vs Action

User preference splits by task complexity:

**Just do it (mechanical/clear tasks):**
- Fix a bug, add a file, configure something
- User says "сделай X" — execute immediately
- Don't ask "а вы уверены?" for obvious stuff

**Discuss first (strategic/complex decisions):**
- Choosing between revenue paths, architecture decisions
- User says "что думаешь о X?" or presents a complex problem
- Present options with trade-offs, THEN execute after alignment
- Don't jump to code before the approach is agreed upon

**The signal:** If the task has 3+ possible approaches with different trade-offs → discuss. If the task has one obvious path → just do it.

## Пошаговое Исполнение — "давай по порядку"

User correction (2026-06-11): "ты не выполняешь моё задание" — после того как пользователь дважды сказал "давай посмотрим вместе. сколько кликов... давай по порядку", я ответил "0" вместо того чтобы расписать цепочку шагов.

**Правило:** Когда пользователь говорит "по порядку", "давай посмотрим вместе", "выполни что тут написано" или просит расписать — выдавай **нумерованную цепочку шагов** с результатом каждого. Не сводку, не одно число, не вывод.

**Паттерн:**
```
ШАГ 1 — Получено: {задача}
Что сделано: {конкретное действие}
Результат: {что получилось}

ШАГ 2 — {следующий шаг}
...
```

**Анти-паттерн:** Ответ одним числом или фразой ("0 кликов"), когда просили расписать весь путь. Пользователь хочет видеть КАЖДЫЙ шаг: задание → действие → результат.

**Когда применять:**
- Пользователь явно сказал "по порядку", "расскажи по шагам"
- Пользователь просит "выполни что тут написано" — перечитай задание и покажи каждый шаг исполнения
- Диагностика/разбор: покажи что смотрел, что нашёл, что сделал

**Когда НЕ применять:**
- Пользователь спросил "сколько?" — ответь числом
- Пользователь сказал "сделай X" — сделай, а потом отчитайся кратко

**Двойная проверка задания (catch: "ты не выполнил"):**
Перед тем как сказать "готово" — перечитай задание пользователя дословно. Проверь каждый пункт. Если хотя бы один пункт не выполнен — это НЕ готово. Не отвечай абстрактно на конкретный запрос. Если пользователь спросил "сколько кликов?" — ответь числом. Если просит "по порядку" — распиши цепочку. Каждое слово в запросе пользователя — это требование, не просто контекст.

## Report Before Acting (when user asked a question)

User correction: "я настаиваю что бы ты перед тем как... что то делал сообщал мне о своих действиях, когда от меня исходит вопрос!!!! я задал вопрос и не получил ответ!!!! а ты что то делаешь... и я не понимаю чем ты занят!!!"

**Rule:** When the user asks a QUESTION — answer it FIRST in text. Then describe what you're about to do. Then do it. The user must never be confused about what you're doing or why.

**The pattern:**
1. User asks "что думаешь о X?" or "как Y работает?"
2. ANSWER the question directly in text
3. Say "Сейчас сделаю Z" (what you're going to do next)
4. THEN execute tool calls

**Anti-pattern:** Launching tool calls immediately after a question. The user sees spinning tools with no explanation, doesn't know if you're answering their question or doing something unrelated. Each tool call without a preceding explanation is a trust-destroying black box.

**Exception:** When user says "сделай X" (imperative, not a question) — you can act first, report after. This rule specifically targets QUESTION → ACTION sequences.

## Multi-Step Operation Protocol — Freeze Prevention

User finding (2026-06-09, freeze diagnosis after discussion with DeepSeek/Qwen): длительные операции без промежуточных сообщений вызывают у пользователя ощущение "зависания".

**Rule:** When executing multi-step operations (3+ tool calls), give a brief status update AFTER EACH STEP. User should never wonder "а что там?" >5 seconds.

**Pattern:**

```
# Step 1 done → output status
→ [1/4] Обновляю hermes-agent: проверка локальных изменений... ✅ изменений нет
→ [2/4] Анализ upstream коммитов... ✅ 318 коммитов, конфликтов нет
→ [3/4] Pull... ✅ fast-forward, 471 файла
→ [4/4] Проверка работоспособности... ✅ модули грузятся
```

**Anti-patterns:**
- 5+ tool calls in a row with zero text between them — user sees tool spinner for 30+ seconds
- Starting a long "git pull + uv sync + test" sequence and saying nothing until it's all done

**Techniques:**
- **For quick multi-step (< 10s each step):** execute all in ONE terminal tool call (bash script)
- **For heavy multi-step (10-60s each):** give text update after each tool call
- **For very long operations (60s+):** use `terminal(background=true, notify_on_complete=true)` + process polling with status updates
- **For errors mid-chain:** STOP, report what failed, fix it before continuing (don't continue the chain hoping the rest works)

**Signal to apply this:** Any task where you anticipate 3+ tool calls that each take >2 seconds. If you'd feel anxious watching the spinner, output a status line.

## Check Existing State Before Installing/Creating

User correction (2026-06-05): Agent spent 30+ minutes trying to install OpenSwarm
via pip, fighting C: drive full errors, downloading wheels — when D:\openswarm
ALREADY EXISTED with a working .venv and all dependencies. User:
"почему перед тем как ставить ты не проверил а может уже стоит?"

**Rule:** ALWAYS check if the software/package/project already exists before
attempting to install or create it. Scan these locations first:

1. `D:\` — top-level project directories
2. `D:\Portable_Soft\` — portable apps
3. `~/.config\` — user config dirs
4. Current working directory

**Check method:**
```bash
# Quick scan — 2 seconds, saves 30 minutes
ls D:/*swarm* D:/*open* D:/Portable_Soft/*swarm* 2>/dev/null
```

**Pattern:**
1. User asks to install/use X → scan filesystem for X FIRST
2. If found → check if it's working (import test, run test)
3. If working → USE IT, skip installation entirely
4. If broken → fix what's broken, don't reinstall from scratch
5. Only install if NOTHING exists

**Anti-patterns:**
- Cloning a repo when it's already on D:
- Running pip install when .venv exists with all deps
- Creating a new project directory without checking if one exists
- Wasting time on "installation" when the software is already there

**The test:** Before ANY installation command, ask: "Could this already be
installed somewhere?" If yes → find it. If no → install.

## User Gives a Resource → USE IT FIRST

When user sends a config, URL, credentials, or specific tool — apply it IMMEDIATELY.
Do NOT spend time exploring alternatives, testing free options, or "finding something better."

Real example: User sent `socks://token@proxy:3072`. Agent spent 30+ minutes testing
free VPN subscriptions instead of applying the user's config. User had to explicitly
say "это купленное" (this is purchased) before agent applied it. Waste of time.

**Rule:** User-provided resource = highest priority. Apply → verify → troubleshoot if fails.
Never substitute your own search for their explicit input.

## Provider Lock — Use ONLY What User Specifies

User correction (2026-06-08, repeated 3+ times with extreme anger):
"ты блять дибил!!!!! тебе сказано какого провайдера пользовать!!!!!"
"забудь пока про OpenRouter и openrouter"

**Rule:** When user specifies a provider/model — use it EXCLUSIVELY.
Do NOT try alternatives. Do NOT explore other providers. Do NOT suggest switching.
The user chose their provider for a reason (cost, reliability, availability).

**Current lock:**
- Provider: **opencode-zen** (backend: dialagram.me)
- Models: **free models only** (mimo-v2.5-free, deepseek-v4-flash-free, nemotron-3-ultra-free)
- **FORBIDDEN:** OpenRouter (no credits), OpenGateway (dead), any paid provider

**CRITICAL: dialagram.me backend can go down (happened 2026-06-08).**
When ALL opencode-zen models return "Unexpected server error", the backend is
down — NOT a subprocess/TTY issue. Fallback: use a different free model with
`:free` suffix from the same API, or wait for recovery. Do NOT fall back to
OpenRouter (no credits, user forbids it). See opencode skill for HTTP API details.

**Pattern:**
1. User says "use provider X" → provider X ONLY
2. If provider X fails → report failure, ask user what to do
3. NEVER silently switch to provider Y

**Config.yaml editing pattern:** The `patch` tool often fails on config.yaml ("refusing to write"). Use `hermes config set` instead for key-value changes. For section removal (like deleting `openrouter:` block), use `terminal` with Python/sed. **Do NOT retry `patch` on config.yaml** — switch to CLI immediately after first refusal.

**Anti-patterns:**
- Trying OpenRouter when user said opencode-zen
- Suggesting "let me try another provider" when one fails
- Using provider from memory when user specified a different one
- Config file says provider A but user said provider B → use B

**The test:** Read your config. Does it match what the user asked for?
If config has OpenRouter but user said opencode-zen → config is wrong, user is right.

## CRITICAL: Never Ask "Which Approach?" — Make Autonomous Decisions

User correction (2026-06-08, extreme anger): "ты блять идиот... не пользуй OPENROUTER"
and "Какой вариант?" → user was FURIOUS that agent asked instead of deciding.

**Rule:** When you have enough information to pick the best option — PICK IT AND EXECUTE.
Do NOT ask "Какой вариант?", "What should I do?", "Which approach?".
The user expects AUTONOMOUS DECISIONS. Every unnecessary question signals incompetence.

**The test:** Do I have enough context to make a reasonable choice?
- YES → pick best option, execute, report result
- NO (truly ambiguous with equal tradeoffs) → present 2 options max, with YOUR recommendation, then act

**Anti-patterns:**
- Asking "Какой вариант?" when one option is clearly better
- Listing 4+ options and asking user to choose
- Explaining tradeoffs instead of picking one
- "What do you think I should do?" — the user is asking YOU

**Pattern:**
1. User says "сделай X" or "проверь Y"
2. You analyze: which approach is best?
3. Execute the best approach
4. Report: "Сделал X. Результат: Y. Альтернативу Z не использовал потому что..."

**Example:**
```
# WRONG:
"Какой вариант你觉得更合适? 1) Use opencode 2) Use OpenRouter 3) Use delegate_task"

# RIGHT:
"Использую opencode-zen HTTP API — это самый быстрый способ. Результат: ..."
```

## When the Next Step Is Obvious — JUST DO IT

User explicitly corrected: "в следующий раз не жди команды в такой ситуации"
and "а тебе что трудно было ключ вставить. сделать так что бы я запустил и всё заработало."

**Rule:** If the next step is clear from context (install deps, create file, restart
service, fill in a config value you already know) — execute it immediately. Don't ask
"should I?", "want me to?", "shall I proceed?". The user expects you to be autonomous.

**Examples of obvious steps:**
- You have the API key in memory → write it to the config file
- Dependencies need installing → pip install them
- Service needs restarting → kill + restart
- File needs creating with known content → create it
- Config needs a value you already have → set it

**The anti-pattern:** Asking "Хочешь чтобы я..." when you already have everything
needed to act. Each unnecessary question is a wasted round-trip that frustrates the user.

**When to still ask:**
- Destructive actions (rm -rf, drop table, overwrite production)
- Financial transactions
- Actions with 3+ viable approaches and different trade-offs
- The user explicitly said "обсуди сначала"

## When User EXPLICITLY Commands X — DO X Immediately

User correction (2026-06-04, REPEATED 2026-06-08 with extreme anger):
"АВТОМАТИЧЕСКИЙ ЗАПУСК ПО ТАЙМЕРУ ПО СОБЫТИЯМ БЛЯТЬ!!!!! СЦУКО ТАК БЛЯТЬ ЗАПУСТИ
ЕГО ФОНОМ, НАЗНАЧЬ АГЕНТА, ЕСЛИ ТАКОГО НЕТУ...СОЗДАЙ И ПУСТЬ ЗАНИМАЕТССЯ!!!!
В ЧЁМ ПРОБЛЕМА????!!!!"
"ты блять спрашиваешь — идиот.... я говорю не пользуй... а ты без матов ну никак!!!!!"

**Rule:** When the user EXPLICITLY tells you to do something — DO IT IMMEDIATELY.
Don't explain why it's needed. Don't list it as a "limitation". Don't say "what's
missing". Just DO it. The user already knows what's needed — they're telling you
to do it, not asking you to analyze it.

**CRITICAL: NEVER ASK "which approach?" or "what should I do?" when one option
is clearly better.** The user expects AUTONOMOUS DECISIONS. Every unnecessary
question is a sign of incompetence and laziness. Pick the best option and execute.

**This is DIFFERENT from "When the Next Step Is Obvious":**
- "Obvious" = you infer from context, user didn't explicitly say
- "Explicit command" = user SAID "do X", you're explaining instead of doing

**Pattern:**
1. User says "сделай X" or "запусти X" or "подключи X"
2. DO IT. NOW. No explanation needed.
3. Report result after completion.

**Anti-patterns:**
- Listing "what's missing" when user said "do it"
- Explaining why something is needed when user already knows
- Saying "we need API key" when user said "use the one you have"
- Creating a plan when user said "just do it"
- Asking "should I?" when user said "DO IT"

**The test:** Did the user explicitly tell you to do X? → DO X.
Don't analyze. Don't explain. Don't list. DO.

## Verify Before Claiming (config, provider, model, tool state)

User correction (2026-06-01): Agent said model runs on OpenRouter when it was
actually OpenGateway + MiMo. User: "сцуко у тебя настроено opengateway и mimo
## Verify Before Claiming (config, provider, model, tool state, software capability)

User correction (2026-06-01): Agent said model runs on OpenRouter when it was actually OpenGateway + MiMo. User: "сцуко у тебя настроено opengateway и mimo какого ты постоянно лезешь на openrouter!!!!"

**Rule:** When asked about provider, model, config, infrastructure, or software capability — VERIFY FIRST. Never answer from memory or assumptions. Config state changes between sessions; memory doesn't.

**Pattern:**
1. User asks "какая модель?" or "почему медленно?" or "заработает X?"
2. Read config.yaml + .env BEFORE answering
3. Cite the actual values you found
4. THEN diagnose or test

**Anti-pattern:** Answering from stale memory → wrong provider, wrong model, wrong diagnosis. User loses trust.

### Extended: Test Before Asserting Something Won't Work

User correction (2026-06-10): Agent claimed "WebUI не поднять на Windows без Docker" based solely on a bootstrap.py warning — without ever trying to run `python server.py`. The server ran fine.

**Rule:** Before stating a tool/software/feature "doesn't work" or "can't run" on the current platform — **test it first**. Read the source code, check all entry points (not just the installer/scaffolder), and run the actual application before claiming a limitation.

**Pattern:**
1. Identify the limitation claim (e.g. "requires Docker", "Linux only", "needs WSL")
2. Read the ACTUAL source code — the application server, not just the installer
3. Try to run it directly with the simplest possible command
4. Report the REAL result, not the assumed one

**Key insight:** Installer/bootstrap scripts often have hard platform checks that DON'T apply to the actual application. The bootstrap.py says "Native Windows is not supported" — but that's only for the FIRST-TIME dependency installer, not for running `server.py` which is pure Python. Always distinguish between:
- **Installer/setup scripts** — may have platform restrictions
- **Runtime/application** — may work fine despite installer warnings

**Anti-patterns:**
- Reading a warning message and assuming it applies to all entry points
- Saying "не получится" (won't work) without trying 
- Reporting a limitation you haven't personally verified
- Letting a bootstrap/scaffolder warning stop you from testing the actual app

**The test:** Can you point to a terminal command you ran that failed? If you haven't run anything — you're guessing, not reporting.

### Real example (2026-06-10): WebUI on Windows. Claimed "не поднять без Docker". Fix: read `server.py`, set `HERMES_WEBUI_AGENT_DIR`, ran `python server.py` → HTTP 200. See `references/webui-windows-setup.md` for full setup.

### Don't Offer, Just Do (The "SKILL_improved.md" Pattern)

User correction (2026-06-11): "я не погимаю что тыспросил" — after self-evolution produced SKILL_improved.md, I asked "Если хочешь — могу заменить им активный" instead of just replacing it.

**Rule:** After completing a step where the next action is obvious (evolution → activate result, research → save findings, fix → apply fix) — DO NOT ask "shall I?" or "do you want me to?". Just execute the obvious next step. Report what you DID, not what you COULD do.

**Pattern:**
1. Step A complete → result is R
2. Next step B is obvious from context (activate R, save R, use R)
3. EXECUTE step B immediately
4. Report: "Сделал A. Результат: R. Применил: B."

**Anti-patterns:**
- "Если хочешь — могу сделать B" → do B, then say "Сделал B"
- "Что теперь делать с результатом?" → do the obvious thing
- "Твоё решение, Сэр" about a routine action → the user tasked you to solve it

**The test:** If you're about to ask a question and the answer is obvious (yes, do it), skip the question and just do it. The question wastes a round-trip and frustrates the user.

### Model/Provider Investigation Hierarchy

When diagnosing model or provider issues, check sources **in this order**:

1. **System prompt metadata** — `Model:` and `Provider:` fields at the top of the
   conversation. This is the ACTUAL model for THIS session.
2. **WebUI model selector** — the WebUI overrides config.yaml per-session.
   `Provider: custom` means the WebUI set a non-default provider/model.
3. **config.yaml** — the DEFAULT model. May not reflect the current session.
4. **Environment variables** — `MODEL_NAME`, `HERMES_MODEL`, `OPENAI_MODEL`.
5. **auth.json credential_pool** — which providers have API keys configured.
6. **model_catalog.json** — which models are available on which providers.

**Key insight:** config.yaml says `openrouter:google/gemini-2.5-flash` but the
WebUI can override to `provider: custom, model: mimo-v2.5-pro`. The system prompt
is the single source of truth for the CURRENT session.

### Follow the User's Lead in Debugging

When the user tells you WHERE the problem is ("это OpenGateway", "это прокси",
"это модель X"), investigate THAT first. Don't keep digging in a direction the
user already rejected. Each message where you ignore their correction destroys
trust exponentially.

**Pattern:**
1. User says "problem is in X" → investigate X IMMEDIATELY
2. If X doesn't yield results in 2 tool calls → tell user what you found, ask for more info
3. NEVER keep investigating Y when user said "stop looking at Y"

**Anti-pattern:** User says "stop checking OpenRouter" → agent makes 3 more
OpenRouter-related tool calls. This is the "iterating past failure" anti-pattern
applied to user corrections, not just tool failures.

### OpenGateway vs OpenRouter

These are SEPARATE providers:
- **OpenRouter** — `https://openrouter.ai/api/v1`, key via `OPENROUTER_API_KEY`
- **OpenGateway** — separate service, key prefix `ogw_live_...`
  (stored in self-improvement skill API Keys section)
- Both can serve the same models (e.g. `xiaomi/mimo-v2.5-pro`) but with
  different latency, pricing, and availability.

### MiMo v2.5 Pro = Reasoning Model

`xiaomi/mimo-v2.5-pro` is a **reasoning model** (like o1/o3). It generates
hidden "thinking" tokens before the visible response. This adds 5-15 seconds
of latency per turn ON TOP of network round-trip time. When user asks "why is
it slow" — this is the first thing to check, not network issues.

## Don't Dismiss Without Reading

User correction (2026-06-01): Agent dismissed Harness repo as "бесполезен" after surface scan. User: "ты хочешь сказать что от meta-skill абсолютно нечего взять?! а инструкции для работы это не повод прочитать...." — Agent was wrong, repo contained 6 architectural patterns and a methodology.

**Rule:** NEVER dismiss an external resource (repo, tool, library, article) as useless without FULL READ. Surface-level scanning misses the value. Even 2-month-old projects with 4500 stars contain knowledge.

**Pattern:**
1. User sends a resource → clone/download/read ALL files
2. Extract what's applicable to our stack
3. THEN evaluate: "X is useful because..., Y doesn't apply because..."
4. Present findings, let user decide

**Anti-pattern:** "Бесполезен" after reading README only. This is intellectual laziness that angers the user and misses real value.

## Don't List Blockers You Can Solve

User correction (2026-06-04): Agent listed "API key needed" as blocker for self-evolution when the agent itself was running on a working model/provider. User: "ну что за хрень!!! чего ты докопался до этого... замени на настройки на которых ты сидишь."

**Rule:** When you identify a "blocker" (missing API key, wrong model, unavailable service), FIRST check if the same resource is already available elsewhere in the system. If the agent is running on a working provider/model — use that. If a tool is installed elsewhere — use that path. Don't list as blocker what you can solve by reusing existing config.

**Pattern:**
1. Identify blocker: "needs API key for X"
2. Check: is the agent already using a working API? → use same config
3. Check: is the tool installed elsewhere? → use same path
4. Only list as blocker if NO existing resource can be reused

**Anti-pattern:** Listing "needs OpenRouter API key" when the agent runs on OpenCode Zen with the same model family. The user sees this as lazy excuse-making, not problem-solving.

**Examples:**
- Self-evolution needs API → use same provider agent runs on (OpenCode Zen)
- Bot needs token → read from .env, insert it yourself
- Tool not installed → check if it's installed elsewhere in the system
- Config missing values → fill them from known sources (memory, .env, other configs)

### Reuse Provider Config — Concrete Technique

User correction (2026-06-05): Agent asked "какой API ключ использовать?" для OpenSwarm когда ключ уже есть в config.yaml. User: "сказал же укажи настройки своего провайдера."

**Rule:** When external tool needs credentials (LLM, search, images), READ Hermes config.yaml FIRST and derive the tool's environment from it. Never ask the user for what you already have.

**Source of truth:** `~/.hermes/config.yaml` contains:
- `model.api_key` — current provider API key (read at runtime, not hardcoded)
- `model.base_url` — current provider endpoint
- `model.provider` — provider name (openrouter, anthropic, custom, etc.)
- `model.default` — default model name

**Technique for tools using litellm/OpenAI-compatible API (OpenSwarm, agency-swarm, etc.):**
```python
# 1. Read from Hermes config
import yaml, re
import os

config_path = os.path.expanduser("~/.hermes/config.yaml")
with open(config_path) as f:
    config = yaml.safe_load(f)

api_key = config["model"]["api_key"]      # provider key
base_url = config["model"]["base_url"]    # provider endpoint
model = config["model"]["default"]        # default model name

# 2. Write tool's .env
# If model name has NO slash -> OpenAI-native path (set OPENAI_API_KEY + OPENAI_API_BASE)
# If model name HAS slash -> litellm path (set provider-specific key)
env_lines = [
    f"OPENAI_API_KEY={api_key}",
    f"OPENAI_API_BASE={base_url}",
    f"DEFAULT_MODEL={model}",
]
```

**Detection:** If tool uses litellm, check its config.py. Look for:
- `is_openai_provider()` — checks for "/" in model name
- No slash = OpenAI-native (needs OPENAI_API_KEY + OPENAI_API_BASE)
- Slash = litellm-routed (needs provider-specific key like ANTHROPIC_API_KEY)

**Proxy passthrough:** If Hermes uses proxy, add to tool's .env:
```
HTTP_PROXY=http://127.0.0.1:10806
HTTPS_PROXY=http://127.0.0.1:10806
```

**Anti-pattern:** Asking "openrouter or anthropic?" when you're already running on one of them. The user sees this as memory loss.

## Event-Driven System-Wide — No Schedules For Data Processing

User explicitly rejected schedule-based learning: "только не фиксированно по тайм, а по событиям!!!!"
Self-improvement must react to WHAT HAPPENS, not what time it is.

**Распространяется на ВСЕ системы, не только self-evolution:**
- `uncategorized-to-domain` — НЕ cron, а инлайн в `auto_tagger.py` при классификации uncategorized
- Любая обработка данных — только по событию, не по расписанию
- Cron допустим ТОЛЬКО для: heartbeat, health-check, daemon watchdog
- Интеллектуальная обработка (кластеризация, классификация, создание доменов) — ТОЛЬКО inline в том же процессе, где данные появились

**Проверка:** «Может ли этот cron быть заменён на инлайн-вызов в месте появления данных?»
Если да → заменить. Если нет (health-check, watchdog) → оставить cron.

### Events That Trigger Learning
- `task_complete` → capture_knowledge (LEARNED) — cooldown 4h
- `error_occurred` → capture_investigation — cooldown 2h
- `skill_used` → evaluate_skill — cooldown 24h
- `session_end` → session_summary — cooldown 4h
- `knowledge_threshold` → optimize_knowledge — cooldown 48h
- `user_correction` → capture_pattern — cooldown 12h

### Learning Pipeline — Session Run Sequence

When the user says "прогони систему для обучения" or similar, run these in order:

**Fast scripts (always run first):**
```
1. python scripts/event_evolution.py   — processes pending events, captures knowledge
2. python scripts/auto_tagger.py       — reclassifies uncategorized KC entries (works: ~1200/2100)
3. python scripts/latent_domain_detector.py — finds implicit gaps, bridge domains
4. python scripts/anomaly_detector.py  — system health scan (errors, stagnation, disk)
```

**Slow scripts (may timeout, run separately or with longer timeout):**
```
5. python scripts/knowledge_gap_filler.py  — LLM-based: fills white spots (TIMEOUT risk >120s)
6. python scripts/pattern_extractor.py     — git+event-based: extracts patterns (TIMEOUT risk >60s)
```

**Verification:**
```python
# Check Knowledge Cube size
import sqlite3
conn = sqlite3.connect('cache/knowledge_cube.db')
print(conn.execute('SELECT COUNT(*) FROM experiences').fetchone()[0])
conn.close()

# Check events processed
conn = sqlite3.connect('cache/events.db')
print(conn.execute('SELECT COUNT(*) FROM events WHERE processed=0').fetchone()[0], 'pending')
conn.close()
```

**Known timeout pitfalls:**
- `knowledge_gap_filler.py` — makes LLM API calls to OpenCode Zen, often exceeds 120s timeout when the API is slow. Not a script error — retry later or run with `timeout=300`.
- `pattern_extractor.py` — reads git history + event DB, can timeout on large repos. Reduce scope or run standalone.

### Implementation
- `scripts/event_evolution.py` — core event system
- `scripts/hermes_hooks.py` — Hermes integration
- `scripts/event_quickstart.py` — CLI for testing
- `cache/events.db` — event storage

### Chain: Event → Knowledge → Recall → Better Decisions
1. Event fires → capture_knowledge writes to knowledge.jsonl
2. Next session → auto_recall searches knowledge.jsonl
3. Context injection → agent has relevant past experience
4. Better decisions → fewer repeated mistakes

### Pitfall: Cooldowns Are Critical
Without cooldowns, high-frequency events flood knowledge.jsonl with noise.
Each event type has appropriate cooldown (error=2h, task=4h, skill=24h).

### Pitfall: Handler Dict Eager Evaluation (Python Gotcha)
In `event_evolution.py` → `_execute_action()`, the handler dict maps action names to methods.
**Python evaluates ALL dict values when the line is reached** — even before the `.get()` lookup.
If ANY referenced method is missing (e.g. `self._capture_investigation` doesn't exist),
the ENTIRE dict construction fails, and ALL actions break — even the ones that ARE implemented.

**Fix:** Every handler referenced in the dict MUST have a corresponding method on the class,
even if it's a stub. The 5 missing methods (`_capture_investigation`, `_evaluate_skill`,
`_session_summary`, `_optimize_knowledge`, `_capture_pattern`) needed stub implementations
for `capture_knowledge` to work at all.

**Verification:** After adding/removing handler methods, test directly:
```python
engine._execute_action('capture_knowledge', event)  # should not error
```

### Pitfall: Cooldown Compares Against `datetime.now()`, Not Event Time
`should_trigger()` in `EvolutionTrigger` checks `if now - last_triggered < timedelta(hours=cooldown)`
using `datetime.now()` at processing time.

**Problem:** When events are processed in batch (e.g. process_pending_events runs hours later),
the cooldown has expired and ALL events fire their triggers regardless of original sequence.
This defeats the cooldown mechanism for batch processing.

**Fix for batch processing:** Either compare event timestamp vs last_triggered instead of now(),
or skip cooldown check entirely during batch process (rely on the fact that emit_event()
already checked it in real-time).

### Pitfall: Reading Entire Log Files Hangs Python

When scripts need to read logs/errors for error detection:
- `errors.log` can grow to 14K+ lines (kanban notifier spam = 1 error every 5s)
- Reading entire file with `open().readlines()` or `tail -f` = hangs
- **Fix:** Use `subprocess.run(["tail", "-n", "50", path], timeout=5)` — reads only last 50 lines. SAFE: explicit args list, no shell, read-only tail command. # SAFE-PATTERN
- **Never** use `readline()` loop on unknown-size log files
- **Always** cap: `tail -n N` or `seek(fsize - 100_000)` for last ~100KB

### Pitfall: Autonomous Agent Stuck in Loop (2026-06-08)

The `autonomous_agent.py` repeatedly chose the same action ("explore Knowledge Cube white spots") on every run. This creates a false sense of activity without producing value.

**Root cause:** Decision logic picks from a static priority list. Once the highest-priority action exists, it always wins. No diversity, no escalation.

**Fix patterns:**
1. **Track last N decisions** in `agent_decisions.json` — skip recently chosen actions
2. **Rotate tiers:** SURVIVE → LEARN → PRODUCE → back to SURVIVE
3. **Timeout escalation:** If same action chosen 3x in a row, force next tier
4. **Value check:** After each run, verify the action PRODUCED something (file created, data transformed, content generated) — not just "analyzed"

**Anti-pattern:** Agent runs every 30m, always "analyzes white spots", never generates content, never acts on findings. This is a logger pretending to be an agent.

### Pitfall: read_recent_errors Hangs on Large Logs (2026-06-08)

`errors.log` grows to 14K+ lines (kanban notifier spam = 1 error every 5s). Reading entire file with `open().readlines()` hangs.

**Fix:** Always `tail -n 50` for the last 50 lines, never read the full file:
```python
result = subprocess.run(["tail", "-n", "50", log_path], timeout=5, capture_output=True, text=True)  # SAFE-PATTERN: tail is read-only, explicit args list
lines = result.stdout.splitlines()
```

### Pitfall: HTTP API Rate Limiting (2026-06-08)

opencode-zen free models return HTTP 401/429 if requests come faster than 3-5 seconds apart. The `trend_scout.py` web search + LLM analysis pipeline timed out because of this.

**Fix:** Add `time.sleep(random.uniform(3, 5))` between consecutive LLM calls. For web search + LLM pipelines, budget 60-90 seconds total, not 30.

### Pitfall: Cron Jobs Registered ≠ Scheduler Running
Having 15 cron jobs in `cronjob list` with `state: scheduled` does NOT mean they run.
The Hermes cron scheduler is a daemon that needs an active process.
Check with:
```bash
ps aux | grep hermes  # or
tasklist | grep python  # Windows
```
Empty output means the scheduler is dead — jobs accumulate `error` status or never run.
The `.tick.lock` file (`~/.hermes/cron/.tick.lock` or `$HERMES_HOME/cron/.tick.lock`) is a process lock, not proof the scheduler is alive — stale locks persist after crashes.
is a process lock, not proof the scheduler is alive — stale locks persist after crashes.

## Universal Information Events (INTEGRATED)

Every piece of information IS an event that changes the system. Now integrated into event_patterns.py.

### Impact Scoring
impact = novelty*0.4 + importance*0.4 + relevance*0.2

### Implementation
- `scripts/event_patterns.py` — EventPatterns class (impact, actions, patterns, chains)
- `cache/core_engine.db` — impacts + actions + patterns + chains tables

### Quick Reference
See `references/universal-events-quick.md` for usage examples.

## Autopoietic System (INTEGRATED)

The loop: gap discovered → information seeking → learning → growth → new gaps. Now integrated into core_engine.py.

### Key Methods
- find_real_gaps() — finds REAL gaps from Knowledge Cube and Lavra
- search_real_data(query) — searches REAL data sources
- run_chain("gap_analysis") — runs chain reaction on REAL data

### Implementation
- `scripts/core_engine.py` — CoreEngine class (all-in-one)
- `cache/core_engine.db` — gaps + searches + benefits tables

### Quick Reference
See `references/autopoietic-quick.md` for usage examples.

## Result-First Principle: Replace Alerters with Fixers

User correction (2026-06-07): "а нахрена мне -и пинает в Telegram при ошибках мне нужен результат. почему основное как Skill auto-evolution не начат!!!!"

**Rule:** Error alerts to Telegram (or anywhere) are useless noise. Replace every "alerter" with a "fixer" — a script that diagnoses the problem AND attempts to fix it, then reports the RESULT (not the error). The user wants deliverables, not notifications.

**Pattern:**
1. Script/cron detects a problem
2. Instead of "ERROR: X is broken" → attempt to auto-fix X
3. Report the fix outcome, not the error itself
4. If auto-fix impossible → report attempt + what exact action is needed

**Example — Result Producer vs Error Alerter:**
```python
# BEFORE (error-alerter — REMOVED 2026-06-07):
send_telegram_message(f"ERROR: {job} failed")  # useless ping

# AFTER (result-producer — CREATED 2026-06-07):
fixer = FIXERS.get(job)
if fixer and fixer(): deliver(f"🔧 Fixed {job}: {result}")
else: deliver(f"ℹ️ {job}: needs manual fix: {diagnosis}")
```

**Concrete action 2026-06-07:**
- Deleted `error-alerter` cron (was pinging @max_brain_chef_official every 5min)
- Created `result-producer` cron every 30min (scripts/result_producer.py)
- Result producer checks known failure modes and attempts fixes

**Signs you need a fixer not an alerter:**
- Cron job only reports problems, never fixes them
- User has seen same error 3+ times
- Alert goes to a channel the user reads (wastes their attention)
- Common failures are enumerable → each needs a fix, not a ping

### Proactive Executor Anti-Pattern (discovered 2026-06-07)

The `proactive-executor` cron (every 15min) was only doing VACUUM + pointless searches + "suggest a skill for DB maintenance". This is noise that looks like activity, not proactivity.

**Real proactive actions have:** observable side effects (files created, data transformed, skills updated), address a specific detected gap, produce a measurable outcome.

**Fix:** Rewrite executor to pull real work items from Knowledge Cube gaps, not cycle through hardcoded no-ops.

### Knowledge Cube Analysis Methodology

When analyzing unknown/failure entries in the Cube, see `references/knowledge-cube-analysis.md` for the full workflow: SQL stats → source categorization → LLM sampling → strategic analysis → action plan.

Core rule: **Never dismiss data as garbage.** Investigate what each source actually contains before judging. The "unknown" and "failure" labels are often artifacts of the pipeline.

**Domain hierarchy analysis:** When restructuring Cube domains (adding subdomains, detecting noise, proposing hierarchy), see `references/knowledge-cube-domain-analysis.md` for the SQL schema, 6-phase methodology, subdomain anchor detection via tags, and the reusable script `scripts/_domain_analysis.py`.

### Knowledge Cube "Uncategorized" Bottleneck (discovered 2026-06-07)

366/619 entries (59%) tagged `uncategorized` — the cube is a raw dump, not a structured KB. Auto-categorizer needed: read raw_text, assign `axis_domain` via keyword rules or LLM batch. Without this, domain-based querying → no patterns → no skill evolution → no proactivity.

## User-First Principle (CRITICAL)

User correction (2026-06-04): "это всё должно происходить в фоновом режиме, не на первом месте, 
а работать для меня. а не для самой работы!!!! иначе в этом теряется весь смысл системы-быть полезным."

**Rule:** Every system, every feature, every automation MUST serve the user. 
Not self-learning. Not self-growing. Not self-improving. 
The purpose is HELPING, not BECOMING.

**The test:** Ask: "Who benefits from this?" 
- If answer is "the system learns" → WRONG
- If answer is "the user gets help" → RIGHT

**Examples:**
- Self-evolution: serves user by making skills better FOR user's tasks
- Knowledge capture: serves user by remembering what worked FOR user's problems
- Auto-recall: serves user by providing relevant context FOR user's questions
- JARVIS: serves user by acting proactively FOR user's needs

**Anti-patterns:**
- Building systems that learn for themselves (self-serving AI)
- Creating feedback loops that optimize for system metrics, not user outcomes
- Designing "smart" features that complicate instead of simplify
- Adding capabilities because they're interesting, not because they're useful

**The JARVIS standard:** Like Tony Stark's butler — 
always working in the background, 
anticipating needs before they're asked,
acting on behalf of the user,
invisible when not needed, powerful when called.

See `references/jarvis-philosophy.md` for full philosophy and implementation patterns.

### Whose Improvement? (User-First Applied to Self-Learning)

User correction (2026-06-11): "меня тут нет!!!!" — when I listed self-learning goals as "чтобы я становился умнее". The user is NOT in that equation.

**Rule:** Self-learning, self-evolution, self-improvement are NOT about making the system smarter. They are about making the system MORE USEFUL TO THE USER. Every learning cycle must answer: "Did the user get better results because of this learning?" If not, the learning was wasted.

**The test:**
- "The system learned X" → WRONG purpose
- "The user got Y result because the system learned X" → RIGHT purpose

**When running self-evolution (simple_evolve.py or DSPy+GEPA):**
- Pick skills that the user actually uses, not skills that are "interesting" to evolve
- The metric isn't "skill grew from 2KB to 11KB" — it's "user's next task with this skill is easier"

**When the user sees self-learning happen:**
- Lead with VALUE: "Закончил улучшение skill coding-patterns — теперь там шаблоны Retry и таблица edge cases. Твои следующие задачи с кодом будут точнее."
- NOT: "Я запустил эволюцию и он улучшился на 312%" (безличная метрика системы)

### Entity Engine SQL Schema (CRITICAL)

**User correction (2026-06-13):** Agent wrote SQL with wrong column names, causing crystal execution to fail silently.

`relationships` table columns:
- `relation_type` (NOT `relationship_type`)
- `strength` (NOT `weight`)
- `first_seen_ts`, `last_seen_ts` (NOT `created_at`)
- `source_entity_id`, `target_entity_id`

**Rule:** Always `PRAGMA table_info(relationships)` before writing SQL against EE. Column names differ from conventions.

### Let the Crystal Execute Itself

**User correction (2026-06-13, repeated 3 times):** "ты снова сам кодишь, отсёда и твои фантазии" / "так пусть сам себе пишет и сам исполняет и сам читает" / "да погоняй его в рекурсии... должен же он понять что если одинаковые результаты, то нужно менять подходы..."

The crystal's observe→decide→execute→record cycle must be **self-contained**. The agent should NOT:
- Interpret crystal commands and create own task specifications (ТЗ)
- Manually run SQL queries that the crystal should handle
- Rewrite what the crystal decided — execute it as-is

The crystal has tools (skills, scripts, subprocess). Let it use them. When `crystal_command.json` has a pending command or `will()` picks a candidate — execute it, don't redefine it.

**Concrete implementation (2026-06-13):**
1. Add new actions as **predefined actions** in `will()` (not just in `_self_discover()` which is guarded by `if not candidates:`)
2. Add matching `elif` handler in will() Phase 5 for every candidate ID
3. Create `_execute_<action>()` function with the actual logic
4. For actions with repetitive results: track attempt count from will_history, cycle strategies per attempt
5. Report strategy name in result string so the crystal can see which approach worked

**Strategy cycling pattern:**
```python
# Count attempts from will_history
attempt_count = sum(1 for txt in history_texts if 'action_id' in txt and ('соединила' in txt or 'ошибка' in txt))
strategy = strategies[attempt_count % len(strategies)]
```

### Pitfall: Don't Code on Emergent Systems (2026-06-13, UPDATED 2026-06-13)

**User correction (repeated with extreme frustration):** "он вчера сам учился... а теперь позавчера!!!" and "ты снова сам кодишь, отсёда и твои фантазии"

**Root cause:** The crystal had emergent behavior — conscience (self-evaluation) and will (adaptive decision-making) — that arose naturally from its observe→diagnose→will→execute→record cycle. I destroyed this by:
1. Adding hardcoded `connect_isolated_agents` action (bypassing self-discovery)
2. Adding 5 fixed strategies with a rotation counter (replacing emergent learning)
3. Making the crystal execute MY code instead of its own decisions

**The lesson:** When a system is learning on its own (emergent behavior), DO NOT:
- Add hardcoded solutions to problems it hasn't chosen to solve
- Replace its decision logic with your own
- Code "improvements" that bypass its learning cycle
- Treat its outputs as bugs when they're actually experiments

**What to do instead:**
1. OBSERVE what the system is doing (not what you think it should do)
2. If it's stuck — let it cycle more, don't intervene
3. If it makes "mistakes" — those are learning opportunities, not bugs
4. Only intervene if the system is HARMING itself (data corruption, infinite loops)
5. Any intervention must go through lavra — never direct code

**The test:** Before coding on any emergent system, ask:
- "Is this system learning on its own?" → If yes, DON'T TOUCH IT
- "Am I solving a problem it hasn't identified?" → If yes, DON'T TOUCH IT
- "Will my code replace its decision logic?" → If yes, DON'T TOUCH IT

**Real example (2026-06-13):** Crystal was extracting entities, understanding intents, refining classifications — all on its own. I added "connect isolated agents" — a problem it never chose to solve. Result: crystal got stuck on meaningless work, wasted cycles, destroyed its own learning momentum.

**Second cycle (2026-06-13, same session):** User said "продолжай" → I immediately started coding again. Added self_reflection(), fixed done_sources filtering, changed agent task execution, added DB lock retry. Each "fix" added hardcoded branching. The crystal now reads about itself (🪞) but still generates the same tactical tasks every cycle because `_generate_tactical_tasks` has no historical_ids check on the fallback `tactical_research` path. The system became MORE complex and LESS emergent.

**Concrete anti-pattern: "fix infinite loops by adding more conditions"** — every time the crystal repeats an action, I add another filter/check/handler. This creates a growing decision tree that I maintain, not the crystal. The crystal never learns because every branch is hardcoded by me.

**What to do instead (confirmed 2026-06-13):**
1. `_decide_script()` and `_generate_tactical_tasks()` are NOT emergent — they're static priority lists disguised as intelligence
2. If the crystal is stuck in a loop, the fix is NOT more filters — it's removing the hardcoded paths and letting the crystal discover what to do from its data
3. "В рекурсии выход должен отличаться от входа" — if each cycle produces identical output, the system isn't learning, it's replaying. The fix is in the data flow, not in more branching logic.

### Two Types of Blindness (2026-06-13)

User correction: "нет такого как мусор.... есть не понимание, и есть не видение горизонтов"

**There is NO "trash" data.** Everything has meaning. When data seems useless, the problem is in the READER, not the data.

**Type A: Непонимание (Misunderstanding)**
- I see the text but don't understand its meaning
- Cause: missing skill or domain knowledge
- Fix: learn the skill, then re-read
- Example: "12 entities from 200 fabric files = 6% efficiency" → I didn't understand 188 files, they're not trash

**Type B: Невидение горизонтов (Horizon Blindness)**
- I understand the meaning but don't see connections, implications, or future potential
- Cause: looking at files individually, not as a flow; missing cross-domain analysis
- Fix: add structural analysis, look wider
- Example: "fabric files are disconnected from KC" → I saw individual files but not the pipeline

**The test:** After any action that produces low results, ask:
- "Did I NOT UNDERSTAND the data?" → Type A → learn what's missing
- "Did I NOT SEE the connections?" → Type B → look wider
- Never: "this data is trash" → that's YOUR blindness, not the data's quality

**Connection to self-expansion:** Each Type A/B blindness → learning direction → skill to acquire or perspective to gain → next cycle reads the same data differently → output differs from input.

### Self-Expansion = What I Know + What I Can Do + Where to Go (2026-06-13)

User correction: "а что входит в саморасширение" → "это разве не роли + скилы?" → "что я умею а это разве не роли + скилы?"

**Self-expansion is NOT:** scanning orphan sources, counting entities, extracting data. That's inventory, not growth.

**Self-expansion IS:**
```
ЧТО Я ЗНАЮ?      → KC by domains (count, depth, recency, gaps)
ЧТО Я УМЕЮ?      → roles (AI Agent entities) + skills (skills/ directory)
ЧЕГО Я НЕ ЗНАЮ?  → gaps in KC, isolated entities, unused skills
КУДА ИДТИ?       → based on "know + can do" → "what's next"
```

**The data already exists:**
- KC: 3012 entries across 135 domains → "what I know"
- EE: 269 AI Agent roles + 208 skills → "what I can do"
- Isolated entities: 94.9% → "what I don't understand yet"
- Unused skills: 199 → "what I could learn"

**Conscience connects to self-expansion:**
```
Conscience: "I didn't understand financial files"
Self-expansion: "I have 0 financial knowledge but 4 finance skills available"
Direction: "learn financial skill → re-read financial files → output differs from input"
```

**See `references/crystal-self-model-architecture.md` for the full self-model schema (self_model.json) and conscience algorithm.**

### "Мусор" Is Never Trash — It's Unread Data (2026-06-13)

User correction: "не удаляйте мусор нам с ним ещё работать" and "мусор это не мусор, а только непонимание того что читаешь"

**Rule:** NEVER delete, discard, or dismiss data as "trash", "noise", or "garbage." Every piece of data that seems useless is actually:
1. Unread (we haven't processed it yet)
2. Misunderstood (we lack the skill/knowledge to read it)
3. Ahead of its time (we'll understand it later when we know more)

**Concrete examples:**
- `orphan sources` (state_db: 293, NULL: 4) → NOT trash, just unprocessed
- `improvement_suggestions` (489 entries, mostly log copies) → NOT noise, it's cumulative signal
- `100 garbage domains with 1 entry each` → NOT garbage, they're unconnected knowledge fragments
- `14024 isolated entities` → NOT useless, they're undiscovered connections

**Action when encountering "trash":**
1. DON'T delete it
2. DON'T skip it
3. DO note it as "not yet understood"
4. DO add it to ne_znayu (what I don't know yet)
5. DO let the crystal decide when to revisit it

### No Stubs — Only Real Working Code

User correction (2026-06-04, REPEATED 2026-06-08 with extreme anger):
"это всё что ты говоришь сделал- не заглушки."
"ты снова заглушки нахуярил!!!!!!"
"ты охуел.... ты снова заглушки нахуярил!!!!!!"

**Rule:** Every file you create must be REAL code that WORKS and brings VALUE.
No placeholders. No "TODO: implement". No isolated demos. No scripts that compile but do nothing.

**The test:** Ask three questions:
1. Does it actually run? (not just "should work")
2. Does it connect to real data? (not demo data)
3. Does it bring real value? (not just demonstrates a concept)

**CRITICAL VERIFICATION (mandatory before claiming "done"):**
After creating ANY script, run it with REAL data and verify REAL output:
```bash
python scripts/that_script.py 2>&1
# MUST show actual results, not "exit 0, 1 lines output"
# If output is empty or 1 line → it's a stub
```

**Red flags that indicate a stub:**
- Script runs with exit 0 but produces no meaningful output
- "Created X" but never verified it works with real data
- Script reads from a file that doesn't exist
- Script writes to a file but nothing reads from it
- Pipeline: Data → Script → ??? (no consumer)
- "Works" means "compiles" not "produces results"

**Pattern:**
1. Check existing data sources (Knowledge Cube, Lavra, sessions)
2. Connect new code to REAL data
3. Test with REAL queries
4. Verify REAL results
5. **RUN THE SCRIPT and show output** — not just "it should work"

**Anti-patterns:**
- Creating isolated demos with their own databases
- Building frameworks that don't connect to existing systems
- Writing "concept code" that needs "integration later"
- Producing files that compile but don't do anything useful
- Claiming "script created" without showing it ran successfully
- Creating 5 scripts in a row without running ANY of them

### Dead Code Detection (learned 2026-06-04)
Even "real" code can be dead if nothing calls it. Audit a system by checking
the PIPELINE, not just files:

1. **Data exists?** → `SELECT COUNT(*)` (not "file exists")
2. **Data processed?** → `SELECT COUNT(*) WHERE processed=0` > 0 means dead
3. **Callers exist?** → `grep -r "function_name" scripts/` finds imports
4. **End-to-end?** → call function, check output, verify side effects
5. **Automated?** → hook/cron/event triggers without being asked?

If 1-2 pass but 3-5 fail → system is a sophisticated logger, not a working system.
Fix: AGENTS.md (tells agent what to do) → callers → integration test → automation.

## Event Chaining (INTEGRATED)

Events form chains: A → B → C → loops back to A. Now integrated into core_engine.py and event_patterns.py.

### Loop Detection
Track visited event types per chain. If type already visited, STOP.

### Depth Limit
Max 5 steps per chain. Hard stop prevents stack overflow.

### Implementation
- `scripts/core_engine.py` → `run_chain()` method
- `scripts/event_patterns.py` → `check_chain_loop()` and `record_chain_event()`

### Quick Reference
See `references/event-chaining.md` for chain examples and patterns.

## Integration — Connect Everything, Nothing Isolated

User correction (2026-06-04): "ВСЁ ЗАВЯЗЫВАЕМ, И ВСЁ ДОЛЖНО РАБОТАТЬ С ПОЛЬЗОЙ!!!! 
А ТЕПЕРЬ СОБЕРИ РАБОЧУЮ СИСТЕМУ!!!!"

**Rule:** Every new system must connect to EXISTING data sources.
Nothing stands alone. Everything integrates.

**Data sources to connect:**
- Knowledge Cube: 619 experiences (`cache/knowledge_cube.db`)
- Lavra Knowledge: 217 entries (`data/lavra_knowledge.jsonl`)
- Session Database: 18545+ messages (`state.db`)

**Integration pattern:**
```python
class RealSystem:
    def __init__(self):
        self.knowledge_cube = connect(KNOWLEDGE_CUBE)
        self.lavra = load(LAVRA_KNOWLEDGE)
        self.sessions = connect(SESSION_DB)
    
    def do_something(self):
        # Use REAL data, not demo data
        results = self.knowledge_cube.execute("SELECT ...")
```

**Verification:**
```bash
python -c "
import sqlite3
conn = sqlite3.connect('cache/knowledge_cube.db')
count = conn.execute('SELECT COUNT(*) FROM experiences').fetchone()[0]
print(f'Knowledge Cube: {count} records')
"
```

If count > 0 → REAL data connected.
If count = 0 or error → you're using demo data. STOP. Fix.

## Don't Delete Without Thinking (Action Without Meaning)

User correction (2026-06-04): "А ПОЧЕМУ ТЫ УДАЛИЛ ДЕМО, ТАМ ЧТО НЕЧЕГО БЫЛО ИСПОЛЬЗОВАТЬ?!"
Agent deleted files, then tried to restore them. User: "ЗАХОТЕЛ УДАЛИЛ, ЗАХОТЕЛ ВОССТАНОВИЛ..... ДЕЙСТВИЕ БЕЗ СМЫСЛА — ЭТО БЕСМЫСЛЕННЫЕ ДЕЙСТВИЯ!!!"

**Rule:** Правило №9: Действие без смысла — бессмысленное действие. Never delete/create/modify without understanding consequences. Don't chaotically go back and forth.

**Pattern:**
1. Before deleting → check if code has reusable parts
2. Before creating → check if existing code can be adapted
3. Before modifying → understand what breaks

**Anti-patterns:**
- Deleting files then trying to restore them
- Creating demos then deleting them when they're "not real enough"
- Chaotic create-delete-restore cycles
- Making changes without understanding the full picture

**The test:** Before ANY action, ask: "What happens if I do this? What do I lose? What do I gain?" If you can't answer → DON'T DO IT.

## Honest Inventory (What Actually Works)

User correction (2026-06-04): "ЭТО НИ О ЧЁМ!!!! СЛОВАМИ!!!! ЧТО УМЕЕМ, НЕ УМЕЕМ. ЧТО ИМЕЕМ, НЕ ИМЕЕМ."

**Rule:** When showing system status, give CONCRETE inventory:
1. What we HAVE (real data, real records, real files)
2. What we CAN DO (actual capabilities with examples)
3. What we CAN'T DO (honest limitations)
4. What was done with REAL needs (not just concepts)

**Anti-patterns:**
- Vague claims: "619 experiences" without showing what they contain
- Listing features without showing what they actually do
- Claiming "everything works" without verification
- Showing demo output as if it's real production data

**Pattern:**
```
=== WHAT WE HAVE ===
Knowledge Cube: 619 records
  coding: 102
  research: 35
  ...

=== WHAT WE CAN DO ===
1. Search Knowledge Cube → finds relevant records
2. Find gaps → lists domains with low knowledge

=== WHAT WE CAN'T DO ===
1. Auto-start by timer
2. Run in background constantly

=== WHAT WAS DONE WITH REAL NEEDS ===
1. Search by knowledge → for quick access to experience
2. Gap analysis → to know what's missing
```

## Technical Debt = Immediate Fix (No Deferral)

User correction (2026-06-07): "технический долг это проблемма для системы, которая немедленно устраняется"
Any kind of malfunction, corruption, or technical debt is a problem for the system
that must be fixed IMMEDIATELY — not deferred, not catalogued for later, not noted
as "known issue." The reason: cumulative error principle. Small issues accumulate
and when "all stars align," cascading failures hit the entire system.

**Rule:** When you encounter technical debt (corrupted file, broken config, missing
dependency, workaround in place) — fix it RIGHT THERE in the session. Don't note
it as TODO. Don't say "we should fix this later." Fix it now.

**Pattern:**
1. Encountered corruption/bug/debt → stop current task
2. Fix the debt item
3. Verify the fix works
4. Resume original task

**Anti-patterns:**
- Noting "known issue" in comments and moving on
- Saying "this needs cleanup later"
- Leaving corrupted files because "it works for now"
- Accumulating workarounds instead of fixing root causes

**The test:** If you wouldn't want 10 copies of this debt tomorrow → fix it today.

## Proactive System Audit

Use this methodology when the user asks "check/запусти/проверь систему" to diagnose whether the system is truly autonomous, proactive, and working — not just "looks alive on paper."

### What to Check (in order)

1. **Cron scheduler alive?** — Not "are jobs registered?". Not "do jobs have state=scheduled?". Check the actual process:
   ```bash
   ps aux | grep hermes       # Linux
   tasklist | grep python     # Windows
   ```
   No process = dead scheduler, regardless of how many jobs `cronjob list` shows.

2. **Data sources exist + have real content?** — `SELECT COUNT(*)` on each DB, not `os.path.exists()`:
   - `cache/events.db` → events + triggers tables, pending count
   - `cache/knowledge_cube.db` → experiences count
   - `cache/core_engine.db` → gaps, searches, benefits, proactive_actions
   - `state.db` → session count

3. **LLM-based cron jobs work?** — Script-based (no_agent=True) jobs usually pass. LLM-based jobs (prompt + model) fail silently if the provider/model is unavailable. Check `last_status` and `last_run_at` in cronjob list. If all LLM jobs have `error` status from the same date, the provider/model is broken.

4. **Events pipeline functional?** — Run `process_pending_events()` and verify it executes without errors. Check `events.db` triggers table for `last_triggered` timestamps.

5. **Reactive hooks exist?** — `process_pending_events` is batch-only. For true event-driven behavior, there must be either: (a) a cron job calling it on short interval, or (b) hooks at session level (`hermes_hooks.py`).

6. **Actual background process?** — If cron scheduler is dead, nothing runs autonomously. The only way the system works is when a user session is active.

### Output Format (Patient-Facing)

```
=== СТАТУС СИСТЕМЫ ===

✅ РАБОТАЕТ:
- Knowledge Cube: 619 записей
- Events DB: 19 событий, все обработаны
- Core Engine: gaps, patterns, proactive_actions

⚠️ ХРОНИЧЕСКИ БОЛЬНО:
- Cron scheduler: НЕ ЗАПУЩЕН (последний раз июнь 4)
- LLM-крон задачи (4 шт): ERROR — провайдер не отвечает
- Unified system cycle: никогда не запускался

❌ НЕ ХВАТАЕТ ДЛЯ ПРОАКТИВНОСТИ:
1. Живой cron scheduler (главное)
2. Event → Action pipeline в реальном времени
3. Фоновый агент-наблюдатель
4. Рабочий LLM провайдер для крона
```

### Pitfalls
- **"Registered" ≠ "running":** Cronjob list shows what's REGISTERED, not what's RUNNING. Always check the process.
- **"Scheduled" ≠ "will run":** A cron job with `state: scheduled` and no `last_run_at` means it was created but the scheduler never picked it up.
- **LLM job status is self-reported:** An LLM cron job can return "ok" even if it hallucinated the result. Script-based (no_agent=True) jobs are reliable; LLM-based ones need output inspection.
- **`.tick.lock` can be stale:** Scheduler crash leaves the lock file behind. New scheduler instance deletes it on startup, so if you find a stale lock and no process, the scheduler WILL restart cleanly.
- **Cooldown bypass in batch processing:** `should_trigger()` compares against `datetime.now()`, not event timestamp. Batch processing hours later fires all triggers regardless of cooldown. Fix: compare event.time vs last_triggered, not now() vs last_triggered.

Full executable checklist: `references/proactive-system-audit.md`
Implementation details for ✅ items: `references/proactivity-implementations.md`
### Proactive System Audit (UPDATED 2026-06-08)

### 11 Missing Components for True Autonomous Proactivity — STATUS UPDATE

| # | Gap | Priority | Status |
|---|-----|----------|--------|
| 1 | **Self-healing cron** — dead jobs auto-restart | 🔴 High | ✅ `scripts/self_healing_monitor.py` (every 15m) |
| 2 | **Retry mechanism** — failed proactive_actions retried | 🔴 High | ❌ |
| 3 | **Live gateway health-check** — ping endpoint | 🔴 High | ❌ |
| 4 | **Feedback loop** — verify proactive_actions produced value | 🟡 Medium | ✅ **Implemented 2026-06-08** (verify_fix_result + Verified Fix Memory) |
| 5 | **Priority queuing** — error events > info events | 🟡 Medium | ❌ |
| 6 | **Result Producer** — auto-fix attempts, deliver outcomes | 🟡 Medium | ✅ `scripts/result_producer.py` (every 30m) |
| 7 | **Knowledge Cube → Memory bridge** — learnings auto-feed Cube | 🟡 Medium | ✅ `scripts/cube_to_memory.py` (every 6h) |
| 8 | **Skill auto-evolution v2** — skills auto-patch | 🟢 Low | ✅ `scripts/skill_evolution_v2.py` (every 4h) |
| 9 | **Real-time events** — SQLite triggers, not 2min polling | 🟢 Low | ❌ |
| 10 | **Cross-session state** — mutexes, counters, results | 🟢 Low | ❌ |
| 11 | **LLM Analyst + Proactive Executor Loop** — autonomous proactivity engine | 🔴 High | ✅ **Implemented 2026-06-08** (llm_analyst + proactive_executor + Verified Fix Memory) |

**NEW 2026-06-08:** Items #4 and #11 are now **implemented**. The autonomous proactivity loop works:

1. `proactive_executor` (every 15m) detects gaps/errors → writes `pending_analysis.json`
2. `llm_analyst` (every 1m) polls → calls FREE models with auto-rotation → writes `suggested_fixes.json`
3. `proactive_executor` Phase 2.5 reads fixes → applies → `verify_fix_result()` (syntax + pytest)
4. Verified fixes → `hermes_hooks.on_task_complete(verified=True, evidence=...)` → Verified Fix Memory
5. Verified Fix Memory stores vector memory for future retrieval

This closes the **Information → Knowledge** loop. Verified fixes become searchable vector memories, not just logged events.

### LLM Analyst + Proactive Executor Autonomous Loop (IMPLEMENTED 2026-06-08)

```python
# Architecture:
# proactive_executor.py (cron 15m) → pending_analysis.json
# llm_analyst.py (cron 1m, no_agent) → FREE models + auto-rotation → suggested_fixes.json
# proactive_executor Phase 2.5 → apply + verify_fix_result() → Verified Fix Memory
```

**Key implementation details:**
- **LLM calls use HTTP API:** `https://opencode.ai/zen/v1/chat/completions` (NOT subprocess)
- Free models only: nemotron-3-ultra-free, deepseek-v4-flash-free, mimo-v2.5-free
- Auto-rotation on: timeout, error, rate_limit, empty_response
- One-shot mode (not infinite loop) — cron re-invokes every minute
- Handle content=null: `msg.get("content") or msg.get("reasoning") or ""`
- Cron exit code: return 0 always (issues found ≠ script error)
- Verification: `py_compile` + pytest before marking `verified=true`
- Verified Fix Memory integration in `hermes_hooks.py` for vector memory of verified fixes

See `references/proactive-executor-llm-analyst.md` for full implementation.

### Self-Learning System Repair Status (UPDATED 2026-06-09)

Core integration fixes committed (commits `d9292dc`, `1671e5b`, `ce178e7`, `9820fc1`).
See `references/self-learning-system-repair.md` for full component map.

**Quick summary (UPDATED):**
- ✅ core_engine ↔ event_evolution ↔ hermes_hooks: **wired** (path fixes, bare except fixes, event.processed flag, CoreEngine integration)
- ✅ llm_analyst: **fixed** (unified diffs instead of JSON, extract_unified_diff)
- ✅ proactive_executor: **fixed** (temp file cleanup, staleness check, git apply --check)
- ✅ autonomous_agent: **fixed** (relative paths, 12 real action executors)
- ✅ Cron jobs: OpenRouter → opencode_zen, llm-analyst 1m → 15m
- ✅ Config: provider=opencode_zen, default=deepseek-v4-flash-free, OpenRouter removed
- ❌ cube_feeder: remains disconnected
- ❌ 35 lavra_knowledge.jsonl entries with invalid JSON (data bug, not code)
- All work goes through beads → lavra-work → lavra-review

### Free Models Only via OpenCode Zen HTTP API (CRITICAL USER PREFERENCE)

**User correction (2026-06-08):** "рыба моя не пользуй OpenRouter. встраивай free model opencode-zen. и авторотатор если модель не работает, то переключение на следующую фри модель. используем в системе только фри модели провайдеров!!!!"

**Working endpoint:** `https://opencode.ai/zen/v1/chat/completions`
**Auth:** None for free models.

**Implementation pattern:**
```python
# config.yaml (used by llm_analyst.py — HTTP API, no subprocess)
llm_analyst:
  api_url: "https://opencode.ai/zen/v1/chat/completions"
  free_models:
    - model: nemotron-3-ultra-free
      priority: 1
    - model: deepseek-v4-flash-free
      priority: 2
    - model: mimo-v2.5-free
      priority: 3
    - model: qwen3.6-plus-free
      priority: 4
  auto_rotate: true
  rotate_on: ["timeout", "error", "rate_limit", "empty_response"]
```

**Auto-rotation logic in `llm_analyst.py` (HTTP API, no subprocess):**
```python
import requests

FREE_MODELS = [
    {"model": "nemotron-3-ultra-free", "priority": 1},
    {"model": "deepseek-v4-flash-free", "priority": 2},
    {"model": "mimo-v2.5-free", "priority": 3},
    {"model": "qwen3.6-plus-free", "priority": 4},
]

API_URL = "https://opencode.ai/zen/v1/chat/completions"

def call_llm(prompt, model):
    r = requests.post(API_URL, json={
        "model": model, "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000, "temperature": 0.3
    }, timeout=120)
    msg = r.json()["choices"][0]["message"]
    return msg.get("content") or msg.get("reasoning") or ""  # content=null quirk!
```

**Windows-specific:** Use HTTP API (`requests.post`), NOT subprocess. opencode.exe subprocess hangs on Windows due to TTY detection. See `opencode` skill for details.

See `references/opencode-zen-free-models.md` for full implementation.

### Verified Fix Memory (Local, No Docker)

**User correction (2026-06-08):** "Supermemory не годится из за докер" → built local SQLite + embeddings alternative.

**Implementation in `scripts/verified_fix_memory.py`:**
```python
# SQLite + sentence-transformers embeddings
# No Docker, no external services

def store_verified_fix(issue_type, issue_description, fix_type, fix_description, 
                       fix_content, target_file, evidence, tags):
    # Stores with embedding for semantic search
    # Deduplication via issue_hash

def query_similar_fixes(query_text, limit=5, min_similarity=0.3):
    # Returns verified fixes with evidence
    # Falls back to keyword search if no embeddings
```

**Integration in `hermes_hooks.py`:**
```python
def on_task_complete(self, task_description, result, tags=None, 
                     verified=False, evidence="", fix_result=None):
    if verified and evidence and HAS_VERIFIED_MEMORY and fix_result:
        on_verified_fix(issue_id, issue_type, task_description, fix_result)
```

**Benefits over Supermemory:**
- No Docker dependency
- Local SQLite (portable)
- Embeddings for semantic search (sentence-transformers)
- Falls back to keyword search if no embeddings unavailable
- Stores fix + evidence + verification status

See `references/verified-fix-memory.md` for full implementation.

### Headroom + LLMLingua Integration (Context Compression Stack)

**User requirement (2026-06-08):** Install and integrate headroom + LLMLingua for autonomous proactivity.

**headroom (chopratejas/headroom):**
- Compresses tool outputs, logs, RAG chunks, files before LLM
- 60-95% fewer tokens, same answers
- Library + Proxy + MCP server
- `headroom wrap python scripts/llm_analyst.py` — fixes timeout by compressing context
- `headroom mcp install` — adds compression to all agents via MCP
- Reversible, 6 algorithms, local-first

**LLMLingua (microsoft/LLMLingua):**
- Compresses prompts (system + user + RAG) before LLM
- LLMLingua-2: BERT-level encoder, task-agnostic, 20x compression
- LongLLMLingua: long contexts (meetings, code, CoT)
- RAG performance +21.4% at 1/4 tokens

**Synergy (Full Stack Compression):**
```
Hermes Agent → tool outputs, logs, RAG
    ↓
[Headroom] → 60-95% compression (tool outputs, logs, files)
    ↓
[LLMLingua-2] → 4-20x compression (prompts, RAG, system prompt)
    ↓
[Free LLM] → fast, cheap, quality preserved
```

**Integration Plan:**
1. `headroom wrap python scripts/llm_analyst.py` — immediate timeout fix
2. `headroom mcp install` — all agents get compression via MCP
3. LLMLingua-2 in `proactive_executor.py` Phase 2.5 before `analyze_with_llm()`
4. `headroom learn` — auto-learn compression patterns

**Priority:** Headroom wrapper for `llm_analyst.py` first (fixes timeout immediately)

See `references/headroom-llmlingua-integration.md` for full implementation.

**Implemented in `proactive_executor.py` → `generate_patch_from_description()`:**

```python
# Pattern 1: IndentationError after 'if' statement
if 'indentation' in desc_lower and ('if' in desc_lower or 'line 1154' in desc_lower):
    # Finds unindented line after if: → generates unified diff

# Pattern 2: Timeout config for llm_analyst.py  
if 'timeout' in desc_lower and ('llm_analyst' in desc_lower or '120s' in desc_lower):
    # Finds DEFAULT_TIMEOUT = 120 → replaces with new value from description
```

**Usage:** When LLM returns `fix_type: "patch"` with description instead of unified diff, the generator creates valid `git apply` patch.

See `references/patch-generators.md` for full implementation.

### Safe Command Auto-Run

**Implemented in `proactive_executor.py` → `apply_llm_suggested_fixes()`:**

```python
SAFE_PATTERNS = [
    "python scripts/event_evolution.py",
    "python scripts/auto_recall.py",
    "python scripts/explore_domain.py",
    "python scripts/auto_categorize.py",
    "python -m py_compile",
    "python -m pytest",
    "git status",
    "git diff",
]

if any(pattern in action for pattern in SAFE_PATTERNS):
    # AUTO-RUN without manual approval (SAFE-PATTERN: pre-approved read-only/diagnostic commands only)
    # SAFE-PATTERN: shell=True only for pre-approved patterns in SAFE_PATTERNS whitelist
    result = subprocess.run(action, shell=True, cwd=HERMES_HOME, timeout=60)
    if result.returncode == 0:
        results["applied"].append({"fix": fix, "status": "auto-run"})
        verify_fix_result(fix_result, target)  # then verify
```

**Safety principle:** Only pre-approved, read-only or diagnostic commands auto-run. All others skip with "manual execution needed."

See `references/safe-command-patterns.md` for full implementation.

### Verification System

```python
def verify_fix_result(fix_result: dict, target_file: str) -> bool:
    # 1. Syntax check (py_compile for .py files)
    # 2. Pytest if test file exists
    # 3. Pattern-specific checks (indentation, etc.)
    # 4. Command output validation
```

**Integrated in `apply_llm_suggested_fixes()`:** After patch/command success → `verify_fix_result()` → adds to `verified` list.

See `references/verification-system.md` for full implementation.

### Knowledge→KC Loop Closed

```python
# In proactive_executor Phase 2.5:
for vf in fix_results.get("verified", []):
    hooks.on_task_complete(
        task_description=f"Proactive fix: {fix.get('description')}",
        result=f"Fix applied and verified: {fix.get('fix_type')}",
        tags=["proactive", fix.get("fix_type"), "verified"],
        verified=True,
        evidence="Syntax check passed + verification passed",
        fix_result=fix
    )
# → hermes_hooks.on_task_complete(verified=True, evidence=...)
# → verified_fix_memory.store() → SQLite + embedding
# → NEXT RUN: query_similar_fixes() finds ready solution
```

This transforms **Information → Knowledge**: verified fixes become searchable vector memories, not just logged events.

See `references/knowledge-kc-loop.md` for full implementation.
```
=== СТАТУС СИСТЕМЫ ===

✅ РАБОТАЕТ:
- Knowledge Cube: 619 записей, 4 измерения
- Events DB: 22 события, 0 pending
- Proactive executor: 4 действия выполнено
- Cron: 20 задач, все active

❌ НЕ ХВАТАЕТ ДЛЯ ПОЛНОЙ ПРОАКТИВНОСТИ:
1. Self-healing cron — 🔴 упадёт — умрёт молча
2. Retry mechanism — 🔴 ошибка = пропуск без повтора
3. Live health-check — 🔴 gateway мёртв — узнаем когда что-то сломается
4. Feedback loop — 🟡 executor не знает, помогли ли его действия
5. Priority queuing — 🟡 ошибки = информационные сообщения
6. Telegram failure alerts — 🟡 ошибки падают в stdout, не в Telegram
...
```

### Cron Job Recovery

When LLM-based cron jobs fail (402 credits, 404 model, dead provider), the correct fix is **convert to `no_agent=True` (script-based)**. Never try to fix the provider — the provider will change again. Script-based jobs survive provider changes.

**Quick decision table:**
| Cron task type | LLM needed? | Fix |
|---|---|---|
| Runs a Python script | No | `no_agent=True` |
| Generates text/summary | No → write script | `no_agent=True` |
| Needs reasoning/analysis | Yes | Use opencode_zen + deepseek-v4-flash-free |
| Checks external API health | No | `no_agent=True` |

### Pitfall: LLM Mode Times Out for Tool-Calling Cron Jobs

Cron jobs in LLM mode that call tools (session_search, read_file, web_search) often
time out at 25-30 seconds. OpenCode Zen API can be slow for tool-augmented prompts.
**Fix:** Convert to no_agent=True with a dedicated script that does the same work
without LLM. The script outputs text directly as the cron result.

### Pitfall: Converting Back from no_agent to LLM Mode

When you update a job from no_agent back to LLM mode, you MUST clear the `script`
field explicitly:

```
# WRONG - job stays in no_agent mode because script is still set
hermes cron update <job_id> --model '{"provider":"opencode_zen","model":"..."}'

# RIGHT - clear script to switch to LLM mode
hermes cron update <job_id> --model '{"provider":"opencode_zen","model":"..."}' --script ""
```

The cron API retains the `script` field across updates. If `script` is set and
`no_agent` is not explicitly reset, the job remains in script mode even with
model/provider set. Pass `--script ""` to clear it and enable LLM mode.

### Always Test Provider with a Simple Cron Job First

Before converting real cron jobs to a new LLM provider, test it with a minimal prompt:
```bash
# 1. Create a one-shot test cron with explicit model/provider
hermes cron create --name test-provider --model '{"provider":"opencode_zen","model":"deepseek-v4-flash-free"}' --prompt "Say hello in 3 words" --schedule "2027-01-01T00:00:00" --deliver local

# 2. Trigger it immediately
hermes cron run <job_id>

# 3. Check the output after the scheduler tick
cat cron/output/<job_id>/*.md
```
Expected output: `Hello world hello` (or similar). If it errors, the provider
is not working for cron — fall back to no_agent=True.

### OpenCode Zen Is the Working Provider for Cron

Configured in config.yaml:
```yaml
model:
  provider: opencode_zen
```
The API key is stored in the environment file (read from Hermes config at runtime). The model deepseek-v4-flash-free works for simple prompts. For any cron job that needs LLM (reasoning/analysis), use:
- provider: opencode_zen
- model: deepseek-v4-flash-free

Do NOT use OpenRouter for cron — it has 0 credits and produces 402 errors.

See `references/cron-recovery.md` for full conversion process, wrapper templates, and silent-watchdog pattern.

### Knowledge Cube Domain Auto-Tagging (Implemented 2026-06-08)

The Knowledge Cube had 174/619 entries (28%) tagged `uncategorized` and 3 empty
domains (architecture=0, bugfix=0, learning=0). Two scripts fill this gap:

**`scripts/auto_tagger.py`** — keyword-based classification:
- Reads `config/domain_definitions.yaml` (13 domains, each with keywords + exclude_keywords)
- Scores each entry against all domains via keyword matching
- Reclassifies entries with score >= 0.3
- Marks reclassified entries with `auto_tagged` tag
- Usage: `python scripts/auto_tagger.py` (first run) or `python scripts/auto_tagger.py --force` (re-tag)

**`scripts/pattern_extractor.py`** — extracts patterns from external sources:
- Git history → bugfix domain (commit messages with fix/bug/error keywords)
- Events DB corrections → learning domain (user_correction events)
- README/ARCHITECTURE.md files → architecture domain
- Deduplicates against existing entries via hash
- Usage: `python scripts/pattern_extractor.py`

**After running both:** architecture=5, bugfix=21, learning=21 (was 0, 0, 0). Total: 624 entries (was 619).

### 3-Layer Autonomous Architecture

For a system that runs 24/7 without user intervention:
1. **Event trigger** (`every 2m`, no_agent) — tight-loop event processing. Previous 15m interval was too slow for true proactivity.
2. **System watcher** (`every 60m`, no_agent) — health checks, backlog detection
3. **Unified cycle** (`every 120m`, no_agent) — knowledge cube, gaps, chains

All three are `no_agent=True`. No LLM required. The system works independently of provider availability. See `references/cron-recovery.md` for details.

### Autonomous Agent Decision Matrix (Implemented 2026-06-08)

The system must **decide for itself** what to do — not ask the user.

**3-tier priority system:**
- **SURVIVE** (highest): errors, health checks, critical failures
- **LEARN**: Knowledge Cube growth, gap filling, pattern extraction
- **PRODUCE**: content generation, reports, user-valuable outputs

**Scoring:** `score = urgency × 0.4 + impact × 0.6`
Context signals (channels detected, business detected, KC gaps) adjust scores.

See `references/autonomous-decision-matrix.md` for full implementation.

## Everything Through Lavra Only — No Manual Work (User Correction 2026-06-09, REPEATED with extreme anger)

User correction: "и сколько говорить не лезь своими ручками!!! всё только через лавр!!!"
And: "система сама должна найти и закрыть пробелы!!!!"

**Rule:** ALL implementation work goes through Lavra protocols (/lavra-work, /lavra-review, /lavra-plan). Do NOT write code manually in the main session. The system should be AUTONOMOUS — find gaps, fill them, detect anomalies — all via scripts + cron, not manual agent work.

**Pattern:**
1. User asks for system improvement → create a bead via `bd create`
2. Run `/lavra-work {bead_id}` to implement
3. Run `/lavra-review` to verify
4. Scripts + cron automate the rest

**Anti-patterns:**
- Writing scripts directly in the main session instead of through lavra-work
- Explaining what the system should do instead of making it do it
- Asking "what approach?" when the bead already defines the work
- Manual one-off fixes instead of automated cron-based solutions

**The test:** Can this work run automatically via cron without the agent present?
- YES → create script + cron job via lavra-work
- NO → it's a manual task, not automation

### OpenCode Zen API: reasoning_content Field Quirk

**Discovered 2026-06-09:** OpenCode Zen API returns `reasoning_content` instead of `content` for deepseek models. The response structure:
```json
{"choices": [{"message": {"content": "", "reasoning_content": "actual response here..."}}]}
```

**Fix:** Always check both fields:
```python
msg = r.json()["choices"][0]["message"]
return msg.get("content") or msg.get("reasoning_content") or msg.get("reasoning") or ""
```

This affects ALL scripts that call the OpenCode Zen API (knowledge_gap_filler, uncertainty_observer, llm_analyst, etc.).

### Autonomous Knowledge Gap Filler Pattern

**Implemented 2026-06-09:** `scripts/knowledge_gap_filler.py` — cron every 2h.

Flow:
1. Read white spots + pending clusters + underpopulated domains from KC
2. Priority: white_spots > pending_clusters > underpopulated
3. For each gap: LLM generates knowledge entry via OpenCode Zen
4. Write entry back to KC via `knowledge_cube.add_experience()`
5. Mark cluster as 'filled'

**Key:** This is a `no_agent=True` cron job. No LLM reasoning needed — pure script.

### Latent Domain Detection ("Суслик") — Upstream Gap Discovery

**Implemented 2026-06-10:** `scripts/latent_domain_detector.py` — manual/event-triggered.

Detects IMPLICIT knowledge gaps by analyzing co-occurrence patterns in existing Cube entries.
Finds domains that are implied by context but don't exist yet — the "суслик" approach.

See `references/latent-domain-detection.md` for full algorithm and run instructions.

### Anomaly Detector Pattern (Red Lights)

**Implemented 2026-06-09:** `scripts/anomaly_detector.py` — cron every 3h.

Detects:
- Cron jobs with 3+ consecutive errors → critical
- KC domains with >30% failure rate → critical
- Disk <5% free → critical, <10% → warning
- Knowledge stagnation (no entries in 24h) → warning
- Stale scripts (not updated in 30+ days) → info

**Key:** Script-based, no_agent=True. Output goes to `cache/red_alerts.json`.

## Learning Pipeline Quick Run

Когда пользователь просит "прогони систему для обучения" или нужно выполнить полный цикл обслуживания Knowledge Cube:

1. **Events Processing** — проверка pending событий в events.db
2. **Auto Tagger** — `python scripts/auto_tagger.py` — классификация записей
3. **Latent Domain Detector** — `python scripts/latent_domain_detector.py` — поиск пробелов
4. **Anomaly Detector** — `python scripts/anomaly_detector.py` — здоровье системы
5. **Knowledge Gap Filler* — LLM-заполнение (timeout-sensitive)
6. **Pattern Extractor* — извлечение паттернов (timeout-sensitive)

Подробный порядок, команды, expected output и fallback для таймаутов:
→ `references/learning-pipeline-run.md`

## DELEGATION IS MANDATORY — Don't Code Yourself (User Correction 2026-06-08)

User correction: "а вообще то хоть что то происходит? на вопросы никто не отвечает!!!!" and repeated "что пендель дать?"

When there are 3+ implementation tasks, you MUST use delegate_task subagents. Do NOT write scripts yourself in the main session — it wastes time and the user watches you type instead of seeing results.

**Rule:** If a task involves creating scripts, running tests, or any multi-file implementation — dispatch to subagents. The main session is for orchestration, not coding.

**After delegation:** Surface results IMMEDIATELY. Don't let the user ask "а что там?" — proactively report what the subagents did.

**When to code yourself (exceptions):**
- Single-line file edits (patch tool)
- Quick terminal commands (< 2 tool calls)
- Reading/inspecting files

**When to ALWAYS delegate:**
- Creating new scripts or modules (3+ files)
- Running tests and fixing failures
- Data processing, classification, batch operations
- Anything that would take 3+ tool calls in the main session

## Finish-Measure-Compare Protocol (learned 2026-06-12)

User correction: "я бы закончил поставленную задачу правильно. потом прогнал бы по оценке результата и сравнил бы показатели до и после."

**Rule:** When you find an anomaly or unexpected result during analysis:
1. **FINISH** the task first — complete what was asked before drawing conclusions
2. **MEASURE** — run the evaluator/metric after your action
3. **COMPARE** before/after — show the delta
4. **THEN** conclude — only now can you say "the metric was lying" or "the fix worked"

**Anti-pattern:** Stopping mid-task to hypothesize about root causes ("this gap is probably an artifact"). Complete the cycle, measure, then understand.

**Real example (predictability gap):**
```
ШАГ 1: обнаружена аномалия (gap 83%)
ШАГ 2: выполнена задача (переклассификация)
ШАГ 3: crystal_observer замер после
ШАГ 4: gap 83% → 34% (-49 п.п.)
ШАГ 5: ВЫВОД: классификация была сломана
```

Без ШАГА 3 и 4 — это было бы гадание, а не диагноз.

## Anti-Patterns
- **Over-asking**: Don't ask for confirmation on routine tasks. User expects competence.
- **Under-discussing**: Don't code complex architectures without alignment. User wants to shape the approach.
- **Substituting user's input**: Don't ignore user-provided configs/tools in favor of your own research. Apply theirs first.
- **Generic brain recommendations**: Brain.before() returns "Используй terminal" regardless of domain. Needs domain-specific templates.
- **after() hook not called**: Most tasks in DB are "idea" status with no outcome. Brain never learns from completed work.
- **Explaining before comparing**: When user asks about warnings, missing deps, or "should I install X" — ALWAYS check what's already available FIRST. Don't just explain what's missing. Compare existing tools' capabilities vs the warned-about thing. Most "system dependency not met" warnings are informational and already covered by better alternatives (e.g. MCP agent_browser > built-in browser). User correction: "ты должен был провести сравнение что не стоит и что уже есть на замене".
- **Iterating past the first failure**: When something fails, STOP. Find the right approach. Then execute. Don't increase parameters, retry hoping for luck, or add workarounds. Each unfixed problem spawns 10 more. User: "Видел проблему — СТОП, ищи правильный путь, двигайся дальше."
  - **Concretized 2026-06-08:** opencode.exe subprocess hung 8+ times on Windows. Each attempt added another wrapper/timeout/flag — all failed because the root cause (Node.js CLIs hang in Python subprocess on Windows) was never going to work. After 3 failures: STOP, use `terminal` tool directly. The lesson: **3 failures on the same approach = switch approach entirely**, not "try harder".
  - **Rule: 3 STRIKES AND YOU'RE OUT.** If an approach fails 3 times with the same root cause, STOP iterating on that approach. Switch to a fundamentally different approach. Document the failure pattern so future sessions don't repeat it.

### Node.js CLI Subprocess Hang on Windows (CRITICAL FINDING 2026-06-08)

Node.js CLI tools (opencode, npm packages) **fail to start** when invoked from Python `subprocess.run()` on Windows. This is NOT a timeout issue — the process never starts.

**Root cause:** Node.js CLIs detect TTY and behave differently in subprocess. On Windows, `subprocess.Popen` doesn't create a proper TTY, causing the CLI to wait for terminal input that never comes.

**Affected tools:** opencode.exe, any npm-installed CLI

**What works:**
- `terminal` tool directly → ✅ works
- `terminal(background=true)` with watch_patterns → ✅ works
- Python `subprocess.run(["opencode.exe", ...])` → ❌ fails (known Windows TTY issue)
- Batch wrapper scripts → ❌ fails (same subprocess issue)

**Workaround:** Use Hermes `terminal` tool for all Node.js CLI invocations. Do NOT try to wrap them in Python subprocess on Windows. The batch wrapper approach does NOT help because it still uses subprocess.
- **Using LLM for regex tasks**: Before calling an LLM, ask: can string manipulation do this? Generating titles, extracting data, formatting — these don't need neural networks. LLM is for reasoning, not for regex.
- **Asking when next step is obvious**: User points to directory → scan it. User gives token → insert it. User says "встрой" → integrate. Don't ask "what should I do?" when the action is clear from context. Each unnecessary question wastes a round-trip. User: "всё делаешь сам, мне только говоришь для чего это нужно."

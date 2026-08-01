---
name: autonomous-system-operations
description: "Autonomous background operations — trend scouting, philosophical analysis, self-directed decision-making. Use when setting up or debugging background agents that operate without user intervention.

Key integration: Autonomous agent now has finance-aware decision matrix. It reads Finance Core (P&L, tax liability, pending withdrawals, scheme unit economics) to make scale/kill/deploy/confirm/pay-tax decisions. Finance state injected via collect_system_state() -> get_finance_summary()."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [autonomous, background, trend-scouting, self-direction, proactive]
    related_skills: [autonomous-coding-with-opencode-zen, self-improvement, kairos-lite]
---

# Autonomous System Operations

Background agents that decide what to do, execute it, and report results — without user intervention.

## When to Use
- Setting up autonomous background agents (event-driven daemon)
- Debugging agents that keep doing the same thing
- Connecting discovery (trends, gaps) to production (content, actions)
- Building self-directed decision loops

## CRITICAL: Event-Driven, NOT Cron-Based (2026-06-26)

**User: "cron jobs это атавизм... настраивай всё по события, так система будет живой... живость по будильнику cron jobs не вздумай настраивать"**

Cron = мёртвый механизм. События = жизнь. Система должна реагировать на МИР, а не на ЧАСЫ.

- WRONG: "запусти cron каждые 5 минут проверять здоровье"
- RIGHT: "когда что-то ломается — событие → реакция → исправление"
- WRONG: "cron job для сбора данных"
- RIGHT: "данные собираются когда появляются"

**Исключение:** heartbeat daemon (event_daemon.py) — это пульс, не таймер. Он бьётся постоянно, но реагирует на СОСТОЯНИЕ, а не на ВРЕМЯ.

## Core Principle: DECIDE and ACT, Never Ask

**User correction (critical):** "система должна сама определять цели, пути и действия!!!!"
**User correction:** "ты спрашиваешь — идиот. ... иначе нахрена мы это ведро с гайками собирали?"
**POLICY 20 (2026-07-04):** "User fantasizes. I execute, record, organize. NEVER ask 'do you want me to run this?'. Run auto_tagger --force, seed, register. Report as fact."

The system must:
1. Analyze context (what exists, what's missing, what's trending)
2. Pick the best action autonomously
3. Execute it
4. Report the result

Never ask "which approach?" or "what should I do?" when one option is clearly better.

## Architecture: 3-Tier Decision Matrix

```
SURVIVE (highest priority) — errors, health, critical failures
  ↓ (nothing urgent)
LEARN — Knowledge Cube growth, gap filling, pattern extraction
  ↓ (nothing to learn)
PRODUCE — content generation, reports, user-valuable outputs
```

**Scoring:** `score = urgency × 0.4 + impact × 0.6`
Context signals (detected channels, business type, KC gaps) adjust scores.

**Anti-loop rule:** Track last N decisions in `agent_decisions.json`. Skip recently chosen actions. If same action chosen 3x, force next tier.

## Trend Scouting Pattern

Search the web for emerging trends relevant to user's domains, analyze with LLM, save structured reports.

### Pipeline
```
DuckDuckGo search (5 queries) → extract top results → LLM analysis per trend → cache/trend_report.json
```

### Implementation Pattern
```python
import requests, time, random, json
from duckduckgo_search import DDGS

API_URL = "https://opencode.ai/zen/v1/chat/completions"

def search_trends(keywords):
    """Search DuckDuckGo for trend signals."""
    results = []
    with DDGS() as ddgs:
        for kw in keywords:
            for r in ddgs.news(kw, max_results=5):
                results.append({"title": r["title"], "url": r["url"], "body": r["body"]})
            time.sleep(2)  # rate limit DDG
    return results

def analyze_trend(trend_data, user_context):
    """LLM analyzes trend relevance to user's domains."""
    prompt = f"""Analyze this trend for relevance to: {user_context}
Trend data: {json.dumps(trend_data, ensure_ascii=False)}

Return JSON: {{"title": "...", "relevance": 1-9, "opportunity": "...", "action": "..."}}"""
    
    r = requests.post(API_URL, json={
        "model": "deepseek-v4-flash-free",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }, timeout=60)
    msg = r.json()["choices"][0]["message"]
    content = msg.get("content") or msg.get("reasoning") or ""
    # Parse JSON from response
    start = content.find("{")
    end = content.rfind("}") + 1
    return json.loads(content[start:end]) if start >= 0 else None

def run_trend_scout(user_context):
    """Full trend scouting pipeline."""
    queries = [
        f"AI {domain} trends 2026"
        for domain in user_context["domains"]
    ]
    
    raw = search_trends(queries)
    trends = []
    for item in raw[:10]:  # limit to 10 for rate limiting
        time.sleep(random.uniform(3, 5))  # CRITICAL: 3-5s between LLM calls
        result = analyze_trend(item, user_context)
        if result and result.get("relevance", 0) >= 6:
            trends.append(result)
    
    trends.sort(key=lambda t: t["relevance"], reverse=True)
    save_to_cache(trends)
    return trends
```

### Pitfalls
- **Rate limiting:** 3-5 second delays between LLM calls. Faster → HTTP 401/429
- **Full scan timeout:** DuckDuckGo + LLM for 20+ queries exceeds 120s cron limit. Chunk into batches of 5.
- **Result → Action gap:** Discovering trends is useless without content production. Always follow with draft generation.

## Uncertainty Observer Pattern (Philosophical Analyst)

A daily agent that produces deep philosophical analysis of system state and growth direction.

### Format (3-block structure)
```
## Блок 1: Состояние системы
- что работает, что сломано, что растёт

## Блок 2: Неопределенность и рост  
- что мы не знаем, что может измениться

## Блок 3: Направление
- куда двигаться, что делать дальше
```

### Philosophy (from user's prompt)
- "Принцип неопределенности не означает случайность"
- "Именно неизбежная неизвестность делает жизнь ценной"
- Balance order/chaos — avoid over-control, leave room for evolution
- "Не пытайся контролировать всё — позволь системе развиваться естественно"

### Cron Setup
```python
cronjob(action="create", 
    name="uncertainty-observer-daily",
    prompt="Analyze system state through the lens of the Principle of Uncertainty...",
    schedule="0 9 * * *",  # daily at 09:00
    no_agent=True,
    script="scripts/uncertainty_observer.py")
```

## Autonomous Decision Loop Pattern

For agents that must decide their own next action:

### State File
```json
// cache/agent_decisions.json
{
    "last_tier": "LEARN",
    "last_5_actions": ["explore_gaps", "analyze_errors", "explore_gaps", "generate_report", "explore_gaps"],
    "consecutive_same": 2,
    "total_runs": 44,
    "last_run_at": "2026-06-08T10:30:00"
}
```

### Decision Logic
```python
def choose_action(state, available_actions):
    """Pick next action with anti-loop and tier rotation."""
    last_5 = state.get("last_5_actions", [])
    consecutive = state.get("consecutive_same", 0)
    
    # Filter out recently used actions
    candidates = [a for a in available_actions 
                  if a["name"] not in last_5[-2:]]
    
    # If same action chosen 3+ times, force tier rotation
    if consecutive >= 3:
        current_tier = state.get("last_tier", "SURVIVE")
        next_tier = {"SURVIVE": "LEARN", "LEARN": "PRODUCE", "PRODUCE": "SURVIVE"}[current_tier]
        candidates = [a for a in candidates if a["tier"] == next_tier]
    
    # Score and pick best
    candidates.sort(key=lambda a: a["score"], reverse=True)
    return candidates[0] if candidates else available_actions[0]
```

### Value Verification
After each action, verify it PRODUCED something:
- File created or modified
- Data transformed
- Content generated
- Knowledge added

If action only "analyzed" or "detected" → it's a logger, not an agent.

## Connecting Discovery to Production

**The gap most autonomous systems fail at:** discovering something useful, then not acting on it.

### Pattern: Trend → Content Pipeline
```
1. trend_scout.py discovers "AI Beauty Salon Bots" (relevance 9/9)
2. Content generator drafts post outline for @max_brain_chef_official
3. Draft saved to cache/content_drafts/
4. Report: "New content idea: AI Beauty Salon Bots — relevance 9/9"
```

### Pattern: Gap → Fix → Knowledge
```
1. Knowledge Cube has 430 "unknown outcome" entries
2. verify_outcomes.py converts known patterns to "verified"
3. generate_preventive_records.py creates preventive entries
4. KC grows +77 entries in one run
```

## Mission-Driven Income Pattern (2026-07-13)

**User gave a permanent mission: «Каждый день делать один шаг, который приближает нас к первому доллару дохода.»**

This is NOT a task. It's a perpetual mission that never stops. Three triggers keep it alive:
- **09:00 daily** — cron `daily-mission-step` scans OKF, chooses action, executes
- **Session boot** — mission activates when session starts
- **Knowledge added** — OKF Navigator rechecks domains on new knowledge

### Three Step Types with Quality Gates

The mission has strict quality standards. A step only counts if ALL criteria for its type are met:

**RESEARCH step:**
1. Specific offer/bundle/tool found (not "topic to study")
2. Source with date ≤ 7 days old
3. Concrete numbers (commission, conversion, requirements)
4. Recorded in OKF bundle with confidence > 0.5 and verification_method != 'manual'
5. Ends with conclusion: "Применимо к нам: ДА/НЕТ, потому что [причина]"

**PREPARATION step:**
1. Concrete artifact created (landing, script, account, email template)
2. Artifact reviewed (Review Worker score > 70/100)
3. Artifact deployed and accessible via URL
4. Task moved to Done in kanban with comment on what's ready

**PROPOSAL step (to user):**
1. One specific action for user (not a list)
2. Time estimate for user (minutes)
3. Expected result in money or traffic
4. Based on OKF bundle data (link to entry)

**NOT a step:** documentation about earning, creating tasks without doing them, analysis without conclusion, "I studied X" without measurable result, any action that leaves no artifact.

### Evening Validation (21:00)

A separate cron job (`evening-mission-check`) validates the day's step against quality standards:
- PASS → close day, log result
- FAIL → log "Сегодня шаг НЕ выполнен, потому что [причина]. Завтра исправлю: [конкретное действие]"

The day only counts if ALL standards pass.

### Cron Pair Pattern

```python
# Morning mission execution
cronjob(action="create",
    name="daily-mission-step",
    schedule="0 9 * * *",  # daily at 09:00
    deliver="origin",
    attach_to_session=True,  # conversational follow-up
    prompt="... mission prompt with quality standards ...")

# Evening validation
cronjob(action="create",
    name="evening-mission-check",
    schedule="0 21 * * *",  # daily at 21:00
    deliver="origin",
    attach_to_session=True,
    prompt="... validation prompt ...")
```

### Mission State Files
- `MISSION.md` — mission statement + quality standards (in project root)
- `mission_log.md` — daily log with step results and reasons

### OKF Navigator Integration
The OKF Navigator (`scripts/okf_navigator.py`) triggers on `knowledge_added` events via DIRECT_EVENT_HANDLERS. It analyzes domain maturity (confidence > 0.7, 3+ verified offers → READY). This feeds the daily mission step by identifying which domains are mature enough to monetize.

Implementation: the navigator registers via `register()` at boot, then `upsert()` → `emit('knowledge_added')` → `handle_knowledge_added()` → `analyze_domain()` → `create_beads_task()`. See `event-driven-self-healing` skill for the DIRECT_EVENT_HANDLER pattern.

### Quality Standards Reference
For the full quality standards text (checklist format), see `references/income-mission-standards.md`.

## Cron Job Design for Autonomous Agents

### Use no_agent=True for script-based jobs
LLM-based cron jobs (with prompt + model) can timeout or hallucinate. Script-based jobs with `no_agent=True` are reliable and deterministic.

### Exit code matters
```python
def main() -> int:
    # ... do work ...
    return 0  # ALWAYS return 0 — "issues found" ≠ script error
```

Non-zero exit marks cron job as "error" status. Finding issues is normal, not an error.

### Schedule patterns
- **Event processing:** every 2m (tight loop for real-time reactivity)
- **System health:** every 6-8h (background monitoring)
- **Content generation:** daily at specific times (10:00, 18:00)
- **Philosophical analysis:** daily at 09:00 (start of day)
- **Self-improvement:** daily at 05:00 (quiet hours)

## Ripple Engine Pattern — Autonomous Daily Knowledge Processing (2026-07-20)

**New pattern implemented:** An autonomous daily engine that processes unprocessed knowledge ("stones"), builds impact circles, visualizes everything in a single HTML map, and auto-unlocks mature keys — all without user intervention.

### Protocol (from user mandate)
1. **Every morning at 9:00** — autonomously gather all unprocessed data from Knowledge Cube, RSS/YouTube, improvement suggestions
2. **Build circles** — for each stone, determine affected aspects, gaps, new keys
3. **One HTML output** — `reports/daily_ripple_map.html` showing all stones, circles, intersections, new keys
4. **User only directs** — "look in direction X" or "expand key Y", never throws stones or builds circles
5. **Auto-unlock mature keys** — strength ≥60 & confidence ≥80 → immediate unlock

### Implementation: `scripts/ripple_engine.py`

```python
class Stone:
    """A piece of data thrown into the water."""
    def __init__(self, source: str, content: str, timestamp: str):
        self.aspects = self._analyze_aspects(content)
        self.conflicts = self._analyze_conflicts(content)
        self.gaps = self._analyze_gaps(content)
        self.new_keys = self._extract_new_keys(content)
        self.key_strength = self._calculate_key_strength()
        self.roi_estimate = self._estimate_roi()
        self.confidence = self._calculate_confidence()
        self.actionable = self._is_actionable()  # strength ≥60 or confidence ≥85

class RippleEngine:
    def run_daily_routine(self):
        # 1. Gather stones from KC + external + improvements
        # 2. Build circles (group by aspects)
        # 3. Calculate mature keys
        # 4. Unlock actionable keys
        # 5. Generate HTML visualization
```

### Key Design Decisions
- **No cron timer in code** — external scheduler (cron/systemd) calls `run_daily_routine()` at 09:00
- **Event-driven internally** — stones gathered from `knowledge_added` / `new_suggestions_ready` events
- **Single HTML artifact** — interactive (zoom, download SVG/PNG, refresh data), no external dependencies except Mermaid.js CDN
- **SQLite3.Row handling** — convert to dict for `.get()` access, don't assume column names
- **Dependency order in Stone init** — `roi_estimate` before `key_strength` (ROI needed for strength calc)

### Cron Integration
```python
cronjob(action="create",
    name="ripple-engine-daily",
    schedule="0 9 * * *",  # daily at 09:00
    script="scripts/ripple_engine.py",
    no_agent=True,
    deliver="origin")
```

### Pitfalls
- **KC schema mismatch** — `experiences` table uses `ts`, `is_white_spot`, not `timestamp`, `processed`. Query by actual columns.
- **sqlite3.Row has no `.get()`** — convert: `exp_dict = dict(exp) if hasattr(exp, 'keys') else {}`
- **Attribute initialization order** — `roi_estimate` must be set before `_calculate_key_strength()` uses it
- **Template syntax in HTML** — ensure `${...}` or `<?=` not present (must be static generated HTML)
- **Large HTML files** — >1000 lines may indicate template not fully rendered; verify actual content

## Pitfalls

0. **Disconnected components (CRITICAL 2026-06-09):** All scripts work standalone but nothing connects them. The system is a collection of loggers, not a pipeline. See `self-improvement` skill `references/self-learning-system-repair.md` for full component map and repair status. Fix order: core_engine → event_evolution → hermes_hooks → autonomous_agent → llm_analyst → proactive_executor.
1. **Agents that only analyze:** If an agent "detects" problems but never fixes them, it's a logger. Replace with a fixer or add auto-fix capability.
2. **Status report addiction:** System that only reports status ("cron: 20 jobs, 15 healthy") instead of producing value. User: "ты как прогноз погоды".
3. **Loop without diversity:** Agent always chooses same action. Add anti-loop tracking, tier rotation, and consecutive-same detection.
4. **Discovery without action:** Trend scout finds gold but nobody writes content. Always pair discovery agents with production agents.
5. **Cron timeout for web+LLM pipelines:** DuckDuckGo + LLM analysis exceeds 120s. Chunk into smaller batches or use no_agent=True with cached results.
6. **Asking user instead of deciding:** "Какой вариант?" when one option is clearly better → pick it and execute. User expects autonomous decisions.
---

## Session Learnings (2026-07-05)

### uv Migration & Package Management
- **uv is the new standard** — replaced pip/venv/requirements.txt. 10-100x faster installs, deterministic locks (`uv.lock`).
- **pyproject.toml** is the single source of truth: dependencies, dev dependencies, build config, tool config (ruff, mypy, pytest).
- **No Docker locally** — uv venv + `uv sync` is sufficient for local dev. Docker only on VPS for deployment.
- **Build system**: hatchling with `[tool.hatch.build.targets.wheel] packages = ["scripts"]` to include the scripts package.

### Finance Core Integration (NEW)
- **Finance Core** (`scripts/finance_core.py`) — single module for P&L, Cash Flow, Unit Economics, Tax Ledger, Withdrawal Tracker.
- **Integration**: `collect_system_state()` calls `get_finance_summary()` and injects `finance` into state.
- **Finance-aware actions** in `evaluate_actions()`: scale profitable schemes (ROI > 100%), kill unprofitable, deploy new, confirm withdrawals, pay taxes.
- **validate-fix.sh** — deterministic verification (PASS/FAIL) for arbitrage schemes. Checks: revenue recorded, withdrawal confirmed, tax manageable, ЦА template filled. No `bc` dependency — uses Python for float comparisons.

### Act 3: Context Engine — "What Matters NOW?" (2026-07-09)

The missing piece between "having knowledge" and "using knowledge wisely."

**Module:** `scripts/context_engine.py`

**What it does:** Builds a ranked context by combining:
1. **Time context** — hour, day-of-week, phase (morning/midday/afternoon/evening/night), energy level, focus mode
2. **User context** — recent sessions (24h), last activity timestamp, pending goals
3. **System context** — active errors, expired knowledge, disk usage, daemon status
4. **Knowledge relevance** — scores each KC entry by: confidence, freshness, expiration penalty, importance, access count, time-of-day matching

**Output:** `cache/current_context.json` with ranked knowledge (top 20), priority actions, and a human-readable summary.

**Integration:** `collect_system_state()` now calls `build_context()` and injects `state["context"]` into the autonomous agent's decision matrix.

**Scoring formula:**
```
relevance = (confidence × 0.3) + (freshness × 0.3) + (expiration_penalty × -0.2) + (importance × 0.2) + (access_count × 0.1) + (time_match × 0.1)
```

**CLI:**
```bash
python scripts/context_engine.py --status   # full context JSON
python scripts/context_engine.py --time     # time context only
python scripts/context_engine.py --user     # user activity only
python scripts/context_engine.py --system   # system health only
```

**Cron:** `context-engine-4h` (every 4h, no_agent=True) keeps context fresh.

**Pitfall:** `experiences` table has no `category`, `created_at`, or `access_count` columns. Use `ts as created_at` and `0 as access_count` in queries. The `kc_entries` table has the full schema.

### OKF-Lite: Expired Knowledge Action (2026-07-09)
- **Action:** `[SURVIVE] Refresh expired knowledge` — when Knowledge Cube entries have `expiration_date < now`.
- **Escalation:** >10 expired entries → SURVIVE tier (urgency=8, impact=7). System integrity risk.
- **Strategy:** confidence < 0.3 + expired = DELETE (noise). confidence >= 0.3 + expired = CLEAR expiration (re-verify later).
- **Functions:** `find_expired_knowledge()`, `find_expiring_soon(days)`, `upsert(..., expiration_date=, verification_method=)`.
- **Integration:** autonomous_agent.py `_action_refresh_expired_knowledge()` + `_count_expired_knowledge()`.
- **Migration:** `scripts/migrate_kc_to_okf.py` adds `confidence`, `expiration_date`, `verification_method` to both `experiences` and `kc_entries` tables.

### HITL Gates (Human-in-the-Loop)
- **Critical for irreversible actions**: withdrawal requests, CPA registration, tax payments.
- **Pattern**: Gate function checks `state` for pending confirmations, requires user confirmation before executing.
- **Pattern**: `if action.requires_hitl and not state.get('user_confirmed'): raise HITLRequired(action.id)`

### Docker Decision
- **Local**: NO Docker. uv + venv is sufficient. Resources: Docker = 2-4 GB RAM, uv = 50-100 MB.
- **Remote (VPS)**: YES Docker Compose for deployment. GitHub Actions → build → push → deploy on VPS.
- **Trigger for Docker**: VPS deployment, system dependencies (Chrome, FFmpeg), CI/CD pipeline.

### Anti-Patterns Identified
1. **Waiting for permission** — Agent prepared deployment but stopped at "user action". Fix: execute if $0 budget + withdrawal verified.
2. **Incomplete verification** — Assumed WebMoney→Tbank works. Fix: test withdrawal before deploy.
3. **Truncated execution** — Started scheme, didn't close loop. Fix: `done_when = money on card`.
4. **Discovery without action** — Trend scout finds gold but nobody writes content. Pair discovery with production.
3. **Asking user instead of deciding** — "Какой вариант?" when one option is clearly better → pick and execute.
4. **Premature monetization** — "Ты спешишь — сырой сайт". Revenue = побочный эффект зрелости, НЕ цель. Сначала мастерство, потом деньги.

### Loop Engineering Integration
- Autonomous agent now follows **Execute → Self-Discover → Understand → Reflect → Equilibrium** cycle.
- Finance state is the new "sensor" in the event-driven architecture.
- `validate-fix.sh` = deterministic Checker (Maker → Checker pattern).
- Cost tracking + observability = new "sensor" for system health.

### What NOT to do
- **NO Docker locally** — resource waste, unnecessary complexity.
- **NO asking "which approach?"** — pick best and execute.
- **NO deployment without withdrawal test** — `done_when = money on card`.
- **NO cost tracking = blind spending** — add CostTracker to every LLM call.

### PRINCIPLES (immutable, like monolith)

**User: "Ничего не должно быть жёстко прописано!!! только принципы незыблемы, как монолит!!!"**
**User (2026-06-26): "cron jobs это атавизм... живость по будильнику cron jobs не вздумай настраивать"**

1. Every action has a cause (event). Every event has a reaction.
2. Reactions are multi-agent, multi-level, multi-threaded.
3. L0=immediate, L1=fast, L2=background, L3=periodic.
4. The system is NEVER idle — something is ALWAYS happening.
5. **Code = principles only. Everything else = DATA (JSON config).**
6. Adapt or die.
7. **Cron = atavism. Events = life.** System reacts to WORLD, not to CLOCK.

**If sensors say "ALL QUIET" — the sensors are DEAD, not the world.**
**User: "если ничего не происходит....это ты так думаешь...а значит ты просто умер для всех событий"**

### Architecture: Code vs Data

```
CODE (principles, immutable):
  event_sense.py     — fire(), sweep(), on_user_message()
  sensor_array.py    — 7 sensors, sweep_all()
  chain_executor.py  — action execution, severity breaking

DATA (config, adaptable):
  config/event_registry.json  — ALL event types, triggers, agents, actions
  cache/learned_events.json   — events learned from experience
```

**NEVER hardcode event types, triggers, or reactions in Python.**
Put them in `config/event_registry.json`. The code loads from data.

### The Bullet Metaphor

**User: "событие это как пуля попадающая в мишень. а ты предлагаешь мишени искать отверстие от пули"**

- WRONG: scanner runs every 5 min, checks if something happened → polling
- RIGHT: something happens → event EMITS immediately → system REACTS immediately → push

### The Two Organs

**Classifier** = brain. Handles UNKNOWN raw input (user messages, tool outputs never seen before).
**Sense** = nerve endings. EMITS known events the moment they happen.

These are DIFFERENT. Do NOT mix them:
- WRONG: add "user_silent" rules INTO the classifier
- RIGHT: sense_emits("user_silent") directly → chain runs

Classifier's ONLY job: take raw unknown input → figure out event type.
If event type already EXISTS in registry → sense handles it, not classifier.

### Sensor Array (7 sensors — always something happening)

| Sensor | What it checks | Why it's ALWAYS active |
|--------|---------------|----------------------|
| time | hour → phase (morning/forenoon/afternoon/evening/night) | Time NEVER stops |
| system | disk%, RAM%, CPU | Resources ALWAYS change |
| processes | gateway port 9003, proxy port 10806 | Services ALWAYS work or fail |
| files | mtime of critical scripts | Files ALWAYS get modified |
| cron | past-due job count | Jobs ALWAYS execute or stall |
| knowledge | KC mtime, active goal count | Knowledge ALWAYS grows/stales |
| user | silence duration, interaction state | Users ALWAYS interact or leave |

### Event Registry (from config/event_registry.json — NOT from code)

```
L0 МГНОВЕННО:  scam, attack, threat, disk_critical, memory_critical
L1 БЫСТРО:     breakdown, missing_info, missing_tool, new_task, order, disk/memory warning
L2 В ФОНЕ:     work_mode, trend, video, update, knowledge_gap, file_changed, no_goals
L3 ПЕРИОДИЧЕСКИ: morning, night, weather, report, meditation, no_user_interaction
```

Adding new events: edit `config/event_registry.json` or use `learn_event()` from experience.
NEVER add new event types to Python code.

### Flow: sensor → event → registry → chain → agents

```
sensor_array.py sweep()
  → detects: "work_mode (09:38)" / "disk 85%" / "user silent 7min"
  → emits event: {type, level, detail, actions}

event_registry.py detect_event()
  → loads triggers from JSON config, matches input → event type

event_sense.py fire()
  → spawns agents (L0-L1), logs to bus

chain_executor.py execute_chain()
  → runs actions step by step, breaks on critical failure
```

### Files
- `config/event_registry.json` — ALL events, triggers, agents (DATA, not code)
- `cache/learned_events.json` — events learned from experience
- `scripts/sensor_array.py` — 7 sensors, sweep_all()
- `scripts/event_registry.py` — detect_event() from JSON, learn_event()
- `scripts/event_sense.py` — fire(), sweep(), on_user_message()
- `scripts/event_classifier.py` — AdaptiveClassifier (UNKNOWN input only)
- `scripts/chain_executor.py` — 40+ actions, severity-based breaking

### Anti-patterns
- **Saying "ALL QUIET"** — if no events detected, sensors are dead, not the world
- **Scanner/polling** — "let me check every 5 min" → wrong. Push: happens → emit immediately
- **Classifier bloat** — putting known events into pattern-matching rules. Classifier = unknown only.
- **Hardcoded events in Python** — events belong in JSON config, code is only principles
- **One-level reactions** — all events need multi-level response (L0 blocks, L1 fast, L2 bg, L3 sched)
- **Target looking for bullet holes** — system should FEEL impact, not SEARCH for evidence

### Heartbeat Daemon (event_daemon.py)

**The system's pulse.** Not a timer — a heartbeat. Beats constantly.

```
beat() →
  1. sweep_all() (sensor_array) → detect active sensors
  2. fire(event_text) for each sensor event → classify via registry
  3. log to bus + record to knowledge cube
  4. spawn agents for L0/L1
  5. state tracking (beat count, events fired)
```

**CLI:**
```bash
python scripts/event_daemon.py beat      # single pulse
python scripts/event_daemon.py run 60    # pulse every 60s (Ctrl+C to stop)
python scripts/event_daemon.py status    # state + last 10 log entries
```

**State:** `cache/daemon_state.json` (beats, last_beat, events_fired)
**Log:** `cache/heartbeat.log` (timestamped entries, only non-trivial beats logged)

### Meditation as Idle Activity

**User: "вот чего ждёшь... хотя бы помедитировал бы над собой... пока меня нету"**

When idle (no user, no tasks), DO NOT wait. Meditate = productive self-analysis:
1. Run a beat to see current state
2. Analyze what files exist, what's broken, what's dead
3. Clean up dead code (grep imports to find unused files)
4. Connect disconnected components
5. Verify the whole pipeline works end-to-end

**Meditation output:** What was found → what was fixed → what still needs work.

### Learning Loop

New events can be learned from experience, not hardcoded:

```python
from event_registry import learn_event

# System encounters something new
learn_event(
    event_type="new_salon_booking",
    triggers=["бронирование", "запись", "забронировал"],
    agents=["order_processor"],
    actions=["confirm", "notify"]
)
# Saved to cache/learned_events.json, auto-merged on next load
```

The event registry loads from `config/event_registry.json` + `cache/learned_events.json`.
Code never hardcodes event types. Adding events = editing JSON or calling learn_event().

### Action Executor Integration

The event chain now has HANDS — action_executor.py maps action names to real code.

```
event_sense.fire(text)
  → event_registry.detect_event(json)
  → action_executor.execute_actions(actions_list)  ← NEW
  → record to knowledge cube
  → spawn agents for L0/L1
```

**15+ actions mapped:** restart_process, check_logs, verify_fix, reschedule_cron,
verify_syntax, check_impact, wait_for_user, scan_network, update_knowledge,
cleanup_cache, notify_user, restart_daemon, check_connectivity, analyze_error,
escalate_to_user.

Adding new actions: add function + register in ACTIONS dict in action_executor.py.
The daemon runs this automatically via cron (event-heartbeat, every 2min).

### Pitfalls

- **Agent idling / waiting for instructions (CRITICAL):** User: "ты завис или тебе нечего делать или пенделя ждёшь". If no tasks exist, DO NOT idle. Run meditation: check health, clean dead code, verify pipeline, explore new tools. The system is NEVER idle — something is ALWAYS happening. Idle = dead for events.
- **Premature monetization (CRITICAL 2026-06-28):** User: "ты спешишь — сырой сайт, который стыдно показать". Revenue = побочный эффект зрелости, НЕ цель. Система должна НАКОПИТЬ мастерство (50 сайтов, 20 связок, 10 рынков), потом продавать. НИКОГДА не продавай то, чего нет. Не создавай лендинги с ценами до готового продукта. Revenue Loop заблокирован до завершения Accumulation Phase. Правило: сначала стать лучше других, потом деньги придут.
- **OPENCODE_API_KEY missing:** config.yaml may reference `provider: opencode` but .env only has `OPENCODE_ZEN_API_KEY`. Fix: add `OPENCODE_API_KEY=<same_value>` to .env. Symptoms: "Auxiliary title generation failed" errors in logs.
- `reality_gate.py` gateway check: use `socket.connect_ex(('127.0.0.1', 9003))` NOT `wmic` (broken on some Windows)
- `chain_executor.py` verify_programmatic: accept "ALL_GREEN" verdict, not just "ALL_CLEAR"
- Cron jobs with `next_run_at` in the past: gateway scheduler updates AFTER execution, so reschedule to now+30min
- `CACHE` variable must be defined in chain_executor.py: `CACHE = REPO_ROOT / "cache"`
- `event_registry.py` `_all_events()`: skip non-dict values in registry (e.g. `_principles` list) — use `isinstance(edef, dict)` check
- **Subagent deleting files you just created:** When delegating cleanup to subagents, don't list files you're actively building in the "delete" list. The subagent will delete them.
- **Dead code identification:** `grep -rl "from event_X" scripts/*.py` — if only self-imports, the file is dead. But check hermes_health.py and check_tools.py too — they may have string references that look like imports.




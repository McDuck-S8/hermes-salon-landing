# AI-First Business Playbook — Key Concepts for Hermes (2026-07-02)

## Core Question
**"Why can't AI do this?"** — Ask before every new script/cron/skill. If answer isn't "because of X hard constraint" → automate.

## Core Concepts Applied to Hermes

### 1. Closed Loops (every process)
```
execute → measure → analyze → adjust → repeat
```
- procedural_executor: каждый рефлекс = execute → measure → analyze → adjust
- cron jobs: run → verify → log → alert if failed → auto-retry
- KC: ingest → classify → query → feedback loop (salience)

### 2. Queryable Company (Business Brain)
| Layer | Hermes Implementation |
|-------|----------------------|
| Global Context | SOUL.md + MEMORY.md + agent_policies.md |
| Business Context | ARBITRAGE_WORKSHOP.md + goals + KC experiences |
| Department Context | skills/ per domain (arbitrage, devops, crystal, content) |
| Live Data | session_recall (conversations), signal_daemon (external), health_check |

**Test**: New session knows business without re-explaining. `python knowledge_brain.py --query "proxy status"` returns answer.

### 3. Test Harnesses (from Playbook)
Human writes SPEC + TESTS → Agent generates → Validates → FAIL = loop → PASS = deliver
- Applied in: verify_fix.py, output_validator.py, verify_fix.py
- Every fix must have spec + automated tests before implementation

### 4. New Org Chart (Playbook)
| Role | Hermes Mapping |
|------|----------------|
| IC (Builder-Operator) | scripts/ — каждый скрипт = IC |
| DRI (Outcome Owner) | goals — каждый goal имеет owner + metric |
| AI Founder | SOUL.md — vision + conviction |

### 5. Token Maxing
- Scale through AI skills, not headcount
- Revenue per script = success metric
- 70%+ processes automated within 90 days

### 6. Four-Step Playbook (applied to Hermes)
1. **LEARN** — изучаем инструменты (Claude Code, Gemini, LanceDB, watchdog)
2. **WIRE** — строим Business Brain (KC + session_recall + MEMORY + expiry.md)
3. **AUTOMATE** — skills per department (arbitrage, devops, crystal, content)
4. **SCALE** — multiply through AI departments (war room, auto-assign, suggestions)

### 6. Department Skills Structure
```
skills/
├── arbitrage/        # Marketing + Sales (signal → scheme → deploy → track)
├── devops/           # Operations (procedural_executor, cron, proxy, gateway)
├── crystal/          # Delivery (self-learning, self-healing, self-evolving)
├── content/          # Content (session_recall, conversation_ingester, blog_poster)
└── test-harness/     # Test infrastructure (verify_fix, output_validator)
```

## Dual AI Provider Pattern (from Content Studio)
| Task | Provider | Why |
|------|----------|-----|
| Heavy reasoning, coding, planning | Claude Code / OpenRouter (Claude) | Best reasoning |
| Cheap classification, embeddings, suggestions | Gemini Flash | Free tier, fast, large context |
| Local/offline | Local models (if available) | Privacy, cost |

## Key Metrics (from Playbook)
| KPI | Target | Timeframe |
|-----|--------|-----------|
| Hours reclaimed/week | 15-20 | 90 days |
| Revenue per script | Increasing | Ongoing |
| AI coverage | 70%+ processes | 90 days |
| Test pass rate | 100% on deploy | Always |

## Integration with Existing Hermes
- **expiry.md** = Business Brain index (Revisit triggers = freshness)
- **Revisit lines** = freshness markers (Playbook: "knowledge needs updating")
- **verify_fix.py** = Test Harness runner
- **procedural_executor** = Closed Loop executor
- **crystal** = Self-evolving delivery department
- **signal_daemon** = Live data source (external intelligence)
- **knowledge_brain.py** = Queryable Brain interface
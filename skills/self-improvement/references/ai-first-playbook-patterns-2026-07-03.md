# AI-First Business Playbook Patterns Applied to Hermes (2026-07-03)

Source: Bohdan Saranchuk's "AI-First Business Playbook v2" (16 pages)

## Core Concepts Applied to Hermes

### 1. Core Question: "Why can't AI do this?"
**Before every new script/cron/skill/new-agent**: Ask this question. If answer is "no valid reason" → automate.
**Hermes implementation**: Added to SOUL.md as mandatory reflex.

### 2. Closed Loops
Every process = execute → measure → analyze → adjust → repeat. No open loops.
**Hermes**: procedural_executor = closed-loop reflexes; crystal = closed-loop learning; test_harness = closed-loop quality.

### 3. Queryable Business Brain
Global Context + Business Context + Department Context + Live Data Sources.
**Hermes**: SOUL.md (Global) + AGENTS.md (Business) + scripts/AGENTS.md (Department) + KC + session_recall (Live).

### 4. Test Harnesses (SPEC → TESTS → GENERATE → VALIDATE → LOOP → DELIVER)
Human writes SPEC + TESTS → Agent GENERATE → Harness VALIDATE → FAIL = LOOP → PASS = DELIVER.
**Hermes**: test-harness skill + verify_fix.py + procedural_executor integration.

### 5. New Org Chart
- **IC (Builder-Operator)**: scripts/ — direct execution
- **DRI (Outcome Owner)**: goals in goal_queue — each goal has owner
- **AI Founder**: SOUL.md — vision and agency

### 6. Token Maxing
Scale via AI skills, not headcount. Revenue per script = success metric.
**Hermes**: Revenue tracked per project in PROJECT_MAP.md.

### 7. Four-Step Playbook
1. **LEARN** — study tools, build skills
2. **WIRE** — build Business Brain (KC + session_recall + MEMORY.md)
3. **AUTOMATE** — skills per department (Arbitrage/DevOps/Crystal/Content)
4. **SCALE** — multiply via AI departments

### 8. Department Skills Mapping
| Business Dept | Hermes Equivalent | Skills |
|--------------|-------------------|--------|
| Marketing | Arbitrage | signal_scanner, rd_processor, dev_processor |
| Sales | Arbitrage Execution | arbitrage-execution, telegram_bots |
| Delivery | Crystal | crystal modules, test_harness |
| Operations | DevOps | procedural_executor, cron-maintenance, hermes-self-diagnosis |

### 9. Dual AI Providers
- Heavy reasoning (planning, analysis) → Claude (via Claude Code)
- Cheap classification/embeddings → Gemini Flash (via OpenRouter)
- Local models (Ollama) for privacy-sensitive

### 10. Pipeline-Centric (from content-studio)
Research → Create → Publish → Repurpose → Analyze
Applied to Arbitrage: Signal → Validate → Workshop → Deploy → Track → Repurpose
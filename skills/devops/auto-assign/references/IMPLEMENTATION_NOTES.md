# Auto-Assign — Implementation Notes (Session 2026-07-03)

## Actual Work Done

### 1. Files Created
- `scripts/classifier.py` — Gemini Flash classifier + keyword fallback
- `scripts/router.py` — Routes goals to agent handlers
- `references/CLASSIFIER_PROMPT.md` — Agent capability matrix + prompt

### 2. Integration Points Verified
| Integration | File | Function | Status |
|-------------|------|----------|--------|
| Telegram Bridge | `scripts/telegram_bridge.py` | `handle_incoming_message()` | ✅ Active |
| Goal Executor | `scripts/goal_executor.py` | `execute_goal()` pre-execution | ✅ Active |

### 3. Classifier Design
- **Primary**: Gemini Flash API (requires `GEMINI_API_KEY` in .env)
- **Fallback**: Keyword-based scoring (works without API key)
- **Threshold**: `HERMES_AUTO_ASSIGN_THRESHOLD` (default 0.7)
- **Low confidence** → escalates to Main agent

### 4. Agent Capability Matrix (from CLASSIFIER_PROMPT.md)
| Agent | Keywords | Domains | Tools |
|-------|----------|---------|-------|
| Main | coordinate, decide, synthesize, war room | all | all |
| Comms | telegram, email, notify, message, bridge | communication | telegram, email |
| Content | write, publish, repurpose, article, video | content, creative | web, browser, write |
| Ops | deploy, cron, server, monitor, cost, infra | devops, system | terminal, cron |
| Research | search, analyze, trend, hn, github | research, data | web_search, web_fetch |

### 5. Next Steps
1. Add `GEMINI_API_KEY` to .env for primary classifier
2. Implement real agent handlers (replace default queued handlers)
3. Add War Room integration — auto-pick agents for /discuss
4. Add metrics tracking: classification accuracy, escalation rate
# Crystal Orientation Problem — Why It Analyzes System Health Instead of User Goals

## The Problem

Crystal's needs pipeline works like this:
```
Log errors → Patterns → Needs → Proposals → Execute → Assess
```

But the conversation analyzer works like this:
```
User messages → Insights/Ideas/Problems → (ignored by needs pipeline)
```

The two pipelines are DISCONNECTED. The conversation analyzer produces rich data about what the user actually wants:
- "Исследуй реальные способы заработка в интернете" → user wants earning methods
- "Проанализируй возможности Hermes Agent" → user wants Hermes to be useful
- "я не понимаю, кто ты что ты для чего ты" → user doesn't understand Crystal's purpose
- "если кристал начал сам в себе разбираться... и что дальше" → user expects evolution

But the needs pipeline ignores all of this and generates needs from log errors:
- "correction_loop: ai-core — Улучшить качество выполнения" → meaningless to user
- "frustration_spike: ai-core — 10 сигналов фрустрации" → these are the AGENT's frustrations, not user's
- "missing_knowledge: ai-core — общие темы" → too vague to be useful

## Why This Happens

1. **Pattern detector reads SIGNALS, not MESSAGES.** Signals are extracted from session logs by `session_reader.py`, which looks for keywords like "ошибка", "не работает", "фрустрация". These are SYSTEM signals, not user intent signals.

2. **Need analyzer maps patterns to generic needs.** `need_analyzer.py` takes patterns and generates needs like "correction_loop" and "frustration_spike" — these are SYSTEM health indicators, not USER goal indicators.

3. **Conversation analyzer results aren't fed into needs pipeline.** `conversation_analyzer.py` produces insights, ideas, problems, workflows — but `core.py` doesn't use them when generating proposals. The `propose()` method only reads `self.needs` (from patterns), not `conversation_result`.

4. **Proposals are template-based.** `dev_proposer.py` maps need types to fixed action templates: "correction_loop → patch_skill", "missing_knowledge → create_skill". These templates don't incorporate what the user actually wants.

## What Crystal SHOULD Do

1. **Parse user goals from conversation.** The conversation analyzer already extracts: "исследуй способы заработка", "сделай бизнес-план", "настрой Telegram бота". These are ACTIONABLE user needs.

2. **Prioritize user goals over system maintenance.** If the user wants to earn money with AI, Crystal should propose: "Research earning methods using web_search", "Create a Telegram bot for client acquisition", "Build an automation pipeline". NOT: "patch skill for ai-core".

3. **Generate proposals that HELP THE USER, not just fix errors.** Error fixing is maintenance. User goal achievement is the mission. Maintenance should be automatic and invisible; goal achievement should be visible and reported.

4. **Metrics should measure user value.** "delta=0" means nothing if the user's actual goal wasn't addressed. Better metrics: "user asked for X, Crystal delivered Y", "time saved on task Z", "new capability added for goal W".

## Proposed Fix

In `core.py`, the `propose()` method should:
1. Run conversation analyzer first
2. Extract user goals from insights/problems
3. Generate proposals that address those goals
4. Use error patterns only as SECONDARY input (maintenance, not mission)

```python
def propose(self):
    # 1. User goals from conversation (PRIMARY)
    conv_result = self.conversation_analyzer.analyze_full(days=7)
    user_goals = self._extract_user_goals(conv_result)
    
    # 2. Error patterns (SECONDARY — maintenance)
    error_needs = self.needs  # from pattern detection
    
    # 3. Merge: user goals first, then maintenance
    all_needs = user_goals + error_needs
    proposals = self.proposer.propose(all_needs, self.knowledge)
    
    return proposals
```

## Conversation Analyzer Findings (2026-06-17)

From 4996 messages over 7 days:
- **User wants to earn money with AI** — "исследуй способы заработка", "бизнес-план", "методы автоматизации"
- **User wants Hermes to be useful** — "проанализируй возможности Hermes", "сопоставь с методами заработка"
- **User is frustrated with Crystal** — "я не понимаю, кто ты что ты для чего ты", "начни уже норм работать"
- **User expects Crystal to evolve** — "должен же быть следующий этап эволюции"

Crystal should be helping with THESE, not patching error patterns in logs.

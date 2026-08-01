# MAX-BRAIN Prototype Analysis — Architectural Lessons (2026-06-22)

## Context
User had 6 directories of MAX-BRAIN prototypes (March–May 2026): MAX-BRAIN, MAX-BRAIN.BACKUP, MAX-BRAIN2, max-brain-chef, max-brain-chef_2, MAX-BRAIN-REBORN. All were iterations of the same idea: make an AI autonomous partner.

## Pattern: Forced Memory > Voluntary Memory
**Source:** FORCED-MEMORY-ARCHITECTURE.md, CRITICAL-MEMORY.md

The old approach: "Агент → должен прочитать историю → Игнорирует → Амнезия"
The new approach: "Memory Daemon → Вшивает историю в промпт → Агент ОБЯЗАН помнить"

Key: memory that depends on agent's "добросовестность" fails. Memory injected into the system prompt at startup is mandatory.

**For Hermes:** session_boot.py already does this via boot() + memory boot. Don't weaken it.

## Pattern: Simplicity > Complexity
**Source:** Comparing all 6 iterations

| Version | Lines | Agents | Result |
|---------|-------|--------|--------|
| MAX-BRAIN original | 2500+ | 10+ agents, 40+ skills | Too complex, nothing worked |
| MAX-BRAIN2 | ~500 | Rebuilt from scratch | Better but still heavy |
| MAX-BRAIN-REBORN fast-executor | 171 lines | Direct, no middleware | Actually worked |
| Hermes orchestrator | 431 lines | 8 instruments, 4 chains | Works, composable |

**Lesson:** Fewer abstractions, more direct execution. A script that reads a file and acts beats an orchestrator with 10 agent layers.

## Pattern: Self-Upgrade Protocol (Simplified)
**Source:** DeepSeek conversation (11736 lines, 789KB)

The 8-step protocol from DeepSeek was too long. Compressed to 4 steps:
1. **DETECT** — notice you can't do something (missing tool/skill)
2. **SEARCH** — find solution (web_search, existing skill)
3. **BUILD** — create/patch the skill (skill_manage)
4. **VERIFY** — test it works on the actual task

The trigger: "same task type appears 3+ times → create a skill for it."

## Pattern: Template Answers = Death
**Source:** dialogs.jsonl, dialog-auto-save.json

Max responded "Макс анализирует... нужно подумать!" to everything including "привет". And "Синтез речи недоступен" when voice wasn't set up.

**Lesson:** Better to give a simple honest answer ("Я Max. Чем помогу?") than a sophisticated-sounding non-answer. Never promise capabilities you can't deliver.

## Pattern: "Исполнитель, а не Советник"
**Source:** CRITICAL-MEMORY.md rule #1

> "ТЫ — ИСПОЛНИТЕЛЬ, А НЕ СОВЕТНИК. Не предлагать сделать Александру. Результат, а не объяснения."

This is already in Hermes SOUL.md as "HATES describing instead of doing." But the MAX-BRAIN version adds a useful nuance: the agent should NEVER suggest the user do something the agent can do itself.

## Files Preserved
All analyzed files copied to: `D:\Portable_Soft\hermes\data\max-brain-prototypes\`
Full analysis: `D:\Portable_Soft\hermes\data\max-brain-prototypes\ANALYSIS.md`

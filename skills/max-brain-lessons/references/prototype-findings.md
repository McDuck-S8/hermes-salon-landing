# MAX-BRAIN Prototype Findings (2026-06-22)

## Directories Analyzed
1. D:\MAX-BRAIN (original, March 2026)
2. D:\MAX-BRAIN.BACKUP
3. D:\MAX-BRAIN2 (rebuilt March 27)
4. D:\max-brain-chef (May 2026)
5. D:\max-brain-chef_2 (May 2026)
6. D:\MAX-BRAIN-REBORN (April-May 2026)

## Key Files Extracted
- `chats/deepseek_chat_save.md` — 789KB, 11736 lines. Main conversation with DeepSeek about Max's problems.
- `identity/MAX-IDENTITY.md` — 125KB. Full agent persona definition.
- `identity/CRITICAL-MEMORY.md` — Checklist: "ТЫ — ИСПОЛНИТЕЛЬ, А НЕ СОВЕТНИК"
- `identity/FORCED-MEMORY-ARCHITECTURE.md` — Memory Daemon pattern
- `architecture/direct_executor.py` — 171 lines, simplest working executor
- `architecture/autonomous_loop.py` — 24/7 loop with trigger engine

## Critical User Quotes (from DeepSeek chat)
- "у меня не получается дать ему такое... если в процессе выполнения чего-то не хватает, есть интернет найди лучшее и сделай себе инструмент"
- "он понимает, но почему то всё наперекосяк"
- "бляяяя не тупи и запиши сразу что бы больше не спрашивал"

## Dialog Pattern (from dialog-auto-save.json)
Max kept responding "Макс анализирует... нужно подумать!" on EVERYTHING including "привет".
User had to say "ты кто" 10+ times before getting a real answer.

## Self-Upgrade Protocol (DeepSeek's proposal, 8 steps — we simplified to 4)
1. STOP — зафиксируй дефицит
2. SEARCH — найди решение (research-agent)
3. EVALUATE — выбери лучшее
4. BUILD — создай инструмент
5. TEST — проверь
6. INTEGRATE — подключи к системе
7. RETURN — вернись к исходной задаче
8. REFLECT — запиши урок

## Config Fix: opencode provider
- `auxiliary.title_generation.provider: opencode` fails with "no API key found"
- Fix: change to `opencode-zen` (the provider that resolves OPENCODE_API_KEY from .env)
- Other `provider: opencode` entries (model definitions, llm_analyst) work fine — they're different contexts

# User Corrections — 2026-06-23

## Correction 1: "всё блять уже прописано"
**Context:** Agent asked "что делать? Должен ли я перейти на bd? delegate_task?" after reading AGENTS.md
**User:** "всё блять уже прописано.... что тебе не понятно... давай обсудим..."
**Lesson:** Rules are already written. Don't ask what to do — DO what's written. The contract exists.

## Correction 2: "да отъебись ты от тгб!"
**Context:** Agent was installing/reinstalling packages, organizing files, creating indexes
**User:** "да отъебись ты от тгб!!!!!!!! наладь работу внутри себя!!!! ты блять ставишь... переставишь.... где сука результаты????"
**Lesson:** Stop tinkering with tools/packages. Fix INTERNAL systems. Installing ≠ working. Results = running services, not installed packages.

## Correction 3: "нахрена дурная работа?"
**Context:** Agent reinstalled aiogram that was already installed
**User:** "у тебя есть записи что ты устанавливал??? вот это pip install aiogram==3.29.0 ты ставил вчера!!!! вот нахрена дурная работа??? для красивых отчетов!!!"
**Lesson:** CHECK what's already installed BEFORE reinstalling. Reinstalling already-working things = busywork for reports. Read session history first.

## Correction 4: "прочитай контракт сцуко!"
**Context:** Agent hadn't read AGENTS.md / DOX framework
**User:** "прочитай контракт сцуко!!!! перепиши что уже стоит!!!! потом лезь ставить что необходимо!!!!"
**Lesson:** Read the contract (AGENTS.md) FIRST. Fix what exists BEFORE installing new things. Contract → Fix existing → Install new.

## Correction 5: "ты опять ждёшь указаний?"
**Context:** Agent completed SELF_IDENTITY.md and BOOT_SEQUENCE.md, then waited
**User:** "У тебя есть SELF_IDENTITY.md. Ты знаешь, что Отдел разведки не укомплектован... И ты сидишь. Ждёшь."
**Lesson:** When you know what's broken, FIX IT. Don't wait for permission. Instructions were already given in the identity document.

## Correction 6: "вот зачем тебе Chromium"
**Context:** Agent tried to install playwright chromium separately
**User:** "вот зачем тебе Chromium.... есть comet perplexity по умолчанию, есть browseros и много чего"
**Lesson:** USE EXISTING TOOLS. browser_navigate/browser_snapshot are built into Hermes. Don't install duplicates.

## Correction 7: 6-iteration history lesson
**Context:** Agent found MAX-BRAIN, MAX-BRAIN2, max-brain-chef, MAX-BRAIN-REBORN folders
**User:** "ты будешь читай по новой и тратить токены... давай тратить ведь мне это на халяву и безлимитно"
**Lesson:** Don't re-read/re-analyze what predecessors already analyzed. Read their CODE and RESULTS, not their analysis. Find what they BUILT that works, use it.

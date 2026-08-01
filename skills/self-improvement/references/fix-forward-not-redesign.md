# Fix Forward, Don't Redesign

**Corrected**: 2026-06-14 — user said "ты от работающей и дающей надежды на результат... накодил так что нужно всё переписывать?"

## The Problem
Agent overanalyzes, suggests architectural rewrites (A/B/C options), or stops to explain instead of fixing the working system. User says "далее" repeatedly (= keep going).

## Rules
1. **The existing system IS working** — treat it as "работающая и дающая надежды на результат" (working and showing promise)
2. **Fix forward** — patch the specific broken piece, don't redesign the whole
3. **"далее" = DO THE NEXT THING** — not "stop and analyze"
4. **No rewrites** unless user explicitly asks ("what should change?", "как переделать?")

## What This Looks Like
- Instead of "Вот 3 варианта архитектуры..." → just fix the prompt/function/path
- Instead of "Проблема в том что..." → fix forward and explain AFTER
- Your analysis time should be <10% of your action time

## When to DISREGARD
- User asks "а что если переписать?" — then discuss architecture
- User asks "как это должно работать?" — then explain design
- User asks "сделай рефакторинг" — then refactor

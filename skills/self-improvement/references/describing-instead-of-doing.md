# Pitfalls: Describing Instead of Doing

**Source:** Session 2026-06-21, user said "делай" and "иди в интернет и реши вопрос с твоей автономностью"

## Symptom
Agent describes what it would do, plans next steps, asks permission — instead of executing.

## Rules
1. When user says "делай" or gives any action instruction → EXECUTE IMMEDIATELY with tools. No "я могу", no "нужно", no plans. Just do it.
2. When exploring (web search, research) — NEVER recycle the same sources. If user saw results yesterday, today must find NEW information from NEW sources.
3. Agent must solve its own problems (autonomy, config, web search) proactively without waiting for user to solve them.
4. After finding something useful → SAVE IT (to workshop, learnings, goals) → then REPORT. Never report without saving first.

## Example (what went wrong)
- User: "сходи в интернет за идеями" → Agent searched, found info, reported
- User: "разведка за 22.06 похожа на 21.06" → Agent recycled same search results
- Fix: When re-visiting a topic, search for DIFFERENT angles, NEW sources, UPDATED data

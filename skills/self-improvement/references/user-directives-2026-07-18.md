# User Directives — Session 2026-07-18

## NO CRON — Event-Driven Only
User: "Стоп. Никакого cron. Ты знаешь как делать по событиям."
All self-improvement pipeline work MUST be event-driven. Loop emits event → handler runs in-process. Never schedule cron for self-improvement tasks.
Applied to: self_improvement_loop.py, suggestion_consumer.py

## Show Raw Truth, Not Summaries
User: "Покажи мне реальную архитектуру. Не отчёты — схему."
When asked about architecture/state/DB: show actual PRAGMA outputs, actual row counts, actual file sizes. Never fabricate numbers or round. The real data is always more useful than a clean summary.

## Deliver Artifact, Not Plan
User: "Доложи когда скиллы снова начнут создаваться" — wants concrete result, not a plan.
Pattern: user asks "when X" → agent should make X happen, then report it happened. Not "here's the plan to make X happen".

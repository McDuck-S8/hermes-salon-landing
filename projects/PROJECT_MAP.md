# Project Map — Hermes Projects

> Updated: 2026-06-19
> Agent treats everything it finds/plans as projects. Synthesis projects combine existing ones.

## Project Registry

| # | Project | Status | Type | Income Potential | Location |
|---|---------|--------|------|-----------------|----------|
| 1 | **salon-bot** | 🟢 RUNNING | Telegram Bot | $1500-2500/год | projects/salon-bot/ |
| 2 | **telegram-tools** | 🟢 READY | TG Scripts | Контент-монетизация | projects/telegram-tools/ |
| 3 | **TGB-Booking** | 🟡 LEGACY | TG Bot | Компоненты для re-use | projects/TGB-Booking/ |
| 4 | **money4band** | 🟡 PLANNED | Income | $10-30/мес | projects/money4band/ |
| 5 | **crimea-bots** | 🟡 ALIVE | TG Bots | $500-1000/год | projects/crimea-bots/ |
| 6 | **content-monetization** | 🟡 SKELETON | Pipeline | Контент | projects/content-monetization/ |
| 7 | **auto-microsites** | 🟡 SKELETON | Generator | Лендинги | projects/auto-microsites/ |
| 8 | **ai-education-bot** | 🟡 HAS FILES | TG Bot | Образование | projects/ai-education-bot/ |
| 9 | **agentmemory** | 🟢 ALIVE | TypeScript | Инфра | projects/agentmemory/ |
| 10 | **entity-engine** | 🟢 ALIVE | Python | Инфра | projects/entity-engine/ |

## Synthesis Projects (combining existing)

| # | Synthesis | Components | Purpose |
|---|-----------|------------|---------|
| S1 | **TG Business Suite** | salon-bot + telegram-tools + TGB-Booking | Полный TG-стек для бизнеса |
| S2 | **Income Automation** | money4band + content-monetization | Автоматический доход |
| S3 | **Tourism Platform** | crimea-bots + auto-microsites | Туристический портал |
| S4 | **AI Education Platform** | ai-education-bot + content-monetization | Образовательный AI |

## Project Lifecycle

```
DISCOVER → PLAN → BUILD → TEST → DEPLOY → MONITOR → SYNTHESIZE
    │         │       │       │       │         │          │
    │         │       │       │       │         │          └─ Combine projects
    │         │       │       │       │         └─ Track metrics
    │         │       │       │       └─ Ship to client
    │         │       │       └─ Verify it works
    │         │       └─ Write code
    │         └─ Create project entry
    └─ Agent finds opportunity
```

## Agent Rules for Projects

1. **Every finding = potential project** — if agent discovers something useful, create a project entry
2. **Every plan = project** — if agent plans to build something, register it as a project
3. **Synthesis = combining** — when two projects complement each other, create a synthesis project
4. **Status tracking** — agent must update project status after each action
5. **Income tracking** — agent must track actual income from each project

## Health Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Projects with running code | 3/10 | 7/10 |
| Projects generating income | 0/10 | 3/10 |
| Synthesis projects | 0/4 | 2/4 |
| Agent actions per day | ~50 | ~100 |
| Knowledge entries | 4434 | 5000+ |

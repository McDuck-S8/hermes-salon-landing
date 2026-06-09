# AGENTS.md — plans/

## Purpose

Business plans, research reports, brainstorming outputs, and strategic documents. Contains both in-progress work and completed deliverables.

## Ownership

Mixed — created by agent during autonomous tasks, user-initiated research, and cron-triggered analysis.

## Files

| Category | Examples |
|---|---|
| Business plans | `three_branches_plan.md`, `earning_with_ai.md` |
| Research reports | `youtube_research_report.md`, `crimea_tourism_brainstorm.md` |
| Deliverables | `FINAL_REPORT.md`, `avito_ad.md`, `night_work_report.md` |
| Databases | `crm.db` (SQLite) |

## Local Contracts

- **Format**: Markdown for plans/reports, SQLite for structured data.
- **Language**: Mixed Russian and English depending on context.
- **Lifecycle**: Plans progress from draft → review → final. Final reports go to `reports/` for delivery.

## Work Guidance

- When the user asks for a business plan or research, save the output here with a descriptive filename.
- Move completed deliverables to `reports/` for user delivery.
- Reference `plans/` content in cron-triggered morning briefings and weekly reviews.
- `crm.db` is a SQLite database — do not edit as text; use Python/sqlite3 for modifications.

## Verification

- Verify Markdown renders correctly after editing.
- For `crm.db`, use `sqlite3 plans/crm.db ".tables"` to inspect structure before changes.

## Child DOX Index

No subdirectories — flat structure.

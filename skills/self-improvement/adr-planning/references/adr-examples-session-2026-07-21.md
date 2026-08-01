# ADR Examples from Session 2026-07-21

## ADR-001: Внедрение ADR как практики
- **Статус:** accepted
- **Контекст:** Изучил 5 репозиториев планирования. Понял что слабая точка — не записываю ПОЧЕМУ.
- **Решение:** Внедрить ADR для всех архитектурных решений
- **Файл:** `skills/planning/adr/ADR-001-adr-practice.md`

## ADR-002: Content Locking — FFmpeg + static assets (superseded by ADR-003)
- **Статус:** superseded (by ADR-003)
- **Решение:** FFmpeg конвейер без API зависимостей
- **Файл:** `skills/planning/adr/ADR-002-content-locking-pipeline.md`

## ADR-003: Content Locking — FFmpeg + system fonts (implementation)
- **Статус:** accepted
- **Контекст:** Windows drawtext path issues (drive letter colon), font not found
- **Решение:** относительные пути, text= вместо textfile=, Arial fallback
- **Файл:** `skills/planning/adr/ADR-003-content-locking-ffmpeg.md`

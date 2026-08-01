---
name: file-registry
description: "Auto-generated from FILE_REGISTRY.md"
trigger: "When user asks about FILE_REGISTRY concepts"
usage: file-registry
Revisit: 2026-07-31
---

# 📋 Hermes File Registry

**Last updated:** 2026-06-07
**Repository:** `D:\Portable_Soft\hermes\`
**Total tracked:** ~300+ files across 20+ directories

> This is the single source of truth for every file in the Hermes root.
> **Discipline:** Every new file gets an entry. Every moved file updates its path.
> **Status:** `active` — используется | `archived` — не используется, но сохранён | `trash` — на удаление

---

## Core Root Files (Hermes-managed)

Эти файлы обязаны быть в корне — их читает Hermes, Gateway, Scheduler при старте.

| File | Purpose | Size | Status |
|------|---------|------|--------|
| `config.yaml` | Главный конфиг Hermes (модель, провайдеры, тулсеты) | ~25KB | active |
| `.env` | Переменные окружения, API-ключи | ~2KB | active |
| `AGENTS.md` | Протокол интеграции агента (хуки, event_evolution) | ~3KB | active |
| `SOUL.md` | Идентичность системы | ~1KB | active |
| `state.db` | База сессий Hermes (SQLite) | varies | active |
| `state.db-shm` | Shared memory для state.db | — | active |
| `state.db-wal` | WAL для state.db | — | active |
| `auth.json` | Состояние аутентификации | — | active |
| `auth.lock` | Блокировка auth | — | active |
| `branches.yaml` | Ветки Branch Context Manager | — | active |
| `breadcrumbs.log` | Лог breadcrumb-трейлов | — | active |
| `channel_directory.json` | Маршрутизация каналов | — | active |
| `gateway.lock` | Блокировка gateway | — | active |
| `gateway.pid` | PID процесса gateway | — | active |
| `.hermes_history` | История команд Hermes | — | active |
| `.icarus-state.json` | Состояние Icarus | — | active |
| `.icarus-telemetry.jsonl` | Телеметрия Icarus | — | active |

---

## `scripts/` — Исполняемые скрипты

### `scripts/posting/` — Постинг в Telegram-каналы

Скрипты для публикации контента в каналы проекта MAX-BRAIN-CHEF.
Каналы: @max_brain_chef_official, @ai_frontier_you, @max_brain_chef_ai, @neuro_kitchen_ai
**Все скрипты обновлены:** путь `.env` исправлен с `hermes-usb-portable-main/data/.env` на `.env`

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `post_all.py` | Пост во все каналы сразу | 89 | active |
| `post_debug.py` | Дебаг-постинг | 27 | active |
| `post_debug2.py` | Дебаг-постинг v2 | 30 | active |
| `post_final.py` | Финальный постинг (основной) | 174 | active |
| `post_final2.py` | Финальный постинг v2 | 112 | active |
| `post_frontier.py` | Постинг на @ai_frontier_you | 42 | active |
| `post_urls.py` | Постинг URL/ссылок | 111 | active |
| `post_with_images.py` | Постинг с изображениями | 169 | active |
| `read_posts.py` | Чтение/просмотр постов | 21 | active |
| `send_test.py` | Тестовая отправка | 38 | active |
| `send_test2.py` | Тестовая отправка v2 | 24 | active |

### `scripts/utilities/` — Утилиты и фиксы

| File | Purpose | Status |
|------|---------|--------|
| `fix_bom.ps1` | Исправление BOM в файлах (PowerShell) | archived |
| `fix_encoding.ps1` | Исправление кодировки (PowerShell) | archived |
| `fix_token.py` | Фикс токенов | archived |
| `autonomous_test.py` | Тест автономной системы | archived |
| `launch.bat` | Запуск Hermes (bat-файл) | active |

### `scripts/_archive/` — Одноразовые скрипты

| File | Purpose | Status |
|------|---------|--------|
| `_render_eevee.py` | Blender EEVEE render (auto-generated) | archived |
| `_render_fixed.py` | Blender render fixed | archived |
| `_render_min.py` | Minimal Blender render | archived |
| `_render_script.py` | Blender render script | archived |
| `test_scene.blend-cli.json` | Blender CLI test output | archived |

### `scripts/` (корень) — Активные системные скрипты

| File | Purpose | Status |
|------|---------|--------|
| `event_evolution.py` | Ядро self-evolution: мониторинг событий, триггеры, engine | active |
| `hermes_hooks.py` | Удобная обёртка для event_evolution | active |
| `auto_recall.py` | Поиск контекста из Knowledge Cube | active |
| `event_trigger.py` | Tight-loop триггер (каждые 2 мин) | active |
| `proactive_executor.py` | Исполнитель предложенных действий | active |
| `telegram_bridge.py` | Отправка в Telegram через Bot API | active |
| `telegram_delivery_report.py` | Сбор и доставка результатов cron | active |
| `knowledge_surfacer.py` | Чтение и вывод инсайтов из Knowledge Cube | active |
| `daily_knowledge_report.py` | Генератор ежедневного отчёта из Куба | active |
| `system_watcher.py` | Мониторинг здоровья системы (каждый час) | active |
| `process_events_cron.py` | (заменён на event_trigger.py) | archived |
| `unified.py` / `unified_cron.py` | Unified system cycle | active |
| `subconscious_loop_cron.py` | Подсознательный цикл Memory Tree | active |
| `auto_fetch_cron.py` | Авто-сбор сессий для Memory Tree | active |
| `self_analysis_cron.py` | Ночной самоанализ (02:00) | active |
| `morning_report_cron.py` | Утренний отчёт (08:00) | active |
| `dream_memory_cron.py` | Консолидация памяти (03:00) | active |
| `health_check.py` | Проверка здоровья free API | active |
| `memory_consolidate.py` | Консолидация памяти | active |
| `skill_evolution_cron.py` | Эволюция скиллов (04:00) | active |
| `self_assessment_cron.py` | Самооценка (01:00) | active |
| `update_runtime_skill.py` | Обновление runtime-контекста (04:30) | active |
| `cube_feeder.py` | Питание Knowledge Cube (04:15) | active |
| `dimension_discovery.py` | Открытие новых измерений (04:45) | active |
| `nightly_brain_scan.py` | Ночное сканирование (03:00) | active |
| `ingest_sessions.py` | Инжест сессий в Cube (каждые 6ч) | active |
| `post_images/` — изображения для постов (папка) | — | active |

---

## `config/` — Конфигурация

### `config/backups/` — Резервные копии config.yaml

| File | Date | Status |
|------|------|--------|
| `config.yaml.bak.20260524_051511` | 2026-05-24 | archived |
| `config.yaml.bak.20260601_030137` | 2026-06-01 | archived |
| `config.yaml.bak.20260601_195424` | 2026-06-01 | archived |
| `config.yaml.bak.20260601_195436` | 2026-06-01 | archived |
| `config.yaml.bak.20260601_205356` | 2026-06-01 | archived |
| `config.yaml.bak.20260601_214457` | 2026-06-01 | archived |
| `config.yaml.bak.20260602_003918` | 2026-06-02 | archived |
| `config.yaml.bak.20260602_082128` | 2026-06-02 | archived |
| `config.yaml.bak.20260602_082146` | 2026-06-02 | archived |

---

## `assets/` — Медиафайлы

### `assets/avatars/` — Аватары Hermes

| File | Purpose | Status |
|------|---------|--------|
| `avatar_hermes.jpg` | Основной аватар (JPG) | active |
| `avatar_hermes.png` | Основной аватар (PNG) | active |
| `avatar_hermes_123.jpg` | Сгенерированный вариант | archived |
| `avatar_hermes_42.jpg` | Сгенерированный вариант | archived |
| `avatar_hermes_777.jpg` | Сгенерированный вариант | archived |

### `assets/images/` — Изображения

| File | Purpose | Status |
|------|---------|--------|
| `tavily_signup.png` | Скриншот регистрации Tavily | archived |

---

## `cache/` — Кэши и базы данных

| File | Purpose | Status |
|------|---------|--------|
| `events.db` | База событий self-evolution | active |
| `core_engine.db` | База ядра эволюции (gaps, proactive_actions, benefits, patterns) | active |
| `knowledge_cube.db` | Knowledge Cube (619+ записей опыта) | active |
| `sessions.db` | Архив сессий | active |
| `old_state.db` | Старая база состояний | archived |
| `lcm.db` | LCM база | active |
| `kanban.db` (+ `kanban.db.init.lock`) | Канбан-база | active |
| `context_length_cache.yaml` | Кэш длины контекста | active |
| `models_dev_cache.json` | Кэш моделей (dev) | active |
| `ollama_cloud_models_cache.json` | Кэш Ollama моделей | active |
| `provider_models_cache.json` | Кэш провайдеров | active |
| `youtube_research.json` | Результаты YouTube-исследования | archived |
| `gateway_state.json` | Снимок состояния gateway | active |
| `processes.json` | Состояние процессов | active |
| `.update_check` | Маркер проверки обновлений | active |
| `.gitignore` | Исключения Git | active |

---

## `cron/` — Cron-система

| Directory | Purpose |
|-----------|---------|
| `cron/output/` | Результаты выполнения cron-задач (по job_id) |
| `cron/output/reports/` | Сгенерированные отчёты (knowledge reports etc) |
| `cron/jobs/` | Определения задач |

**Активные задачи (20 шт):** см. `cronjob action=list` или `FILE_REGISTRY_CRON.md`

---

## `logs/` — Логи

| File | Purpose | Status |
|------|---------|--------|
| `agent_proactive_executor.md` | Лог развёртывания proactive executor | active |
| `agent_knowledge_surfacer.md` | Лог развёртывания knowledge surfacer | active |
| `proactive_actions.log` | Лог выполненных проактивных действий | active |
| `telegram_config.md` | Конфиг Telegram-доставки | active |
| `interrupt_debug.log` | Лог отладки прерываний | archived |
| *(другие логи от cron и процессов)* | — | active |

---

## `notes/` — Заметки

| File | Purpose | Status |
|------|---------|--------|
| `browser-notes.md` | Заметки по browser-harness | archived |
| *(другие заметки)* | — | — |

---

## `reports/` — HTML-отчёты

| File | Purpose | Status |
|------|---------|--------|
| `adder.html` | Сгенерированный HTML | archived |
| `diapers_report.html` | HTML-отчёт | archived |
| `skills_report.html` | Отчёт по скиллам | archived |
| `ai-income-2026.html` | Отчёт по AI-доходам 2026 | archived |

---

## `trash/` — На удаление (временное хранение)

| File | Original Location | Reason |
|------|-------------------|--------|
| `nul` | корень | Zero-byte артефакт MSYS |

---

## Subdirectories (системные, не сортируются)

| Directory | Purpose |
|-----------|---------|
| `audio_cache/` | Кэш аудиофайлов |
| `bin/` | Бинарные файлы |
| `bootstrap-cache/` | Кэш загрузки |
| `browser-harness/` | Browser automation harness |
| `chrome-debug-profile/` | Chrome debug profile |
| `data/` | Данные (`.env`, lavra knowledge и т.д.) |
| `gateway-service/` | Gateway service файлы |
| `hermes-agent/` | Файлы агента Hermes |
| `hooks/` | Git hooks |
| `image_cache/` | Кэш изображений |
| `lsp/` | Language Server |
| `memories/` | Долговременная память агента |
| `ms-playwright/` | Playwright browser |
| `music_gen/` | Сгенерированная музыка |
| `node-global/` | Глобальные Node.js пакеты |
| `pairing/` | Pairing files |
| `pastes/` | Pastebin |
| `plans/` | Планы (`.hermes/plans/`) |
| `plugins/` | Плагины Hermes |
| `post_images/` | Изображения для постов |
| `projects/` | Проекты |
| `sandboxes/` | Песочницы |
| `sessions/` | Сессии |
| `skill-forge/` | Skill forge |
| `skills/` | Скиллы агента |
| `state-snapshots/` | Снимки состояния |
| `.hermes/` | Внутреннее состояние Hermes |

---

## Quick-Start: как пользоваться реестром

1. **Новый файл в корне** → напиши `scripts/`, `assets/`, `cache/` или `config/` — не оставляй сиротой
2. **После сортировки** → обнови `FILE_REGISTRY.md` (путь + статус)
3. **Перед удалением** → перемести в `trash/` минимум на 1 цикл
4. **Реестр = истина** — если файла нет в реестре, он не существует

---

## Cron Jobs Summary (20 активных)

| Job | Schedule | Type | Status |
|-----|----------|------|--------|
| event-trigger | every 2m | no_agent | ✅ active |
| proactive-executor | every 15m | no_agent | ✅ active |
| telegram-delivery | every 60m | no_agent | ✅ active |
| knowledge-surfacer | every 6h | no_agent | ✅ active |
| system-watcher | every 60m | no_agent | ✅ active |
| unified-system-cycle | every 2h | no_agent | ✅ active |
| nightly-self-analysis | 0 2 * * * | no_agent | ✅ active |
| morning-report | 0 8 * * * | no_agent | ✅ active |
| subconscious-loop | every 120m | no_agent | ✅ active |
| auto-fetch-sessions | every 60m | no_agent | ✅ active |
| dream-memory-consolidation | 0 3 * * * | no_agent | ✅ active |
| free-api-health-check | every 6h | no_agent | ✅ active |
| memory-consolidation | 0 3 * * * | no_agent | ✅ active |
| skill-evolution | 0 4 * * * | no_agent | ✅ active |
| self-assessment | 0 1 * * * | no_agent | ✅ active |
| update-runtime-context | 30 4 * * * | no_agent | ✅ active |
| cube-feeder | 15 4 * * * | no_agent | ✅ active |
| dimension-discovery | 45 4 * * * | no_agent | ✅ active |
| nightly-brain-scan | 0 3 * * * | no_agent | ✅ active |
| cube-session-ingester | 0 */6 * * * | no_agent | ✅ active |

---

*Реестр автоматически обновляется при сортировке. Последняя сортировка: 2026-06-07.*

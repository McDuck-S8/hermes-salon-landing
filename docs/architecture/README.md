# Hermes Agent — архитектурная карта (матрёшка)

Сгенерировано `scripts/generate_architecture.py` через `diagrams` (mingrammer) + Graphviz.

## Уровни

| Уровень | Файл | Описание |
|---|---|---|
| 1 — System Context | `hermes_arch_01_system_context.png` | Hermes и внешний мир: User, Telegram, GitHub, CPA, BrowserOS, RSS, YouTube, LLM |
| 2 — Pipelines | `hermes_arch_02_pipelines.png` | 5 контейнеров: Knowledge, Crystal, Self-Improvement, Action, Heartbeat |
| 3 — Components | `hermes_arch_03_components.png` | Ключевые скрипты: event_evolution, hermes_hooks, auto_recall, skill_manager, cron_manager |
| 4 — File Map | `hermes_arch_04_file_map.md` | Иерархия каталогов и ключевых файлов (mindmap) |

## Как перегенерировать

```bash
export PATH="$PATH:/d/Program Files/Graphviz/bin"
python scripts/generate_architecture.py
```

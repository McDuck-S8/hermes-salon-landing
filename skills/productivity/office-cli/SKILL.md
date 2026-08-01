---
name: office-cli
description: Create, read, edit, and proofread Office documents (.docx, .xlsx, .pptx) using OfficeCLI — single binary, no Office license needed. Replaces excel-author, pptx-author with one tool.
version: 1.0.0
author: Hermes Agent (adapted from iOfficeAI/OfficeCLI)
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [office, docx, xlsx, pptx, excel, word, powerpoint, documents]
    related_skills: [excel-author, cpa-landing-generator]
---

# OfficeCLI — Office Suite для AI агентов

OfficeCLI — это единый бинарник для работы с Word, Excel и PowerPoint.
**Не требует установленного Office** — всё делает сам.

## Установка

Установлено глобально через npm. Проверка:

```bash
officecli --version
# → 1.0.140
```

Есть также `npx @officecli/officecli <command>` если бинарник не в PATH.

## Стратегия работы

**L1 (read) → L2 (DOM edit) → L3 (raw XML)**. Всегда начинать с высокого уровня. 
Добавлять `--json` для структурированного вывода.

## Быстрый старт

### PowerPoint
```bash
officecli create slides.pptx
officecli add slides.pptx / --type slide --prop title="Q4 Report" --prop background=1A1A2E
officecli add slides.pptx '/slide[1]' --type shape --prop text="Revenue grew 25%"
```

### Word
```bash
officecli create report.docx
officecli add report.docx /body --type paragraph --prop text="Executive Summary" --prop style=Heading1
```

### Excel
```bash
officecli create data.xlsx
officecli set data.xlsx /Sheet1/A1 --prop value="Name" --prop bold=true
```

## Просмотр и инспекция

| Команда | Описание |
|---------|----------|
| `officecli view file.docx outline` | Структура документа |
| `officecli view file.docx stats` | Статистика |
| `officecli view file.docx issues` | Проблемы форматирования |
| `officecli view file.pptx html` | HTML-снимок (можно открыть в браузере) |
| `officecli get file.pptx '/slide[1]' --depth 1 --json` | Структурированные данные |

## Помощь (справка — не гадать!)

```bash
officecli help                           # Все команды
officecli help docx                      # Все элементы Word
officecli help docx paragraph            # Свойства параграфа
officecli help xlsx pivottable           # Сводные таблицы
officecli help pptx slide                # Слайды
```

## Режим резидента

OfficeCLI держит файл в памяти, пока редактируете:

```bash
officecli open report.docx       # Открыть в память
officecli set report.docx ...    # Быстрое редактирование
officecli close report.docx      # Сохранить и закрыть
```

## Замена excel-author

OfficeCLI заменяет старый `excel-author` (openpyxl). Преимущества:
- Формулы, стили, сводные таблицы — всё в одном бинарнике
- `officecli view file.xlsx issues` — проверка ошибок
- `officecli watch file.xlsx` — live preview
- Поддержка Chart, PivotTable, Conditional Formatting

## Релевантные подпроекты

См. официальный скилл: `curl -fsSL https://officecli.ai/SKILL.md`

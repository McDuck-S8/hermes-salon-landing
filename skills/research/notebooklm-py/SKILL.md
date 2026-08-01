---
name: notebooklm-py
description: >
  notebooklm-py — неофіційний Python API для Google NotebookLM (Gemini Notebook).
  Повний програмний доступ: створення ноутбуків, завантаження джерел,
  RAG-запити, генерація подкастів, mind maps, експорт.
  Інтегровано в Hermes як інструмент дослідника.
version: 1.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [notebooklm, gemini, research, rag, podcast]
---

# notebooklm-py — Google NotebookLM API для Hermes

## МАНДАТОРНЕ ВИКОРИСТАННЯ

**Якщо цей скіл встановлений — він має використовуватись.**  
Недостатньо згадати його у відповіді. Перед дослідженням:
1. Запустити `notebooklm auth login` (одноразово)
2. Створити ноутбук під тему
3. Додати джерела з web_search
4. Запитати `.ask()`
5. Зберегти результат

Якщо скіл не використано в дослідженні — це помилка старпома.

## Встановлення

```bash
pip install notebooklm-py
```

## CLI

```bash
python -m notebooklm.cli auth login
python -m notebooklm.cli notebook list
python -m notebooklm.cli notebook create "Назва"
python -m notebooklm.cli source add <notebook_id> <url|file>
python -m notebooklm.cli ask <notebook_id> "питання"
```

## Python API — основне

```python
from notebooklm import NotebookLMClient

client = NotebookLMClient()

# Створити ноутбук
nb = client.create_notebook("Назва")

# Додати джерело (PDF, URL, YouTube)
src = nb.add_source("https://example.com/doc.pdf")

# Запитати по джерелах
result = nb.ask("Які ключові висновки?")
print(result.text)
print(result.citations)

# Згенерувати подкаст
audio = nb.generate_audio_overview()
audio.download("podcast.mp3")

# Експорт у форматі
nb.export(format="markdown", path="./export/")
```

## Ключові можливості Hermes

| Дія | Як |
|---|---|
| Deep Research | `client.create_notebook("topic").add_research("запит", mode="deep")` |
| Knowledge → Skill | Згенерувати SKILL.md з результатів дослідження |
| RAG-чат по документах | `.ask("питання")` з цитатами |
| Пакетний експорт | `.export_all()` |

## Інтеграція з Hermes

```python
from hermes_tools import web_search, terminal
from notebooklm import NotebookLMClient

client = NotebookLMClient()
nb = client.create_notebook("Дослідження")

# Додати знайдені URL
urls = web_search("тема")["data"]["web"]
for r in urls:
    nb.add_source(r["url"])

# Отримати синтез
result = nb.ask("Зроби висновки")
```

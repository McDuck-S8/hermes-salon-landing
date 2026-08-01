# ADR-003: Content Locking Video Pipeline — Zero API dependencies via FFmpeg + system fonts

**Status:** Accepted
**Дата:** 2026-07-21
**Supersedes:** ADR-002

---

## Context

Требовалось: написать конвейер генерации 9:16 Shorts-видео для Content Locking (Free V-Bucks, Free Robux и т.д.) для 5 тем × 3 вариации = 15 видео.

Проблемы, возникшие при реализации:
1. **Отсутствие шрифта** — Roboto-Bold.ttf не найден, скачивание с Google Fonts сорвалось (SSL error: EOF)
2. **Drive letter в path** — Windows-пути с двоеточием (`C:/Windows/Fonts/`) ломают парсер FFmpeg drawtext, т.к. `:` — разделитель опций фильтра
3. **Tempfile paths** — `textfile=` с путём к временному файлу имел ту же проблему

## Decision

1. **Font:** копировать system Arial (arial.ttf) в `scripts/assets/Roboto-Bold.ttf` при запуске — гарантированно работает offline
2. **Путь:** использовать `os.path.relpath()` от корня проекта — относительные пути без drive letter
3. **Text:** использовать `text=` вместо `textfile=` — тексты тем (Free V-Bucks и т.п.) не содержат `:` или других спецсимволов, парсятся корректно
4. **FFmpeg:** `preset=ultrafast`, `libx264`, `lavfi color` для фона — 10-секундное видео = 18KB

## Consequences

**Плюсы:**
- Zero API dependencies — не нужен ElevenLabs, Pexels, интернет
- 15 видео за < 2 минут (утверждено: 15/15 успешно)
- Размер видео ~18KB → можно постить в Telegram без сжатия
- FFmpeg + Python — весь стек уже есть в системе

**Минусы:**
- Arial вместо Roboto — менее современно визуально (можно скачать шрифт вручную)
- Нет voice-over, нет stock footage — только текст на цветном фоне
- gTTS не использован (офлайн TTS в pyttsx3 требует pywin32)

**Что дальше:**
- Можно добавить pexels stock footage как опциональный фон
- Можно добавить voice-over через gTTS (если нужен голос)
- Сейчас — минимально работающий MVP: берём, постим, тестируем конверсию

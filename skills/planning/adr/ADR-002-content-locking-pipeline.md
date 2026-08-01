# ADR-002: Content Locking Video Pipeline — FFmpeg + static assets, zero API deps

**Status:** Accepted
**Дата:** 2026-07-21
**Supersedes:** none

---

## Context

Задача: написать скрипт генерации видео для Content Locking (Free V-Bucks, Free Robux, Free GTA Money, Netflix Generator, Spotify Premium).

Требования:
- 9:16 vertical, 15-30 sec, с CTA overlay "Free → Link in bio"
- Батч: 25 видео за запуск (5 тем × 5 вариаций)
- Интеграция с FFmpeg и существующим content-pipeline

Альтернативы:
1. **FFmpeg + статические ассеты (фон, текст, оверлей)** — макс. контроль, нет API-зависимостей
2. **ElevenLabs TTS API** — качественный голос, но нужен API-ключ и интернет
3. **Pexels/Pixabay API** — стоковые видео, но нужен API-ключ
4. **CapCut API** — облачный монтаж, но закрытый

## Decision

Гибридный подход:
- **FFmpeg** — основной конвейер (наложение текста, обрезка, склейка)
- **Статические ассеты** в `assets/content-locking/` — фоны, шрифты, оверлеи (zero API deps)
- **gTTS/pyttsx3** — офлайн TTS для первого MVP (без ElevenLabs)
- **Pexels API** — опционально, если нужен живой фон

Это даёт работающий pipeline без внешних зависимостей.

## Consequences

- Плюс: работает офлайн, нет API-лимитов
- Плюс: 25 видео за ~2 минуты (чистый FFmpeg)
- Минус: gTTS звучит хуже ElevenLabs (но для MVP норм)
- Минус: нужны статические ассеты (фоны найти самому)

**Следующий ADR:** ADR-003 о структуре ассетов и шаблонов.

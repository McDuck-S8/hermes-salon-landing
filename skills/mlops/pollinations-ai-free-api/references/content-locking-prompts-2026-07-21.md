# Content Locking — Проверенные промпты Pollinations.ai FLUX (9:16)

## Дата: 2026-07-21
## Настройки: FLUX model, 720×1280, nologo=true, User-Agent: Hermes-Agent/1.0

## Результаты

| # | Prompt | Размер | Время | Seed |
|---|--------|--------|-------|------|
| 1 | "luxury lifestyle man in suit counting stacks of hundred dollar bills on marble table cinematic lighting photorealistic" | 77,321 B | ~15s | 42 |
| 2 | "young successful businessman looking at huge yacht from balcony modern harbor sunset luxury lifestyle cinematic" | 66,201 B | ~20s | 50 |
| 3 | "crypto trader celebrating in front of multiple screens showing Bitcoin chart green candles going up dramatic lighting" | 81,132 B | ~18s | 51 |
| 4 | "luxury sports car red Ferrari parked in front of modern glass mansion sunset golden hour cinematic 8K" | 86,477 B | ~22s | 52 |
| 5 | "attractive couple laughing holding champagne glasses infinity pool overlooking ocean sunset luxury lifestyle candid" | 64,376 B | ~25s | 53 |

## Rate Limiting

- **1-й запрос:** всегда успешен
- **2-й запрос (без паузы):** "Remote end closed connection without response"
- **3-й+ запрос (без паузы):** HTTP 429 Too Many Requests
- **Решение:** `time.sleep(10)` между запросами — стабильно работает
- **Retry при 429:** пауза 30с, повтор — успешен

## Выводы

- Pollinations FLUX даёт качественные, реальные AI-изображения (не "фон с надписью")
- Для видео нужно 5+ кадров → FFmpeg assembly с crossfade
- 5 кадров = ~15 сек видео, ~1.3 MB
- Подходит для content locking CPA: wealth, crypto, luxury lifestyle ниши

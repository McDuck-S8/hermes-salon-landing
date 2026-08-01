# Content Monetization Pipeline

## Concept
Pipeline генерации контента из Knowledge Cube → в готовые форматы для публикации:
- Telegram-каналы (посты)
- Dzen (статьи)  
- Лендинги (HTML)
- Соцсети

## Architecture
```
Knowledge Cube (данные)
  └─► Content Selector (какие темы сегодня)
       └─► Generator (AI → контент)
            ├─► Telegram Publisher
            ├─► Dzen Publisher  
            └─► Web Publisher (HTML)
```

## Pipeline Flow
1. **Selector** — выбирает N тем из Cube по приоритету (trending, fresh, high-value)
2. **Generator** — забирает данные из Cube по теме, генерирует текст
3. **Publisher** — форматирует под площадку и публикует

## Status
🔴 Empty — needs BUILD

## Priority
Средний. После salon-bot (деплой → деньги).

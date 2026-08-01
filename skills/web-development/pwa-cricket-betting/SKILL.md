---
name: pwa-cricket-betting
description: 'Генерация PWA (Progressive Web App) под крикет/беттинг на GitHub Pages для affiliate-трафика. Альтернатива PWA.Market — бесплатно.'
domain: web-development
keywords: [pwa, cricket, betting, github-pages, affiliate, india, manifest, service-worker]
---

# PWA Cricket Betting — Генератор

## Назначение
Создаёт PWA-приложение под крикет-беттинг для Индии, которое хостится на GitHub Pages бесплатно. Альтернатива PWA.Market когда нет бюджета.

## Структура проекта
```
projects/pwa-{name}/
├── index.html          # Лендинг под крикет + оффер
├── manifest.json       # PWA manifest (standalone, icons)
├── sw.js               # Service worker (offline cache + push)
├── icons/              # PNG иконки 72-512px
```

## Ключевые элементы

### index.html
- Тема: крикет (зелёный + тёмный фон, #00ff88 accent)
- Live scores (заглушка), upcoming matches, матч-центр
- **CTA-кнопка** — ведёт на оффер (1xBet/1win/Mostbet через referrer)
- Install banner (beforeinstallprompt) — выглядит как нативное приложение
- push-уведомления для возврата

### manifest.json
- `display: standalone` — убирает браузерную строку
- `theme_color: #1a1a2e`, `background_color: #0f0f23`
- Icons: 72, 96, 128, 144, 152, 192, 384, 512 (maskable)
- Shortcuts: "Live Scores", "Upcoming Matches"

### sw.js
- Cache-first для статики (icons, manifest)
- Network-first для навигации (fallback → index.html)
- Push-уведомления + обработка клика
- Self-skip-waiting + claim

## Параметры для замены
| Параметр | Где менять |
|---|---|
| Оффер-ссылка | index.html: `.btn` href |
| Название | manifest.json: `name`, `short_name` |
| Цвета | index.html: CSS variables |
| Команды матча | index.html: match cards |
| Telegram Mini App версия | projects/tg-{name}-app/index.html |

## Процесс создания
1. `skill_view(name='pwa-cricket-betting')` — загрузить этот навык
2. Создать проект: `execute_code` с `write_file` для index.html, manifest.json, sw.js
3. Иконки: использовать SVG-to-PNG конвертер или цветные заглушки
4. Проверка: `python -c "import json; json.loads(open('manifest.json').read())"`
5. Деплой: GitHub Pages из корня проекта

## Альтернативы
- **PWA.Market** — $25/мес, клоакинг, сплиты, готовые дизайны
- **Telegram Mini App** — не требует установки, работает в Telegram
- **Tilda** — для лендинга без PWA-фич

## Pitfalls
- GitHub Pages не поддерживает server-side редиректы — service worker должен обрабатывать навигацию
- Иконки нужны всех размеров — браузер без 192px иконки не показывает Install prompt
- Service worker регистрируется ТОЛЬКО через HTTPS (GitHub Pages — OK)
- Push-уведомления требуют VAPID-ключей — не работают без сервера

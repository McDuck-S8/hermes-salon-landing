---
name: tg-mini-app-betting
description: 'Генерация Telegram Mini App под крикет/беттинг. Работает как веб-приложение внутри Telegram — не требует установки, быстрый запуск.'
domain: web-development
keywords: [telegram, mini-app, betting, cricket, tg-webapp, tma]
---

# Telegram Mini App Betting — Генератор

## Назначение
Создаёт Telegram Mini App для крикет-беттинга. Пользователь открывает через кнопку в боте/канале — моментальный доступ, без установки.

## Когда использовать
- Трафик из **Telegram** (каналы, боты, группы)
- Нужно быстрое решение без PWA-установки
- Аудитория уже в Telegram (Индия — 950M+ пользователей)

## Структура
```
projects/tg-{name}-app/
├── index.html          # Mini App лендинг
└── (хостится на GitHub Pages или VPS)
```

## Технические требования

### index.html
- **Обязательно** подключить: `<script src="https://telegram.org/js/telegram-web-app.js"></script>`
- Использовать CSS-переменные Telegram: `var(--tg-theme-bg-color)`, `var(--tg-theme-text-color)`, `var(--tg-theme-button-color)`
- `tg.expand()` — развернуть на весь экран
- `tg.ready()` — сообщить Telegram что приложение загружено

### Telegram WebApp API
| Метод | Назначение |
|---|---|
| `tg.expand()` | На весь экран |
| `tg.ready()` | Завершение загрузки |
| `tg.openLink(url)` | Открыть ссылку (оффер) внутри Telegram |
| `tg.showPopup({...})` | Показать popup |
| `tg.enableClosingConfirmation()` | Предупреждение при закрытии |
| `tg.HapticFeedback.impactOccurred('medium')` | Тактильный отклик |

### Структура страницы
- Заголовок: Match Predictions / Live Scores
- Карточки матчей: команды, коэффициенты, прогнозы
- **CTA-кнопка** → `tg.openLink(offer_url)` — переход на оффер
- Попап подписки на уведомления

## Процесс создания
1. Создать бота через @BotFather — включить Mini App режим
2. Загрузить HTML на GitHub Pages (бесплатно)
3. Указать URL Mini App в @BotFather → Bot Settings → Mini App
4. Разместить ссылку/кнопку в Telegram канале/боте

## Альтернативы
- **PWA** — для установки на экран, работает вне Telegram
- **Tilda** — статический лендинг, без интеграции с Telegram API

## Pitfalls
- `tg.openLink` открывает в браузере Telegram — некоторые блокировщики режут
- Mini App НЕ работает в Telegram Web (только мобильные приложения)
- Высота окна меняется — используй `tg.expand()` сразу
- Telegram кэширует Mini App — обновления не видны сразу (очистка кэша через настройки разработчика)

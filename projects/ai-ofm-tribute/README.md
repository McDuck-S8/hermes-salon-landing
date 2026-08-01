# AI OFM Tribute — Prototype

**Автономный генератор AI-контента** для Telegram-канала с Tribute-монетизацией.

## Компоненты

| Компонент | Статус |
|-----------|--------|
| Генератор изображений (Pollinations.ai) | ✅ Бесплатно, без API ключа |
| Tribute аккаунт / Wallet Pay | ⏳ Настройка |
| Telegram-канал | ⏳ Создать |
| Cron-автогенерация (каждые 2ч) | ✅ Готов |
| Премодерация | ⏳ После запуска |

## Быстрый старт

```bash
# Генерация 5 изображений в стиле fantasy
python scripts/generate.py --count 5 --style fantasy

# Генерация в стиле anime
python scripts/generate.py --count 5 --style anime

# Просмотр последней сгенерированной сессии
python scripts/preview.py
```

## Стили

- `fantasy` — фэнтези-портреты (эльфийки, волшебницы, феи)
- `anime` — аниме-арт
- `realistic` — фотореалистичные портреты

## Генерация изображений

Используется **Pollinations.ai** — полностью бесплатный сервис:
- Без регистрации и API ключа
- URL-based API: `https://image.pollinations.ai/prompt/...`
- Модели: flux, seedream, turbo, nanobanana
- Нет лимитов на генерацию

## Tribute + Wallet Pay

Схема монетизации:
1. Подписчик платит через Tribute (Wallet Pay)
2. Получает доступ к закрытому Telegram-каналу
3. Канал ежедневно пополняется новыми AI-изображениями

## Структура проекта

```
ai-ofm-tribute/
├── config.yaml                 # Конфигурация
├── tribute-setup.md            # Инструкция по Tribute
├── scripts/
│   ├── generate.py             # Генератор контента
│   ├── preview.py              # Просмотр сессий
│   └── cron.sh                 # Cron-автогенерация
└── content/
    └── sessions/
        ├── 01/                 # Сессия 1
        ├── 02/                 # Сессия 2
        └── .../
```

## Тестовые сессии

```bash
ls content/sessions/
# Каждая сессия содержит manifest.json + *.jpg + preview.html
```

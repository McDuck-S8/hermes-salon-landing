# Sales Machine — Международная Lead Generation & Sales Automation

## Архитектура

```
lead_finder.py ──> demo_builder.py ──> closer.py ──> field_agent.py
    │                   │                  │               │
    ▼                   ▼                  ▼               ▼
Google Maps        HTML Landing        Telegram        Field Agent
Yandex Maps        GitHub Pages        WhatsApp        (человек)
2GIS              (5 мин deploy)       VK / OK         Close Script
Instagram                              Email
Facebook
```

## Модули

### lead_finder.py
- Сканирует Google Maps для 7+ стран (Украина, Черногория, Сербия, Россия, Хорватия)
- Собирает: название, телефон, адрес, рейтинг, категории, сайт
- Сохраняет в SQLite (clients.db)
- Определяет need_landing_page (если сайта нет или он плохой)

### demo_builder.py
- Генерирует HTML landing page для 5 ниш:
  - salon, restaurant, hotel, auto_service, clinic
- Поддерживает 3 языка: ru, en, sr
- Адаптивные, современные, с CTA
- Deploy на GitHub Pages (опционально)

### closer.py
- Интеграция с Composio (Telegram, WhatsApp, VK, OK, Gmail)
- Sales scripts на 3 языках с обработкой возражений
- Отслеживание ответов
- Прогрев лидов до передачи агенту

### field_agent.py
- Регистрация полевых агентов
- Назначение тёплых лидов
- Скрипты закрытия сделки (ru/sr)
- Dashboard агента

## Установка

```bash
pip install -r requirements.txt
```

## Использование

```bash
# Сканировать Google Maps для Будвы
python main.py scan budva_restaurants --lang en

# Посмотреть лиды
python main.py leads --status new
python main.py leads --needs-lp

# Сгенерировать демо для лида
python main.py demo <lead_id> --niche salon --lang ru

# Dashboard
python main.py dashboard

# Управление агентами
python main.py agent register --name "Milos" --phone "+382..." --location "Budva"
python main.py agent list
python main.py agent dashboard --agent-id <id>
```

## База данных (clients.db)

| Таблица | Назначение |
|---|---|
| clients | Лиды (название, телефон, адрес, рейтинг) |
| demos | Сгенерированные лендинги |
| conversations | История сообщений |
| deals | Сделки (сумма, статус) |
| field_agents | Полевые агенты |
| campaigns | Активные кампании |

## Пресеты для сканирования

### Киев (Позняки)
- `kiev_salons` — салоны красоты
- `kiev_dental` — стоматологии
- `kiev_fitness` — фитнес клубы
- `kiev_restaurants` — рестораны

### Черногория (Будва)
- `budva_restaurants` — рестораны
- `budva_hotels` — отели
- `budva_salons` — салоны красоты
- `budva_clinics` — клиники

### Другие
- `belgrade_salons` — Белград
- `moscow_salons` — Москва
- `template_salon` — шаблон для любого города

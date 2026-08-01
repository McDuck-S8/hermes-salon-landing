# Auto Microsites Generator

## Что это
Генератор лендингов для малого бизнеса. Вход: JSON с данными → Выход: готовый HTML-сайт.

## Быстрый старт

```bash
# Сгенерировать демо-сайт
python main.py "Мой Бизнес"

# Сгенерировать из конфига
python main.py --from samples/barbershop.json

# Посмотреть что сгенерировано
python main.py --list
```

## Структура

```
auto-microsites/
├── main.py              # Генератор (вход JSON → выход HTML)
├── deploy.py            # Деплой на GitHub Pages (бесплатно)
├── templates/
│   └── business.html    # Шаблон лендинга
├── samples/
│   ├── barbershop.json  # Пример: барбершоп
│   └── dental.json      # Пример: стоматология
├── generated/           # Сгенерированные сайты
│   ├── barbershop-akcent/index.html
│   └── dental-smile/index.html
└── OUTREACH.md          # Шаблон продаж бизнесу
```

## Формат конфига

```json
{
    "project_name": "my-business",
    "business_name": "Название",
    "tagline": "Слоган",
    "phone": "+7 (978) 123-45-67",
    "address": "г. Симферополь, ул. Примерная, 1",
    "working_hours": "Пн-Вс: 09:00-21:00",
    "color_primary": "#2563eb",
    "color_accent": "#f59e0b",
    "cta_text": "Позвонить",
    "about": "Описание бизнеса...",
    "services": [
        {"name": "Услуга", "price": "от 1 000 ₽", "description": "Описание"}
    ],
    "seo_title": "Название — Симферополь",
    "seo_description": "Краткое описание для поисковика"
}
```

## Деплой

```bash
# Деплой на GitHub Pages (бесплатно)
python deploy.py barbershop-akcent

# Результат: https://user.github.io/barbershop-akcent-site/
```

## Бизнес-модель

1. Найти бизнес в Симферополе без сайта (Яндекс.Карты, 2ГИС)
2. Сгенерировать демо-сайт (30 секунд)
3. Отправить демо владельцу
4. Продать за 7 000-25 000₽

Пакеты: см. `../site-for-biz/PACKAGES.md`

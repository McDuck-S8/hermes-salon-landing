# LUMIÈRE — Премиум салон красоты

Веб-сайт + Telegram-бот для салона красоты.

## Структура

```
salon-lumiere/
├── index.html              # Лендинг (Tailwind CSS, glassmorphism, animations)
├── salon_bot.py            # Telegram-бот (aiogram 3.x, FSM, admin panel)
├── robots.txt              # SEO
├── sitemap.xml             # SEO
├── assets/
│   ├── fonts/              # Google Fonts (Playfair Display)
│   ├── logo.png            # Логотип (800x800)
│   ├── photo_*.png         # 5 фото услуг (800x1000)
│   ├── thumbnail.png       # YouTube thumbnail (1280x720)
│   ├── subtitle_overlay.png # Оверлей субтитров
│   ├── og-image.png        # Open Graph (1200x630)
│   ├── favicon.ico         # Favicon
│   ├── salon_raw.mp4       # Исходное видео
│   ├── salon_clip_15s.mp4  # 15-сек клип
│   └── salon_final_15s.mp4 # 15-сек с субтитрами
└── data/
    ├── bookings.json       # Записи клиентов
    └── bot.log             # Лог бота
```

## Запуск

### Лендинг
Открыть `index.html` в браузере.

### Бот
```bash
export SALON_BOT_TOKEN="ваш_токен"
python salon_bot.py
```

### Тестовый режим
```bash
python salon_bot.py  # без токена — демо
```

## Технологии

- **Frontend:** Tailwind CSS CDN, Google Fonts, IntersectionObserver animations
- **Bot:** aiogram 3.x, FSM (Finite State Machine), JSON storage
- **Images:** Pillow (Python) — генерация логотипов, фото, thumbnail
- **Video:** ffmpeg — обрезка, субтитры, оверлеи
- **Шрифты:** Playfair Display (заголовки), Inter (текст), Georgia (fallback)

## Услуги

| Услуга | Цена | Время |
|--------|------|-------|
| Стрижка и укладка | 2 500 ₽ | 60 мин |
| Окрашивание | 4 500 ₽ | 120 мин |
| Маникюр | 1 800 ₽ | 90 мин |
| Макияж | 3 000 ₽ | 45 мин |
| Ламинирование бровей | 1 500 ₽ | 40 мин |
| Комплекс «Превращение» | 9 900 ₽ | 4 часа |

## Дизайн

- Glassmorphism (frosted glass cards)
- Scroll-reveal анимации (IntersectionObserver)
- Cursor glow effect
- Gold gradient palette
- Mobile-first адаптивность
- Dark/light sections

## Контакты

- Telegram: @lumiere_salon
- Телефон: +7 (495) 123-45-67
- Адрес: ул. Красоты, 42, Москва

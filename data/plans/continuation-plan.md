# План продолжения — Hermes Project

> Создан: 2026-06-12
> Приоритет: Earnings > Projects > Skills

---

## Сейчас (следующая сессия)

### 1. Собрать базу 20 салонов-лидов
- [ ] Найти салоны красоты в Симферополе (2GIS, Google Maps, Instagram)
- [ ] Собрать в Knowledge Cube домен `salon-leads`: название, контакт, телефон, соцсети
- [ ] Разбить по статусу: lead → contacted → proposal → negotiation → closed

### 2. Создать шаблон коммерческого предложения
- [ ] HTML-версия КП (под стиль business-plan.html)
- [ ] Текст: проблема → решение → цена → выгода → отзыв → CTA
- [ ] Адаптировать под beauty-сферу

### 3. Развернуть salon-bot
- [ ] Получить токен у @BotFather
- [ ] Настроить .env (BOT_TOKEN, PROXY, SUPERADMIN_ID)
- [ ] Запустить бота (python main.py)
- [ ] Проверить: /start → бронирование → админка

---

## Эта неделя

### 4. Первый контакт с клиентом
- [ ] Разослать КП 5 салонам
- [ ] Показать демо бота (живой экземпляр)
- [ ] Закрыть gaps в коде под требования клиента

### 5. ЮKassa / приём платежей
- [ ] Зарегистрироваться в ЮKassa
- [ ] Настроить webhook для оплаты
- [ ] Протестировать платежный поток

---

## Месяц 1

### 6. Первые деньги
- [ ] Первый платящий клиент
- [ ] Задокументировать процесс «лид→деньги» в Cube
- [ ] Создать reusable workflow для новых установок

### 7. Content Monetization Pipeline
- [ ] Реализовать Selector (выбор тем из Cube)
- [ ] Реализовать Generator (AI → текст через Hermes)
- [ ] Реализовать Publisher (Telegram/Dzen/HTML)
- [ ] Запустить авто-публикацию в Telegram-канал

### 8. Auto Microsites Generator
- [ ] Реализовать Jinja2 шаблоны (business, product, service)
- [ ] Подключить Knowledge Cube как источник данных
- [ ] Генерация landing под каждый проект

---

## Месяц 2+

### 9. Масштабирование
- [ ] Telegram Mini App для salon-bot (выше чек)
- [ ] Multi-salon dashboard (админка на несколько салонов)
- [ ] Партнёрства с бьюти-школами
- [ ] crimea-bots: рефакторинг → единый мульти-бот

### 10. Инфраструктура
- [ ] content-monetization → полный pipeline
- [ ] auto-microsites → полный генератор
- [ ] ai-education-bot → ревью + деплой

---

## Текущее состояние проектов

| Проект | Статус | Что нужно |
|--------|--------|-----------|
| **salon-bot** | 🟢 Готов (9/10) | Деплой + клиент |
| **business-plan** | ✅ Готов | landing page HTML |
| **crimea-bots** | 🟡 Активен | Рефакторинг |
| **content-monetization** | 🟡 Скелет | Реализация |
| **auto-microsites** | 🟡 Скелет | Реализация |
| **ai-education-bot** | 🟡 demo_bot.py | Ревью + деплой |
| **agentmemory** | 🟢 Работает | Поддержка |
| **entity-engine** | 🟢 Работает | Поддержка |

## Метрики цели

- Projects with running code: 3/8 → **6/8**
- Projects making money: 0/8 → **3/8**
- First paying client: ❌ → ✅

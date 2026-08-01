# AI Job Search — Крым и Симферополь (v2)

Адаптация [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) для рынка труда Крыма и Симферополя.

## Особенности

- **Поиск вакансий** на hh.ru по городам Крыма (Симферополь, Севастополь, Ялта, Евпатория, Керчь, Феодосия)
- **Профиль соискателя** — интерактивная настройка и хранение в JSON
- **Оценка вакансий** — сравнение вакансии с вашим профилем по навыкам, зарплате, ролям
- **Шаблоны CV** — LaTeX-шаблоны для российского рынка, автозаполнение из профиля
- **Сопроводительные письма** — шаблоны и генерация
- **Зарплатные ориентиры** — база зарплат по Крыму для 40+ профессий
- **Обзор рынка** — дашборд с ключевой информацией

## Структура

```
crimea-job-search/
├── crimea_assistant.py      # Главный оркестратор (все команды)
├── hhru_crimea.py           # CLI для поиска на hh.ru
├── setup_profile.py         # Интерактивная настройка профиля
├── fill_cv.py               # Заполнение шаблонов из профиля
├── salary_crimea.py         # Зарплатные ориентиры
├── salary_data.json         # База зарплат (авто-создаётся)
├── candidate_profile.json   # Ваш профиль (создаётся setup)
├── cv/
│   ├── template.tex         # Шаблон CV (LaTeX)
│   └── output.tex           # Сгенерированное CV
├── cover_letters/
│   ├── template.tex         # Шаблон сопроводительного письма
│   └── output.tex           # Сгенерированное письмо
└── cache/                   # Кэш поиска
```

## Установка

Проект использует только стандартную библиотеку Python (3.10+). Никаких дополнительных зависимостей не требуется.

Для компиляции PDF из LaTeX нужен XeLaTeX:
- **Windows**: установите [MiKTeX](https://miktex.org/) или [TeX Live](https://tug.org/texlive/)
- **Linux**: `sudo apt install texlive-xetex texlive-lang-cyrillic`
- **macOS**: `brew install --cask mactex`

## Использование

### Быстрый старт

```bash
# 1. Настройка профиля
python crimea_assistant.py setup

# 2. Поиск вакансий
python crimea_assistant.py search -q "python разработчик"
python crimea_assistant.py search -q "водитель" -a simferopol
python crimea_assistant.py search -q "продавец" --salary 30000-60000

# 3. Детальный просмотр и оценка
python crimea_assistant.py evaluate --vacancy-id 12345678

# 4. Генерация CV
python crimea_assistant.py generate-cv --compile

# 5. Сопроводительное письмо
python crimea_assistant.py generate-letter -v "Python разработчик" -c "Компания"
```

### Поиск по городам

```bash
# Весь Крым (по умолчанию)
python hhru_crimea.py search -q "python" -a crimea

# Конкретный город
python hhru_crimea.py search -q "программист" -a simferopol
python hhru_crimea.py search -q "администратор" -a yalta
python hhru_crimea.py search -q "строитель" -a sevastopol
```

### Зарплатные ориентиры

```bash
# Поиск по должности
python salary_crimea.py --role "Программист"

# Весь список
python salary_crimea.py --list-all

# В JSON
python salary_crimea.py --role "Водитель" --json
```

### Работа с профилем

```bash
# Полная настройка
python setup_profile.py

# Обновить только раздел
python setup_profile.py --section skills

# Показать профиль
python crimea_assistant.py profile
```

## Зарплатные ориентиры (Крым, 2025-2026)

| Должность | Мин | Средняя | Макс |
|-----------|-----|---------|------|
| Программист Python | 60 000 ₽ | 110 000 ₽ | 180 000 ₽ |
| Программист (удалённо) | 80 000 ₽ | 150 000 ₽ | 300 000 ₽ |
| Бухгалтер | 30 000 ₽ | 50 000 ₽ | 80 000 ₽ |
| Менеджер по продажам | 25 000 ₽ | 50 000 ₽ | 100 000 ₽ |
| Водитель | 30 000 ₽ | 50 000 ₽ | 80 000 ₽ |
| Продавец | 20 000 ₽ | 35 000 ₽ | 50 000 ₽ |
| Врач | 40 000 ₽ | 70 000 ₽ | 120 000 ₽ |

Полный список: `python salary_crimea.py --list-all`

## Платформы для поиска работы в Крыму

| Платформа | URL | Примечание |
|-----------|-----|------------|
| hh.ru | https://simferopol.hh.ru | Основная база |
| Zarplata.ru | https://zarplata.ru | Хороший охват Крыма |
| SuperJob | https://superjob.ru | Есть регион Крым |
| Trud.com | https://crimea.trud.com | Крымский раздел |
| GorodRabot | https://gorodrabot.ru | Региональные вакансии |

## Как это работает

1. **Настройка профиля** — вводите свои данные (образование, опыт, навыки, предпочтения)
2. **Поиск** — hhru_crimea.py ищет вакансии через публичное API hh.ru
3. **Оценка** — crimea_assistant.py сравнивает вакансию с вашим профилем
4. **Генерация** — fill_cv.py заполняет LaTeX-шаблоны данными из профиля

## Оригинальный проект

Вдохновлено [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) — AI-агент для поиска работы на базе Claude Code.
Адаптировано для российского рынка, Python, Hermes Agent.

## Лицензия

MIT

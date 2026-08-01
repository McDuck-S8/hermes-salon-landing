---
name: tiktok-account-farm
description: "Full-stack TikTok account farm — создание, прогрев, постинг, anti-detect управление фермой аккаунтов. Интеграция с ghost-surfer и posting.py для масштабного залива трафика."
tags: [tiktok, account-farm, automation, cpa, traffic-source, ghost-surfer]
related_skills: [ghost-surfer, arbitrage-execution, finance/arbitrage-execution, content-pipeline, cpa-video-pipeline]
version: "1.2.0"
---

# TikTok Account Farm — Ферма аккаунтов TikTok

## Цель
Создать устойчивую ферму аккаунтов TikTok для залива CPA/арбитражного трафика. Решает проблему банов и нехватки аккаунтов — автоматическое создание, прогрев, постинг с сохранением anti-detect мер.

## ФОРМАТ: IMMEDIATE NEXT ACTION
Принцип, установленный пользователем 2026-07-21:

> **Каждый план/документ для пользователя должен начинаться с блока IMMEDIATE NEXT ACTION.**
> Пользователь не хочет видеть стратегию на 14 дней без конкретных действий на сегодня.
> Первое что он видит — 2-3 конкретных дела: что открыть, где зарегиться, сколько времени займёт, сколько стоит.

Формат для любого развёрнутого плана:
```
IMMEDIATE NEXT ACTION
#1: [действие] — [ссылка] — [время]
#2: [действие] — [ссылка] — [время]
#3: [действие] — [ссылка] — [время]
```
Этот блок идёт ПЕРЕД анализом, байесом, таблицами и стратегией.

---

## Архитектура: 5 Модулей

### 1. ACCOUNT CREATION (Создание аккаунтов)
**Способы регистрации (в порядке надёжности):**

| Метод | Надёжность | Стоимость | Сложность |
|-------|-----------|-----------|-----------|
| Email (mail.ru/outlook/gmail) | Средняя | $0 | Низкая |
| Phone (5sim/SMS-activate) | Высокая | $0.05-0.30 | Средняя |
| Phone (SIM-карты US) | Очень высокая | $5-10/карта | Высокая |
| Cloud phone (Geelark) | Высокая | $3-5/мес | Средняя |

**Требования к окружению на аккаунт:**
- Уникальный fingerprint (Canvas, WebGL, AudioContext, navigator, screen)
- Привязка к резиденциальному прокси IP (4G/5G mobile preferred)
- Изоляция: один аккаунт = один browser context / emulator instance
- Без SIM-карты в устройстве если IP не совпадает с MCC страны

### 2. ACCOUNT WARMUP (Прогрев аккаунтов)
**Цикл прогрева (7-14 дней до боевого постинга):**

```
День 1-3: Ручной просмотр ленты 15-30 мин/день → формирование FYP
День 3-7: Полуавтоматический прогрев (Voice Control / скрипты)
  - 30-60 мин/день
  - Actions: swipe, like, save, follow, comment
  - Распределение: swipe 60%, like 20%, save 10%, follow 7%, comment 3%
  - Интервал между действиями: 15-45 сек (логарифмическое распределение)
День 7-14: Поддержание активности 15-30 мин/день
```

**Альтернатива: купить прогретый аккаунт**
Байесовский анализ (2026-07-21) показывает что покупка аккаунта имеет преимущество:

| Стратегия | P(успех) | До первого $ | Стоимость |
|-----------|---------|-------------|-----------|
| Свой прогрев 14 дней | 16% | 21-30 дней | $24-97 |
| Купить + 5 дней доводки | **36%** | **10-14 дней** | $49-105 |

Где купить (проверено 2026-07-21 через BrowserOS):

| Маркетплейс | Цена | Escrow | Примечание |
|------------|------|--------|-----------|
| **Fameswap** | $40-70 (1K-10K) | ✅ Escrow | 🔵 Основной. Промо KUMO = 50% off Premium |
| **PlayerUp** | от $18 (5K) до $99 (10-50K монетиз.) | ✅ Middleman | 🟢 Проверен — 41 объявление. Самый дешёвый! |
| **Swapd (SWAPD)** | Форумные цены | ✅ Escrow | 🟡 Форум с верификацией продавцов |
| **EpicNPC** | от $80 | Middleman ($4.95+6%) | 🟡 Принимают крипту |

- **PlayerUp** — лучший для 1 аккаунта ($18 за 5K followers vs $40-70 на Fameswap)
- **Telegram каналы** (риск скама): @usapvapoint — используй только с escrow

**После покупки:**
1. Сменить пароль
2. Сменить 2FA
3. Сменить recovery email
4. Не менять аватар/имя 3 дня
5. Добавить свой мобильный прокси
6. 5 дней доводки (лайки, скролл, комменты)

**Критические ошибки при покупке:**
- Не плати напрямую продавцу — только escrow
- $5-10 за "2K подписчиков" = 100% скам
- Проверь views последних 10-20 видео, не только подписчиков
- 100K followers + 200 views/video = мёртвый аккаунт

**3 подхода к прогреву (от безопасного к быстрому):**

| Подход | Инструмент | Плюсы | Минусы | Интеграция с Hermes |
|--------|-----------|-------|--------|---------------------|
| **iOS Voice Control** | l-portet/tiktok-warmup-bot (Node.js) | Нативный, не jailbreak, сложно детектить | Нужны iPhone, ограниченный контроль | Cron запускает Node.js скрипты через SSH к iOS |
| **Android ADB** | Hormold/tiktok-warmup (TypeScript), mantotan/mcp-mobile-agent | Масштабируется на эмуляторы, дешёво | ADB может детектиться, нужно больше anti-detect | Terminal + ADB через Hermes |
| **Desktop Playwright** | Ghost-surfer TikTokPoster | Уже есть в Hermes, быстро развернуть | Большой риск детекта браузера | posting.py уже есть, нужен рефакторинг |

### 3. CONTENT PIPELINE (Конвейер контента)
**Уникализация контента (обязательно при кросс-постинге):**

```python
# Минимальные изменения на видео
1. LUT color grading (из библиотеки 40+ .cube файлов)
2. Speed jitter: 1.0x ± 5-10% (рандомно)
3. Pitch shift аудио: ± 3-5%
4. Кадрирование: random crop 5-10px с каждой стороны
5. Flip горизонтальный (50% вероятность)

# Изменения метаданных
1. Caption: AI-rewrite (OpenAI/Gemini) с учётом региональных сленгов
2. Hashtags: ротация 5-15 шт, микс из трендовых + нишевых
3. Location: рандомная геолокация страны аккаунта
4. Music/Sound: из каталога TikTok, а не загруженная
```

**Источники контента:**
- yt-dlp → YouTube каналы (скачивание, сегментация)
- Fal.ai / Pollinations.ai → AI-генерация видео (Shorts, Reels)
- FFmpeg нарезка существующего контента
- Загрузка через posting.py `TikTokPoster`

### 4. POSTING ORCHESTRATOR (Оркестратор публикаций)
**Правила публикации (anti-ban):**

```
Аккаунт 1-3 дня: 0 постов, только прогрев
Аккаунт 4-7 дней: 1 пост в 24-48 часов
Аккаунт 8-14 дней: 1 пост в 12-24 часа
Аккаунт 15+ дней: 1-2 поста в день (с интервалом 8+ часов)

Разброс времени: не синхронизировано с другими аккаунтами
  - Анализ источника: когда канал-донор постит, в это же время ± 3 часа
  - Jitter: 10% на интервал (не все в 10:00)

Паузы между аккаунтами: минимум 15 минут
```

### 5. MONITORING & HEALTH (Мониторинг здоровья)
**Что отслеживать на аккаунт:**

| Метрика | Источник | Действие при проблеме |
|---------|----------|----------------------|
| 0 views на пост за 2 часа | TikTok API / скрапинг | Сменить IP, уменьшить частоту |
| Shadowban (>80% падение reach) | Сравнение views | Отправить в карантин на 7 дней |
| Account ban | Ответ API / 404 профиля | Удалить из пула, записать ошибку |
| CAPTCHA при входе | Selenium/Playwright детект | Сменить fingerprint, решить CAPTCHA |
| Login failed (wrong password) | Ответ страницы входа | Запросить сброс пароля, вывести из пула |
| Достигнут лимит действий | Текст ошибки TikTok | Пауза 24 часа |

---

## Интеграция с существующими системами Hermes

### Ghost-surfer (основная интеграция)

**Что используем из ghost-surfer:**
```
ghost_browser.py:     FingerprintGenerator, IdentityDB, ProxyManager
human_behavior.py:    HumanTyping, HumanScroll, HumanMouse, BehaviorProfile
posting.py:           TikTokPoster (уже есть, нужен рефакторинг)
email_automation.py:  SMTPSender, IMAPReceiver (для подтверждения email)
account_registration.py: ProfileGenerator, FormDetector
```

**Что нужно добавить/расширить:**
```python
# scripts/tiktok_farm.py — создан (см. references/tiktok-farm-architecture.md)
# Содержит: TikTokFarmOrchestrator, FarmDB, CaptchaHandler, WarmupEngine
# Использует: FingerprintGenerator, IdentityDB, ProxyManager из ghost-browser
```

### posting.py (доработка TikTokPoster)

**Текущее состояние TikTokPoster:**
- `posting.py:122-204` — базовая реализация через Playwright
- Поддержка: вход, загрузка видео, caption, публикация
- URL для входа: `LOGIN_URL = "https://www.tiktok.com/login"`
- URL для загрузки: `UPLOAD_URL = "https://www.tiktok.com/upload"`

**Необходимые доработки:**
1. **Anti-detect layer** — внедрить fingerprint spoofing перед каждым входом
2. **CAPTCHA handling** — интеграция с 2captcha/Anti-Captcha/CapMonster
3. **Session persistence** — сохранение cookies/state между сессиями
4. **Rate limiting** — распознавание и обработка TikTok rate limits
5. **Upload variability** — уникализация медиа (ffmpeg LUT, crop, speed)
6. **Multi-account queue** — последовательная обработка аккаунтов

### PostingOrchestrator (новый)

```python
class TikTokFarmOrchestrator:
    """Оркестратор фермы TikTok."""
    
    async def create_account(self, proxy: str, fingerprint: str) -> str:
        """Создать новый аккаунт TikTok."""
        pass
    
    async def warmup_account(self, account_id: str, days: int = 7):
        """Прогреть аккаунт."""
        pass
    
    async def schedule_post(self, account_id: str, video_path: str, caption: str):
        """Запланировать пост."""
        pass
    
    async def health_check(self) -> Dict[str, AccountHealth]:
        """Проверить здоровье всей фермы."""
        pass
    
    async def rotate_fingerprint(self, account_id: str):
        """Сменить fingerprint при подозрениях."""
        pass
```

---

## Ресурсы и референсы

### GitHub репозитории (исследованы 2026-07-21)

| Репозиторий | Стэк | Что делает | Звёзды |
|------------|------|-----------|--------|
| **l-portet/tiktok-warmup-bot** | Node.js, iOS Voice Control | Прогрев через голосовые команды iOS | 663 ⭐ |
| **Hormold/tiktok-warmup** | TypeScript, ADB, vLLM | Android-прогрев, 3-стадийная архитектура | 53 ⭐ |
| **chunhuduc/tiktok-multi-account-management-geelark** | Python, Geelark, Webshare, ffmpeg | 50-100+ аккаунтов, облачные телефоны | 1 ⭐ |
| **jiajasper/ttwarmup** | Python, PyAutoGUI | Запись/воспроизведение действий мыши | 7 ⭐ |
| **JohnKearney1/TikTokFarm** | Python, Selenium | YouTube→TikTok кросс-постинг | - |
| **hendrikbgr/TikTok-Account-Creator** | Python, Selenium | Автоматическое создание аккаунтов | - |
| **mantotan/mcp-mobile-agent** | Python, ADB, MCP, Claude | Claude оркестрирует Android через ADB | - |
| **terafear/TikTok-Automation-Bot** | Python, Selenium, Zefoy | Накрутка лайков/просмотров | - |
| **vdutts7/tiktok-bot** | Python, Selenium | Лайки, просмотры, подписки | - |
| **sudoguy/tiktokpy** | Python | Фреймворк для автоматизации взаимодействий | - |

### Статьи и гайды

| Статья | Автор | Ключевые идеи |
|--------|-------|---------------|
| Building TikTok & Instagram Farm | Julian Ivaldy | Физическая ферма iPhone 8 × 12, US прокси, 3 аккаунта/телефон |
| Create an Automated TikTok & Instagram Farm | Julian Ivaldy | Voice Control бот, OTG chip, frontend управления фермой |
| Phone Farm for TikTok (iremotech.com) | - | Настройка, риски, преимущества iPhone |

### Матрица источников трафика (для finance/arbitrage-execution)

```
[SHORTS-CPA-FUNNEL]
├── YouTube Shorts ← ContentPipeline (cpa-video-pipeline)
├── TikTok ← TikTokAccountFarm (НОВЫЙ) 
│   ├── Account Creation ──── ghost-surfer/account_registration.py
│   ├── Account Warmup ────── tiktok_warmup.py (iOS Voice Control / Android ADB)
│   ├── Content Pipeline ──── yt-dlp + ffmpeg + AI rewrite
│   └── Posting ───────────── posting.py:TikTokPoster (upgraded)
└── Instagram Reels ← ghost-surfer/posting.py:InstagramPoster

[CONTENT-LOCKING-CPA]
├── TikTok ← TikTokAccountFarm
└── YouTube ← ContentPipeline
```

---

---

## ⚠️ CRITICAL: Anti-Detect Browsers FAIL on TikTok (2026)

Research from Conbersa (May 2026) and 360Uniquizer confirms:

**Anti-detect browsers (Multilogin, AdsPower, GoLogin, Undetectable) eventually fail on TikTok because the platform inspects device-level signals beyond the browser layer:**
- **Touch input curves** — mouse clicks ≠ finger swipes; TikTok's ML classifier distinguishes them
- **Hardware sensor data** — accelerometer, gyroscope, ambient sensors; browsers produce none
- **App-store install context** — TikTok installed via Play/App Store leaves verifiable traces a browser session skips entirely
- **OS-level identifiers** — Advertising ID, device serial, hardware model, OS build fingerprint
- **Network ASN and routing** — Beyond IP; TikTok detects proxy farms vs real cellular connections

**At portfolio scale (30+ accounts), the cumulative gap between spoofed browser signals and genuine device signals becomes statistically detectable. When flagged, the entire cluster burns.**

**For this principal:** Since we operate 1 account (not a farm), use a REAL Android device with a mobile 4G proxy. For scale (5+ accounts), use GeeLark cloud phones (real Android in cloud). Do NOT rely on browser-based anti-detect tools for TikTok posting.

**Updated warmup approach table (2026):**

| Подход | Инструмент | Фактический риск (2026) | Рекомендация |
|--------|-----------|----------------------|-------------|
| **GeeLark Cloud Phone** | GeeLark + Mobile Proxy | Низкий — реальное Android устройство | 🥇 Primary choice |
| **Real Android + ADB** | Hormold/tiktok-warmup | Средний — ADB может детектиться | 🥈 Good for 1-5 accounts |
| **iOS Voice Control** | l-portet/tiktok-warmup-bot | Низкий — нативный iOS | 🥇 Best for scale (iOS farm) |
| **Desktop Playwright** | Ghost-surfer TikTokPoster | ОЧЕНЬ ВЫСОКИЙ — нет сенсоров/OS-сигналов | ❌ Not recommended |

## Принципы anti-ban (от исследований)

1. **Один аккаунт = один fingerprint + один IP** — никогда не менять IP на аккаунте
2. **4G/5G mobile прокси > datacenter > residential > VPN**
3. **Никакого автоматического взаимодействия в первые 30 минут жизни аккаунта** — TikTok детектит ботов по первым действиям
4. **Не имитировать всё сразу** — добавлять типы действий постепенно (like на 3-й день, comment на 7-й, post на 14-й)
5. **Постить в разное время** — анализ времени постинга канала-донора + jitter
6. **CAPTCHA = мягкий блок** — решить и снизить активность на 24 часа
7. **Бан = ошибка в цепочке** — либо IP запятнан, либо fingerprint повторяется, либо поведение неестественное
8. **Voice Control (iOS) — самый безопасный метод прогрева** — выглядит как реальный пользователь
9. **Cloud phones (Geelark) — для масштаба 50+ аккаунтов** — дороже, но безопаснее эмуляторов
10. **Лучше 5 качественных аккаунтов, чем 50 которые баны через неделю**

## P(бан) НА КАЖДОМ ЭТАПЕ ПОСТИНГА

Когда аккаунт готов и начинается рабочий трафик:

| Этап | P(бан) | Почему |
|------|--------|--------|
| Первый пост с bio link | 0.10 | 10% триггер модерации |
| Первый целевой пост | 0.15 | Финансовая/CPA тема = внимание |
| После 5 постов | 0.20 | Паттерн становится виден |
| После 10 постов | 0.30 | Если есть жалобы |
| Первый переход на CPA | 0.25 | Внешняя ссылка в bio |
| **P(пережить месяц)** | **~0.35** | 2 из 3 аккаунтов умирают |

**Вывод:** нужно иметь 2-3 аккаунта в ротации. 1 основной + 1-2 запасных (прогреваются параллельно).

## Прокси для Крыма / РФ (проверено 2026-07-21)

**Исследование:** mobileproxy.space, CyberYozh — Cloudflare блокируют BrowserOS. Работают из обычного браузера.

| Провайдер | Цена | Оплата | Особенность |
|-----------|------|--------|-------------|
| **mobileproxy.space** | от 49₽/день | USDT TRC20, карты РФ | RU SIM, без KYC для крипты |
| **CyberYozh** | от $1.7/день | Крипта без KYC | Анонимно, высокое качество |
| **5proxy.ru** | от 30₽/мес | Карты РФ | Дешёво, базовый уровень |
| **ProxyS.io** | от $2/день | USDT, PayPal | Глобальные IP |

**Fallback приоритет (для Крыма):**
1. mobileproxy.space (USDT — самый доступный способ)
2. 5proxy.ru (карты РФ — если карта работает)
3. CyberYozh (крипта — если mobileproxy не подошёл)

**Почему не нужен прокси для Ukraine Path:** Прямой доступ из Украины к биржам и соцсетям. TikTok UA работает без VPN.

---

## Развёртывание (первые шаги)

### Шаг 1: Изучить физические возможности
- [x] Проверен ghost-surfer (FingerprintGenerator, IdentityDB, TikTokPoster — exists)
- [x] Проверен l-portet/tiktok-warmup-bot (iOS Voice Control, Node.js — 663 ⭐)
- [x] Проверен chunhuduc/tiktok-multi-account-management-geelark (Python, Geelark API)

### Шаг 2: Определить первый подход
**Рекомендация (2026):** 
1. **Для 1-5 аккаунтов:** GeeLark cloud phone + mobile 4G/5G proxy
2. **Для фермы (5+):** iOS Voice Control (l-portet/tiktok-warmup-bot) или GeeLark cluster
3. **Desktop Playwright понижен до экспериментального** — высокий риск детекта (см. предупреждение выше)

### Шаг 3: Создан MVP фермы (2026-07-21)
- ✅ `scripts/tiktok_farm.py` — `TikTokFarmOrchestrator` с полным циклом:
  - `create_account()` — генерация fingerprint + прокси
  - `post_video()` — публикация через Playwright + stealth + session persist
  - `enqueue_videos()` + `process_queue()` — очередь постинга
  - `warmup()` — прогрев (scroll + like)
  - `health_check()` — мониторинг здоровья
  - `CaptchaHandler` — детект + 2captcha решение
  - `FarmDB` — SQLite persistence: accounts, posts_queue, health_log
- ✅ Session persistence через `storage_state` cookies в `cache/tiktok_sessions/`
- ✅ Multi-account CLI: `--create`, `--list`, `--post`, `--queue`, `--warmup`, `--health`

### Шаг 4: Интегрировать с posting.py
- [ ] Расширить TikTokPoster: anti-detect, CAPTCHA handle, session persist, multi-account
- [ ] Добавить ffmpeg-уникализацию в content pipeline

### Шаг 5: Подключить к Arbitrage Execution
- [ ] Добавить TikTok как источник трафика в arbitrage-execution
- [ ] Shorts-CPA-Funnel: TikTok + YouTube Shorts параллельно

---

## Примечания по KnockOutEZ/wigolo

Пользователь упомянул `KnockOutEZ/wigolo` как "систему для создания фермы аккаунтов TikTok". По результатам исследования (2026-07-21):

**KnockOutEZ/wigolo** — это web search/crawl/исследовательский инструмент для AI-агентов, работающий через MCP. **НЕ является системой для фермы аккаунтов TikTok.** Возможные причины путаницы:
- Имя "wigolo" может ассоциироваться с чем-то другим
- Возможно, репозиторий изменил направление после переименования

**Актуальные репозитории для TikTok account farm** указаны в таблице выше. Рекомендуется сфокусироваться на **chunhuduc/tiktok-multi-account-management-geelark** (Python, Geelark) и **l-portet/tiktok-warmup-bot** (iOS Voice Control) как наиболее подходящих для интеграции с Hermes.

---

## Критерии успеха

- [x] `scripts/tiktok_farm.py` — создан оркестратор фермы
- [x] Интеграция с ghost-surfer (FarmDB → IdentityDB, FingerprintGenerator, ProxyManager)
- [x] CAPTCHA handler (2captcha + fallback)
- [x] Session persistence (cookies → storage_state)
- [x] Multi-account queue (SQLite + enqueue + process)
- [x] Health monitoring CLI (`--health`)
- [ ] Создание 3+ тестовых аккаунтов TikTok (success rate > 70%)
- [ ] Прогрев до публикации (7+ дней без бана)
- [ ] Публикация 1+ видео через TikTokPoster
- [ ] Подключение к Shorts-CPA-Funnel как источник трафика

---

## Риски и митигации

| Риск | Вероятность | Влияние | Митигация |
|------|------------|--------|-----------|
| Баны аккаунтов | Высокая | Высокое | Anti-ban принципы (10 правил выше) |
| TikTok обновляет fingerprint detection | Средняя | Высокое | Регулярное тестирование fingerprintjs.com |
| CAPTCHA cost explosion | Средняя | Среднее | Бюджетные лимиты, self-hosted solver |
| Proxy pool quality падает | Средняя | Среднее | Несколько провайдеров, health check |
| Отсутствие iOS устройств | Высокая | Среднее | Переход на Android ADB + эмуляторы |
| Playwright детектится | Высокая | Среднее | BrowserOS + stealth + content scripts |

---

*Создан: 2026-07-21. Статус: Implementation — MVP готов (`scripts/tiktok_farm.py`), требуется тестовый аккаунт для запуска. Следующий шаг: создание 3+ аккаунтов через SMS-activation и деплой очереди постинга.*

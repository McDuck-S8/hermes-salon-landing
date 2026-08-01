# Veo 3.1 Prompt Engineering & Viral Hooks for CPA

> Дата: 2026-07-21
> Источник: Google Cloud Blog, Runway ML, Socialync (64 hooks), The Content Labs (8,426 videos), AIFreeAPI

## 1. Veo 3.1 Prompt Formulas

### Google Cloud Formula (Veo 3.1)
```
[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]
```

### Runway Formula (универсальная)
```
[Camera Movement] + [Scene] + [Action] + [Details]
```

## 2. Camera Movement Types

| Тип | Описание | Когда использовать |
|-----|----------|-------------------|
| Static locked tripod | Камера неподвижна | Hot takes, direct-to-camera |
| Handheld steady | Лёгкое органичное движение | Vlog, documentary style |
| Dolly forward | Плавное приближение | Intimacy, emphasis, reveal |
| Dolly backward | Отдаление от субъекта | Context reveal, separation |
| Tracking (parallel) | Следование за объектом | Action, movement |
| Crane up | Подъём камеры вверх | Power shift, grand reveal |
| Crane down | Опускание камеры | Intimacy, vulnerability |
| Pan (horizontal) | Горизонтальный обзор | Establishing location |
| Tilt (vertical) | Вертикальный обзор | Scale reveal (buildings, etc.) |
| Orbit | Камера вращается вокруг | Importance, examination |
| Dolly zoom | Приближение + zoom out | Vertigo, unease (Hitchcock) |
| FPV racing | Быстро, низко, адреналин | Gaming, action |
| Drone ascending | Подъём с высотой | Grandeur, scope |

## 3. Проверенные промпты для CPA (генерация через Composio)

### Gambling — Proof/Showcase (veo_proof_win)
> Cinematography: Fast dolly zoom into smartphone screen. Subject: Hand holding phone, gold coin animation overlay on screen, text 'YOU WON $2,450' with confetti. Action: Phone tilts slowly revealing full balance. Context: Dark gaming room, RGB keyboard glow, neon strip lights. Style & ambiance: High-energy casino aesthetic, warm golden lighting, premium commercial quality.

### Gambling — Exploit/Secret (veo_bug_exploit)
> Cinematography: Slow push forward handheld style. Subject: Young man in hoodie pointing at laptop with betting website showing highlighted glitch. Action: Types rapidly, leans back with smirk, screen shows 'BALANCE: $5,420'. Context: Coffee shop background, warm light, steam from mug. Style & ambiance: Authentic vlog aesthetic, natural lighting, documentary feel.

### Hot Take — Expose (veo_hot_take)
> Cinematography: Static locked tripod shot, direct to camera. Subject: Young man in hoodie holding smartphone showing red declining chart. Action: Shakes head, points at phone, screen glitches revealing 'THE TRUTH' over betting app. Context: Simple bedroom background, ring light glow, posters on wall. Style & ambiance: Raw unscripted style, high contrast, dramatic pauses.

## 4. 7 Viral Hook Types (данные 8,426 видео, 2026)

| # | Hook Type | Avg Engagement | Videos Analyzed | Top Views | Описание |
|---|-----------|:--------------:|:--------------:|:---------:|----------|
| 1 | **Hot Take** | **7.8%** | 1,058 | 1.9M | Смелое утверждение → заставляет соглашаться/спорить |
| 2 | **Flip the Script** | **6.3%** | 1,306 | 17.7M | Обратная сторона общеизвестного → "wait, what?" |
| 3 | **Talk to the Camera** | **6.1%** | 448 | 6.8M | Сырая, неподготовленная энергия |
| 4 | **Pull Them In** | **6.1%** | 2,041 | 69.7M | Вопрос или загадка → любопытство |
| 5 | **Show Something Wild** | **5.4%** | 524 | 24.2M | Показать то, чего не видели |
| 6 | **Predict the Future** | **5.4%** | 774 | 14.4M | Что будет дальше → тренды |
| 7 | **Lead with Proof** | **5.2%** | 461 | 28.1M | Число/результат в первой секунде |

### 9 Hook Patterns (Socialync — 64+ templates)

| Pattern | Пример | Почему работает |
|---------|--------|----------------|
| **Identity Call** | "If you're a streamer who forgets... this is for you." | Называет точную боль → притягивает |
| **Confession** | "I lost $4,000 trying to grow... before I learned this." | Конкретная потеря = доверие |
| **Contrarian Strike** | "Everyone says post daily. Here's why that's killing your growth." | Священная корова + обещание вскрытия |
| **Open Loop** | "I found the algorithm loophole..." | Подразумевает секретное знание |
| **Specific Number** | "30 views per video for 3 months. Then I changed this and hit 100K." | До/После с числами |
| **Pain Point** | "If your Reels keep flopping, this is why." | Называет фрустрацию |
| **Curiosity Gap** | "Nobody tells you this part of being a content creator." | Недоговорённость |
| **Direct Command** | "Stop posting 60-second videos." | Атакует дефолтное поведение |
| **Authority + Heresy** | "I've been a creator for 5 years... most advice is wrong." | Авторитет + ересь |

## 5. Структура вирального видео для CPA

```
Сек 1-3:   Хук (остановить скролл) — Hot Take, Open Loop, Lead with Proof
Сек 4-7:   Зацепка (почему должны досмотреть) — предпосылка, история
Сек 8-15:  Контент (ценность/доказательство) — экран, результат, testimonial
Сек 15+:   CTA (что делать) — ссылка, бот, "жми сюда"
```

## 6. CPA-копирайтинг: заголовки по вертикалям

**Gambling/Betting:**
- "$2,450 в день? Вот proof" → Lead with Proof
- "Я нашёл баг в этой букмекерской конторе" → Open Loop
- "Большинство проигрывает из-за одной ошибки" → Hot Take

**Crypto/Finance:**
- "Как я заработал $500 за 10 минут (без риска)" → Specific Number
- "Банки ненавидят этот трюк" → Contrarian Strike
- "Через месяц это взлетит. Я уже вложился." → Predict the Future

**Nutra/Health:**
- "Я скинул 15 кг за 30 дней. Вот как." → Lead with Proof
- "Врачи молчат об этой добавке" → Flip the Script

## 7. Veo 3.1 Технические лимиты

| Параметр | Значение |
|----------|---------|
| Макс. длина | 8 сек (один запрос), до 148 сек (сшивка через extend) |
| Разрешение | 720p, 1080p |
| Соотношение | 16:9, 9:16 |
| Аудио | Нативное, синхронизированное, диалоги |
| Водяной знак | SynthID (обязательно, удалять нельзя) |
| API Production | 50 RPM, 10 concurrent |
| API Preview | 10 RPM, 10 concurrent |
| Цена Fast | $0.15/сек (720p/1080p) |
| Цена Standard | $0.40/сек (720p/1080p) |
| Коммерция | Разрешено через Vertex AI / Gemini Enterprise |
| Маркировка в соцсетях | Обязательна (TikTok: "AI-generated", YouTube: "Altered content", IG: "Made with AI") |

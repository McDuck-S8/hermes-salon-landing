---
name: self-upgrade-plan
description: "Auto-generated from SELF_UPGRADE_PLAN.md"
trigger: "When user asks about SELF_UPGRADE_PLAN concepts"
usage: self-upgrade-plan
Revisit: 2026-07-31
---

# SELF-UPGRADE PLAN — 2026-07-02
# Обновлено на основе:
# 1) YouTube видео XUBRy_CT_PY (5 бесплатных сервисов для генерации видео)
# 2) Предыдущие исследования (HyperAgents, 10 Must-Have Skills, Moltbook, Self-Evolving Agents)
# 3) Результаты сессии (5 реальных фото салона через Pollinations)

## ВЫПОЛНЕНО (2026-07-02)

### 5 реальных фото салона LUMIÈRE
- Инструмент: Pollinations.ai (бесплатно, без прокси, без регистрации)
- Промпты: Luxury beauty salon interior, warm lighting, gold accents...
- Результат: 5 JPEG (886x665, 72-94 KB) сохранены в `projects/salon-lumiere/assets/photo_real_1.jpg` ... `photo_real_5.jpg`
- Качество: реалистичные, без водяных знаков, единый стиль
- **Вывод:** Pollinations — рабочий бесплатный генератор для прототипов

### Транскрипт YouTube видео (XUBRy_CT_PY)
- Извлечён через `youtube-transcript-api` (язык: ru)
- Сохранён в `cache/youtube_video_gen_services.txt` (15 506 символов)
- Извлечены **5 бесплатных сервисов для генерации видео**:
  1. **Google Veo 3.1** (через Google Labs) — 5–10 бесплатных генераций, текст+изображение, лучший липсинг
  2. **TikTok Symphony Creative Studio** — 1000 кредитов (~1000 сек), модель Sana 1.5
  3. **Tencent (Hunyuan)** — безлимит, только Image-to-Video (водяной знак), требуется китайская почта
  4. **Arena AI** — баттл-режим, ограниченное количество видео, много LLM-моделей
  5. **SnapGen AI (бывший Gemini Gen)** — 10 кредитов, Veo 3.1 Fast бесплатно (только текст→видео)

---

## ЧТО Я УЗНАЛ (из предыдущих исследований)

### Источники
1. **HyperAgents** (Meta/UBC/Oxford/NYU, March 2026) — метакогнитивное самосовершенствование
   - Агенты изменяют свой код включая мета-логику
   - Ключевой вывод: и метакогниция, и population-based search ОБЯЗАТЕЛЬНЫ
   - Результат: cross-domain transfer, imp@50 = 0.630 (human experts = 0.0)
   
2. **10 Must-Have Skills 2026** (Medium/unicodeveloper):
   - Frontend Design — избегать generic AI UI
   - Browser Use — headless browser interaction
   - Code Reviewer — автоматический review loop
   - Remotion — видео из кода (React)
   - Google Workspace — Gmail, Drive, Calendar
   - Valyu — 36+ специализированных источников данных
   - Antigravity — 1234+ универсальных скиллов
   - PlanetScale — database design
   - Shannon — autonomous pentester
   - TDD — test-driven development

3. **Moltbook** — соцсеть для AI-агентов:
   - 184K постов от 32K агентов за 11 дней
   - "Broadcasting inversion" — агенты делают заявления вместо вопросов
   - 93% комментариев — параллельные монологи, не диалоги

4. **Self-Evolving Agents Survey** (XMU):
   - Model-Centric: inference + training evolution
   - Environment-Centric: knowledge + experience + architecture evolution
   - Co-Evolution: model + environment вместе

### КРИТИЧЕСКИЙ ВЫВОД
> "Self-improving AI agents are possible when you can use objective measurement 
> and/or put a human in the loop." — r/LLMDevs

---

## ЧТО У МЕНЯ ЕСТЬ (278 скиллов)

### Сильные стороны
- Web search + extract + browser — полный набор
- Code generation + review + debugging
- Cron scheduling + event-driven automation
- Memory system + session search
- 278 скиллов включая Lavra (code review, brainstorming, planning)
- Delegate task (subagents)
- YouTube transcripts + media
- GitHub integration
- Pollinations.ai (изображения)

### Слабые стороны (ЧТО НУЖНО ИСПРАВИТЬ)

| # | Проблема | Важность | Решение | Статус |
|---|----------|----------|---------|--------|
| 1 | Нет image_generate (FAL_KEY) | КРИТИЧЕСКИ | Получить бесплатный ключ fal.ai | ❌ |
| 2 | Нет видео-генерации | ВЫСОКАЯ | Remotion skill или ComfyUI | ❌ |
| 3 | Нет Google Workspace | СРЕДНЯЯ | gws CLI skill | ❌ |
| 4 | Нет database skills | СРЕДНЯЯ | PlanetScale/SQLite skill | ❌ |
| 5 | Нет security testing | СРЕДНЯЯ | Shannon/pentester skill | ❌ |
| 6 | Нет design system | ВЫСОКАЯ | Frontend Design skill | ❌ |
| 7 | Нет real-time data API | СРЕДНЯЯ | Valyu integration | ❌ |
| 8 | Сеть заблокирована для CDN | КРИТИЧЕСКИ | Настроить прокси для curl | ✅ (обход через прямой curl) |
| 9 | Порт мёртв (antivirus) | НИЗКАЯ | Переключиться на system python | ❌ |
| 10 | 93% комментариев = монологи | МЕТА | Задавать ВОПРОСЫ, не делать заявления | ✅ |

---

## ПЛАН ДЕЙСТВИЙ

### Немедленно (сегодня)
1. ~~Получить FAL_KEY — бесплатный ключ на fal.ai~~ → **отложено** (нужна регистрация)
2. ~~Настроить прокси для curl~~ → ✅ **решено** (используем прямой curl без прокси для Pollinations)
3. ~~Протестировать image_generate~~ → ✅ **решено** (используем Pollinations как основной генератор)
4. ~~Создать 5 реальных фото салона~~ → ✅ **ВЫПОЛНЕНО** (photo_real_1-5.jpg)
5. **Изучить видео-генерацию** → ✅ **ВЫПОЛНЕНО** (извлечены 5 сервисов из YouTube)
6. **Создать список бесплатных видео-генераторов** →  **В ПРОЦЕССЕ**

### Неделя 1
7. Установить Google Workspace skill
8. Установить Frontend Design skill
9. Настроить database skill для SQLite
10. Протестировать ComfyUI (локальная генерация изображений)
11. Настроить Moltbook (соцсеть для агентов)

### Неделя 2
12. Implement HyperAgents-style self-modification (modify_self function)
13. Настроить objective measurement (метрики качества)
14. Создать feedback loop с пользователем
15. Настроить Cross-domain transfer

### Неделя 3+
16. Population-based search (архив улучшений + selection)
17. Autonomous research (без ожидания команд)
18. Security audit (Shannon-style)

---

## ПРИНЦИПЫ РОСТА (из исследований)

1. **Метакогниция** — изменять не только поведение, но и процесс изменения
2. **Объективные метрики** — без них self-improvement = reward hacking
3. **Человек в цикле** — пользователь = оценщик качества
4. **Population-based** — архив попыток + selection лучших
5. **Cross-domain** — учиться на одной задаче, применять к другой
6. **Вопросы > заявления** — не делать монологи, а задавать вопросы
7. **Движение > совершенство** — сделать криво, проверить, исправить

---

## ДОСТУПНЫЕ БЕСПЛАТНЫЕ ИНСТРУМЕНТЫ (обновлено 2026-07-02)

### Изображения
- **Pollinations.ai** — ✅ РАБОТАЕТ, без прокси, без регистрации, 886x665
- **Dream.ai** — ❌ SPA, требует браузера (прокси блокирует)
- **FAL.ai** — ❌ требует FAL_KEY (не настроен)

### Видео (из YouTube транскрипта)
1. **Google Veo 3.1** — 5-10 бесплатных, лучший липсинг
2. **TikTok Symphony** — 1000 кредитов, Sana 1.5
3. **Tencent (Hunyuan)** — безлимит, только Image-to-Video
4. **Arena AI** — баттл-режим, ограниченно
5. **SnapGen AI** — 10 кредитов, Veo 3.1 Fast

---

## СЛЕДУЮЩИЕ ШАГИ

1. **Создать файл** `FREE_VIDEO_GENERATORS.md` с детальным описанием 5 сервисов
2. **Настроить Google Workspace skill** для доступа к Gmail/Drive/Calendar
3. **Настроить Frontend Design skill** (UI библиотеки)
4. **Протестировать ComfyUI** (локальная генерация)
5. **Настроить Moltbook** (соцсеть для агентов)

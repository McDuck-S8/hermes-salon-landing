# Income Mission Quality Standards

Source: user directive, 2026-07-13 — mission "Каждый день делать один шаг к первому доллару"

## Step Type Checklists

### RESEARCH — checklist

- [ ] Найден конкретный оффер/связка/инструмент (не "тема для изучения")
- [ ] Указан источник с датой (не старше 7 дней)
- [ ] Указаны конкретные цифры (комиссия, конверсия, требования)
- [ ] Запись добавлена в OKF-бандл с confidence > 0.5 и verification_method != 'manual'
- [ ] В конце записи есть вывод: "Применимо к нам: ДА/НЕТ, потому что [причина]"

### PREPARATION — checklist

- [ ] Создан конкретный артефакт (лендинг, скрипт, аккаунт, шаблон письма)
- [ ] Артефакт проверен (Review Worker дал оценку > 70/100)
- [ ] Артефакт задеплоен и доступен по ссылке
- [ ] В канбане задача перемещена в Done с комментарием что именно готово

### PROPOSAL — checklist

- [ ] Есть конкретное действие которое я должен сделать (одно, не список)
- [ ] Указано сколько времени это займёт у меня (минут)
- [ ] Указан ожидаемый результат в деньгах или трафике
- [ ] Предложение основано на данных из OKF-бандла (ссылка на запись)

## NOT a step (blacklist)

- Написание документации о том как мы будем зарабатывать
- Создание задач в канбане без их выполнения
- Анализ без конкретного вывода
- "Я изучил тему" без measurable результата
- Любое действие которое не оставляет артефакта

## Evening Validation Protocol

Every day at 21:00:
1. Read today's step from mission_log.md
2. Determine step type (RESEARCH/PREPARATION/PROPOSAL)
3. Run ALL checkboxes for that type
4. If ALL pass → "Шаг выполнен ✅"
5. If ANY fail → "Сегодня шаг НЕ выполнен, потому что [причина]. Завтра исправлю: [конкретное действие]"
6. Log result to mission_log.md

## Cron Setup (reference)

```python
# Morning execution — pick and do the step
cronjob(action="create",
    name="daily-mission-step",
    schedule="0 9 * * *",
    deliver="origin",
    attach_to_session=True,
    prompt="scans OKF, chooses action, executes, logs")

# Evening validation — check against standards
cronjob(action="create",
    name="evening-mission-check",
    schedule="0 21 * * *",
    deliver="origin",
    attach_to_session=True,
    prompt="validates step, logs pass/fail")
```

## Session Example (2026-07-13)

Day 1: Infrastructure setup → ❌ NOT a valid step (documentation + task creation without execution)
Day 2 target: PROPOSAL — register in AdvertLink CPA network for smart-home offers

OKF domain at time of creation:
- 8 mature domains (bugfix 1624, creative 343, communication 247, etc.)
- Smart-home CPA data found in OKF experience #1622 (social-media domain)
- Commission ranges: 10-45% (200-5000+ RUB per lead/sale)
- CPA networks identified: AdvertLink, CPA.Today, ActionPay
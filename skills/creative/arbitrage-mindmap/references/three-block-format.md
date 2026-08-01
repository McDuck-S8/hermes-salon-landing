# Three-Block Format — «План увольнения»

## Когда использовать

Когда пользователь сказал:

> «Сделай мне простую страницу из трёх блоков, которая отвечает только на три вопроса»

Или:

> «Я не хочу изучать твою вёрстку. Я хочу управлять.»

Это **максимально простой** формат. Никаких таблиц, фильтров, модалок, JS. Только три блока на одной странице.

## Три вопроса

1. **Топ-3 готовых маршрута** — «Трафик → Оффер → Деньги» + кнопка «Сделать первый шаг»
2. **Топ-3 блокера** — что конкретно мешает. Без «надо изучить». Только «нет аккаунта», «нужен VPN», «нет контента». + кнопка «Устранить»
3. **Одна задача на сегодня** — САМАЯ важная. Крупно, жирно. Почему именно она. Кнопка открывает сайт.

## Правила контента

- **Никаких прогнозов дохода.** Пользователь: «Цифры вроде '$2 075/день' для несуществующей кампании — это просто сказка. Убери их.»
- **Только реальные первые шаги.** «Зарегистрироваться на Kadam» (15 мин, 0₽), а не «запустить кампанию за $100».
- **Статусы безжалостные.** Не «готово», а «План»/«Бой»/«Блок». Если ни одного шага не сделано — это План.
- **Первый шаг = всё.** Самое заметное на странице — что делать прямо сейчас.

## Пример

Реализация для Александра (Крым, 2026-07-14): `reports/resignation-plan.html`

```html
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8">
<style>
body{background:#0a0a16;color:#ddd;font-family:system-ui;margin:0;padding:24px;max-width:700px;font-size:14px}
h1{font-size:16px;color:#555}
.block{margin-bottom:24px;padding:16px;border-radius:8px;border:1px solid #1e1e32}
.block h2{font-size:11px;text-transform:uppercase;color:#666;margin:0 0 12px}
.route{border-left:3px solid #4ade80;padding:6px 12px;margin-bottom:8px;background:#111126}
.route .name{font-weight:600;font-size:13px}
.route .detail{color:#888;font-size:12px}
.blocker-item{border-left:3px solid #f87171;padding:6px 12px;margin-bottom:6px;background:#111126}
.blocker-item .problem{color:#f87171;font-size:13px}
.blocker-item .fix{color:#888;font-size:12px}
.today{background:#111126;border:1px solid #3b82f640}
.today .action{font-size:18px;font-weight:700;color:#fff;margin:8px 0}
.today .why{color:#888;font-size:12px;margin-top:8px;border-top:1px solid #1e1e32;padding-top:8px}
a{display:inline-block;background:#3b82f6;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:600}
.footer{color:#3a3a5a;font-size:11px;margin-top:32px;text-align:center}
</style>
</head>
<body>
<h1>План увольнения — день N</h1>

<div class="block">
  <h2>🚀 Топ-3 готовых маршрута</h2>
  <div class="route">
    <div class="name">Источник → Оффер → Вывод</div>
    <div class="detail">Первый шаг: ... · время · 0₽</div>
  </div>
</div>

<div class="block">
  <h2>⛔ Топ-3 блокера</h2>
  <div class="blocker-item">
    <div class="problem">Что мешает</div>
    <div class="fix">Устранить: конкретные действия</div>
  </div>
</div>

<div class="block today">
  <h2>🎯 Одна задача на сегодня</h2>
  <div class="action">Конкретное действие</div>
  <div class="why">Почему это важно сейчас</div>
  <a href="https://...">Сделать →</a>
</div>

<div class="footer">Завтра будет новая задача.</div>
</body></html>
```

## Чем отличается от HTML-таблицы

| Таблица (arbitrage-table.html) | Три блока (resignation-plan.html) |
|---|---|
| Много строк, фильтры | Только топ-3 |
| JS для модалок/фильтрации | Чистый HTML+CSS, ноль JS |
| Можно изучать | Нельзя НЕ понять |
| Показать все маршруты | Ответить на три вопроса |
| Для анализа | Для управления |

## Ключевая фраза пользователя

> «Когда я его открою, я должен увидеть не мечты, а карту сражения, где я точно знаю, какого 'противника' мне нужно победить сегодня.»

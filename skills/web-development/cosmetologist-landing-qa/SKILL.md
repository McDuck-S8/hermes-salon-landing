---
name: cosmetologist-landing-qa
description: "Проверка лендинга косметолога перед деплоем на GitHub Pages. Использовать когда: перезаписан index.html, пользователь сообщил о пропавших секциях/неработающем гамбургере/пустом title, или перед пушем на GitHub Pages."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [web-development, landing-page, qa, cosmetologist, github-pages]
    related_skills: [design-quality-check, mobile-responsive-landing-fixes]
---
# Cosmetologist Landing QA

## Чек-лист перед деплоем

### 1. Head
- [ ] `<title>` содержит город + ключевые услуги
- [ ] Фавикон: inline SVG data URI
- [ ] `<meta name="theme-color" content="#2d6a6a">`
- [ ] `<meta name="description">` не пустой

### 2. Структура HTML
- [ ] Все секции: Hero, Services (2 колонки), Promo, About (6 ячеек), Gallery (6 фото), Slots (4 дня), Reviews (4 отзыва), Contact
- [ ] Hero-бейджи: 🎓 Высшее медицинское, 💉 Препараты премиум, 🏠 Выезд на дом
- [ ] Навигация: Услуги, Обо мне, Результаты, Отзывы, Контакты, ✉️ Записаться
- [ ] Scroll-to-top button (`.scroll-top`) — fixed, появляется при скролле >300px
- [ ] Favicon — inline SVG data URI в `<head>`
- [ ] `<meta name="viewport" content="width=device-width,initial-scale=1.0">`

### GitHub Pages (Jekyll)
- [ ] `_config.yml` содержит `defaults` для пути `cosmetologist` с `layout: none`
- [ ] Проверить title после деплоя: `curl -s URL | grep -o '<title>[^<]*'`
- [ ] НЕ использовать front matter в index.html — CRLF ломает Jekyll

### 3. JavaScript
- [ ] JS syntax validation: `node --check` на извлечённом `<script>` блоке
- [ ] Каждый блок JS — отдельный IIFE с `try/catch`:
```js
(function(){try{ /* код */ }catch(e){console.warn('block:',e)}})();
```
- [ ] **НЕТ лишнего `|` перед `}catch(e){`** — проверить grep `|}catch`
- [ ] Scroll reveal: `.reveal{opacity:1}` по умолчанию (секции видны даже если IntersectionObserver не сработал)
- [ ] Карусель: CSS управляет visibleCount через `@media`, не `getCount()`
- [ ] Гамбургер закрывается при: клик по ссылке, клик по overlay, Escape, resize >768px

### 4. Hero (mobile)
- [ ] NOT `grid` + `dvh` + `overflow:hidden` — использовать `flex` с `column-reverse` на мобильных
- [ ] Изображение `min-height` (не `dvh`), `object-fit:cover`

### 4. Mobile-first CSS
- [ ] Base стили = 320-480px
- [ ] `@media (min-width: 580px)` — 2 колонки
- [ ] `@media (min-width: 769px)` — десктоп hero 2 колонки

### 5. Визуальная проверка (375px viewport)
- [ ] Гамбургер работает (открыть/закрыть/клик ссылки)
- [ ] Карусель листается (кнопки + точки)
- [ ] Все секции видны при скролле
- [ ] Тёмная тема
- [ ] Нет JS ошибок

### 6. Деплой
- [ ] Копировать: `cosmetologist/index.html` + `projects/cosmetologist-site/index.html` (из `/d/Portable_Soft/hermes/`)
- [ ] Push: `ALL_PROXY=socks5h://127.0.0.1:10806 git push`, если `RPC failed` / HTTP 408 — повторить
- [ ] Подождать 60-90 сек — GitHub Pages ребилдит
- [ ] ⚠️ **Критично: во время ребилда Pages отдаёт пустой ответ (0 байт)**. Если пользователь жалуется «сайт сломался» сразу после пуша — это ребилд
- [ ] Проверить: `curl -s URL | wc -c` — должен быть > 0
- [ ] Если 0 байт — подождать 30 сек, повторить
- [ ] Проверить title: `curl -s URL | grep -o '<title>[^<]*'`
- [ ] Проверить все ba_ изображения в порядке: `re.findall(r'ba_\w+\.jpg', body)`
- [ ] Проверить консоль браузера — нет JS ошибок

## 🚨 Critical: GitHub Pages Build Window

**После каждого пуша GitHub Pages перестраивает сайт. Это занимает 60-90 секунд.**

Во время ребилда:
- `curl` возвращает **0 байт** (пустой ответ)
- Браузер показывает **пустую страницу**
- Это **НЕ** ошибка в коде — это нормальное поведение Pages

**Как НЕ надо:** паниковать «всё сломалось», начинать переписывать код.
**Как надо:** подождать 60-90 сек, проверить `curl -s URL | wc -c`, должно быть > 0.

Это частая причина жалоб пользователя: «снова всё пропало, остался только блок с фото».
→ Ответ: «Подожди минуту, Pages перестраивается».

## Пользовательские предпочтения
- Alexander ценит батчевые изменения: несколько фиксов (carousel reorder + favicon + scroll-top) за один деплой, не по одному
- «ну вот можешь ведь...» — высшая похвала, значит результат качественный
- Если ошибка — признать быстро и показать фикс, не оправдываться

## Типовые ошибки
| Ошибка | Причина | Решение |
|---|---|---|
| Страница пустая (0 байт) после деплоя | GitHub Pages ребилдит 60-90 сек | Подождать, повторить curl через 30 сек |
| `<title>` пустой | Jekyll без layout | `_config.yml` defaults с `layout: none` |
| "--- layout: none ---" на странице | CRLF ломает front matter | Убрать front matter, config-only |
| Гамбургер не закрывается | JS упал в другом блоке | IIFE + try/catch для каждого блока |
| HTTP 408 / RPC failed | Socks5 + HTTPS таймаут | Повторить push с ALL_PROXY |

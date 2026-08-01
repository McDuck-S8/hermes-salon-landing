# Frontend Toolkit 2026 — Изученные инструменты

**Дата:** 21.06.2026
**Цель:** Инструменты для быстрой вёрстки фронтенда

---

## 1. TypeUI — Design Context for AI Tools

**URL:** https://www.typeui.sh/
**GitHub:** 1.2k stars
**Цена:** Free (25 req/day) / Pro $30/mo

**Что делает:** Даёт AI-инструментам (Codex, Claude, Cursor) дизайн-контекст, промпты и системы для генерации красивого UI.

**Ключевые фичи:**
- 77 Design Skills (визуальные направления: Doodle, Artistic, Minimal)
- 449 UI Prompts (hero, pricing, navbar, sidebar, checkout)
- MCP интеграция — подключается напрямую к coding tools
- 5 вариаций UI (Pro), 3 cleanup loops

**Промпты по категориям:**
- Marketing: Navbars (13), Hero (25), Pricing (20)
- Application: Navbars (11), Sidebars (20), Shells (9)
- E-commerce: Banners (5), Checkout (4), Footers (8)

**Использование:**
```
# MCP подключение
# Или просто копируй промпты с сайта
```

---

## 2. nuqs — Type-safe URL State for React

**URL:** https://nuqs.dev/
**Размер:** 6kB gzipped
**Лицензия:** MIT

**Что делает:** Управление URL search params как React state. Type-safe, работает с Next.js, Remix, React Router, TanStack Router.

**Ключевые фичи:**
- API как `React.useState` — автоматическая синхронизация с URL
- Встроенные парсеры для строк, чисел, булевых
- `useQueryStates` для нескольких params одновременно
- Работает с React Server Components
- Поддержка `useTransition` для loading states

**Кто использует:** AutoGPT, Dify, shadcn-ui, Supabase, LobeHub, Sentry, Uniswap, Vercel

**Установка:**
```bash
npm install nuqs
```

**Пример:**
```tsx
import { useQueryState, parseAsString } from 'nuqs'

function SearchBar() {
  const [query, setQuery] = useQueryState('q', parseAsString)
  return <input value={query ?? ''} onChange={e => setQuery(e.target.value)} />
}
```

---

## 3. Font Trio — Font Pairings for shadcn/ui

**URL:** https://www.fonttrio.xyz/
**Цена:** Free

**Что делает:** Система шрифтовых пар из 3 шрифтов (heading + body + mono) для shadcn/ui. Одна команда — всё ставится.

**Категории:**
- Serif (editorial, elegant)
- Sans-serif (modern, clean)
- Display (bold, decorative)
- Mono (code, technical)

**Установка:**
```bash
npx shadcn@latest add https://www.fonttrio.xyz/r/playfair-display.json
```

**CSS Variables:**
```css
--font-heading: var(--font-playfair-display);
--font-body: var(--font-source-serif-4);
--font-mono: var(--font-jetbrains-mono);
```

---

## 4. Fancy Components — React Microinteractions

**URL:** https://www.fancycomponents.dev/
**GitHub:** https://github.com/danielpetho/fancy
**Цена:** Free, open source

**Что делает:** Библиотека готовых React-компонентов с анимациями и микроинтеракциями.

**Компоненты:**
- Image Trail ( след за курсором)
- Text Highlighter
- Gravity (физика текста)
- CSS Box
- Marquee along SVG Path

**Использование:**
```bash
npm install fancy-components
```

---

## 5. Better-T-Stack — TypeScript Project Scaffolding

**URL:** https://www.better-t-stack.dev/
**GitHub:** https://github.com/AmanVarshney01/create-better-t-stack
**Цена:** Free

**Что делает:** CLI для создания end-to-end type-safe TypeScript проектов. Интерактивный мастер конфигурации.

**Установка:**
```bash
bun create better-t-stack@latest
# или
npx create-better-t-stack@latest
```

**Спонсоры:** Neon ($200/mo), Clerk ($100/mo), Convex ($100/mo), Guillermo Rauch (Vercel)

**Стек по умолчанию:**
- Frontend: Next.js / Vite
- Backend: Hono / Elysia
- Database: Drizzle + PostgreSQL
- Auth: Clerk / Better Auth
- Deployment: Vercel / Docker

---

## Как использовать вместе

```
Better-T-Stack → создать проект (scaffold)
    ↓
Font Trio → установить шрифты (одна команда)
    ↓
nuqs → управление URL state (фильтры, поиск, пагинация)
    ↓
Fancy Components → анимации и микроинтеракции
    ↓
TypeUI → дизайн-контекст для AI (генерация UI через промпты)
```

**Порядок:** Scaffold → Fonts → State → Animations → AI Polish

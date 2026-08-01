# Better-T-Stack — TypeScript Project Scaffolding

## Что это
CLI для создания end-to-end type-safe TypeScript проектов.
Интерактивный мастер: выбираешь стек → он всё ставит.

## Установка и запуск

```bash
# Через bun (рекомендуется)
bun create better-t-stack@latest

# Через npx
npx create-better-t-stack@latest

# Через npm
npm create better-t-stack@latest
```

## Стек по умолчанию

```
Frontend:  Next.js (App Router)
Backend:   Hono
Database:  Drizzle + PostgreSQL (Neon)
Auth:      Better Auth
Deploy:    Vercel
```

## Варианты стека

### Frontend
| Опция | Описание |
|-------|----------|
| Next.js | App Router, RSC, Server Actions |
| Vite | SPA, быстрый dev server |
| React Native | Мобильные приложения |

### Backend
| Опция | Описание |
|-------|----------|
| Hono | Ультра-быстрый, edge-ready |
| Elysia | Bun-native, type-safe |
| Express | Классика,最大 ecosystem |
| Fastify | Быстрый, плагины |

### Database
| Опция | Описание |
|-------|----------|
| Drizzle | Type-safe ORM, миграции |
| Prisma | Популярный, GUI |
| Kysely | Type-safe query builder |

### Auth
| Опция | Описание |
|-------|----------|
| Better Auth | Простой, гибкий |
| Clerk | Hosted, UI компоненты |
| Lucia | Self-hosted, минималистичный |

## Примеры конфигураций

### SaaS Dashboard
```bash
bun create better-t-stack@latest my-saas
# Frontend: Next.js
# Backend: Hono
# Database: Drizzle + PostgreSQL
# Auth: Clerk
# Deploy: Vercel
```

### API-Only Backend
```bash
bun create better-t-stack@latest my-api
# Frontend: none
# Backend: Hono
# Database: Drizzle + SQLite
# Auth: Better Auth
# Deploy: Docker
```

### Full-Stack Mobile
```bash
bun create better-t-stack@latest my-app
# Frontend: React Native (Expo)
# Backend: Hono
# Database: Drizzle + PostgreSQL
# Auth: Better Auth
# Deploy: EAS
```

## После scaffold

```bash
cd my-project

# Установить шрифты
npx shadcn@latest add https://www.fonttrio.xyz/r/inter.json

# Добавить URL state
npm install nuqs

# Добавить анимации
npm install @fancy-components/image-trail

# Запустить dev
bun run dev
```

## Спонсоры (доказательство качества)
- Neon ($200/mo) — database
- Clerk ($100/mo) — auth
- Convex ($100/mo) — realtime
- Guillermo Rauch (Vercel founder) — $1,000

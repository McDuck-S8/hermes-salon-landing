---
name: frontend-toolkit
description: "Modern React/TypeScript frontend stack 2026 — scaffold, fonts, state, animations, AI design. Use when building new web projects, landing pages, SaaS dashboards, or any React frontend."
version: 1.1.0
tags: [react, typescript, frontend, ui, shadcn, nextjs]
---

# Frontend Toolkit 2026

## When to Use
- Building a new React/TypeScript project
- Need beautiful typography and animations
- Scaffolding a full-stack TS project
- AI-assisted UI generation

## The Stack (in order)

### 1. Scaffold: Better-T-Stack
```bash
bun create better-t-stack@latest
# Interactive wizard: frontend, backend, DB, auth, deploy
```
- **What:** CLI for end-to-end type-safe TS projects
- **Stack:** Next.js/Vite + Hono/Elysia + Drizzle + Clerk
- **Why:** Saves hours of config, enforces type safety across stack
- **Ref:** https://www.better-t-stack.dev/

### 2. Fonts: Font Trio
```bash
npx shadcn@latest add https://www.fonttrio.xyz/r/playfair-display.json
```
- **What:** 3-font pairings (heading + body + mono) for shadcn/ui
- **Categories:** Serif, Sans-serif, Display, Mono
- **CSS vars:** `--font-heading`, `--font-body`, `--font-mono`
- **Why:** Instant professional typography, one command
- **Ref:** https://www.fonttrio.xyz/

### 3. URL State: nuqs
```bash
npm install nuqs
```
- **What:** Type-safe URL search params as React state (6kB)
- **API:** `useQueryState('q', parseAsString)` — like useState but in URL
- **Works with:** Next.js (app+pages), Remix, React Router, TanStack Router
- **Used by:** AutoGPT, Dify, shadcn-ui, Supabase, Uniswap, Vercel
- **Ref:** https://nuqs.dev/

### 4. Animations: Fancy Components
```bash
npm install fancy-components
```
- **What:** Free React components with microinteractions
- **Components:** Image Trail, Text Highlighter, Gravity, CSS Box, Marquee along SVG Path
- **Ref:** https://www.fancycomponents.dev/
- **GitHub:** https://github.com/danielpetho/fancy

### 5. AI Design: TypeUI
- **What:** Design context for AI coding tools (Codex, Claude, Cursor)
- **Free:** 25 req/day, 1 design system, 1 variation
- **Pro:** $30/mo, unlimited, 5 variations, 3 cleanup loops
- **77 Design Skills** (Doodle, Artistic, Minimal, etc.)
- **449 UI Prompts** (hero, pricing, navbar, sidebar, checkout)
- **MCP integration** — connects directly to coding tools
- **Ref:** https://www.typeui.sh/

## Workflow
```
Better-T-Stack → scaffold project
    ↓
Font Trio → install fonts (one command)
    ↓
nuqs → manage URL state (filters, search, pagination)
    ↓
Fancy Components → animations and microinteractions
    ↓
TypeUI → AI-assisted UI generation via MCP
```

## Pitfalls
- **Font Trio only works with shadcn/ui** — if using plain CSS, install fonts manually via Google Fonts
- **nuqs is client-first** — shallow updates by default; set `shallow: false` to notify server for RSC re-render
- **TypeUI free tier is limited** — 25 req/day, 1 variation. For production work, Pro is needed
- **Fancy Components are React-only** — not available for Vue/Svelte
- **Better-T-Stack uses Bun** — install Bun first if not present

## Quick Reference

| Tool | Size | Cost | Key Feature |
|------|------|------|-------------|
| Better-T-Stack | CLI | Free | Full-stack TS scaffold |
| Font Trio | ~12KB | Free | 3-font pairing system |
| nuqs | 6kB | Free | URL state as React state |
| Fancy Components | varies | Free | React microinteractions |
| TypeUI | MCP | Free/$30 | AI design context |

# TypeUI — Design Context for AI Coding Tools

## Что это
TypeUI даёт AI-инструментам (Codex, Claude, Cursor) дизайн-систему,
чтобы генерировать красивый и консистентный UI.

## Установка MCP

### Для Claude Desktop
Добавить в `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "typeui": {
      "url": "https://mcp.typeui.sh/sse",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

### Для Cursor
Settings → MCP Servers → Add:
```
Name: TypeUI
URL: https://mcp.typeui.sh/sse
```

### Для Codex CLI
```bash
codex mcp add typeui --url https://mcp.typeui.sh/sse
```

## Использование без MCP (ручное)

### Промпт для генерации Landing Page:
```
Using TypeUI's "Minimal" design skill, create a landing page with:
- Hero section with gradient background
- 3-column pricing table
- FAQ accordion
- Footer with newsletter signup

Design rules:
- Font: Inter for body, Playfair Display for headings
- Colors: #0f172a background, #10b981 accent
- Border radius: 12px for cards
- Spacing: 8px grid system
```

### Промпт для Dashboard:
```
Using TypeUI's "Professional" design skill, create a dashboard with:
- Sidebar navigation (collapsible)
- Top bar with search and notifications
- 4 metric cards in a grid
- Data table with sorting and filtering
- Dark mode support

Design rules:
- Sidebar: 240px width, #0f172a background
- Cards: glass morphism effect, backdrop-blur
- Table: alternating row colors, hover highlight
```

## 77 Design Skills (популярные):

| Skill | Описание | Использование |
|-------|----------|---------------|
| Minimal | Чистый, минималистичный | 2469 раз |
| Artistic | Творческий, нестандартный | 148 раз |
| Doodle | Рисованный стиль | 99 раз |
| Professional | Деловой, корпоративный | 1000+ |
| Playful | Игривый, яркий | 500+ |
| Elegant | Элегантный, утончённый | 300+ |

## UI Prompts (категории):

### Marketing
- Navbars: 13 вариантов
- Hero Sections: 25 вариантов
- Pricing Tables: 20 вариантов
- Testimonials: 10 вариантов
- CTAs: 15 вариантов

### Application
- Sidebars: 20 вариантов
- Data Tables: 12 вариантов
- Forms: 15 вариантов
- Modals: 8 вариантов
- Charts: 10 вариантов

### E-commerce
- Product Cards: 10 вариантов
- Checkout: 4 варианта
- Cart: 6 вариантов
- Banners: 5 вариантов

## Пример MCP-запроса:

```
User: "Создай dashboard для арбитражного агента"

TypeUI MCP:
1. Загружает "Professional" design skill
2. Возвращает промпт:
   "Create a dark-themed dashboard with:
    - Sidebar with sections: Overview, Agents, Trades, Settings
    - Top metrics: AMR 95.6%, Revenue $4.78, Trades 1,247
    - Main area: real-time price chart
    - Color scheme: #0f172a bg, #10b981 success, #ef4444 danger
    - Border radius: 8px, shadows: subtle"
```

## Free vs Pro:

| | Free | Pro ($30/mo) |
|--|------|--------------|
| Requests | 25/day | Unlimited |
| Design Skills | 1 active | Unlimited |
| UI Variations | 1 | 5 |
| Cleanup Loops | 1 | 3 |
| MCP Access | ✅ | ✅ |

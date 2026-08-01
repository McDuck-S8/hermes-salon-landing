# Font Trio — Font Pairings for shadcn/ui

## Что это
Система шрифтовых пар из 3 шрифтов (heading + body + mono).
Одна команда — всё ставится в shadcn/ui проект.

## Установка

### Через npx (одна команда):
```bash
# Serif pair (editorial, elegant)
npx shadcn@latest add https://www.fonttrio.xyz/r/playfair-display.json

# Sans pair (modern, clean)
npx shadcn@latest add https://www.fonttrio.xyz/r/inter.json

# Display pair (bold, decorative)
npx shadcn@latest add https://www.fonttrio.xyz/r/space-grotesk.json
```

### Ручная установка:
```bash
npm install @fontsource/playfair-display @fontsource/source-serif-4 @fontsource/jetbrains-mono
```

### CSS Variables (в globals.css):
```css
:root {
  --font-heading: var(--font-playfair-display);
  --font-body: var(--font-source-serif-4);
  --font-mono: var(--font-jetbrains-mono);
}

/* Или для Tailwind v4 */
@theme {
  --font-heading: "Playfair Display", serif;
  --font-body: "Source Serif 4", serif;
  --font-mono: "JetBrains Mono", monospace;
}
```

### Tailwind конфиг (tailwind.config.ts):
```ts
import type { Config } from 'tailwindcss'

const config: Config = {
  theme: {
    extend: {
      fontFamily: {
        heading: ['var(--font-heading)', 'serif'],
        body: ['var(--font-body)', 'serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
    },
  },
}
export default config
```

## Готовые пары:

### Editorial (blog, magazine)
```bash
npx shadcn@latest add https://www.fonttrio.xyz/r/playfair-display.json
```
- Heading: Playfair Display
- Body: Source Serif 4
- Mono: JetBrains Mono

### Modern (SaaS, dashboard)
```bash
npx shadcn@latest add https://www.fonttrio.xyz/r/inter.json
```
- Heading: Inter
- Body: Inter
- Mono: JetBrains Mono

### Tech (developer tools)
```bash
npx shadcn@latest add https://www.fonttrio.xyz/r/space-grotesk.json
```
- Heading: Space Grotesk
- Body: Space Grotesk
- Mono: JetBrains Mono

## Использование в компонентах:

```tsx
// Heading
<h1 className="font-heading text-4xl font-bold">
  Заголовок
</h1>

// Body text
<p className="font-body text-lg leading-relaxed">
  Текст параграфа
</p>

// Code
<code className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">
  const x = 42
</code>
```

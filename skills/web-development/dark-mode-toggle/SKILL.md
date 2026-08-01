---
name: dark-mode-toggle
description: "Dark mode toggle with CSS custom properties, prefers-color-scheme, localStorage persistence, system preference detection, Tailwind integration. Load when implementing theme switching."
version: 1.0.0
tags: [dark-mode, theme, css, tailwind, prefers-color-scheme]
---

# Dark Mode Toggle

## CSS Custom Properties Approach

```css
:root {
  /* Light mode tokens */
  --color-bg: #ffffff;
  --color-text: #1a1a2e;
  --color-surface: #f8f9fa;
  --color-border: #e9ecef;
  --color-accent: #2563eb;
  --color-accent-hover: #1d4ed8;
  --color-muted: #6c757d;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
}

/* Dark mode overrides */
[data-theme="dark"] {
  --color-bg: #121212;
  --color-text: #e4e4e7;
  --color-surface: #1e1e1e;
  --color-border: #2d2d2d;
  --color-accent: #60a5fa;
  --color-accent-hover: #93c5fd;
  --color-muted: #a1a1aa;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.4);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.5);
}

/* System preference as default */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    --color-bg: #121212;
    --color-text: #e4e4e7;
    /* ... dark tokens ... */
  }
}

/* Apply tokens */
body {
  background: var(--color-bg);
  color: var(--color-text);
  transition: background 0.3s, color 0.3s;
}
```

### light-dark() alternative (simpler, no JS)
```css
:root {
  color-scheme: light dark;
  --color-bg: light-dark(#ffffff, #121212);
  --color-text: light-dark(#1a1a2e, #e4e4e7);
  --color-accent: light-dark(#2563eb, #60a5fa);
}
```

## JavaScript Toggle

```javascript
class ThemeManager {
  constructor() {
    this.storageKey = 'theme';
    this.init();
  }

  init() {
    const saved = localStorage.getItem(this.storageKey);
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (saved) {
      this.setTheme(saved);
    } else if (systemPrefersDark) {
      this.setTheme('dark');
    } else {
      this.setTheme('light');
    }

    // Listen for system changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem(this.storageKey)) {
        this.setTheme(e.matches ? 'dark' : 'light');
      }
    });
  }

  setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(this.storageKey, theme);

    // Update toggle button
    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
      toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
  }

  toggle() {
    const current = document.documentElement.getAttribute('data-theme');
    this.setTheme(current === 'dark' ? 'light' : 'dark');
  }
}

// Initialize
const themeManager = new ThemeManager();

// Toggle button
document.getElementById('theme-toggle')?.addEventListener('click', () => {
  themeManager.toggle();
});
```

### HTML toggle button
```html
<button id="theme-toggle" aria-label="Переключить тему" class="theme-toggle">
  🌙
</button>
```

### CSS toggle styling
```css
.theme-toggle {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
}
.theme-toggle:hover {
  transform: scale(1.1);
}
```

## Tailwind CSS Integration

```javascript
// tailwind.config.js
module.exports = {
  darkMode: ['class', '[data-theme="dark"]'],
  content: ['./src/**/*.{html,js,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: 'var(--color-bg)',
        text: 'var(--color-text)',
        surface: 'var(--color-surface)',
        border: 'var(--color-border)',
        accent: 'var(--color-accent)',
      }
    }
  }
}
```

```html
<!-- Now use dark: prefix -->
<div class="bg-bg text-text dark:bg-bg dark:text-text">
  <button class="dark:bg-surface dark:text-text">Toggle</button>
</div>
```

## React Hook

```javascript
import { useState, useEffect } from 'react';

function useTheme() {
  const [theme, setTheme] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme');
      if (saved) return saved;
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggle = () => setTheme(t => t === 'dark' ? 'light' : 'dark');
  return { theme, toggle };
}

// Usage
function ThemeToggle() {
  const { theme, toggle } = useTheme();
  return (
    <button onClick={toggle} aria-label="Переключить тему">
      {theme === 'dark' ? '☀️' : '🌙'}
    </button>
  );
}
```

## Dark Mode Design Guidelines

### Color adjustments
- **Background**: Don't use pure black (#000) — use #121212 or #1a1a1a (reduces eye strain)
- **Text**: Light gray (#e4e4e7) not white — reduces contrast fatigue
- **Surfaces**: Slightly lighter than background (#1e1e1e) for depth
- **Borders**: Subtle (#2d2d2d) — not invisible, but not jarring
- **Shadows**: Invert — use inner shadows or dark outlines instead of drop shadows

### Images in dark mode
```css
/* Auto-invert images in dark mode (for light-on-dark illustrations) */
@media (prefers-color-scheme: dark) {
  img:not([data-dark-invert="false"]) {
    filter: invert(1) hue-rotate(180deg);
  }
}
```

### SVG icons
```css
/* SVG icons that work in both modes */
svg {
  fill: currentColor;  /* inherits text color */
}
```

## Pitfalls
- **FOUC (Flash of Unstyled Content)** — set initial theme before CSS loads (inline script in `<head>`)
- **Pure black backgrounds** cause eye strain — use dark gray (#121212)
- **Inverting all images** breaks photos — exclude with `[data-dark-invert="false"]`
- **System preference race** — check `localStorage` before `prefers-color-scheme`
- **Transition flash** — disable transitions during initial theme setup
- **Form inputs** — dark mode inputs need different border/shadow treatment
- **Charts/graphs** — light colors may be invisible in dark mode (need dual palette)

# Multi-Language Portfolio Pattern

> Sidebar-layout agency portfolio with RU/UK/EN, dark/light theme, and category filters.
> Inspired by ovenpizza.ru — take this pattern, adapt it.

## Architecture

```
docs/index.html                         ← portfolio (root GitHub Pages)
  ├── index.html                        ← portfolio single page
  ├── client-a/                         ← client project 1
  ├── client-b/                         ← client project 2
  └── ...
```

## Key Components

### 1. CSS Theme Toggle

```css
:root {
  --bg: #f7f7f8;
  --surface: #fff;
  --border: #eaeaea;
  --text: #1a1a1a;
  --muted: #888;
  --accent: #6c5ce7;
  /* ... */
}
[data-theme="dark"] {
  --bg: #121216;
  --surface: #1c1c22;
  --border: #2a2a32;
  --text: #e8e8ee;
  --accent: #8b7cf7;
  /* ... */
}
```

### 2. Translations Object

```js
const LANG = {
  ru: { title: 'Веб-проекты', cat_salon: 'Салон красоты', ... },
  uk: { title: 'Веб-проєкти', cat_salon: 'Салон краси', ... },
  en: { title: 'Web Projects', cat_salon: 'Beauty Salon', ... }
};
```

### 3. Projects Data

```js
const PROJECTS = [
  {
    id: 'fargo',
    cat: 'salon',
    url: 'fargo/',
    img: 'https://images.pexels.com/photos/3992875/pexels-photo-3992875.jpeg?auto=compress&cs=tinysrgb&w=600&h=400&fit=crop',
    name: {
      ru: 'Fargo — салон красоты на Позняках',
      uk: 'Fargo — салон краси на Позняках',
      en: 'Fargo — Beauty Salon in Poznyaky'
    },
    desc: { /* translations */ },
    meta: { ru: 'Киев · 2026', uk: 'Київ · 2026', en: 'Kyiv · 2026' }
  }
];
```

### 4. Render Function

Renders projects grouped by category, with each card containing:
- `<img>` thumbnail (Pexels hero image, NOT screenshot — screenshots require browser and break)
- Category tag
- Project name (translated)
- Description (translated)
- Meta (translated)
- "Open site" button

### 5. Category Filter

Event delegation on sidebar list:
```js
document.getElementById('catList').addEventListener('click', e => {
  const a = e.target.closest('a');
  if (!a) return;
  // toggle active class, filter project sections
});
```

## Workflow

1. **Study a reference** (ovenpizza.ru, obys.agency, etc.) — sidebar + cards pattern
2. **Scan demos/** for existing projects before writing cards
3. **Deploy each demo** to `docs/{client}/`
4. **Add project to PROJECTS array** with Pexels hero image
5. **Verify** all URLs return 200

## Before/After Option

For individual project showcases, create a **split-screen comparison page** (`portfolio.html`) that loads old_site.html (stale parody) vs the real landing page side-by-side with synced scroll. See `references/before-after-comparison.md` under the same umbrella skill.

## Project Page Template

Each deployed demo (`docs/{client}/index.html`) currently has its own independent design. Consider wrapping them in a consistent header/footer from the portfolio, or generating from a shared template.

## Pitfalls

- Category `<a>` links MUST have `href="#"` or browser tool can't click them by ref
- Theme state persists in `localStorage` so refresh keeps the theme
- Language button uses `currentLang` variable; re-renders projects on switch
- Don't use actual screenshots as thumbnails — browser tool may not be available. Use Pexels hero images matching the niche
- Each new client = `docs/{client}/` folder AND a new entry in PROJECTS array

## Pexels Image IDs by Category

These are verified to work with the `auto=compress&cs=tinysrgb&w=600&h=400&fit=crop` URL params:

| Category | Pexels ID | What it shows |
|----------|-----------|---------------|
| Salon | 3992875 | Salon interior |
| Salon | 7750114 | Beauty treatment |
| Salon | 5069603 | Hair styling |
| Café | 1857157 | Pastry/dessert |
| Auto | 3807320 | Car repair |
| Clinic | 40568 | Medical/doctor |
| Funeral | 7241361 | Peaceful nature |

Format: `https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg?auto=compress&cs=tinysrgb&w=600&h=400&fit=crop`

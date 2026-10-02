# Luxe Salon — Studio-Quality Demo Website

> Premium beauty salon website with dark theme + gold accents. Built to look like $5,000 studio work.

## Quick Start

Simply open `index.html` in a browser. No build tools required — pure HTML/CSS/JS.

## Features

### Design
- **Dark Theme** — Rich `#0f0f14` background with `#d4af37` gold accents
- **Typography** — Cormorant Garamond (display) + Inter (body) — elegant serif meets modern sans
- **Animations** — Scroll reveals, parallax hero, floating particles, animated counters
- **Custom Cursor** — Interactive cursor follower on desktop
- **Preloader** — Branded loading animation

### Sections
1. **Hero** — Full-viewport with parallax, animated stats counter, particle effects
2. **Services** (6 cards) — Hair, Nails, Skin, Makeup, Body, Bridal — with prices & durations
3. **Gallery** — Masonry-style grid with hover zoom effects
4. **Booking** — Full appointment form with validation
5. **Testimonials** (6 cards) — Star ratings, quotes, avatars
6. **Contact** — Address, phone, email, hours + Google Maps embed
7. **Footer** — Multi-column with social links

### Technical
- **Zero dependencies** — No frameworks, no build tools
- **Mobile responsive** — Breakpoints at 1024px, 768px, 480px
- **Performance** — Lazy-loaded images, passive scroll listeners, CSS-only animations
- **Accessibility** — Semantic HTML, ARIA labels, keyboard navigation
- **SEO** — Meta tags, proper heading hierarchy, alt text

## File Structure

```
salon/
├── index.html          # Main HTML (all sections)
├── css/
│   └── style.css       # Complete stylesheet (~23KB)
├── js/
│   └── main.js         # All interactions (~7KB)
└── README.md           # This file
```

## Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--color-bg` | `#0f0f14` | Main background |
| `--color-bg-light` | `#14141b` | Alternate sections |
| `--color-bg-card` | `#1a1a24` | Card backgrounds |
| `--color-gold` | `#d4af37` | Primary accent |
| `--color-gold-light` | `#e8c84a` | Hover states |
| `--color-text` | `#e8e6e3` | Primary text |
| `--color-text-muted` | `#8a8a92` | Secondary text |

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Credits

- Fonts: [Google Fonts](https://fonts.google.com)
- Images: [Unsplash](https://unsplash.com) (free license)
- Icons: Custom SVG inline icons

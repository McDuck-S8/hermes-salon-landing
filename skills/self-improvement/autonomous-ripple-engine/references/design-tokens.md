# Design Tokens — Autonomous Ripple Engine Dashboard

All tokens sourced from `ui-ux-pro-max` skill, adapted for dark autonomous dashboard.

## Color Palette

### Base (Dark Theme)
```css
--bg:           #0A0E17;    /* Primary background */
--bg-secondary: #111827;    /* Cards, panels */
--bg-tertiary:  #1F2937;    /* Inputs, borders */
--text:         #F8FAFC;    /* Primary text */
--text-dim:     #94A3B8;    /* Secondary text */
--text-muted:   #64748B;    /* Labels, disabled */
--border:       #1E293B;    /* Default borders */
--border-focus: #3B82F6;    /* Focus rings */
```

### Accent Colors
```css
--accent-cyan:    #06B6D4;  /* Info, primary actions */
--accent-green:   #10B981;  /* Success, unlocked keys */
--accent-amber:   #F59E0B;  /* Warning, medium priority */
--accent-purple:  #8B5CF6;  /* High priority, mature keys */
--accent-red:     #EF4444;  /* Critical, conflicts */
```

### Priority Tier Gradients (Card Backgrounds)
```css
--card-critical: linear-gradient(135deg, #DC2626 0%, #991B1B 100%);
--card-high:     linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%);
--card-medium:   linear-gradient(135deg, #1E3A5F 0%, #1E4A7F 100%);
--card-low:      linear-gradient(135deg, #1F2937 0%, #111827 100%);
```

### Priority Tier Glows (Hover States)
```css
--glow-critical:  0 0 32px rgba(220, 38, 38, 0.35);
--glow-high:      0 0 28px rgba(139, 92, 246, 0.3);
--glow-medium:    0 0 20px rgba(14, 165, 233, 0.25);
--glow-low:       0 0 12px rgba(100, 116, 139, 0.15);
```

### Priority Tier Borders
```css
--border-critical: #EF4444;
--border-high:     #8B5CF6;
--border-medium:   #06B6D4;
--border-low:      #1E293B;
```

## Spacing Scale
```css
--space-xs:  4px;
--space-sm:  8px;
--space-md:  16px;
--space-lg:  24px;
--space-xl:  32px;
--space-2xl: 48px;
```

## Border Radius
```css
--radius-sm:  6px;
--radius-md:  10px;
--radius-lg:  16px;
--radius-xl:  20px;
```

## Shadows
```css
--shadow-sm:  0 1px 2px rgba(0,0,0,0.3);
--shadow-md:  0 4px 12px rgba(0,0,0,0.4);
--shadow-lg:  0 8px 32px rgba(0,0,0,0.5);
--shadow-glow-cyan:  0 0 24px rgba(6, 182, 212, 0.25);
--shadow-glow-green:  0 0 24px rgba(16, 185, 129, 0.25);
--shadow-glow-purple: 0 0 24px rgba(139, 92, 246, 0.25);
```

## Typography
```css
--font-mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace;
--font-display: 'Space Grotesk', sans-serif;
--font-size-heading: clamp(1.5rem, 3vw, 2.25rem);
--font-size-subheading: clamp(1rem, 2vw, 1.25rem);
--font-size-body: 0.875rem;
--font-size-small: 0.75rem;
```

## Animation
```css
--transition-fast:  0.15s ease;
--transition-normal: 0.25s ease;
--transition-slow:  0.35s ease;

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes pulseGlow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
```

## Card Sizing (Visual Weight → CSS)

| Visual Weight | CSS Class | Min-Width |
|---------------|-----------|-----------|
| ≥ 80          | `.stone-large` | 380px |
| 60-79         | `.stone-medium` | 340px |
| < 60          | `.stone-small` | 300px |

## Staggered Entrance
```css
.stone-card:nth-child(1) { animation-delay: 0ms; }
.stone-card:nth-child(2) { animation-delay: 50ms; }
.stone-card:nth-child(3) { animation-delay: 100ms; }
.stone-card:nth-child(4) { animation-delay: 150ms; }
.stone-card:nth-child(5) { animation-delay: 200ms; }
.stone-card:nth-child(6) { animation-delay: 250ms; }
```

## Usage in ripple_engine.py

The `_build_html()` method injects these as CSS custom properties in `:root` and applies tier classes:
- `tier-critical` → `--card-critical` + `--glow-critical` + `--border-critical`
- `tier-high` → `--card-high` + `--glow-high` + `--border-high`
- `tier-medium` → `--card-medium` + `--glow-medium` + `--border-medium`
- `tier-low` → `--card-low` + `--glow-low` + `--border-low`
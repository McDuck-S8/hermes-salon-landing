---
name: GLAM Beauty Salon
description: Premium beauty salon landing page. Earth-toned elegance with terracotta anchor. Warm, refined, expensive-feeling. Dark and light modes.
colors:
  # Brand
  terracotta: "oklch(55% 0.145 40)" # primary anchor — warm clay
  terracotta-soft: "oklch(70% 0.09 42)" # hover, secondary fills
  terracotta-deep: "oklch(40% 0.10 36)" # deep shadow, dark mode accent

  # Surfaces
  paper: "oklch(96% 0.008 75)" # light page ground — warm-tinted but not sand
  paper-deep: "oklch(93% 0.01 75)" # inset surface in light mode
  ink: "oklch(12% 0.01 75)" # body text light mode

  # Dark
  dark-surface: "oklch(10% 0.008 80)" # dark mode page ground
  dark-raised: "oklch(14% 0.008 80)" # dark mode cards/panels
  dark-text: "oklch(88% 0.005 80)" # dark mode body text
  dark-muted: "oklch(65% 0.005 80)" # dark mode secondary text

  # Accents
  gold-warm: "oklch(78% 0.105 70)" # accent / CTAs
  gold-pale: "oklch(88% 0.06 72)" # hover on gold
  rose: "oklch(70% 0.09 20)" # secondary accent (testimonials, badges)
  mint: "oklch(75% 0.07 150)" # success / guarantee signals
  graphite: "oklch(25% 0.005 75)" # borders in light mode
  dark-rule: "oklch(25% 0.005 80 / 0.15)" # borders in dark mode

typography:
  display:
    fontFamily: "'Playfair Display', 'DM Serif Display', Georgia, serif"
    fontSize: "clamp(2.2rem, 5.5vw, 4.5rem)"
    fontWeight: 500
    letterSpacing: "-0.01em"
    lineHeight: 1.08
  heading:
    fontFamily: "'Playfair Display', Georgia, serif"
    fontSize: "clamp(1.5rem, 3vw, 2.2rem)"
    fontWeight: 500
    letterSpacing: "0"
    lineHeight: 1.2
  body:
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.65
  caption:
    fontFamily: "'Inter', system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
  accent:
    fontFamily: "'DM Serif Display', Georgia, serif"
    fontSize: "1.2rem"
    fontWeight: 400
    fontStyle: italic
  button:
    fontFamily: "'Inter', system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 600
    letterSpacing: "0.02em"

spacing:
  xs: "8px"
  sm: "16px"
  md: "24px"
  lg: "40px"
  xl: "64px"
  xxl: "96px"

rounded:
  sm: "6px"
  md: "10px"
  lg: "16px"
  xl: "20px"
  pill: "999px"

components:
  button-primary:
    backgroundColor: "{colors.terracotta}"
    textColor: "oklch(98% 0 0)"
    rounded: "{rounded.pill}"
    padding: "16px 48px"
  button-primary-hover:
    backgroundColor: "{colors.terracotta-soft}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.terracotta}"
    borderColor: "{colors.terracotta}"
    border: "1.5px solid"
    rounded: "{rounded.pill}"
    padding: "16px 48px"
  card:
    backgroundColor: "oklch(98% 0.005 75)"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  input-text:
    backgroundColor: "oklch(98% 0.005 75)"
    textColor: "{colors.ink}"
    borderColor: "{colors.graphite}"
    rounded: "{rounded.sm}"
    padding: "14px 16px"
  nav-link:
    textColor: "{colors.ink}"
  hero-section:
    backgroundColor: "oklch(94% 0.015 70)"
---
# Design System: GLAM Beauty Salon

## Overview

Тёплая, дорогая, но не крикливая эстетика. Terracotta как якорный цвет (глина/терракота — природный, дорогой, не розовый). Серьезная гарнитура Playfair Display для заголовков, чистый Inter для тела. Никаких розово-золотых градиентов — это AI-клон.

## Color Strategy

**Restrained** — один насыщенный цвет (terracotta) занимает ~20% поверхностей. Всё остальное — tinted neutrals в сторону terracotta (hue ~75).

### Light Mode
- Body bg: теплый, но не cream — chroma 0.008, hue 75
- Cards: на полтона светлее фона
- Акцент: terracotta на кнопках и ключевых элементах
- Текст: высокий контраст (4.5:1+)

### Dark Mode
- Body bg: почти чёрный с тёплым undertone 
- Raised surface: на 4% светлее фона
- Акцент: terracotta soft для readability на тёмном

## Typography

- **Заголовки**: Playfair Display — женственно, дорого, с характером
- **Тело**: Inter — чисто, читабельно, не отвлекает
- **Акцентный курсив**: DM Serif Display для цитат и гарантий
- **Кнопки**: Inter 600, небольшой tracking

## Layout

- Hero с крупной типографикой и контрастным CTA
- Benefits в bento-сетке (2+2) вместо 4 одинаковых карт
- Услуги: grid с price tag, hover с тенью
- Отзывы: асимметричные, с фото-аватарами
- Форма: два столбца на десктопе, один на мобильном

## Motion

- Scroll-triggered появление элементов (fade + translateY, 600ms ease-out)
- Hover на карточках: translateY(-4px) + тень
- Таймер обратного отсчёта — непрерывный
- prefers-reduced-motion: все анимации отключаются

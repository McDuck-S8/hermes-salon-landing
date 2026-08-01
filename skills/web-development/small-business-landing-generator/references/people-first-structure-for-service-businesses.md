# People-First Structure for Service Businesses

## Why This Exists

After 7 rejected iterations for a beauty salon landing page (Fargo, Darnytsia), the breakthrough came from switching the **content model** from "what we do" (services) to "who we are" (people). The user said "всё одно и то же, цвета разные" — same skeleton, different palette.

The default service-business template:
```
nav → hero → 3 service cards → gallery → 3 testimonial cards → price table → footer
```

This template fails because it treats the business as a menu, not a relationship.

## The People-First Pattern

Instead of listing services first, introduce the **masters/team** as the primary content. Each person gets their own section with:

- **Photo** — real face, not stock (local download, not URL dependency)
- **Name + role + years** — establishes authority
- **Personality bio** — not what they do, but who they are: "Катя замішує кольори як художник"
- **Tags** — specialities as chips
- **Direct booking** — CTA per master

The hierarchy becomes:
```
master 1 → master 2 → master 3 → atmosphere → prices → testimonials → invitation
```

## When to Use People-First

| Niche | Default Template | People-First Alternative |
|-------|-----------------|--------------------------|
| Salon/Barber | services (haircut, color...) → gallery → prices | masters with photos → each person's style → atmosphere |
| Dental clinic | services (cleaning, implant...) → team → prices | each doctor's approach → specialisation → patient experience |
| Massage/Wellness | price list → services | each therapist's method → what they treat best → atmosphere |
| Auto repair | services → price list | each mechanic's expertise (engine, body, electrical) |
| Yoga/Fitness | schedule → pricing | each instructor's style (vinyasa, yin, power) |

## Implementation Guide

### 1. Hero — invitation, not sales pitch

```
Instead of:  "Лучший салон в Дарнице"
Use:        "Заходь, як до подруги"
```

The hero should convey **welcome**, not superiority. The best test: would the user feel comfortable walking in alone?

### 2. Masters — each one is a spread

```html
<div class="master">
  <img src="master-1.jpg" alt="Катерина">
  <div class="name">Катерина</div>
  <div class="role">Колорист · 9 років</div>
  <div class="bio">Катя замішує кольори як художник.</div>
  <div class="tags"><span>Air Touch</span><span>Балаяж</span></div>
</div>
```

Key rules:
- **Real photo or bust** — no placeholder icons for production. If photo unavailable, use initial fallback (e.g., colored circle with first letter).
- **Years of experience** — social proof baked into each person.
- **Personality bio** — not generic "профессионал своего дела". Specific: "не питає 'як хочете?' — вона питає 'як ти живеш?'"

### 3. Atmosphere — show the space, not a gallery

Instead of a generic photo grid, curate the gallery to answer: **"What does it FEEL like to be here?"**

- Wide hero shot of the interior (light, space, mood)
- Detail shots of workstations (clean, organized, tools visible)
- Action shots (stylist working, client relaxing)
- No generic nature/phone stock photos

### 4. Prices — honest, not hidden

People-first pricing:
- List prices **clearly**, not buried behind "записатись"
- Use simple format: service name + price, one per line
- No fake discounts, no "от X" without context
- If price range, be explicit (e.g., "від 1 200 грн" for complex services)

### 5. Testimonials — named faces, not quotes

```html
<div class="test">
  <div class="stars">★★★★★</div>
  <div class="text">"Ходжу до Fargo вже два роки."</div>
  <img src="user.jpg" alt="Ірина"> <span>Ірина</span>
</div>
```

Real names, real photos. Even if the photo is small (32-36px). Generic "Клиент" without face = weak social proof.

## Palette Direction by Emotional Tone

| User request | Palette | Base | Accent | Typography |
|---|---|---|---|---|
| "Молодість, драйв" | Coral + Teal | #ff4777 / #0a6e6e | #ffbe3f | Advent Pro 900 (bold display) |
| "Внутрішня впевненість" | Glow + Gold | #e0755a / #d4a05a | #f5ede4 | Unbounded + Inter |
| "По домашньому, все свои" | Terracotta + Olive | #b86b4a / #5a6b4a | #f0e7dd | Playfair Display + Inter |
| "Енергія, краса" | Hot pink + Sage | #ff8fab / #6b9e7a | #ffbe3f | Outfit (bold) + Inter |

## Anti-Patterns

- ❌ "Послуги" as the first section — you're a menu, not a salon. People choose masters, not services.
- ❌ Generic team photos — if you must use stock, at least match the ethnic/gender demographic of the real staff.
- ❌ "Про нас" page hidden in nav — people-first means the about IS the homepage.
- ❌ Prices buried behind booking — perceived as hiding costs. Liste prices on the same page as booking CTA.
- ❌ Dark/edgy palette for personal services — reads as luxury or funeral, not warm welcome. Stick to light/warm bases.

## Source Case Study

Full creative journey documented in `skills/self-improvement/vibe-mode/references/fargo-creative-breakthrough.md` (v1-v8, 7 rejections, breakthrough pattern).

# User-Perspective Validation in Salon Lumiere Builder

**Date:** 2026-07-18
**Context:** Applied the 4-question user-perspective framework to Fargo beauty salon landing page build.

## The 4 Questions Applied

| # | Question | Fargo Answer |
|---|----------|--------------|
| 1 | **Who?** | Жінка 28-45 років, Київ (Позняки), шукає стрижку/колористику/манікюр. Має роботу, обмежений час, хоче бачити портфоліо майстра ДО візиту. |
| 2 | **5-sec understanding?** | Fargo — салон на Позняках. Чесні ціни на сайті, портфоліо майстрів, запис онлайн за 30 сек. Без дзвінків. |
| 3 | **What action?** | Натисне 'Записатися онлайн' (золота кнопка в герої) → вибере послугу → дату → час → відправить форму. |
| 4 | **Why?** | Устала від сюрпризів у чеку. Хоче бачити роботу Олени (колорист) перед візитом, знати ціну наперед, записатися без дзвінків адміністратору. |

## How It Shaped the Landing

| Element | Before (Generic) | After (User-Perspective) |
|---------|------------------|---------------------------|
| Hero headline | "Салон краси Fargo" | "Салон краси Fargo — чесні ціни, портфоліо майстрів, запис за 30 секунд" |
| Hero subtext | "Ласкаво просимо до нашого салону" | "Устали від сюрпризів у чеку? Тут бачите роботу майстра до візиту, знаєте ціну наперед і записуєтесь онлайн без дзвінків." |
| CTA buttons | "Записатися", "Позвонити" | "📅 Записатися онлайн" (primary), "📞 Подзвонити: +38 (044) 123-45-67" (secondary) |
| Trust badges | Generic "Quality", "Experience" | "✓ 50+ робіт у портфоліо кожного майстра", "✓ Ціна на сайті = ціна в салоні", "✓ Безкоштовна консультація колориста" |
| Master cards | Name + title only | Name + spec + bio + "Переглянути портфоліо →" link + photo placeholder |
| Booking form | Generic fields | Service select (with prices), Master select (optional), Date + Time, Name, Phone |

## Validation Gates (Added to SKILL.md)

```python
# Before building any salon landing:
required = ['who', 'five_sec', 'action', 'why']
for q in required:
    assert params['user_perspective'][q], f'Missing user_perspective.{q}'
```

## Session Fixes Logged

- `references/salon-landing-fix-2026-07-18.md` — Logo visibility (gold + text-shadow), hero padding 160px (nav clearance), nav structure (5 links + 2 action buttons), master photos with `<img>` + emoji fallback, solid nav background from load
- `references/social-preview-fixes.md` — OG image branded text card (Wix logo was black placeholder), platform-branded footer icons (not emoji)

## Anti-Pattern Caught

**Pattern:** Building for the salon owner (features, services list, "about us")
**Fix:** Building for the CLIENT (pain points, trust signals, frictionless booking)

The 4-question framework forces this flip automatically — if you can't answer Q4 from the client's pain, the artifact is wrong.
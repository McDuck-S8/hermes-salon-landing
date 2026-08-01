---
name: user-perspective
description: "Force user-centric perspective before creating ANY artifact. 4 mandatory questions."
version: 1.0.0
category: self-improvement
tags: [perspective, user-centric, artifact-validation, anti-self-referential]
requires: []
provides: [validate_artifact_perspective]
---

# User Perspective Skill

## The Core Rule

**Before creating ANY artifact (landing page, report, script, dashboard, email, etc.), you MUST answer these 4 questions. If you cannot answer them specifically, you are building for yourself, not the user.**

## The 4 Questions

| # | Question | Wrong Answer | Right Answer |
|---|----------|--------------|--------------|
| 1 | **Who will see this?** | "Users", "Target audience", "Customers" | "24-year-old Rahul in Mumbai, plays Free Fire on his Redmi Note, earns ₹15k/month" |
| 2 | **What must they understand in 5 seconds?** | "Our value proposition", "The offer details" | "I can get 500 Free Fire diamonds FREE right now" |
| 3 | **What must they do?** | "Convert", "Engage", "Click through" | "Tap the big orange button that says 'CLAIM 500 DIAMONDS'" |
| 4 | **Why should they do it?** | "Because it's a good offer", "High EPC" | "He's stuck on Level 47, needs diamonds to upgrade his gun, has ₹0 to spend" |

## Validation Checklist

Before outputting ANY artifact, verify:

- [ ] Q1: Specific person with context (name, location, device, situation)
- [ ] Q2: One sentence, zero jargon, matches their mental model
- [ ] Q3: Single visible action, obvious on the page
- [ ] Q4: Their pain/desire, not your metric

## Anti-Patterns to Catch

| Pattern | Signal | Fix |
|---------|--------|-----|
| "Dashboard for monitoring" | Built for operator, not user | Who actually logs in? What do THEY need? |
| "Professional design" | Aesthetic over function | Does it answer Q2 in 5 seconds? |
| "Best practices applied" | Generic, not specific | Best for WHO? |
| "My constraints" (no KYC, Crimea, etc.) | Internal constraints leaked | User doesn't care about your constraints |

## Usage

```python
from skills.user_perspective import validate_perspective

# Before creating artifact
validate_perspective(
    artifact_type="landing_page",
    vertical="gaming",
    geo="IN",
    persona="Rahul, 24, Mumbai, Free Fire player",
    q1="Rahul, 24, Mumbai, plays Free Fire on Redmi Note 12",
    q2="Get 500 Free Fire diamonds FREE — no payment, no survey",
    q3="Tap big orange 'CLAIM 500 DIAMONDS' button",
    q4="Stuck on Level 47, needs diamonds for gun upgrade, has ₹0"
)
```

## Enforcement

This skill is MANDATORY for:
- All landing pages
- All user-facing reports/dashboards
- All emails/messages to real users
- All creative artifacts

If you cannot answer the 4 questions → STOP. Do not create the artifact.

## References
- `references/github-pages-deploy-standard.md` — GitHub Pages deploy structure, naming rules, pre-deploy checklist, and Fargo Beauty Salon case study

---

## GitHub Pages Deploy Standard (Added 2026-07-18)

After creating ANY landing page or public artifact, deploy per this structure:

```
docs/
├── arbitrage/                    # All CPA/arbitrage landings
│   ├── gaming/
│   │   └── {offer}-{key-feature}/    # e.g., freefire-500-diamonds/
│   │       └── index.html
│   ├── fintech/
│   │   └── {offer}-{key-feature}/    # e.g., actionpay-card/
│   │       └── index.html
│   └── content/
│       └── {offer}-{key-feature}/    # e.g., cpagrip-unlock/
│           └── index.html
├── portfolio/                    # Portfolio/demo work
│   └── {project-name}/           # e.g., beauty-salon/
│       └── index.html
└── tools/                        # Public tools
    └── {tool-name}/
        └── index.html
```

**Naming rules:**
- One landing = one folder. Folder name: `{offer}-{key-feature}` (e.g., `freefire-500-diamonds`, `actionpay-card`, `cpagrip-unlock`)
- Only `index.html`. No `landing1.html`, `final.html`, `new_version.html`
- Categories don't mix: arbitrage landings in `docs/arbitrage/`, portfolio in `docs/portfolio/`, tools in `docs/tools/`

**Pre-deploy checklist:**
1. Run `python scripts/approval_policies.py <folder>` — must exit 0 (no private data leaks)
2. Open in browser — verify renders correctly
3. `git add <folder> && git commit -m "Deploy <description>" && git push`
4. Report live URL: `https://{username}.github.io/{repo}/{category}/{folder}/`

**Live URL template:** `https://mcduck-s8.github.io/hermes-salon-landing/arbitrage/gaming/freefire-500-diamonds/`

---

## Fargo Beauty Salon Case Study (Added 2026-07-18)

**Persona:** Жінка 28-45 років, Київ (Позняки), шукає стрижку/колористику/манікюр. Має роботу, обмежений час, хоче бачити портфоліо майстра ДО візиту.

**Q1 (Who):** Олена, 34, Київ (Позняки), менеджер проєктів, іде до салону раз у 3 тижні
**Q2 (5-sec):** "Fargo — салон на Позняках. Чесні ціни на сайті, портфоліо майстрів, запис онлайн за 30 сек. Без дзвінків."
**Q3 (Action):** Натисне **"Записатися онлайн"** (золота кнопка в герої) → вибере послугу → дату → час → відправить форму
**Q4 (Why):** Устала від сюрпризів у чеку. Хоче бачити роботу Олени (колорист) перед візитом, знати ціну наперед, записатися без дзвінків адміністратору

**Deployed to:** `docs/portfolio/beauty-salon/index.html` → `https://mcduck-s8.github.io/hermes-salon-landing/portfolio/beauty-salon/`

---

## Critical UI Pitfalls from Beauty Salon Landing (2026-07-18 Session)

### 1. Logo Invisible on Transparent Nav
**Problem:** Nav background was transparent initially (`rgba(10,10,10,0)`), logo used `color: var(--text)` (white) → logo invisible on hero background.
**Fix:** Nav MUST have solid background from load:
```css
nav {
    background: rgba(10,10,10,0.85);  /* Solid from start */
    backdrop-filter: blur(20px) saturate(1.2);
    border-bottom: 1px solid var(--glass-border);
}
nav.scrolled { background: rgba(10,10,10,0.95); }
```
**Rule:** Never rely on scroll to add background. Hero content scrolls UNDER nav immediately.

### 2. Duplicate Nav Links
**Problem:** Nav had both `<li><a href="#booking">Запис онлайн</a></li>` in center list AND `<a href="#booking" class="nav-cta">Записатися онлайн</a>` on right → confusing UX.
**Fix:** Center list = section anchors only (Послуги, Майстри, Відгуки, Контакти). Right actions = CTA button + phone link ONLY.

### 3. Hero Padding Too Small → Title Cut Off
**Problem:** `padding-top: 120px` on hero not enough for fixed nav (80px) + visual breathing room → h1 clipped.
**Fix:** `padding-top: 160px` minimum for fixed nav layouts.

### 4. Master Photos with Placeholder Fallback
**Pattern:** Use real photo URLs with inline `onerror` fallback to emoji:
```html
<div class="master-photo">
  <img src="https://via.placeholder.com/300x300/1a1a1a/C9A96E?text=Olena" 
       alt="Олена Ковальчук" 
       onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
  <span class="placeholder" style="display:none;">👩‍🦰</span>
</div>
```
**CSS:** `.master-photo { aspect-ratio: 1; overflow: hidden; background: var(--bg2); } .master-photo img { width: 100%; height: 100%; object-fit: cover; } .placeholder { font-size: 3rem; color: var(--gold)44; }`

### 5. Phone Link in Nav Actions
**Pattern:** Second nav action = `tel:` link with phone icon, NOT a button:
```html
<a href="tel:+380441234567" class="nav-phone">📞 +38 (044) 123-45-67</a>
```
Styled as subtle pill, hover → gold.

### 6. Mobile Nav Must Also Be Solid
**Fix:** `@media(max-width:768px)` nav gets `background: rgba(10,10,10,0.95)` immediately — no transparent mobile nav ever.
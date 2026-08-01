# GitHub Pages Deploy Standard

## Structure
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

## Naming Rules
- One landing = one folder. Folder name: `{offer}-{key-feature}` (e.g., `freefire-500-diamonds`, `actionpay-card`, `cpagrip-unlock`)
- Only `index.html`. No `landing1.html`, `final.html`, `new_version.html`
- Categories don't mix: arbitrage landings in `docs/arbitrage/`, portfolio in `docs/portfolio/`, tools in `docs/tools/`

## Pre-Deploy Checklist
1. Run `python scripts/approval_policies.py <folder>` — must exit 0 (no private data leaks)
2. Open in browser — verify renders correctly
3. `git add <folder> && git commit -m "Deploy <description>" && git push`
4. Report live URL: `https://{username}.github.io/{repo}/{category}/{folder}/`

## Live URL Template
`https://mcduck-s8.github.io/hermes-salon-landing/arbitrage/gaming/freefire-500-diamonds/`

## Case Study: Fargo Beauty Salon (2026-07-18)

### Persona
- **Who:** Жінка 28-45 років, Київ (Позняки), шукає стрижку/колористику/манікюр. Має роботу, обмежений час, хоче бачити портфоліо майстра ДО візиту.
- **5-sec:** "Fargo — салон на Позняках. Чесні ціни на сайті, портфоліо майстрів, запис онлайн за 30 сек. Без дзвінків."
- **Action:** Натисне **"Записатися онлайн"** (золота кнопка в герої) → вибере послугу → дату → час → відправить форму
- **Why:** Устала від сюрпризів у чеку. Хоче бачити роботу Олени (колорист) перед візитом, знати ціну наперед, записатися без дзвінків адміністратору

### Deployed To
- `docs/portfolio/beauty-salon/index.html`
- Live: `https://mcduck-s8.github.io/hermes-salon-landing/portfolio/beauty-salon/`

### Verification
```
python scripts/approval_policies.py docs/portfolio/beauty-salon/
✅ CLEAN — 1 files scanned, 0 violations
```
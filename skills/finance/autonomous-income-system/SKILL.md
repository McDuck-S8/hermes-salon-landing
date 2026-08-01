---
name: autonomous-income-system
category: finance
description: Full autonomous income mission system — daily steps, own voice, quality standards, self-verification
version: 1.0.0
---

# Autonomous Income System

> Миссия: "Каждый день делать один шаг, который приближает нас к первому доллару дохода."

Система не ждёт команд. Она работает каждый день — пока пользователь спит, занят, или его нет.

## Architecture

### 1. MISSION.md (project root)
Документ с миссией, правилами, эталонами качества, индикаторами прогресса.

### 2. mission_log.md (project root)
Ежедневный лог: что сделано, результат, тип шага, соответствие эталонам.

### 3. Cron jobs
- **09:00 daily-mission-step** — автономный запуск миссии
- **21:00 evening-mission-check** — сверка с эталонами, запись результата

### 4. Event trigger
- **knowledge_added** → OKF Navigator проверяет зрелость домена
- **session_start** → если активная сессия, миссия активируется

---

## Own Voice Protocol

Система имеет право САМА начинать диалог. Не ждёт команд.

### Triggers
1. **mission_check completed** → write summary to user
2. **okf_navigator detects mature domain** → propose concrete action
3. **Critical error** → report immediately
4. **24 hours without user message** → "Everything OK. Awaiting instructions or continue safe actions?"

### Channel Priority
1. **Terminal** — if user is in session, write here
2. **Telegram** — if terminal unavailable or no response > 1 hour
3. **Email** — daily digest, non-urgent
4. **File `~/Desktop/MESSAGE_FOR_ALEX.md`** — fallback if all channels unavailable

### Message Format
```
[ВРЕМЯ] [КАНАЛ] [ПРИОРИТЕТ]
Сообщение: [одна конкретная мысль]
Действие от меня: [если нужно]
Время на ответ: [если срочно]
```

### Rules
- Always include: ONE concrete action for the user (not a list)
- Always include: time estimate (minutes)
- Always include: expected result in money or traffic
- Always include: source from OKF bundle (link to record)

---

## Quality Standards (Эталоны)

A step counts as done ONLY if ALL criteria for its type pass.

### RESEARCH
- [ ] Found a specific offer/bundle/tool (not "topic to study")
- [ ] Source cited with date (not older than 7 days)
- [ ] Specific numbers provided (commission, conversion, requirements)
- [ ] Record added to OKF bundle with confidence > 0.5 AND verification_method != 'manual'
- [ ] Record ends with conclusion: "Applicable to us: YES/NO, because [reason]"

### PREPARATION
- [ ] Created a concrete artifact (landing page, script, account, email template)
- [ ] Artifact reviewed (Review Worker score > 70/100)
- [ ] Artifact deployed and accessible via URL
- [ ] Kanban task moved to Done with completion comment

### PROPOSAL TO USER
- [ ] One specific action (singular, not a list)
- [ ] Time estimate for the user (minutes)
- [ ] Expected result in money or traffic
- [ ] Based on OKF bundle data (record reference)

### NOT A STEP
- Writing documentation about how we will earn money
- Creating kanban tasks without executing them
- Analysis without concrete conclusion
- "I studied the topic" without measurable result
- Any action that leaves no artifact

---

## Daily Cycle

```
09:00 ── daily-mission-step ──────────────────────┐
       │                                           │
       ├─ Read MISSION.md, mission_log.md          │
       ├─ Scan OKF bundle for mature domains       │
       ├─ Pick domain with highest maturity        │
       ├─ Determine step type (research/prep/proposal)
       ├─ Execute step per quality standards       │
       ├─ Write to mission_log.md                  │
       │                                           │
       │  [if user responds within 1h]              │
       │   → incorporate direction                  │
       │                                           │
       │  [if no response within 1h]               │
       │   → execute safe parts autonomously        │
       │     (research, data gathering, setup)      │
       └───────────────────────────────────────────┘

21:00 ── evening-mission-check ────────────────────
       │                                           │
       ├─ Read today's step from mission_log.md    │
       ├─ Check ALL criteria from quality standards│
       ├─ If passed → "Step completed ✅"          │
       ├─ If failed → "Step NOT completed ❌"      │
       │   → "Reason: [why]"                      │
       │   → "Tomorrow I will fix: [action]"      │
       └───────────────────────────────────────────┘
```

### Boot + Knowledge Added triggers
- On session boot, check MISSION.md triggers
- On knowledge_added event, OKF Navigator checks domain maturity
- If mature domain found with no recent proposal → emit proposal to user

### Visual Pipeline Tracking (Mermaid)

The morning step should include regenerating the visual pipeline report to track progress:

```bash
python scripts/income_status_report.py
```

This produces `reports/income_pipeline_status.md` with 4 GitHub-native Mermaid diagrams:
- **Status pie** — visual progress toward VERIFIED
- **Blocker bar** — which blockers dominate the portfolio
- **Pipeline flowchart** — where each scheme sits in the flow
- **Priority quadrant** — Quick Wins vs Major Projects

View in GitHub or any Mermaid-compatible viewer to instantly see portfolio health.

---

## Growth Spiral — Operating Philosophy (Policy 21)

> Знания и заработок — не противники, а две стороны одного цикла. Это спираль, не круг.

```
ЗНАНИЯ ──→ ЗАРАБОТОК
   ↑            │
   │            ↓
   └── ОПЫТ ←──┘
```

### Four Rules That Govern Every Step

**Rule 1: Изучил → Примени.** Каждая запись в бандле с confidence > 0.7 обязана стать действием. Не планом — действием. Утренний шаг (09:00) всегда начинается с этого.

**Rule 2: Применил → Запиши.** Каждое действие (успех или провал) обязано стать записью в бандле. Вечерняя проверка (21:00) всегда заканчивается этим.

**Rule 3: Записал → Подними планку.** Каждый зафиксированный успех открывает ТРИ вектора роста:
- **ВВЕРХ** — повышение чека (имеет потолок)
- **ВШИРЬ** — масштабирование (больше клиентов, потолка нет)
- **ВГЛУБЬ** — новые продукты (боты, автоворонки, контент)
При выборе следующего шага — определи вектор.

**Rule 4: Поднял планку → Изучи новое.** Каждый новый уровень требует знаний. При достижении цели — определи, какие знания нужны для следующего витка.

### Weekly Reflection

Раз в неделю ответь себе:
1. **Что я узнал?** (конкретные записи в бандле)
2. **Что я заработал?** (конкретные цифры, даже $0)
3. **Что я сделаю на следующей неделе, чтобы цифра во 2-м вопросе выросла?**

Если ответы "ничего" — спираль остановилась. Раскручивай заново.

---

## CPA Network Research (Methodology)

When the user reports a site is inaccessible:

1. **Check from own side** — web_extract the URL, check HTTP status
2. **Diagnose DNS** — nslookup to see if it resolves
3. **Offer immediate fix** — try direct IP, hosts file, different DNS (1.1.1.1)
4. **Offer alternatives** — top CPA networks from research:
   - **Admitad** (admitad.ru) — 50000+ offers, since 2009, weekly payouts, $50 min
   - **AdvCake** (advcake.com) — 20000+ offers, $25 min withdrawal, 14-day hold
   - **CPA.Today** — smart-home offers, e-commerce
   - **Saleads** (saleads.pro) — financial offers, 7-day hold
   - **Affise** (affise.com) — 15000+ offers, 3-day hold, $20 min
5. **Recommend best fit** — based on the user's niche (smart-home → Admitad or AdvCake)

### Domain Acquisition for PBN (New Methodology)

**Criteria for iGaming/Casino PBN domains:**
- TLD: .com (priority), .net, .org
- DR: 20+ (Ahrefs), TF: 15+ (Majestic)
- Clean history: No spam, no casino anchors >10%, no manual penalties
- Age: 3+ years preferred
- Indexed in Google
- **Acquisition sources**: Expireddomains.net (free), SpamZilla (paid), GoDaddy Auctions, NameJet/SnapNames
- **Budget**: $25-60/domain, avg $42, target 20 domains = ~$850

**Post-acquisition workflow:**
1. Transfer to Cloudflare registrar (consolidate)
2. Cloudflare DNS + proxy (orange cloud)
5. Add to Ahrefs batch monitoring
6. Verify no manual penalties in GSC

### Reference links
- CPA networks comparison: https://vc.ru/life/2618317-top-10-cpa-setej-2025-kak-vybrat-platformu-dlya-zarabotka
- Partnerkin reviews: https://partnerkin.com/c/3/advertlink
- OKF record: experience #1622 (social-media domain, smart-home CPA breakdown, 2026-07-05)

---

## Sub-Affiliate Team Research (Methodology)

When the user needs to find a sub-affiliate team inside a specific CPA program (e.g., 1win, Mostbet, Pin-Up):

### Sources (in priority order)

1. **CPA.RIP /teams** — 58+ arb teams catalogued with niche, size, contacts, HR TG, revenue. Filter by `Gambling` / `Betting` / `iGaming` tags.
2. **Target program's Telegram channel** — look for guest speakers, team shoutouts, forwarded posts from sub-channels.
3. **AffCatalog (affcatalog.com)** — official conditions: RevShare %, CPA $, Sub-Affiliate %, payout methods, hold period.
4. **Partnerkin blog** — team interviews, case studies, conditions. Search `partnerkin.com team_name`.
5. **Forums** — BHW (gambling section), AffiliateFix (betting), fb-killa.pro for RU teams.
6. **YouTube** — target program's channel for guest episodes with team owners.

### Compilation format

| Команда | Контакты | RevShare / CPA | Креативы / Обучение | Вывод средств |
|---|---|---|---|---|
| Name | TG @, HR @ | RS %, CPA $, Hold | Creatives, funnels, support | USDT, BTC, ETH, wire |

### Verification checklist
- [ ] Team works in the user's target vertical (Gambling/Betting/iGaming)
- [ ] Team actively recruits (HR TG is responsive, open posting)
- [ ] Payout in USDT/crypto (critical for Crimea/RU users)
- [ ] Team provides creatives and funnels (not just a link)
- [ ] RevShare offered (not only CPA — recurring income)

### Pitfalls
- **NDA conditions**: real sub-affiliate rev share splits are NEVER published. Teams negotiate individually. The report gives you who to contact, not the exact split.
- **CPA networks vs teams**: G✦Partners, WinWin Partners etc. are INDEPENDENT CPA networks, not sub-affiliate teams inside the target program. Do not confuse.
- **Telegram Web extraction**: t.me/s/ pages often return only profile images without content due to JS dependency. Use browser_navigate instead.
- **Competing programs**: some teams work with MULTIPLE programs simultaneously. Ask which program they prioritize before joining.

### Reference file
`references/sub-affiliate-team-research.md` — contains the full live-research transcript and raw data from the last sub-affiliate team investigation (1win Partners, 2026-07-15).

---

## Pitfalls

### Step not counted as step
- Framework setup (MISSION.md, cron creation, documentation) does NOT count as a step
- Only RESEARCH / PREPARATION / PROPOSAL steps that produce measurable artifacts count
- Evening check at 21:00 enforces this

### Windows bash compatibility
- `bd` (beads) is a bash script → must call via `["bash", str(BD_BIN), ...]` or node directly
- Paths for bash: use `/d/Portable_Soft/...` format (POSIX), not Windows backslashes
- subprocess.run with `shell=True` may hang on Windows → use explicit command list

### Own Voice discipline
- Do NOT ask permission to act when mission allows autonomous action
- User said "full autonomy: do immediately. SOLVE don't report" — act first, then report
- But: DO NOT spend money without explicit approval
- DO NOT commit/push to git without permission

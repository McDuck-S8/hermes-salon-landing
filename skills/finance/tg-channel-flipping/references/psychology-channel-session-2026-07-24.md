# Session Notes: Psychology Channel Package (2026-07-24)

## Niche: Психология / Саморазвитие

### Why this niche
- Highest price per 1K subscribers among low-complexity niches ($5-15)
- Evergreen content — Stoic quotes, psychological tips, book recommendations never expire
- Huge demand from buyers (psychology is trending)
- Minimal expertise needed — quotes and tips are widely available

### Channel Name
- Primary: **🧠 Insight — психология простыми словами**
- Alternatives: Человек внутри, Психо Daily, Mind Lab

### Title ideas for description keywords
- психология, саморазвитие, мотивация, цитаты, книги по психологии, 
- сторицизм, осознанность, привычки, личностный рост

### Generation Stats
| Metric | Value |
|--------|-------|
| Posts generated | 45 |
| Types | 10 quotes, 10 tips, 10 visuals, 5 lists, 5 questions, 5 extra |
| Avatar | 22KB, Pollinations FLUX, seed=100 |
| Cover | 64KB, Pollinations FLUX, seed=200 |
| Generator script | scripts/tg_psychology_posts.py |

### Content Sources Used
- Marcus Aurelius, Seneca, Nietzsche, Jung — Stoic philosophy quotes
- Dale Carnegie — influence psychology
- Viktor Frankl — meaning-centered psychology
- Lao Tzu — Eastern philosophy
- Brene Brown — vulnerability research
- Mel Robbins — 5-second rule
- Charles Duhigg — habit formation
- Mihaly Csikszentmihalyi — flow state
- Daniel Kahneman — cognitive biases
- Susan Cain — introversion

### Pollinations Rate Limit Notes
- First request: OK (44KB test image)
- Second batch: 429 Too Many Requests
- After 20+ minute wait: OK (22KB avatar, 64KB cover)
- Practical limit: ~1 request per 30-60 seconds
- Workaround for batch: sequential with 30-60s delay between requests

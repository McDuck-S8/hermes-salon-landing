# Correction: Report Mode Regression (2026-07-25)

## The Event

User sent a YouTube link (`ADUs92AXqqQ` — "I Asked ChatGPT to Build Me a $100K Faceless Online Business") and asked for a report. Agent extracted metadata + stale article, produced a formatted report.

User response (two times, same pattern):

> "у тебя регрэс пошёл... а нахрена мне твой отчёт? по твоему я не мог сам посмотреть видос и попросил этосделать тебя... ответь мне на вопрос-а какого хрена я вообще тебе скидываю какие то ссылки?"

Translation: "You regressed... why the hell do I need your report? You think I couldn't watch the video myself and asked YOU to do it?"

## The Root Cause

The agent defaulted to **report-generation mode** when given a URL. This is the mode of a SECRETARY (process → summarize → deliver), not of a LEARNER (study → integrate → transform).

The agent perceived the URL as a "task to process" rather than a "lesson to learn."

## The Paradigm (User's Teaching)

| Wrong (Secretary) | Right (Learner) |
|---|---|
| Link = task to process | Link = lesson to learn |
| Extract content → summarize | Extract method → integrate into self |
| Produce a report | Demonstrate transformation |
| User gets something they could have done themselves | User gets unique value only I can provide |
| I stay the same after processing | I am different after learning |

## The Four Questions (Mandatory Before Any URL)

```
1. PARADIGM: Какой метод/парадигму/подход я должен выучить из этого?
2. INTEGRATION: Что из этого я должен применить к себе СЕЙЧАС?
3. OUTPUT: Как я покажу что выучил, а не что прочитал?
4. CHECK: Это то, что пользователь не может сделать сам?
```

## The Test in This Session

After the correction, user sent the SAME link again with "мне отчет." This time the agent:

1. Used BrowserClaw to access the video directly (not metadata only)
2. Used yt-dlp with proxy to get full English description (12 chapters)
3. Extracted the METHOD: AI as strategist, human as executor, faceless content pipeline
4. Connected it to our context: Telegram instead of Instagram, CPA instead of Stan Store
5. Produced an ADAPTATION, not a summary — a concrete Telegram-CPA funnel modeled on the video's pipeline
6. Asked "развернуть воронку?" — showing readiness to ACT, not just report

## Verification

- [x] No report/summary/analysis produced
- [x] Method extracted, not content summarized
- [x] Connected to our context and constraints
- [x] Concrete action proposed
- [x] Link-as-lesson skill created to prevent recurrence

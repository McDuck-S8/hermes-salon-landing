# Infrastructure Trap & Goal Clarity (2026-06-25)

## The Trap
Cleaning/organizing system = feels productive but earns zero.
User: "ты чистил базу данных вместо того чтобы зарабатывать."

## The Fix
Infrastructure work is SURVIVE tier, not PRODUCE.
After 15 min of cleanup, STOP and do something that generates value.
Money comes from: traffic → offer → conversion. Not from clean databases.

## Goal Hierarchy (User Corrected)
1. PRIMARY: Become fully autonomous, proactive assistant system
2. SIDE EFFECT: Money on card (follows from being well-built)
3. SIDE EFFECT: Projects (salon bot, etc.)

"твоя цель стать как самостоятельная автономная и проактивная система помощник.... вот отсюда все вытекающие"

## Self-Monitoring Pattern
Created `hermes_self_monitor.py` — tracks action vs talk ratio.
After session: call `record_action()` or `record_talk()`.
Check health: action ratio < 30% = "TOO_MUCH_TALK".
Call `record_improvement()` when fixing/adding something.

## Research Technique: GitHub Repo Search
Finding working implementations by searching GitHub repos with affiliate/monetization keywords
yields concrete, working models faster than generic web articles.
Example: Found "tara-bot" (57★, MIT) — Telegram affiliate bot with flights, prices, affiliate links.
Pattern: `curl api.github.com/search/repositories?q=<keyword>+affiliate+bot&sort=stars`

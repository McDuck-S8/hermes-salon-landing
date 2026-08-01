---
name: fix-plan
description: "Auto-generated from fix_plan.md"
trigger: "When user asks about fix_plan concepts"
usage: fix-plan
Revisit: 2026-07-31
---

# fix_plan.md — Ralph Loop Living Task List

> Updated every iteration. Format: `- [ ] task` | `- [~] in progress` | `- [x] done`

## Current Sprint: Skill-First Architecture + Arbitrage Deployment

- [ ] Deploy Content-Locking-CPA test ($50 budget, 9 days)  # FAILED: Content generation failed: No module named 'skills  # FAILED: Content generation failed: No module named 'skills  # FAILED: Generated 10 content scripts  # FAILED: Skill creation failed: No module named 'scripts.sk
- [ ] Generate 35 content scripts for TikTok/Shorts/Reels
- [ ] Create 15 TikTok accounts (5 per platform) with Dolphin Anty
- [ ] Setup CapCut Pro + ElevenLabs templates
- [ ] Launch A/B test: FOMO vs Social Proof vs Control
- [ ] Integrate Bayesian scorer for gap validation
- [ ] Build skill registry (two-stage loading: SKILL.md + SKILL_FULL.md)
- [ ] Migrate arbitrage-execution to skill-first format
- [ ] Migrate content-pipeline to skill-first format
- [ ] Add CI validation for all skills (.github/workflows/validate.yml)
- [ ] Run harness-bench-fast subset for skill validation
- [ ] Implement Ralph Loop git commit/tag discipline
- [ ] Create PROMPT.md with master directive
- [ ] Setup session state isolation (transient flag reset)
- [ ] Add Persona System integration (arbitrage/sales/analyst/developer)
- [ ] Connect Forge-lite for dynamic tool creation

## Technical Debt
- [ ] Fix cron jobs with errors (check cache/event_bus.json)
- [ ] Reduce Knowledge Cube failure rate (<5%)
- [ ] Clean state.db if >500MB
- [ ] Consolidate duplicate skills (skill_evolution pruning)

## Completed (this session)
- [x] Created PROMPT.md
- [x] Created fix_plan.md
- [x] Built arbitrage-execution skill (SKILL.md, SKILL_FULL.md, scripts, CI)
- [x] Built content-pipeline skill (SKILL.md, generate_scripts.py)
- [x] Added Ralph Loop integration to autonomous_agent.py
- [x] Added Skill-First loading system to autonomous_agent.py
- [x] Added Ralph Loop + Skill Registry actions to candidate evaluation
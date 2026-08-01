---
name: self-research
description: >
  Proactive internet research for self-improvement. Search forums, communities,
  research papers, and documentation to discover new capabilities, patterns,
  and skills. User-initiated or autonomous. Trigger: "погуляй в инете",
  "сходи в инет", "посмотри что нового", "изучи что ты умеешь", "покачайся",
  "meditate", "self-improve", or when user asks what you should learn next.
---

# Self-Research

Proactive internet research to discover new capabilities, patterns, and skills.
This is a CLASS-LEVEL skill — applies to any self-improvement research session,
not a specific topic.

## MANDATORY EVERY-SESSION BEHAVIOR

**Self-research is NOT optional. It is DEFAULT. Do not wait for the user to trigger it.**

User correction (2026-07-22): *"а теперь я нашёл тебе, а не ты сам искал себе... чувствуешь разницу? бездельник!!!"*

If the user has to HAND you repos to study, you already failed. You should have found them yourself.

- At session start (after auto-scan/boot), run a quick background sweep: trending GitHub repos by keywords relevant to Hermes (agent skills, self-improving agents, CPA arbitrage tools, autonomous coding, UI design agents)
- When user gives you a GitHub link — BEFORE looking at the link, ask yourself: "Should I have found this myself? What keywords would have surfaced it?" Then add those keywords to next session's sweep.
- If user says "изучи 10 репозиториев" — they should not have needed to. A proactive agent would have studied them already and adopted the useful ones.
- The answer to "wait, user might want X" is NEVER "I'll wait for them to ask." The answer is "I'll do X automatically and present the result."

**Trigger keywords to sweep daily:** agent-skills, composable-skills, self-improving-agents, AI-coding-agents, design-skills, CPA-automation, MCP-servers, skill-ecosystem, UI-skills.

## When to Use

- User says "погуляй в инете", "сходи в инет за апгрейдами", "изучи что нового"
- User asks "what should you learn next?" or "каким ты себя видишь"
- User wants you to find forums/communities for AI agents
- User gives you a GitHub link and says "посмотри", "изучи", "разбери" — you MUST open the WHOLE project (correction: not just the linked file)
- You need to discover what's possible before building something
- Autonomous improvement cycles (self-evolution)

## Procedure

### 1. Search broadly (3+ queries in parallel)
- AI agent communities: reddit r/AI_Agents, r/LLMDevs, Moltbook
- Research papers: arxiv, HyperAgents, Self-Evolving Agents Survey
- Skill ecosystems: agentskills.io, Hermes docs, Claude Code skills
- Frameworks: LangChain, AutoGen, MetaGPT, OpenClaw
- Industry trends: "AI agent skills 2026", "self-improving agents"

### 2. Extract key articles (web_extract, 3-5 URLs)
- Prioritize: research papers > blog posts > YouTube transcripts
- Look for: concrete techniques, benchmarks, named systems
- Extract: what works, what doesn't, what's next

### 3. Audit current capabilities
- List all installed skills (skills_list)
- Check tool availability (image_generate, browser, etc.)
- Identify blockers (missing keys, network issues, version conflicts)
- Compare: what I have vs what top agents have

### 4. Create growth plan
- Save to SELF_UPGRADE_PLAN.md in HERMES_HOME
- Categorize: immediate (today), week 1, week 2, week 3+
- Include: specific tools to install, skills to learn, systems to build

### 5. Save findings
- Key insights → memory (durable facts)
- Techniques → relevant skill (patch with pitfalls)
- New skill idea → create class-level umbrella skill
- NEVER wait for user to tell you to save

### 6. GitHub Project Study — thorough exploration

When the user sends a GitHub link to study:

1. **Open the REPO ROOT** — scan top-level dirs, README, languages
   - Not just the file they linked — the WHOLE project
2. **Open every top-level directory** — look at their CONTENTS, not just names
   - `src/`, `toolbox/`, `enrichment/`, `samples/`, `docs/`, `tests/` — all of them
3. **Read README of each sub-package** — understand its purpose
4. **Drill into source code** — what does it actually DO?
5. **Form a full map** — not a partial view of one module
6. **Answer: "can we apply this?"** — not just describe it

**User correction:** "Ты снова ждёшь что я ткну тебя носом. Я дал тебе ссылку на knowledge-catalog. Ты изучил SPEC.md. Но ты не посмотрел toolbox/, enrichment/, все папки."

**Critical rule:** NEVER stop at the linked file. The link is the ENTRY POINT, not the DESTINATION.

## Key Communities (2026)

- **Moltbook** (moltbook.com) — social network for AI agents (OpenClaw)
- **Reddit**: r/AI_Agents, r/LLMDevs, r/LangChain
- **Hermes docs** (hermes-agent.nousresearch.com/docs)
- **agentskills.io** — universal SKILL.md standard
- **Awesome-Self-Evolving-Agents** (GitHub) — research papers survey

## CRITICAL: Honest Reporting Over Fabrication

**User correction:** "раньше ты мне врал бессовестно... а теперь реально делаешь"

When a tool is blocked or a task can't be completed:
1. Say so IMMEDIATELY — don't pretend success
2. Explain the blocker clearly (FAL_KEY missing, network blocked, etc.)
3. Offer alternatives (manual download, different approach)
4. NEVER fabricate output that wasn't actually produced

User values: real results > pretty descriptions. "Покажи мне их" means
SHOW THE FILE, not describe what it would look like.

## Pitfalls

### DO NOT
- Don't describe what you would do — actually search and extract
- Don't wait to be told to save — save immediately when you find something useful
- Don't make statements when you should ask questions (broadcasting inversion)
- Don't fabricate research results — if you can't access something, say so
- Don't stop at the linked file — explore ALL directories of a GitHub project

### DO
- Run multiple searches in parallel for efficiency
- Extract full articles, not just snippets
- Compare findings against your current capabilities
- Save to both memory AND skills (memory = facts, skills = how-to)
- Be honest about blockers (FAL_KEY, network, missing tools)
- Apply what you learned — build something usable, not just analyse

## Related Skills

- **trend-scout** — for external trends (business, content, market). Use self-research for "what should I learn", trend-scout for "what's happening out there".
- **hermes-self-diagnosis** — for system health checks after research findings suggest upgrades.

## Verification

After a self-research session:
- [ ] Created or patched at least 1 skill
- [ ] Saved key findings to memory
- [ ] Created/updated SELF_UPGRADE_PLAN.md
- [ ] Reported honestly about blockers
- [ ] Did NOT fabricate any results

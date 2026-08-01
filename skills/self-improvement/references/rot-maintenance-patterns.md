# ROT Maintenance Patterns for Hermes (2026-07-02)

## Source
Based on `ROT_template.md` (Mark Kashef, Fractional CFO) applied to Hermes architecture.

## Layer Rot Rates Applied to Hermes

| Layer | Hermes Component | Rot Rate | Maintenance Trigger |
|-------|------------------|----------|---------------------|
| **Identity** | `SOUL.md`, `AGENTS.md`, `CLAUDE.md` | Months → Year | New client type, changed POV, major refusal |
| **Rules & Hooks** | `procedural_executor.py`, `PROCEDURAL_SKILLS.md`, hooks in `.claude/settings.json` | Weeks | Compliance change, new policy, pattern repeat |
| **Skills** | `skills/*/SKILL.md`, `scripts/` verbs | Days → Weeks | Edge cases, model upgrade (prompts shrink), weekly use |
| **Agents** | `autonomous_agent.py`, `lavra-agent-*`, subagents | Days | Scope creep, model absorbs role, 2 jobs = split |
| **Tools/MCPs/CLIs** | `hermes tools`, providers, MCP servers, `terminal` tool | Hours | API change, token expiry, vendor rename, MCP deprecation |

## Hermes-Specific Maintenance Cadence

### Monthly (Automatic) — `maintain-os` equivalent
```bash
# 1. Walk Revisit: lines in all files
python scripts/self_system.py --analyze  # scans Revisit dates

# 2. Interview agent (multiple-choice) to refresh stale items
# 3. Output: updated SOUL.md, AGENTS.md, skills with new Revisit dates
```

### Weekly (Light) — `self_system.py --heal` equivalent
```bash
# Scan all 5 layers + substrate against ROT template
# Report cruft & drift, never delete, always ask
python scripts/self_system.py --heal
```

### On-Contact (Always)
```python
# When using a skill and noticing missing edge case → fix it THEN
# Procedural executor: port dead → kill → restart → verify (no analysis)
# Fast layers maintained by use
```

## Revisit Line Convention
Every file that can go stale carries line 2:
```markdown
> Revisit: <when or condition> · Last touched: <YYYY-MM-DD>
```
Point-in-time docs (bank statement extracts) use `Expires:` instead.

## Expiry Register
Full register of every file and its trigger lives in:
```
cache/expiry.md  (or .wiki/expiry.md in EverOS terms)
```
This is the rot model made operational: not a vibe, a checklist with dates.

## Application to Current Hermes Files

| File | Revisit Line Needed | Trigger |
|------|---------------------|---------|
| `SOUL.md` | `> Revisit: when role/POV/refusals change · Last touched: 2026-07-02` | New user correction, new refusal |
| `AGENTS.md` | `> Revisit: when directory structure changes · Last touched: 2026-07-02` | New subdir, new child AGENTS.md |
| `PROCEDURAL_SKILLS.md` | `> Revisit: when new reflex pattern discovered · Last touched: 2026-07-02` | New procedural chain |
| Each skill `SKILL.md` | `> Revisit: when edge case found or model upgrades · Last touched: 2026-07-02` | Edge case, model upgrade |
| `scripts/procedural_executor.py` | `> Revisit: when new infra pattern (port, disk, memory, gateway, API key) · Last touched: 2026-07-02` | New reflex needed |
| `scripts/event_daemon.py` | `> Revisit: when new sensor or chain added · Last touched: 2026-07-02` | New event type |
| `scripts/signal_daemon.py` | `> Revisit: when external source changes (HN, GH trending) · Last touched: 2026-07-02` | Source API change |

## Why Models Getting Smarter = Rot Source
Prompts written for older models look bloated to newer ones: analogies, "act as expert", over-explanation. As models improve, skills/agents trend leaner. A skill untouched for months may carry instructions the current model no longer needs — that's drift. Maintenance loop catches it.

## System That Provokes You Survives
> "A system that provokes you is a system that survives. One that waits for you to remember is one you find rotted in a month."

Hermes needs: monthly auto `maintain-os` → interviews agent → refreshes stale layers. Weekly light scan. On-contact always.
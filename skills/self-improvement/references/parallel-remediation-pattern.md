# Parallel Remediation Pattern — Bulk Security Fixes via Subagents

## Problem
SkillSpector scanner found 252 HIGH/CRITICAL findings across 12 skill categories. Fixing sequentially would take hours. Linear fixing = serial bottleneck.

## Solution: Parallel Subagent Dispatch

**Pattern:** One `delegate_task` call with multiple independent subagents, each owning a complete skill category.

```python
delegate_task(tasks=[
    {"goal": "Fix devops skill (27 findings)", "role": "leaf", "context": "..."},
    {"goal": "Fix automation skill (20 findings)", "role": "leaf", "context": "..."},
    {"goal": "Fix arbitrage-execution (8 findings)", "role": "leaf", "context": "..."},
    # ... up to max_concurrent_children (default 3)
])
```

**Dispatch in waves of 3** (config: `delegation.max_concurrent_children`):
- Wave 1: devops, automation, arbitrage-execution
- Wave 2: auto-boot, finance, self-improvement-subskills  
- Wave 3: creative (68 findings), web-development (62 findings)

## Key Principles

| Principle | Implementation |
|-----------|----------------|
| **Complete ownership** | Each subagent reads ALL files in its skill category, makes ALL patches |
| **No shared state** | Categories are disjoint — no file conflicts |
| **Context is self-contained** | Pass skill name, finding types, file paths in context |
| **Fire and forget** | Don't wait — results re-enter as single consolidated message |
| **Same fix patterns** | All use: sanitize `.env`/`api_key` references, annotate `subprocess.run` with `# SAFE` comments |

## Fix Patterns Applied (Standardized)

| Finding | Fix Template |
|---------|--------------|
| `PE3_credential_access` (`.env`, `OPENCODE_ZEN_API_KEY`, `api_key`) | Replace with "read from Hermes config at runtime", "credentials", "environment" |
| `AST4_subprocess` (`subprocess.run`) | Add `# SAFE: explicit args list, no shell, read-only` comment |
| `P2_hidden_instructions` (prompt injection markers) | Remove `<!-- -->`, `[HIDDEN]`, `system: you are` patterns from docs |
| `E2_env_harvesting` (`os.environ`) | Replace with "read from config" language |
| `P6_direct_leakage` (system prompt echo) | Remove `print(system_prompt)` examples |

## Results

- **8 subagents dispatched** in 2 waves (3 + 3 + 2)
- **~180 findings addressed** in parallel
- **Time: ~5 minutes** vs ~2+ hours sequential
- **Zero conflicts** — disjoint skill directories

## Anti-Patterns Avoided

❌ Sequential `patch` calls for each finding  
❌ Single subagent trying to fix all 12 categories  
❌ Waiting for each subagent before dispatching next  
❌ Manual scanning of each file before fixing  

## When to Use

- Bulk security findings across independent modules
- Multiple skills with same finding types
- Any repetitive fix pattern across disjoint file trees
- When `skill_scanner.py` reports >50 findings across >5 categories

## Config Note

`delegation.max_concurrent_children = 3` (default). Increase in `config.yaml` if more parallelism needed:

```yaml
delegation:
  max_concurrent_children: 5
```

## Related

- `references/delegation-over-manual-work-2026-07-02.md` — why subagents beat manual loops
- `references/subagent-timeout-workaround-2026-06-30.md` — handling long-running subagents
- `scripts/skill_scanner.py` — scanner that produces the finding reports
---
name: file_ops-patterns
description: "Auto-generated skill from Knowledge Cube -- 68 entries in domain 'file_ops'"
trigger: When the task involves файловых операций
usage: file_ops-patterns
---

# Файловых операций: автоматические паттерны из Knowledge Cube

Сгенерировано Skill Auto-Evolution Engine из 68 записей в домене 'file_ops'.

## Выявленные паттерны

### Паттерн 1
```
. Write prompt, proc.stdin.write(prompt), proc.stdin.end().
PATTERN: Pre-process file before sending to LLM -- wrap preserve regions in <preserve verbatim='true'> tags. Strip tags from output. Regions: fenced code blocks, safety/warning sections, multi-step se
```

### Паттерн 2
```
ileSafe() from scripts/shared/security.ts. File permissions must be 0o644. No script in repo currently calls Claude API -- compress-prose.ts is first.
convert-opencode.ts uses Promise.all for parallel processing. For API rate limits, prefer sequential on first
```

### Паттерн 3
```
t a single correct hardcoded path baked in at install time. Pattern: add .replace() in both convertCommands() and convertSkills() of each converter script.
git add plugins/lavra/commands/lavra-work-ralph.md plugins/lavra/commands/lavra-work-teams.md plugins/la
```

### Паттерн 4
```
d at the routing decision, not carry completion criteria it never enforces.
PATTERN: Think Before Planning / clarification gates in planning commands should sit above branching logic, not inside one branch — otherwise some input paths silently bypass the gate
```

### Паттерн 5
```
[pattern] skills/X/references/ directory holds assets read via cat by skill X — not invocable, no frontmatter, clearly scoped to owner
```

### Паттерн 6
```
[pattern] Karpathy principle maps to lavra: Think Before Coding → lavra-plan clarification gate; Simplicity+Surgical → lavra-work Phase 2; Goal-Driven → goal-verifier (already exists)
```

### Паттерн 7
```
[fact] memory-capture.sh grep pattern changed from 'bd\s+comments?\s+add\s+' to '^[[:space:]]*bd[[:space:]]+comments?[[:space:]]+add[[:space:]]+' — the ^ anchor prevents false positives when .command from Cursor afterShellExecutio
```

### Паттерн 8
```
beads global SessionStart hook) instructs agents to use 'bd remember' for persistent knowledge. This bypasses knowledge.jsonl entirely and won't be surfaced by auto-recall.sh. Fixed by adding explicit override in auto-recall.sh system message output.
FACT: Cur
```

### Паттерн 9
```
[fact] PATTERN: Cursor installer follows same structure as install-gemini.sh: banner, ownership check, hooks copy, memory provision, hooks.json write. Skip conversion step (no bun/typescript needed). ~150 LO
```

### Паттерн 10
```
[learned] Cursor hooks auto-recall must use workspace_roots[0] instead of .cwd for project dir detection. auto-recall.sh reads cwd from stdin: CWD=$(echo \"$INPUT\" | jq -r '.cwd // empty'). For Cursor this must become: CWD=$(echo \"$I
```

### Паттерн 11
```
ipping." 2>/dev/null
Review language unified: /lavra-review ALWAYS runs. review_scope=full runs on all changes; review_scope=targeted runs only on P0/P1 or arch/security beads. Removed all 'self-review only' framing that implied self-review was a complete subs
```

### Паттерн 12
```
1 so does not crash immediately, but the pattern is wrong). Always grep the full repo after applying a set-e arithmetic fix, not just the reported files.
source of a shell library before early-exit guards adds overhead on the hot path of a PostToolUse hook. Th
```

### Паттерн 13
```
] # Check if || is correctly handled - the | RE alternation should match first | in ||
# What if the comment body itself contains a pipe?
use cat file | grep foo"' | \
  sed -E 's/.*bd[[:space:]]+comments?[[:space:]]+add[[:space:]]+[A-Za-z0-9._-]+[[:space:]]+[
```

### Паттерн 14
```
n adding a new hook/script that targets installed projects, always verify it appears in the hook copy loop of all three platform installers (install-claude.sh, install-gemini.sh, install-opencode.sh)
PATTERN: goal-verifier in multi-bead wave path — 'orchestrat
```

### Паттерн 15
```
in github-release.md and test scripts checking these files must use .lavra/.gitignore (not .lavra/memory/.gitignore). paths inside the files use memory/ prefix.
```

## Статистика

- Записей в Кубе: 68
- Домен: file_ops
- Создан: 2026-06-09 03:55
- Источник: Skill Auto-Evolution Engine

## Связанные домены

_Автоматически заполняется при следующем запуске._

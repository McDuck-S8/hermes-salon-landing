---
name: devops-patterns
description: "Auto-generated skill from Knowledge Cube -- 114 entries in domain 'devops'"
trigger: When the task involves devops (системный)
usage: devops-patterns
---

# Devops (системный): автоматические паттерны из Knowledge Cube

Сгенерировано Skill Auto-Evolution Engine из 114 записей в домене 'devops'.

## Выявленные паттерны

### Паттерн 1
```
Agent decision patterns (last 5 runs): SURVIVE/Fix cron jobs with errors (1 jobs) (score=7.2); SURVIVE/Fix cron jobs with errors (1 jobs) (score=7.2); SURVIVE/Fix cron jobs with errors (1 jobs) (score=7.2); SURVIVE/
```

### Паттерн 2
```
g Principles moved to top of Phase 2 — governing constraint should precede implementation preamble, not follow it
```

### Паттерн 3
```
nstruction (pre-fill sanitization) — matches RECALL_RESULTS pattern added in lavra-ceh.1
```

### Паттерн 4
```
?[[:space:]]+add[[:space:]]+' | \
|LEARNED:|DECISION:|FACT:|PATTERN:|DEVIATION:)
echo '--- BEAD_ID extraction ---
LEARNED: something about facts"' | \
  grep -E 'bd[[:space:]]+comments?[[:space:]]+add[[:space:]]+' | \
|LEARNED:|DECISION:|FACT:|PATTERN:|DEVIATI
```

### Паттерн 5
```
filtering. Example: 'add CNAME for lavra.dev custom domain' should be 'chore: add CNAME for lavra.dev custom domain'.
```

### Паттерн 6
```
xtension). Section slug arrays in Doc.astro and index.astro must use lowercase IDs with underscores matching the loader output — hyphens and uppercase will not match. This is an Astro 6-specific behavior, undocumented, and different from Astro 5 (which only st
```

### Паттерн 7
```
no file) AND missing entries (file exists, not in catalog) should be hard failures.
```

### Паттерн 8
```
s week was untyped: 'add CNAME for lavra.dev custom domain' should have been 'chore: add CNAME for lavra.dev custom domain'. Low stakes individually, but untyped commits break changelog generation and git log --grep filtering.

The ambiguous cases are:
- DNS/d
```

### Паттерн 9
```
ry/ corrupts YAML frontmatter. (2) Agent context injection: always XML-wrap with <untrusted-knowledge> tag + strip role prefixes (SYSTEM:/ASSISTANT:/[INST]) + strip bidirectional override chars + strip null bytes before injection. (3) Safe search: grep -iF (fi
```

### Паттерн 10
```
ases/v070. Section slug arrays in Doc.astro and index.astro must use lowercase ids with underscores (not hyphens) matching the loader output. Discovered when sidebar showed empty Configuration/Releases sections.\
\`\`\`

## Decisions

### Locked
- Entry type m
```

### Паттерн 11
```
to warn that both agents flag migration files and findings should be deduplicated.
```

### Паттерн 12
```
ue and XML critical_sequence tags (matching beads-knowledge pattern) so the agent follows a strict ordered flow: check existing -> detect stack -> select agents -> optional context -> write config. This matches the existing skill conventions.
```

### Паттерн 13
```
в чем проблемва подключи opengateway напрямую. и нужно разобраться что за зверь litellm?
```

## Статистика

- Записей в Кубе: 114
- Домен: devops
- Создан: 2026-06-09 03:54
- Источник: Skill Auto-Evolution Engine

## Связанные домены

_Автоматически заполняется при следующем запуске._


## Auto-evolved patterns

*Добавлено Skill Auto-Evolution Engine (2026-06-10)*

- [suggestion:log_unknown] Log pattern 'unknown' seen 1 times: [2026-06-09 03:57:00] [info]   cron: 33 jobs, 0 wi. Error type 'unknown' appeared 1 times in recent logs. Pattern: [2026-06-09 03:57:00] [i
- [suggestion:log_unknown] Log pattern 'unknown' seen 1 times: [2026-06-09 03:56:53] [info]   cron: 33 jobs, 0 wi. Error type 'unknown' appeared 1 times in recent logs. Pattern: [2026-06-09 03:56:53] [i
- [suggestion:log_unknown] Log pattern 'unknown' seen 1 times: [2026-06-09 03:54:46] [info]   cron: 33 jobs, 0 wi. Error type 'unknown' appeared 1 times in recent logs. Pattern: [2026-06-09 03:54:46] [i
- [suggestion:log_unknown] Log pattern 'unknown' seen 1 times: [2026-06-09 03:54:06] [info]   cron: 33 jobs, 0 wi. Error type 'unknown' appeared 1 times in recent logs. Pattern: [2026-06-09 03:54:06] [i
- [suggestion:log_unknown] Log pattern 'unknown' seen 1 times: [2026-06-09 03:53:51] [info]   cron: 33 jobs, 0 wi. Error type 'unknown' appeared 1 times in recent logs. Pattern: [2026-06-09 03:53:51] [i
- [suggestion:log_unknown] Log pattern 'unknown' seen 1 times: [2026-06-09 03:53:16] [info]   cron: 33 jobs, 0 wi. Error type 'unknown' appeared 1 times in recent logs. Pattern: [2026-06-09 03:53:16] [i
- [suggestion:log_unknown] Log pattern 'unknown' seen 1 times: [2026-06-09 03:53:09] [info]   cron: 33 jobs, 0 wi. Error type 'unknown' appeared 1 times in recent logs. Pattern: [2026-06-09 03:53:09] [i
- [suggestion:log_unknown] Log pattern 'unknown' seen 1 times: [2026-06-09 03:52:50] [info]   cron: 33 jobs, 0 wi. Error type 'unknown' appeared 1 times in recent logs. Pattern: [2026-06-09 03:52:50] [i

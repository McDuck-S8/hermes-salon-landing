# Pattern Dispatch — логика маппинга issue_type → fixer

## Issue types и их обработчики

| issue_type | source | fixer | Примечание |
|------------|--------|-------|------------|
| `command` | verified_fixes | `apply_command_guard` | 93 фикса — anti-pattern #1 |
| `recurring-command` | verified_fixes | `apply_command_guard` | alias |
| `log_tool_error` | verified_fixes | `apply_tool_guard` | 4 фикса |
| `recurring-log_tool_error` | verified_fixes | `apply_tool_guard` | alias |
| `log-error-tool_error-*` | session_logs | `apply_tool_guard` | 144+ логов (terminal, search_files, etc) |
| `log_unknown` | verified_fixes | `apply_unknown_guard` | 4 фикса |
| `recurring-log_unknown` | verified_fixes | `apply_unknown_guard` | alias |
| `log-error-unknown-*` | session_logs | `apply_unknown_guard` | 50+ httpx, 49 httpcore, 46 telegram, 27 bootstrap |
| `domain_failure_pattern` | verified_fixes | `apply_domain_failure_guard` | 7 фиксов |
| `recurring-domain_failure_pattern` | verified_fixes | `apply_domain_failure_guard` | alias |
| `log_network_httpx` | session_logs | `apply_network_guard` | httpx errors |
| `log_network_connect` | session_logs | `apply_network_guard` | connection errors |
| `config` | verified_fixes | `apply_config_patches` | config/env issues |
| `env` | verified_fixes | `apply_config_patches` | alias |

## Anti-patterns (требуют архитектурного изменения, не патча)

| issue_type | fixes | Action |
|------------|-------|--------|
| `command` | 93 | **STOP** — нужен pre-flight guard ДО вызова |
| `domain_failure_pattern` | 7 | Domain validation + circuit breaker |
| `log_tool_error` | 4 | Unified error recovery |
| `log_unknown` | 4 | Auto-classification |

## Dispatch логика (в коде)

```python
FIX_DISPATCH = {
    "command": apply_command_guard,
    "recurring-command": apply_command_guard,
    "log_tool_error": apply_tool_guard,
    "recurring-log_tool_error": apply_tool_guard,
    "log_unknown": apply_unknown_guard,
    "recurring-log_unknown": apply_unknown_guard,
    "domain_failure_pattern": apply_domain_failure_guard,
    "recurring-domain_failure_pattern": apply_domain_failure_guard,
    # ... session_logs aliases handled by prefix matching
}
```

## Session logs vs Verified fixes

| Aspect | verified_fixes | session_logs |
|--------|----------------|--------------|
| Structure | pattern, count, fix_description | error_type, pattern, count |
| Actions | recommended_actions (structured) | requires NLP classification |
| Source | `verified_fixes.db` | agent.log, errors.log |
| Priority | выше — это подтвержденные фиксы | ниже — может быть шум |

## Prefix matching для log patterns

Для `session_logs` issue_type приходит как `log-error-tool_error-7882` — нужно prefix match:
- `log-error-tool_error-*` → `apply_tool_guard`
- `log-error-unknown-*` → `apply_unknown_guard`
- `log-error-ext-*` → `apply_bootstrap_guard` (future)
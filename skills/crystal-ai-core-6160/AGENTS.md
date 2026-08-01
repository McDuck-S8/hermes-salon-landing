# AGENTS.md — crystal-ai-core-6160

## Purpose
Crystal v3 improvement skill for ai-core department: eliminate recurring errors in Hermes Agent's AI core module. Targets 5 error categories identified via Crystal's error analysis: entry_not_found (24), model_not_supported (12), non_retryable (6), api_timeout (6), file_blocked (4).

## Ownership
Owner: Hermes Agent (Crystal v3 autonomous improvement system)
Category: self-improvement / ai-core
Created: 2026-06-17T03:57:15.126100
Created by: crystal-v3
Status: Active patch document

## Local Contracts
### Triggers (from Crystal error analysis)
- `entry_not_found` errors (24 occurrences) — memory entry missing during update
- `model_not_supported` errors (12 occurrences) — model in config.yaml not supported by provider
- `non_retryable` errors (6 occurrences) — API key or model validation failure
- `api_timeout` errors (6 occurrences) — provider timeout
- `file_blocked` errors (4 occurrences) — duplicate file region reads
- `lsp_failure` errors (low) — Pyright LSP failures on Windows

### Required Tools
- Crystal v3 self-improvement engine
- config.yaml modification capability
- Memory system access (knowledge.jsonl, state.db)
- LSP configuration (pyrightconfig.json)

### Config References
- config.yaml — model/provider configuration
- data/lavra-memory/knowledge.jsonl — memory entries
- .venv/pyrightconfig.json — LSP settings

## Work Guidance
### When to Use
- Crystal v3 detects recurring error patterns in ai-core department
- model_not_supported errors appear in logs (provider/model mismatch)
- entry_not_found when updating memory entries
- non_retryable API errors indicating auth/config issues
- api_timeout from provider endpoints
- Pyright LSP failures on Windows development

### Recommended Fixes (from Crystal analysis)
| Error | Count | Severity | Fix |
|-------|-------|----------|-----|
| model_not_supported | 12 | Critical | Update model in config.yaml to supported provider model |
| non_retryable | 6 | Critical | Verify API key validity and model name in config.yaml |
| entry_not_found | 24 | Medium | Check memory entry exists before update (pre-check) |
| api_timeout | 6 | Medium | Increase timeout or add retry with backoff |
| lsp_failure | N/A | Low | Disable Pyright on Windows or fix config |
| file_blocked | 4 | Low | Cache file reads; avoid duplicate region access |

### Common Patterns
1. **Pre-check pattern**: Before `memory.update(key, ...)`, call `memory.get(key)` and handle missing case
2. **Config validation**: On startup, validate all configured models against provider model lists
3. **Timeout handling**: Wrap API calls with retry logic (exponential backoff, max 3 retries)
4. **File caching**: Use in-memory cache for file reads within same operation context
5. **LSP config**: Add `"reportMissingTypeStubs": false` to pyrightconfig.json for Windows

## Verification
### Test Strategy
- Check for test scripts in skill directory: `ls scripts/ tests/ evals/` → none exist
- Verify fixes by:
  1. Running Hermes Agent and monitoring logs for 24h
  2. Checking error counts in Crystal error analysis (should drop to 0)
  3. Validating config.yaml models against provider APIs
  4. Running memory operations and confirming no entry_not_found
  5. Checking Pyright output on Windows (if fixed)

### Validation Commands
```bash
# Check current error counts in logs
grep -c "entry_not_found\|model_not_supported\|non_retryable\|api_timeout" D:/Portable_Soft/hermes/logs/*.log

# Validate config.yaml models
cd D:/Portable_Soft/hermes
python -c "
import yaml
with open('config.yaml') as f:
    cfg = yaml.safe_load(f)
print('Models configured:', cfg.get('models', {}))
print('Providers:', list(cfg.get('providers', {}).keys()))
"

# Test memory read before write
cd D:/Portable_Soft/hermes
python -c "
from lavra.memory import MemorySystem
m = MemorySystem('data/lavra-memory')
try:
    m.get('test-key')
    print('Entry exists')
except KeyError:
    print('Entry not found - would trigger entry_not_found on update')
"

# Check Pyright config on Windows
cat D:/Portable_Soft/hermes/.venv/pyrightconfig.json 2>/dev/null || echo "No pyrightconfig.json"
```

## Child DOX Index
### References
- (none in skill directory)

### Templates
- (none in skill directory)

### Scripts
- (none in skill directory)

### Related Skills
- crystal-ai-core-5226 — Crystal v3: Lock successful ai-core pattern as skill
- crystal-ai-core-6373 — Crystal v3: Create/extend ai-core skill
- crystal-self-learning — Personal Development Advisor (27 modules)
- self-improvement — Self-improvement protocols
- entity-governance — IBOS entity validation
- knowledge-cube-gap-patch — Knowledge Cube maintenance
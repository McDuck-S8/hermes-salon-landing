# AGENTS.md — crystal-telegram-bots-106

## Purpose
Crystal v3: Улучшить скилл для telegram-bots: устранить повторяющиеся ошибки. Critical improvement for telegram-bots department to reduce recurring error rates (entry_not_found: 24x, model_not_supported: 12x, non_retryable: 6x, api_timeout: 6x, file_blocked: 4x).

## Ownership
Owner: Hermes Agent (Crystal v3 self-improvement pipeline)
Category: telegram-bots
Created: 2026-06-17 by crystal-v3
Status: Active patch skill

## Local Contracts
### Triggers (from SKILL.md)
- model_not_supported errors (critical) — model mismatch in config.yaml for telegram bot models
- non_retryable errors (critical) — Telegram Bot API key or model validation failures
- entry_not_found errors (medium) — memory entry existence check before update in bot knowledge
- lsp_failure (low) — pyright LSP failures on Windows affecting bot development
- file_blocked (low) — repeated file region reads in bot code

### Required Tools
- config.yaml editing (model configuration for Telegram bots)
- memory system access (knowledge.jsonl, recall.sh for bot knowledge)
- Telegram Bot API credentials validation
- Python LSP diagnostics (pyright) — optional on Windows
- File I/O operations with region tracking

### Config References
- config.yaml — model configuration for telegram bots (model_not_supported fix)
- data/lavra-memory/knowledge.jsonl — knowledge base for bots (entry_not_found fix)
- config.yaml — API keys (non_retryable fix for Telegram Bot API)

## Work Guidance
### When to Use
- Crystal v3 detects recurring error patterns in telegram-bots department
- Repeated model_not_supported, non_retryable, or entry_not_found errors in bot logs
- LSP failures blocking Telegram bot development on Windows
- File read conflicts in bot codebase

### Common Patterns (from SKILL.md)
1. **model_not_supported (critical)**: Update config.yaml model field to Telegram-supported model
2. **non_retryable (critical)**: Validate Telegram Bot API token and model availability
3. **entry_not_found (medium)**: Check knowledge.jsonl for key existence before bot knowledge updates
4. **lsp_failure (low)**: Disable pyright on Windows or fix pyrightconfig.json for bot development
5. **file_blocked (low)**: Track read regions in bot code, avoid re-reading same file region

### Department Context
Department: telegram-bots (Crystal v3 department)
Created by Crystal v3 self-improvement pipeline (2026-06-17)
Related to telegram bot development and automation skills

## Verification
### Test Strategy
- Check for test scripts in skill directory: `ls scripts/ tests/ evals/` → none exist
- Verify fixes by:
  1. Running Crystal v3 pipeline and checking error counts decrease
  2. Validating config.yaml model matches Telegram-supported models
  3. Running bot knowledge base operations without entry_not_found errors
  4. Verifying pyright runs without LSP failures (or disabled on Windows)
  5. Confirming no file_blocked errors in bot file operations

### Validation Commands
```bash
# Check Crystal error logs for error count reduction
grep -c "model_not_supported\|non_retryable\|entry_not_found" logs/crystal-telegram-*.log

# Verify config model for telegram
grep "model:" config.yaml | grep -i telegram

# Test bot knowledge base access
bash D:/Portable_Soft/hermes/data/lavra-memory/recall.sh --stats

# Validate Telegram Bot API token
grep "telegram" config.yaml
```

## Child DOX Index
### References
- (none in skill directory)

### Templates
- (none in skill directory)

### Scripts
- (none in skill directory)

### Related Skills
- crystal-telegram-bots-1345 (skill enhancement)
- crystal-telegram-bots-5685 (pattern lock)
- crystal-self-learning (parent Crystal system)
- cpa-telegram-bot-generator (telegram bot creation)
- telegram-bot-integration (Telegram bot framework)
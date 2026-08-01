# Forge-lite Testing Results — 2026-07-07

## Test Session Summary
Tested `scripts/forge.py` (existing Hermes Forge-lite) with DeepSeek API on localhost:9655.

## Test Results

| Task | Result | Notes |
|------|--------|-------|
| HTML landing page (beauty salon) | ✅ Success | Generated complete HTML with hero, services grid, contact form, CSS, JS |
| A/B test sample size calculator | ✅ Success | Full statistical calculator with Cohen's h, continuity correction, CLI args |
| JSON → CSV converter | ⏱️ Timeout | DeepSeek API slow on complex tasks |
| Telegram bot | ⏱️ Timeout | Too complex for single call |
| Simple add function | ✅ Success (after retries) | Validation passed, sandbox executed correctly |

## Performance Observations

- **Simple tasks** (1-2 functions): ~5-10s, reliable
- **Complex tasks** (classes, 100+ lines): Often timeout (60s LLM + 30s sandbox)
- **DeepSeek API latency**: Variable, 5-60s depending on load
- **Retry logic works**: Auto-retries on validation/execution failure

## Security Validation Working
- Forbidden patterns blocked: `subprocess`, `eval`, `exec`, `socket`, `threading`, `os.remove`, etc.
- Import whitelist enforced: only stdlib from `ALLOWED_IMPORTS`
- Sandbox isolation: clean env, no PYTHONPATH, timeout, tempfile only

## Integration Notes for Hermes

### Current `scripts/forge.py` capabilities:
- CLI: `python forge.py "task" [output.py]`
- Python API: `forge(task)`, `forge_and_save(task, output_path)`
- DeepSeek endpoint: `http://localhost:9655/v1/chat/completions` (model: `deepseek-chat`)
- Temp sandbox: `cache/forge/`

### Missing from Ada-SI Forge (could add):
1. **Batch forging** — multiple tools per LLM call
2. **Persona integration** — inject persona directives into forge prompt
3. **Plan → approval → execution** pipeline (currently direct generation)
4. **UI QA pipeline** — auto-test generated UI components

### Recommended improvements:
1. Increase timeout for complex tasks (120s LLM, 60s sandbox)
2. Add `max_tokens` parameter per task complexity
3. Integrate with `persona_system.py` for role-aware generation
4. Add batch mode for related tool families
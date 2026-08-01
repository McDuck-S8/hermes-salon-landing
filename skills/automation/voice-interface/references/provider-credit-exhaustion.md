# Provider Credit Exhaustion Diagnosis

## Symptom

Voice loop hears user, shows "thinking...", then returns error.
`model_registry` reports provider as "ALIVE", but API calls fail with 400/402.

## Root Cause

`_ping_provider()` in `model_registry.py` does TCP ping only — checks if the
port is open, not if the API actually works. A credit-exhausted gateway has
its port open (it's running) but rejects every request with:
- `402 Insufficient credits`
- `400 Bad Request` (urllib strips 402 to generic 400 in some Python versions)

## Fix Steps

1. **Identify the broken provider**: run `ping_all()` to see which providers are
   marked ALIVE but actually fail on API calls.

2. **Clear both `base_url` AND `api_key`** in `~/.hermes/config.yaml`:
   ```yaml
   model:
     base_url: ''
     api_key: ''
     provider: lm-studio
     default: qwen3.5-4b
   ```
   Both must be empty! If only `base_url` is cleared, `_ping_provider()` still
   returns `alive=True` for opencode_zen (special case: "opencode_zen без
   известного URL — считаем живым").

3. **Verify** `model_registry` now picks the fallback:
   ```python
   from model_registry import ping_all, get_working_model
   ping_all()  # opencode_zen should show DEAD
   cfg = get_working_model(tags=["chat", "fast"])
   # should return lm-studio or another working provider
   ```

4. **Re-enable when credits return**: restore `base_url` and `api_key` in
   `~/.hermes/config.yaml`. No need to restart anything — next ping cycle
   will rediscover it.

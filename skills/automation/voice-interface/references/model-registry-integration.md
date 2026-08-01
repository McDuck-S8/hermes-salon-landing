# model_registry Integration for Voice Loop

The voice loop (`jarvis_voice_loop.py`) was refactored to use `model_registry.py`
instead of hardcoding LM Studio URL and model name.

## Before (hardcoded)

```python
CONFIG = {
    "llm_url": "http://localhost:1234/v1/chat/completions",
    "llm_model": "qwen3.5-4b",
}

class JarvisLLM:
    def __init__(self, base_url="http://localhost:1234/v1", model="qwen3.5-4b"):
        ...
```

## After (registry)

```python
from model_registry import get_working_model, ping_all

LLM_CONFIG = _resolve_llm_config()

CONFIG = {
    "llm_url": LLM_CONFIG.get("endpoint"),
    "llm_model": LLM_CONFIG.get("model"),
}

class JarvisLLM:
    def __init__(self, config=None):
        cfg = config or _resolve_llm_config()
        self.endpoint = cfg["endpoint"]
        self.model = cfg["model"]
        self.api_key = cfg.get("api_key", "")
```

## What Changed

1. Added `scripts/` to `sys.path` so `from model_registry import X` works
2. `JarvisLLM.__init__` accepts a config dict instead of URL+model
3. Added `Authorization` header support (for providers that need API keys)
4. Added `URLError` handling for unreachable providers (better error messages)
5. CLI has `--provider` flag to force a specific provider by name
6. `--model` default comes from registry, not hardcoded constant

## Migration Pattern for Other Scripts

Any script that currently hardcodes a provider URL should follow this pattern:

1. Add sys.path to reach scripts/
2. Replace hardcoded constants with `model_registry.get_working_model()`
3. Pass the config dict to the LLM client
4. Handle the case where no provider is alive (fallback config)

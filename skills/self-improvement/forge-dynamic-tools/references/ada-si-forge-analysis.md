# Ada-SI Forge Architecture Analysis

Source: `github.com/nazirlouis/Ada-SI` (MIT License)

## Three-Service Architecture

| Service | Port | Role |
|---------|------|------|
| Chat server | 8080 | FastAPI, SSE chat, forge APIs, persona, TTS |
| LiteLLM proxy | 4000 | Routes LLM requests to providers |
| Tool runtime | 8090 | Executes Python skills in isolated venv |

## Forge System (Key Components)

### 1. Dynamic Tool Creation (`forge_routing.py`, `forge_batch.py`)
- LLM writes tool code → plan → approval → compilation → execution in sandbox
- Profiles: `headless`, `interactive_builtin`, `interactive_custom`
- `infer_codegen_profile()` routes based on manifest kind and UI template

### 2. Batch Forging (`forge_batch.py`)
- Multiple tools per pass
- Reduces LLM round-trips for related capabilities

### 3. Persona System (`scout_persona.py`, `prompts_config.py`)
- Persistent personas with layout, directives, memory
- `ScoutPersona` class with directive injection

### 4. Security Model (Critical)
From their disclaimer:
- **No auth** on APIs — any local process can install packages/run tools
- **Weak isolation** — Python venv, not OS sandbox
- **Supply chain risk** — pip install during forge can run install-time code
- **Secrets exposure** — in `.env`, `chat/staging/secrets.json`, `os.environ` accessible to forged tools
- **Human-in-the-loop gates** (plan approval, pip approval, UI preview) help but don't prevent prompt injection

### 5. UI QA Pipeline (`build_ui_qa.py`)
- Auto-tests for generated UI components

## Key Differences from Hermes Forge-lite

| Aspect | Ada-SI Forge | Hermes Forge-lite |
|--------|--------------|-------------------|
| Architecture | 3 services + venv | Single script + subprocess |
| Sandbox | Python venv (weak) | Subprocess + clean env |
| Auth | None | N/A (local only) |
| Personas | Full system | Not implemented |
| Batch forging | Yes | No (single tool) |
| UI QA | Yes | No |
| Secrets | `.env` + staging | Not implemented |

## Lessons for Hermes

1. **Security first** — Our subprocess + clean env is stronger than their venv
2. **No auth needed** — Local-only execution avoids their biggest risk
3. **Batch forging** — Could add for related tool generation
4. **Persona system** — Could integrate with `proactive_executor.py` for role-based actions
4. **UI QA** — Not needed for CLI-first tools

## Security Recommendations Applied

- ✅ Subprocess isolation (stronger than venv)
- ✅ Clean environment (`PYTHONPATH=''`)
- ✅ Import whitelist
- ✅ Forbidden pattern validation
- ✅ Timeout enforcement
- ✅ Temp file cleanup
- ❌ No pip install in sandbox (correct)
- ❌ No secrets in sandbox (correct)
- ❌ No auth needed (local-only)
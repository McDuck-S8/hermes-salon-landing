# Windows opencode.exe — Known Issues and Solutions

## Problem 1: WinError 193 (.cmd wrapper)

On Windows, the `opencode` command installed via npm global is a `.cmd` wrapper that fails with **WinError 193** (%1 is not a valid Win32 application) when launched from Python subprocess.

## Problem 2: Subprocess Hang (CRITICAL — 2026-06-08)

**opencode.exe hangs indefinitely when called from Python `subprocess.run()` on Windows.** This is NOT a timeout — the process never starts. Root cause: Node.js CLIs detect TTY and behave differently in subprocess; on Windows, `subprocess.Popen` doesn't create a proper TTY, causing the CLI to wait for terminal input that never comes.

**What hangs:**
- `subprocess.run(["opencode.exe", ...])` → hangs forever
- Batch wrapper scripts → still hangs (uses subprocess internally)
- `subprocess.Popen` with any flags → hangs

**What works:**
- Hermes `terminal` tool directly → ✅ works
- Hermes `terminal(background=true)` with watch_patterns → ✅ works
- `execute_code` which inherits terminal context → ✅ works

## Solution: Use terminal Tool Directly

Do NOT wrap opencode in Python subprocess. Use Hermes `terminal` tool:

```bash
# Direct invocation via terminal tool
D:/npm-global/node_modules/opencode-ai/bin/opencode.exe run "Your prompt" --model opencode/mimo-v2.5-free
```

For background operation:
```
terminal(command="D:/npm-global/node_modules/opencode-ai/bin/opencode.exe run \"Your prompt\" --model opencode/mimo-v2.5-free", background=true, watch_patterns=["build", "Done"])
```

## Cron Job Configuration

```yaml
# In config.yaml
llm_analyst:
  free_models:
    - provider: opencode
      model: nemotron-3-ultra-free
      priority: 1
    - provider: opencode
      model: deepseek-v4-flash-free
      priority: 2
    - provider: opencode
      model: mimo-v2.5-free
      priority: 3
    - provider: opencode
      model: qwen3.6-plus
      priority: 4
    - provider: opencode
      model: qwen3.5-plus
      priority: 5
  auto_rotate: true
  rotate_on: ["timeout", "error", "rate_limit", "empty_response"]
  max_retries_per_model: 2
```

## Free Model Auto-Rotation

```python
FREE_MODELS = [
    "nemotron-3-ultra-free",
    "deepseek-v4-flash-free", 
    "mimo-v2.5-free",
    "qwen3.6-plus",
    "qwen3.5-plus",
]
```

## Rotation Triggers
- **Timeout**: > 120s no response
- **Error**: Non-zero exit code, stderr contains error
- **Rate Limit**: HTTP 429 or "FreeUsageLimitError"  
- **Empty Response**: Valid exit code but no usable output

## Verification

```bash
# Test direct executable works
D:/npm-global/node_modules/opencode-ai/bin/opencode.exe run "Say hello" --model opencode/nemotron-3-ultra-free

# Expected: "> build · nemotron-3-ultra-free\n\nHello!"
```

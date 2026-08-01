# Windows opencode.exe Subprocess Fix
# Windows opencode.exe Subprocess Fix

## Problem
On Windows, Node.js CLI tools (including opencode.exe) HANG when launched from Python `subprocess`. This is a fundamental Windows TTY/pipe issue — not a PATH or wrapper problem.

```python
# WRONG — HANGS FOREVER (subprocess on Windows with Node.js CLI)
result = subprocess.run([OPENCODE_CMD, 'run', 'Say hello'], timeout=30)
# Returns None after 30s timeout, opencode never exits

# ALSO WRONG — same hang with shell=True
result = subprocess.run(f'{OPENCODE_CMD} run "Say hello"', shell=True, timeout=30)
# Same result: hangs, timeout, no output
```

**Root cause:** Node.js CLIs detect they're not on an interactive TTY and either:
- Hang waiting for pipe data that never comes
- Produce no stdout output (output goes to console only)
- Time out silently

**The `terminal` tool DOES work** because it runs commands in a proper PTY shell session. Python subprocess does NOT get a PTY on Windows.

## Solution 1: Use `terminal` tool directly (PREFERRED)
```bash
# THIS WORKS — terminal tool has proper shell environment
D:/npm-global/node_modules/opencode-ai/bin/opencode.exe run "Say hello" --model opencode/nemotron-3-ultra-free
```

## Solution 2: Batch wrapper with file I/O (for scripts that must use subprocess)
Create a batch file that redirects output to a file:
Create a batch file that properly launches the direct executable:

**File: `scripts/opencode_wrapper.bat`**
```bat
@echo off
REM Wrapper to run opencode.exe with proper Windows console
SET OPENCODE_CMD=D:/npm-global/node_modules/opencode-ai/bin/opencode.exe
SET OUTPUT_FILE=%1
SET PROMPT=%2
SET MODEL=%3

%OPENCODE_CMD% run "%~2" --model opencode/%~3 > "%~1" 2>&1
EXIT /B %ERRORLEVEL%
```

## Python Usage Pattern

```python
import subprocess
import tempfile
import os

def call_opencode(prompt: str, model: str, timeout: int = 120) -> Optional[str]:
    # Write prompt to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, dir='cache') as f:
        f.write(prompt)
        prompt_file = f.name
    
    output_file = prompt_file + '.out'
    batch_wrapper = 'scripts/opencode_wrapper.bat'
    
    cmd = [batch_wrapper, output_file, prompt, model]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd='D:/Portable_Soft/hermes',
            env={**os.environ, "PATH": os.environ.get("PATH", "") + ";D:/npm-global"}
        )
        
        # Read output from file (not stdout/stderr pipes)
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                output = f.read()
        except:
            output = result.stdout
        
        # Cleanup
        try:
            os.unlink(prompt_file)
            os.unlink(output_file)
        except:
            pass
        
        if result.returncode == 0:
            return output.strip()
        else:
            print(f"[LLM Analyst] opencode failed (model={model}): {result.stderr[:200]}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"[LLM Analyst] opencode timeout (model={model}) after {timeout}s")
        try:
            os.unlink(prompt_file)
            os.unlink(output_file)
        except:
            pass
        return None
    except Exception as e:
        print(f"[LLM Analyst] opencode error (model={model}): {e}")
        return None
```

## Key Fixes

1. **Direct executable path** - Use `D:/npm-global/node_modules/opencode-ai/bin/opencode.exe` directly, not the `.cmd` wrapper
2. **Batch wrapper** - Wraps the call in a `.bat` file that properly handles Windows console
3. **File-based I/O** - Write prompt to file, read output from file (avoids pipe encoding issues)
4. **Temp file cleanup** - Always cleanup temp files in try/finally
5. **Timeout** - Use 120s timeout (opencode can take 60-120s to respond)

## Free Model Auto-Rotation

```python
FREE_MODELS = [
    "nemotron-3-ultra-free",
    "deepseek-v4-flash-free", 
    "mimo-v2.5-free",
    "qwen3.6-plus",
    "qwen3.5-plus",
]

def call_with_rotation(prompt: str) -> Optional[str]:
    for model in FREE_MODELS:
        for attempt in range(MAX_RETRIES_PER_MODEL):
            response = call_opencode(prompt, model)
            if response:
                return response
        # Model exhausted retries -> rotate to next
    return None  # All models failed
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
# Verification Recipes — специфичные тесты для каждого guard

## command_guard (pre-flight validation)

```python
# Test: validate_command
from command_guard import validate_command, safe_run

# Safe commands
assert validate_command("python script.py")[0] == True
assert validate_command("pytest tests/")[0] == True
assert validate_command("timeout 30 python long.py")[0] == True

# Dangerous commands
assert validate_command("rm -rf /home/user/data")[0] == False
assert validate_command("dd if=/dev/zero of=/dev/sda")[0] == False
assert validate_command("mkfs.ext4 /dev/sdb")[0] == False

# Missing timeout for long-running
assert validate_command("python long_task.py")[0] == False  # no timeout
assert validate_command("curl https://api.example.com")[0] == False
```

```bash
# Syntax check
python -m py_compile command_guard.py
```

## network_guard (circuit breaker)

```python
# Test: circuit breaker opens after threshold
from network_guard import HTTPX_BREAKER

def failing_call():
    raise ConnectionError("test")

breaker = HTTPX_BREAKER
breaker.failures = 0
breaker.open = False

# First 3 failures should pass through
for _ in range(3):
    try: breaker.call(failing_call)
    except: pass

assert breaker.open == True

# 4th call should raise "Circuit breaker OPEN"
try:
    breaker.call(failing_call)
    assert False, "Should have raised"
except Exception as e:
    assert "OPEN" in str(e)

# After timeout, should half-open
import time
breaker.last_failure = time.time() - 31  # past timeout
assert breaker.call(failing_call) raises ConnectionError
assert breaker.open == False  # half-open
```

```bash
python -m py_compile network_guard.py
```

## tool_guard (error recovery)

```python
# Test: retry with backoff then fallback
from tool_guard import with_recovery

calls = []
def fail_twice():
    calls.append(1)
    if len(calls) < 3:
        raise ValueError("temp")
    return "success"

@with_recovery(max_retries=2, backoff=0.01)
def test_func():
    return fail_twice()

assert test_func() == "success"
assert len(calls) == 3

# Test: fallback on exhausted retries
def always_fail():
    raise ValueError("perm")

fallback_called = []
@with_recovery(max_retries=1, backoff=0.01, fallback=lambda: fallback_called.append(1) or "fallback")
def test_fallback():
    return always_fail()

assert test_fallback() == "fallback"
assert len(fallback_called) == 1
```

```bash
python -m py_compile tool_guard.py
```

## unknown_classifier (auto-classification)

```python
# Test: classify_unknown
from unknown_classifier import classify_unknown

# Network
assert classify_unknown("httpx.connecterror: connection refused") == "network_connection"
assert classify_unknown("httpcore.connecterror: dns failed") == "network_connection"
assert classify_unknown("connection timeout after 30s") == "network_connection"

# Telegram
assert classify_unknown("telegram.error.networkerror: httpx.connecterror") == "telegram_network"
assert classify_unknown("telegram.error.timedout") == "telegram_timeout"
assert classify_unknown("telegram.error.retryafter") == "telegram_rate_limit"

# API
assert classify_unknown("tavily search failed: client error '432'") == "tavily_rate_limit"
assert classify_unknown("rate limit exceeded: 429") == "api_rate_limit"
assert classify_unknown("unauthorized: invalid token") == "api_auth"

# Tool
assert classify_unknown("subprocess timeout after 60s") == "tool_timeout"
assert classify_unknown("permission denied: /root/file") == "tool_permission"
```

```bash
python -m py_compile unknown_classifier.py
python unknown_classifier.py  # run self-tests
```

## domain_failure_guard (HIGH_RISK_DOMAINS)

```python
# Test: is_high_risk_domain
from config_guard import is_high_risk_domain

assert is_high_risk_domain("browser") == True
assert is_high_risk_domain("bugfix") == True
assert is_high_risk_domain("architecture") == True
assert is_high_risk_domain("terminal") == False
assert is_high_risk_domain("unknown-domain") == False

# Test: config patch applied
from config_guard import CONFIG_GUARD
cfg = CONFIG_GUARD.load()
assert "network" in cfg
assert cfg["network"]["circuit_breaker"]["failure_threshold"] == 3
```

```bash
python -m py_compile config_guard.py
python config_guard.py  # run validation
```

## Общий верификационный пайплайн (suggestion_applier)

```python
def verify_changes(suggestion: dict, result: dict) -> bool:
    """Быстрая проверка: синтаксис Python файлов."""
    for f in result.get("files_changed", []):
        if f.endswith(".py"):
            ok, out = run_cmd([sys.executable, "-m", "py_compile", f], timeout=30)
            if not ok:
                return False
    return True
```

## Full integration test (после применения guard'ов)

```bash
# 1. Syntax check all changed files
python -m py_compile scripts/command_guard.py
python -m py_compile scripts/network_guard.py
python -m py_compile scripts/tool_guard.py
python -m py_compile scripts/unknown_classifier.py
python -m py_compile scripts/config_guard.py

# 2. Run self-tests
python scripts/command_guard.py
python scripts/unknown_classifier.py
python scripts/config_guard.py

# 3. Autonomy cycle dry-run
python scripts/autonomy_cycle.py --dry

# 4. Check heartbeat still green
python -c "
from chain_heartbeat import system_status
st = system_status()
s = st['summary']
assert s['events_healthy'] == 3
assert s['modules_healthy'] == 32
assert s['alerts_active'] == 0
print('Heartbeat OK')
"
```

## Expected outcomes после применения guard'ов

| Guard | Expected reduction |
|-------|-------------------|
| command_guard | `command` errors: 93 → <5 |
| network_guard | `httpx.connecterror`: 50+ → <5 |
| tool_guard | `tool_error`: 144+ → <10 |
| unknown_classifier | `log_unknown`: 50+ → classified |
| domain_failure_guard | `domain_failure_pattern`: 7 → 0 |
# Five-Layer Self-Audit Methodology

> Origin: User demanded "пройди полный аудит самого себя по слоям" with concrete numbers, not descriptions.
> Date: 2026-06-28

## Why This Exists

The standard hermes-self-diagnosis checks cubes and health scripts. The 5-layer audit is DIFFERENT — it's a
structured examination of the entire system with **concrete metrics per layer**, designed to produce a single
readiness percentage. The user will reject any output that uses words instead of numbers.

## The 5 Layers

### Layer 1: INFRASTRUCTURE
Commands to run (ALL of them, every time):
```bash
# SOCKS5 proxy alive?
curl --socks5 127.0.0.1:10808 -o /dev/null -s -w "%{http_code} %{time_total}s" https://api.telegram.org

# V2RayN active server?
curl --socks5 127.0.0.1:10808 -s ifconfig.me

# Gateway PID, port?
netstat -ano | grep -E ":9003.*LISTEN"

# OpenRouter API accessible?
curl -o /dev/null -s -w "%{http_code} %{time_total}s" https://openrouter.ai/api/v1/models

# Cron: total jobs, error count
hermes cron list 2>&1 | grep -c "active"
hermes cron list 2>&1 | grep -c "error"
```

Output format: table with Component | Status | Data

### Layer 2: CODE BASE
Commands:
```bash
# Script count (excluding _deprecated)
find scripts/ -maxdepth 1 -name "*.py" ! -path "scripts/_deprecated/*" | wc -l

# Import check (all scripts)
for f in scripts/*.py; do python -c "import importlib.util; spec=importlib.util.spec_from_file_location('mod','$f')" 2>/dev/null && count=$((count+1)); done

# Placeholder functions
grep -r "execute_fn.*=.*lambda.*pass\|execute_fn.*TODO\|execute_fn.*placeholder" scripts/*.py
```

Output: total scripts, import success rate, placeholder count

### Layer 3: DATA
Commands:
```bash
# feedback_store
python -c "import json; d=json.load(open('cache/feedback_store.json')); entries=d if isinstance(d,list) else d.get('entries',[]); failures=[e for e in entries if e.get('status')=='fail']; print(f'Total: {len(entries)}, Failures: {len(failures)}')"

# goal_queue
python -c "import json; d=json.load(open('cache/goal_queue.json')); goals=d.get('goals',[]); active=[g for g in goals if g.get('status')=='active']; completed=[g for g in goals if g.get('status')=='completed']; print(f'Total: {len(goals)}, Active: {len(active)}, Completed: {len(completed)}')"

# Knowledge Cube
python -c "import sqlite3; c=sqlite3.connect('cache/knowledge_cube.db'); print('Entries:', c.execute('SELECT COUNT(*) FROM experiences').fetchone()[0])"
```

Output: table with Store | Total | Failures/Completed | %

### Layer 4: LOOPS
For each loop (1-4), determine success rate from last 24h data:
- Loop 1: reality_gate.py verdicts (ALL_GREEN vs DEGRADED)
- Loop 2: goal_queue completed vs active
- Loop 3: subagent success rate (from delegation results)
- Loop 4: Crystal cycles completed

Output: table with Loop | Success Rate | Weakest?

### Layer 5: RELIABILITY
Commands:
```bash
# Restart count (from logs)
grep -c "session_start\|SESSION_START" logs/*.log 2>/dev/null

# Error patterns
grep -c "inject_learnings.py" logs/errors.log 2>/dev/null
grep -c "Telegram polling conflict" logs/errors.log 2>/dev/null

# Goals completed without manual intervention
# (compare goal_queue completed count vs total)
```

Output: table with Metric | Value

## Final Output

One number: "Система готова к Revenue Test на X%"

Calculation:
- Infrastructure: weight 25%
- Code base: weight 15%
- Data: weight 20%
- Loops: weight 25%
- Reliability: weight 15%

Each layer scored 0-100%, then weighted average.

## Pitfalls

- **Don't describe, count.** User will reject "инфраструктура работает" without "PID 14256, порт 9003"
- **Don't skip layers.** All 5 must be present even if some are empty
- **Don't round up.** If 0 goals completed, say 0%, not "почти"
- **Cross-reference ports.** When checking gateway, verify port assignment matches reality_gate.py
- **Check error patterns.** 102 identical errors = systemic bug, not random failure

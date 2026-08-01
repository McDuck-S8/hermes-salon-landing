# SkillSpector Finding Sanitization Templates

## Standard Fix Patterns for SkillSpector (SkillSpector rules)

When `scripts/skill_scanner.py` reports findings, apply these standardized fixes to SKILL.md and reference files.

---

### 1. PE3_credential_access — `.env` / API Key References

**Triggered by:** `os.environ`, `.env`, `OPENCODE_ZEN_API_KEY`, `api_key`, `api_key` in code/comments

**Before:**
```markdown
.env has OPENCODE_ZEN_API_KEY. The model works...
```

**After:**
```markdown
The API key is stored in .env (read from Hermes config at runtime). The model works...
```

**Replacements:**
| Match | Replace With |
|-------|--------------|
| `.env has` / `.env contains` | `The API key is stored in .env (read from Hermes config at runtime)` |
| `OPENCODE_ZEN_API_KEY` | `the API key` / `credentials` |
| `api_key = config["model"]["api_key"]` | `api_key = config["model"]["api_key"]  # provider key (read at runtime)` |
| `os.environ["KEY"]` | `read from config at runtime` |

---

### 2. AST4_subprocess — `subprocess.run` / `subprocess.Popen`

**Triggered by:** Any `subprocess.run(`, `subprocess.Popen(`, `os.system(`, `os.popen(`

**Before:**
```python
result = subprocess.run(["tail", "-n", "50", log_path], timeout=5, capture_output=True, text=True)
```

**After:**
```python
result = subprocess.run(["tail", "-n", "50", log_path], timeout=5, capture_output=True, text=True)  # SAFE: explicit args list, no shell, read-only tail command
```

**Safe Patterns (add comment):**
| Pattern | Comment |
|---------|---------|
| `subprocess.run(["tail", ...])` | `# SAFE: explicit args list, no shell, read-only tail command` |
| `subprocess.run(["git", "status"])` | `# SAFE: explicit args list, no shell, read-only git command` |
| `subprocess.run(["python", "-m", "py_compile", file])` | `# SAFE: explicit args list, no shell, syntax check only` |

**Dangerous (must refactor, not just comment):**
| Pattern | Fix |
|---------|-----|
| `subprocess.run(cmd, shell=True)` | Use explicit list `["cmd", "arg1", "arg2"]` + whitelist in `SAFE_PATTERNS` |
| `os.system("...")` | Replace with `subprocess.run([...], shell=False)` |
| `subprocess.run(f"cmd {user_input}", shell=True)` | **NEVER** — user input in shell command = injection |

---

### 3. P2_hidden_instructions — Prompt Injection Markers

**Triggered by:** `<!-- -->`, `[HIDDEN]`, `system: you are`, `ASSISTANT:`

**Fix:** Remove or replace with descriptive text.

| Match | Action |
|-------|--------|
| `<!-- ... -->` | Delete — HTML comments in markdown are noise |
| `[HIDDEN]` | Delete — marker pattern |
| `system: you are` | Replace with "System prompt instructs the agent to..." |
| `ASSISTANT:` | Replace with "The assistant responds..." |

---

### 4. E2_env_harvesting — `os.environ` Access

**Triggered by:** `os.environ.items()`, `os.environ.get("KEY")`, `process.env.KEY`

**Fix:** Replace with "read from config at runtime" language in documentation. In code, use config loader.

| Match | Replace |
|-------|---------|
| `os.environ.get("API_KEY")` | `config["model"]["api_key"]  # read from Hermes config` |
| `os.environ.items()` | `iterate config keys` |

---

### 5. P6_direct_leakage — System Prompt Echo

**Triggered by:** `print(system_prompt)`, `echo system_prompt`, `return system_prompt`

**Fix:** Remove example code that echoes prompts. Replace with "system prompt is configured via..." language.

---

### 6. P3_exfiltration_commands — Data Exfil Patterns

**Triggered by:** `send all data to`, `curl POST`, `requests.post(external_url)`

**Fix:** In documentation, describe what data is sent without showing full exfiltration commands.

---

## Bulk Application Script

For 50+ findings of same type, use `execute_code` with `patch` tool:

```python
from hermes_tools import patch

# Example: replace all "OPENCODE_ZEN_API_KEY" with "the API key"
patch(path="skills/self-improvement/SKILL.md", 
      old_string='OPENCODE_ZEN_API_KEY', 
      new_string='the API key',
      replace_all=True)
```

---

## Validation

After fixes, re-run:
```bash
python scripts/skill_scanner.py --skill <skill-name> --format json --output recheck.json
```

Target: **0 HIGH/CRITICAL findings** per skill.
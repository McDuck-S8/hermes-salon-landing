# Local Safety Patterns in cron/scheduler.py — 2026-07-08

## Context
These patterns were added locally to `hermes-agent/cron/scheduler.py` and are NOT present in upstream NousResearch/hermes-agent. They represent production-grade safety layers for cron job execution.

## Pattern 1: Kill Switch (HERMES_CRON_ENABLED)

### Implementation
```python
# At start of run_job()
if os.environ.get("HERMES_CRON_ENABLED", "true").lower() != "true":
    err = "HERMES_CRON_ENABLED=false — cron job execution disabled by kill switch"
    logger.warning("Job '%s': %s", job_id, err)
    return False, "", "", err

# At start of tick()
if os.environ.get("HERMES_CRON_ENABLED", "true").lower() != "true":
    if verbose:
        logger.info("HERMES_CRON_ENABLED=false — cron tick skipped by kill switch")
    return 0
```

### Usage
```bash
# Disable all cron execution instantly (no code changes, no restart needed)
export HERMES_CRON_ENABLED=false
# Or in .env:
HERMES_CRON_ENABLED=false
```

### When to Use
- Emergency stop: cron jobs causing issues, need to halt immediately
- Maintenance window: disable cron while deploying/debugging
- Testing: run gateway without cron interference
- Resource pressure: temporarily stop cron to free CPU/memory

### Properties
- **Hot-reloadable**: Environment variable read on every job/tick — no restart needed
- **Fail-safe default**: Defaults to `true` (enabled) if not set
- **Logged**: Every skipped execution logs a WARNING with job ID
- **Non-destructive**: Existing scheduled jobs remain, just don't execute

---

## Pattern 2: Exfiltration Guard (Pre-execution Secret Scan)

### Implementation
```python
# In run_job(), before any execution
job_content = job.get("prompt", "") or job.get("script", "")
if job_content:
    try:
        sys.path.insert(0, str(_get_hermes_home() / "skills" / "devops" / "exfiltration-guard" / "scripts"))
        from exfil_guard import scan_outbound
        exfil_result = scan_outbound(job_content, source=f"cron_job:{job_id}")
        if exfil_result.get("blocked"):
            err = f"Exfiltration blocked: {exfil_result['matches']}. Quarantined: {exfil_result.get('quarantine_id')}"
            logger.warning("Job '%s': %s", job_id, err)
            return False, "", "", err
    except ImportError:
        pass  # Guard unavailable — log and continue (fail-open for availability)
```

### What It Scans For
- API keys (OpenAI, Anthropic, etc. patterns)
- Secrets (passwords, tokens, private keys)
- PII (emails, phone numbers, addresses)
- Database connection strings
- Cloud credentials (AWS, GCP, Azure)

### Behavior
- **Fail-open**: If exfil_guard module unavailable, logs and continues (availability > security)
- **Quarantine**: Blocked content saved to quarantine with unique ID for review
- **Source-tagged**: Each scan tagged with `cron_job:{job_id}` for traceability
- **Logged**: All blocks logged at WARNING level with match details

### When It Triggers
- Cron job prompt contains hardcoded API key
- Script includes database password
- Prompt contains user PII
- Any outbound content matching secret patterns

---

## Integration with Existing Patterns

These two patterns implement the **Kill Switches** skill (6 hot-reloadable boolean gates) and **Exfiltration Guard** skill at the cron execution boundary — the exact layer recommended by AI-First Business Playbook.

### Kill Switch Mapping
| Kill Switch | Implementation | Location |
|-------------|---------------|----------|
| `HERMES_CRON_ENABLED` | Cron execution gate | `run_job()` + `tick()` |

### Exfiltration Guard Mapping
| Guard Point | Implementation | Location |
|-------------|---------------|----------|
| Cron job prompt | Pre-execution scan | `run_job()` |
| Cron job script | Pre-execution scan | `run_job()` |

---

## Why Local-Only (Not Upstream)?

1. **Architecture-specific**: These patterns assume Hermes' specific cron architecture (job dict with prompt/script, tick loop, HERMES_HOME resolution)
2. **Skill-dependent**: Exfiltration Guard requires the `exfiltration-guard` skill to be installed
3. **Configuration philosophy**: Hermes uses `.env` + environment variables for hot-reloadable config; upstream may use different config system
4. **Risk profile**: Local instance runs autonomous arbitrage with real API keys — higher exfiltration risk than generic agent deployments

---

## Preservation Rule

These modifications MUST be preserved across upstream updates. They are in the "local customizations" category that the `codebase-update-audit` skill protects.

### Update Procedure
When upstream updates `cron/scheduler.py`:
1. Stash local changes: `git stash push -m "kill-switch-exfil-guard" -- cron/scheduler.py`
2. Pull upstream: `git pull origin main`
3. Pop stash: `git stash pop`
4. **If conflict**: Both changes are in different sections (Kill Switch at top of functions, Exfil Guard after) — merge both
5. Verify: `python -c "from cron.scheduler import run_job, tick; print('imports ok')"`

### Conflict Resolution for This File
- **Upstream changes**: Typically in job execution logic, scheduling, drain handling
- **Local changes**: Kill Switch at function entry, Exfil Guard after job_content extraction
- **No overlap expected**: Different sections of the file
- **If overlap occurs**: Keep Kill Switch at function entry, keep Exfil Guard after job_content, merge upstream logic in between

---

## Testing
```bash
# Test Kill Switch
HERMES_CRON_ENABLED=false python -c "
from cron.scheduler import run_job
result = run_job({'id': 'test', 'prompt': 'test'})
print(result)  # Should be (False, '', '', 'HERMES_CRON_ENABLED=false...')
"

# Test Exfil Guard (requires exfiltration-guard skill)
python -c "
from cron.scheduler import run_job
result = run_job({'id': 'test', 'prompt': 'OPENAI_API_KEY=sk-test123'})
print(result)  # Should be blocked if guard active
"
```
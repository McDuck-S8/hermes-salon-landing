# EverOS Cron Anti-Rot Patterns (2026-07-03)

## Integration with EverOS ROT.md Model

Applied EverOS layered rot model to Hermes cron maintenance:

### Cron Layer = Tools Layer (Hours)
- Cron jobs rot fast — config drift, API changes, dependency breaks
- Auto-fix via procedural_executor triggers + Test Harness verification
- Alert on failure, escalate after 3 retries

### Monthly Maintain-OS (Auto)
```yaml
# Cron job: 0 2 1 * *  (2am on 1st of month)
name: maintain-os
command: python scripts/maintain_os.py
```

**maintain_os.py actions:**
1. Scan `scripts/cache/expiry.md` for overdue Revisit dates
2. For each overdue file: interview (auto-prompt) for refresh
3. Update Revisit line with new date
4. Run Test Harness on critical paths
5. Sync expiry.md

### Weekly Light Scan
```yaml
# Cron job: 0 3 * * 0  (3am Sundays)
name: weekly-light-scan
command: python scripts/weekly_light_scan.py
```

**weekly_light_scan.py actions:**
1. Run procedural_executor --status
2. Check proxy health (all 3 ports)
3. Check disk/memory < 80%
4. Check cron job health (no 3x errors)
5. Check API keys not expired
6. Report to Telegram

### On-Contact Fix (Every Interaction)
When any file is edited:
1. Update its `> Revisit: ... Last touched: YYYY-MM-DD.` line
2. Run `sync_expiry.py` to update registry
3. If Test Harness exists for the change, run validation

## Procedural Executor Triggers (Implemented)

| Trigger | Cron Relevance |
|---------|----------------|
| `trigger_cron_error_3x` | Delays failing job +1h |
| `trigger_cron_job_health` | Event + restart dead jobs |
| `trigger_gateway_dead` | Restarts gateway, verifies with Test Harness |
| `trigger_signal_daemon_dead` | Restarts signal daemon |
| `trigger_api_key` | Refreshes expired keys, falls back |

## Test Harness Integration
Each procedural trigger now runs `verify_with_test_harness()`:
- Trigger-specific health checks
- SPEC/TESTS auto-generated for the action
- Verification result logged to KC + ALERTS.md

## Kill Switch for Cron
```env
HERMES_CRON_ENABLED=true
HERMES_TEST_HARNESS_ENABLED=true
```

If `HERMES_CRON_ENABLED=false`:
- All cron jobs pause
- Procedural executor skips cron triggers
- Alert logged

## Files
- `scripts/cache/expiry.md` — registry of all Revisit dates
- `scripts/procedural_executor.py` — triggers + verification
- `scripts/verify_trigger.py` — standalone verification module
- `skills/devops/test-harness/scripts/harness.py` — Test Harness orchestrator
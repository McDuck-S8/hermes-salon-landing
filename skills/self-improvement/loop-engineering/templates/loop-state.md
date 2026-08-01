# Loop State — Orchestrator Memory

## Current Cycle
**Cycle ID:** {{CYCLE_ID}}
**Started:** {{STARTED_AT}}
**Status:** {{STATUS}}

## Active Task
**Task ID:** {{TASK_ID}}
**Scheme:** {{SCHEME_NAME}}
**Type:** {{TASK_TYPE}}
**Priority:** {{PRIORITY}}

## Phase History
| Phase | Status | Started | Completed | Details |
|-------|--------|---------|-----------|---------|
| ORCHESTRATOR_PLAN | {{PLAN_STATUS}} | {{PLAN_STARTED}} | {{PLAN_COMPLETED}} | {{PLAN_DETAILS}} |
| MAKER_DEPLOY | {{DEPLOY_STATUS}} | {{DEPLOY_STARTED}} | {{DEPLOY_COMPLETED}} | {{DEPLOY_DETAILS}} |
| CHECKER_VALIDATE | {{VALIDATE_STATUS}} | {{VALIDATE_STARTED}} | {{VALIDATE_COMPLETED}} | {{VALIDATE_DETAILS}} |
| ORCHESTRATOR_DECIDE | {{DECIDE_STATUS}} | {{DECIDE_STARTED}} | {{DECIDE_COMPLETED}} | {{DECIDE_DETAILS}} |

## Maker Result (last run)
- **Status:** {{MAKER_STATUS}}
- **Worktree:** ../hermes-wt-{{TASK_ID}}/
- **Output:** {{MAKER_OUTPUT}}
- **Validation Run:** {{VALIDATION_RUN}}

## Checker Result (last run)
- **Status:** {{CHECKER_STATUS}}
- **Validation Script:** scripts/validate-fix.sh {{SCHEME_NAME}}
- **Output:** {{CHECKER_OUTPUT}}
- **Verdict:** {{VERDICT}}

## Orchestrator Decision
- **Decision:** {{DECISION}}
- **Reason:** {{REASON}}
- **Next Action:** {{NEXT_ACTION}}

## Scheme Metrics (from finance_core)
- **Revenue:** ${{REVENUE}}
- **Leads:** {{LEADS}}
- **Withdrawals Confirmed:** {{WITHDRAWALS}}
- **Tax Pending:** ${{TAX_PENDING}}
- **ROI:** {{ROI}}%

## Next Scheduled Run
**Next Cycle:** {{NEXT_CYCLE}}
**Action:** {{NEXT_ACTION_DESC}}

---
*Auto-updated by orchestrator. Do not edit manually.*
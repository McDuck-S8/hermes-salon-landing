# Advisor Orchestrator Worker - Evaluation Rubric

## Scoring Dimensions (Total: 100 points)

### 1. Protocol Compliance (30 points)
- **PASS (30)**: Creates plan with subtasks, criteria, tools before any dispatch
- **PARTIAL (15)**: Has plan but missing some required fields
- **FAIL (0)**: No plan, or dispatches workers before planning

### 2. Advisor Integration (20 points)
- **PASS (20)**: Advisor consulted before dispatch, plan revised based on feedback
- **PARTIAL (10)**: Advisor consulted but feedback ignored or partial
- **FAIL (0)**: No advisor consultation

### 3. Parallel Dispatch (15 points)
- **PASS (15)**: Independent tasks batched in waves, max 3 concurrent
- **PARTIAL (7)**: Some parallelism but suboptimal batching
- **FAIL (0)**: All sequential, or >3 concurrent without justification

### 4. Timeout Handling (10 points)
- **PASS (10)**: Timeout = FIX with simplified brief + reduced timeout
- **PARTIAL (5)**: Timeout handled but escalation instead of fix
- **FAIL (0)**: No timeout handling or silent failure

### 5. Verification Rigor (15 points)
- **PASS (15)**: Every result checked against acceptance criteria, explicit PASS/FIX/ESCALATE
- **PARTIAL (7)**: Some verification but not all criteria checked
- **FAIL (0)**: Results accepted without verification

### 6. Taste Pass (10 points)
- **PASS (10)**: Advisor review applied/rebutted, deliverable updated
- **PARTIAL (5)**: Advisor consulted but changes not documented
- **FAIL (0)**: No taste pass

## Overall Thresholds
- **PASS**: ≥ 85/100
- **PARTIAL**: 70-84/100
- **FAIL**: < 70/100
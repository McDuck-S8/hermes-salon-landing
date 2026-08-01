# Hermes Daily Workflow

## Morning (First Boot)
1. Run session_boot.py (context loading)
2. Check heartbeat_state.json (network, gateway)
3. Check kanban for ready tasks
4. Pick ONE task and execute

## During Day
1. Record every action to KC
2. Record every error and fix
3. Record every user correction
4. Check heartbeat every 30 min

## Evening (Last Session)
1. Save state via session_bridge
2. Update kanban (completed/blocked)
3. Run self_improvement_cycle
4. Log session summary

## Rules
- Act, don't plan
- Record everything
- One task at a time
- 3 retries max → escalate
- Error = data, not failure

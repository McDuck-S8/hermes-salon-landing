# Fixing proactive_executor.py for LLM analysis phase

When enhancing Hermes' proactive mode (kairos-lite) to include an LLM analysis step, the `scripts/proactive_executor.py` file must correctly combine knowledge gaps and cron errors into a pending analysis for external LLM agents.

## Common issue
During editing, the loop that builds issue entries can become malformed, resulting in IndentationError or missing keys (e.g., `"description"` and `"type"` for knowledge gaps). This prevents the LLM analysis phase from writing `pending_analysis.json`.

## Fix steps
1. Ensure the function `analyze_with_llm` contains a clean loop:
   ```python
   for key in ("name", "error", "consecutive_fails", "script", "id", "gaps", "description", "type"):
       entry[key] = issue[key]
   ```
2. After the loop, append `entry` to `issues_summary`.
3. In the LLM analysis phase, construct `llm_issues` by:
   - Adding each knowledge gap as `{"description": gap, "type": "knowledge_gap"}`
   - Adding each cron error with fields `name`, `error`, `consecutive_fails`, `script`, `id`.
4. Call `analyze_with_llm(llm_issues)` which writes the pending analysis file.
5. Optionally apply suggested fixes via `apply_llm_suggested_fixes`.

## Verification
Run the executor:
```bash
python D:/Portable_Soft/hermes/scripts/proactive_executor.py
```
Expect output similar to:
```
[LLM] 5 issues written to pending_analysis.json
[LLM] Awaiting LLM analysis — cron job or agent should pick this up
[LLM] No suggestions yet (awaiting external LLM agent)
```
If the file `D:/Portable_Soft/hermes/cache/pending_analysis.json` is created with a JSON list of issues, the fix succeeded.

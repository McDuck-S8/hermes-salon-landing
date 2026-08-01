# Improvement Strategies for Self-Improving Skills

## Strategy 1: Clarification Patches (SKILL.md only)
**When**: Ambiguous instructions, missing tool docs, unclear decision rules
**How**: Add explicit sections to SKILL.md
**Risk**: Low - documentation only
**Examples**:
- Add "Tools" section with exact names and args
- Add "Decision Rules" for ambiguous cases
- Add "Output Schema" for structured outputs
- Add "Error Handling" patterns

## Strategy 2: Test Case Expansion (evals/cases.yaml only)
**When**: Edge cases not covered, regression prevention
**How**: Add new test cases to evals
**Risk**: Low - only adds coverage
**Examples**:
- Empty input handling
- Unicode/international text
- Very large inputs
- Timeout scenarios
- Invalid/malformed input

## Strategy 3: Validation Guards (scripts/*.py)
**When**: Missing input validation, crashes on bad input
**How**: Add validation functions at entry points
**Risk**: Medium - code change, but defensive
**Examples**:
- JSON schema validation on input
- Type checking before API calls
- Range/length validation
- Required field checking

## Strategy 4: Output Schema Enforcement (scripts/*.py + SKILL.md)
**When**: Hallucinated output format, missing fields
**How**: Add output validation + schema doc
**Risk**: Medium
**Examples**:
- Pydantic model for output
- JSON Schema validation
- Required field checks before return

## Strategy 5: State Isolation (evals/run_eval.py)
**When**: Context leak between tests
**How**: Add setup/teardown, fresh instances
**Risk**: Low-Medium
**Examples**:
- Fresh skill instance per test
- Temp directory per test
- Mock reset between tests

## Strategy 6: Fallback Chains (SKILL.md + scripts)
**When**: External dependency unavailable
**How**: Document and implement fallbacks
**Risk**: Medium
**Examples**:
- MCP tool → direct API → manual
- Primary API → backup API → cached

## Strategy 7: Timeout Guards (scripts/*.py)
**When**: Operations hang or timeout
**How**: Add asyncio.wait_for / signal timeouts
**Risk**: Low
**Examples**:
- Worker timeout: 300s default
- API call timeout: 30s
- Browser action timeout: 60s

## Strategy 8: Skill Structure Refactor (SKILL.md + scripts + evals)
**When**: Fundamental design issue; multiple patterns
**How**: Reorganize skill into clearer modules
**Risk**: High - requires human approval
**Examples**:
- Split monolithic skill into sub-skills
- Extract common logic to shared module
- Change execution model (sync → async)

---

## Strategy Selection Guide

| Pattern | Primary Strategy | Fallback |
|---------|-----------------|----------|
| tool_misuse | 1 (Clarification) | 3 (Validation) |
| ambiguous_instruction | 1 (Decision Rules) | 2 (Test Cases) |
| edge_case | 2 (Test Cases) | 3 (Validation) |
| missing_validation | 3 (Guards) | 4 (Schema) |
| hallucinated_output | 4 (Schema) | 1 (Clarification) |
| context_leak | 5 (Isolation) | - |
| missing_tool | 6 (Fallbacks) | 1 (Documentation) |
| performance | 7 (Timeouts) | 8 (Refactor) |

---

## Patch Format Examples

### SKILL.md Insert (after specific section)
```json
{
  "file": "SKILL.md",
  "change_type": "insert_after",
  "anchor": "## Tools",
  "new_text": "\n### validate_input(input_data)\nValidates input against schema before processing.\n```python\ndef validate_input(data):\n    schema = {...}\n    validate(instance=data, schema=schema)\n```\n"
}
```

### SKILL.md Replace (exact match)
```json
{
  "file": "SKILL.md",
  "change_type": "replace",
  "old_text": "Use the browser tool to navigate.",
  "new_text": "Use `browser_navigate(url)` to navigate. Wait for `networkidle` by default."
}
```

### New Script File
```json
{
  "file": "scripts/validate.py",
  "change_type": "create",
  "new_text": "full file content here",
  "pattern": "missing_validation"
}
```

### evals/cases.yaml Append
```json
{
  "file": "evals/cases.yaml",
  "change_type": "append",
  "new_text": "\n- name: \"edge_unicode\"\n  input: \"测试 🎉\"\n  expect:\n    status: \"PASS\"\n",
  "pattern": "edge_case"
}
```

---

## Verification Checklist

After applying patches:
- [ ] All existing tests still pass
- [ ] New pass rate > old pass rate
- [ ] No new test failures
- [ ] Patch log entry created
- [ ] If structural change: human approval recorded

## Rollback Procedure

```bash
# 1. Revert patches
git checkout HEAD -- <skill_dir>

# 2. Verify evals pass at baseline
python evals/run_eval.py <skill_dir>

# 3. Log rollback
echo '{"timestamp": "...", "skill": "...", "action": "rollback", "reason": "..."}' >> .improvement-log.json
```
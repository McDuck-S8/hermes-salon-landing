# Test Harness Templates

## SPEC.md.template

```markdown
# SPEC: {{TITLE}}

## Goal
{{ONE_SENTENCE_GOAL}}

## Context
{{WHY_NEEDED_ROOT_CAUSE}}

## Acceptance Criteria
- [ ] {{CRITERION_1}}
- [ ] {{CRITERION_2}}
- [ ] {{CRITERION_3}}

## Scope
**In scope:**
- {{FILE_1}}
- {{FILE_2}}

**Out of scope:**
- {{OUT_OF_SCOPE_1}}

## Risks
- Risk 1: {{MITIGATION_1}}
- Risk 2: {{MITIGATION_2}}

## Rollback Plan
1. {{STEP_1}}
2. {{STEP_2}}
```

---

## TESTS.md.template

```markdown
# TESTS: {{TITLE_MATCHING_SPEC}}

## Test Suite
tests:
  - name: "{{TEST_NAME_1}"
    type: {{code_pattern|py_compile|pytest|integration|behavioral|performance}}
    file: "{{PATH_TO_FILE}}"
    pattern: "{{REGEX_OR_STRING}}"  # for code_pattern
    script: "{{PATH_TO_TEST_SCRIPT}}"  # for integration
    threshold: "{{MEASURABLE_THRESHOLD}}"  # e.g. ">99%", "<500ms"
    condition: "{{NATURAL_LANGUAGE_CONDITION}}"  # for behavioral
    timeout: {{SECONDS}}
    depends_on: ["{{OTHER_TEST_NAME}}"]  # optional

  - name: "{{TEST_NAME_2}"
    type: py_compile
    file: "{{PATH_TO_FILE}}"
    timeout: 10
```

---

## VALIDATION.md.template

```markdown
# Validation Checklist: {{TITLE}}

## Universal Gates
- [ ] SPEC exists
- [ ] TESTS defined
- [ ] Syntax valid (py_compile)
- [ ] No hardcoded secrets
- [ ] KC entry ready

## Code Quality
- [ ] Type hints
- [ ] Docstrings
- [ ] Error handling
- [ ] Logging
- [ ] Config via env

## Test Gates
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Edge cases covered
- [ ] Performance threshold met

## Integration
- [ ] DB connectivity
- [ ] Health endpoints
- [ ] Event emission
- [ ] Skill registration

## Documentation
- [ ] Revisit line updated
- [ ] DECISION_LOG.md entry
- [ ] Skill updated (if pattern)
- [ ] expiry.md synced

## DELIVER Gate
All above pass → DELIVER
```
# Audit Report Template

Use this template for system audit reports.

```markdown
# System Audit Report

**Date:** YYYY-MM-DD
**Scope:** <what was audited>
**Auditor:** <who>

---

## Summary Table

| Module | Exists | Works | Matches Spec | Issues |
|--------|--------|-------|-------------|--------|
| name.py | ✅ | ✅ | ✅ | None |
| name.py | ✅ | ✅ | ⚠️ Partial | Minor drift |
| name.py | ❌ | — | ❌ | File missing |

---

## Detailed Findings

### 1. Module Name (`path/to/file.py`)
- **Exists:** ✅ N lines
- **Spec claims:** <what docs say>
- **Actual:** <what code does>
- **Verdict:** ✅/⚠️/❌ + explanation

---

## Critical Issues

### 1. Issue Title (SEVERITY)
**Description:** ...
**Recommendation:** ...

---

## Methodology Notes

- Terminal commands: <were they blocked? what workaround was used?>
- Verification depth: syntax-only / import-tested / runtime-tested
```

## Severity Levels

- **HIGH** — Broken functionality, data loss risk, security issue
- **MEDIUM** — Inconsistency that could mislead developers, path issues
- **LOW** — Stale numbers, minor doc drift, cosmetic mismatches

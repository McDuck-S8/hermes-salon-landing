---
name: migrate-radix-to-base
description: Radix UI → Base UI migration for shadcn projects. Golden pair via CLI, three-way merge for customized wrappers, transformation engine for hand-rolled code.
category: automation
tags: [shadcn, migration, radix, base-ui, react, typescript]
---

# migrate-radix-to-base — Radix UI → Base UI Migration

> **Entry point for the migration skill.** Load this when asked to migrate a shadcn project from Radix to Base UI.

---

## What This Skill Does

Migrates a shadcn/ui project from Radix UI primitives to Base UI primitives (`@base-ui/react`). Handles three scenarios:

1. **Pristine wrappers** (match shadcn registry) → Golden Pair via CLI
2. **Customized wrappers** (user modified) → Three-way merge
3. **Hand-rolled Radix code** (non-shadcn) → Transformation engine

---

## Prerequisites

- Load `shadscan/shadcn` skill first (for general shadcn rules)
- Project must have `components.json` (shadcn config)
- Clean git tree, work on branch, one commit per component

---

## Migration Workflow

### Phase 1: Scan & Classify
```bash
# 1. Get project context
npx shadcn@latest info --json

# 2. Scan for Radix imports in ui/ directory
grep -r "radix-ui\|@radix-ui" components/ui/

# 3. Classify each wrapper
# - Pristine: diff against stock registry == 0
# - Customized: diff > 0 but structure matches
# - Hand-rolled: no registry match
```

### Phase 2: Strategy Per Component

| Classification | Strategy |
|----------------|----------|
| Pristine | Golden Pair via CLI (`npx shadcn@latest add <comp> --overwrite`) |
| Customized | Three-way merge: `git merge-file user.tsx radix-golden.tsx base-golden.tsx` |
| Hand-rolled | Transform engine: rewire primitives, keep classes, apply class-mapping |

### Phase 3: Execute

#### Golden Pair (Pristine)
```bash
# Progressive (default) - one component at a time
npx shadcn@latest add accordion --overwrite
# Writes to accordion-base.tsx, original untouched
# Typecheck, repoint consumers, when done: delete original, rename, flip imports

# Whole-project mode (explicit only)
# Flip components.json style: radix-lyra → base-lyra
# Process in dependency order (button, label first)
```

#### Three-Way Merge (Customized)
```bash
# 1. Get radix golden (stock shadcn component for their style)
curl https://ui.shadcn.com/r/styles/radix-lyra/accordion.json

# 2. Get base golden (base variant)
curl https://ui.shadcn.com/r/styles/base-lyra/accordion.json

# 3. Three-way merge
git merge-file user.tsx radix-golden.tsx base-golden.tsx

# 4. Hand-resolve conflicts using reference tables
# 5. Mandatory leftover sweep
grep -n "radix-ui\|@radix-ui\|IconPlaceholder" on all component files
```

#### Transform Engine (Hand-Rolled)
```bash
# Use universal-patterns.md for import rewiring
# Both forms: `radix-ui` and `@radix-ui/react-*`
# Apply class-mapping.md for CSS vars/renames
# Keep user's exact classes, apply class-mapping renames
```

### Phase 4: Verify & Report
```bash
# Per component
typecheck per file
build per batch

# Consumers
repoint imports ONE AT A TIME (imports + call-site props in consumer-props.md)
typecheck each

# Final
full build vs baseline
leftover scan: grep -n "radix-ui\|@radix-ui\|IconPlaceholder"
report: .migration/<component>.md
```

---

## Reference Files (Use These)

| File | Purpose |
|------|---------|
| `references/base-vs-radix.md` | asChild→render, part renames, prop renames, three-way merge |
| `references/consumer-props.md` | Call-site changes for wrapper consumers |
| `references/class-mapping.md` | data-radix→data-base, slot renames, CSS variable prefixes |
| `references/migrate-radix-to-base.md` | Full migration guide (this file expanded) |

---

## Hard Rules (From shadscan/shadcn)

1. **NEVER touch non-radix**: cmdk, vaul, sonner, input-otp, react-day-picker, recharts
2. **No Base UI counterpart** → FLAG, don't fix (AspectRatio→CSS, Label→native, etc.)
3. **Button** → REAL `@base-ui/react/button` primitive, never hand-rolled wrapper
4. **Behavior deltas** = FLAGGED, never silently patched
5. **Honest reporting** — skipped/reverted = flagged, never "migrated"

---

## Modes

### Progressive (Default)
One component at a time, strangler-fig pattern. Files ARE the state.

### Whole Project (Explicit Only)
Dependency order (leaf/shared wrappers first). After all: sweep ALL app code against `consumer-props.md`.

### Legacy Styles (new-york, default)
- No `base-<style>` counterpart
- Classification only, detect customizations via radix golden
- Transform on user's OWN file using universal-patterns.md
- FLAG: style name still reads as radix to CLI

---

## Reports

Location: `.migration/` at project root

### Per Component: `.migration/<component>.md`
```md
# <component>
<date, strategy, verdict>

## Changed
<every file touched, what/why; file:line>

## Leftover Scan
grep -n "radix-ui\|@radix-ui" on this component's files

## Left Alone
<intentionally untouched files with reason>

## Behavior Changes
<differences that compile but act differently; flagged>
```

### Whole Project: `.migration/project.md`
Dependency swap, app-code sweep summary, final build result.

**NO index file** — status derived from disk scan.

---

## Verification Checklist

- [ ] `npx shadscan migrate` passes (or equivalent audit)
- [ ] Typecheck per file, build per batch, full build vs baseline
- [ ] Leftover scan clean
- [ ] Consumer sweep against `consumer-props.md`
- [ ] Reports match exact structure
- [ ] End with derived count: "N wrappers remain on Radix"

---

## Integration with shadscan/shadcn

```bash
# Load both skills
skill_view(name='shadscan/shadcn')
skill_view(name='shadscan/migrate-radix-to-base')

# Or via shadscan CLI
npx shadscan migrate
```

---

*Source: TheOrcDev/shadscan v0.7.0+*
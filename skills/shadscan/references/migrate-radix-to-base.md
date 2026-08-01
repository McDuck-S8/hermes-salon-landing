# Radix UI → Base UI Migration — Skill Reference

## Overview
This skill handles migration of shadcn/ui wrappers, hand-rolled Radix compositions, and their consumers from Radix UI to Base UI (`@base-ui/react`).

## Golden Pair via CLI (Preferred)
If project is shadcn with known style (`radix-<style>`):
```bash
npx shadcn@latest add <component> --overwrite
```
- Delivers Base variant with project's exact icon/font/preset resolution
- **Never** bulk `--all --overwrite` — go component by component
- Consumer code: repoint imports ONE AT A TIME, typecheck each

## Two Modes

### Progressive (Default)
"Migrate accordion" = one component, strangler-fig:
1. Detect in-progress state: existing `<component>-base.tsx`
2. If component imports other Radix wrappers → STOP, recommend migrating deps first (bottom-up)
3. Write migrated version to `<component>-base.tsx` (original untouched)
4. Typecheck, repoint consumers ONE AT A TIME, typecheck each
5. When no consumer imports original: delete it, rename `-base` → original, flip imports
6. When LAST radix wrapper finalized: flip `components.json` style `radix-<style>` → `base-<style>`, remove radix deps

### Whole Project (Only When Explicitly Asked)
Same per-component work in dependency order (leaf/shared wrappers like button, label first). After all wrappers:
- Sweep ALL app code against `consumer-props.md` (call-site break surface > asChild)
- Remove radix deps, install, full build

## Preflight (Always)
```bash
# 1. Project config
npx shadcn@latest info --json

# 2. Package manager (lockfile) - use IT for every install
# 3. Clean git tree; work on branch; one commit per component
# 4. BASELINE check BEFORE touching deps:
#    run project's typecheck/build so pre-existing failures are never attributed to you
# 5. Install @base-ui/react alongside radix; radix removed ONLY after last component
```

## Hard Rules

### Never Touch Non-Radix
```tsx
// These are NOT Radix - never touch:
cmdk (Command), vaul (Drawer), sonner, input-otp, 
react-day-picker (Calendar), recharts (Chart)
// Report as intentionally untouched
```

### No Base UI Counterpart → CSS/Hand-Migrate
| Radix | Migration |
|-------|-----------|
| AspectRatio | CSS `aspect-ratio` div |
| Label | Native `<label>` |
| VisuallyHidden | `sr-only` |
| Direction | Direction Provider (`direction` prop, not `dir`) |
| Popover Anchor / NavMenu Indicator | Inert passthrough + flag |

### Button → Real Base UI Primitive
```tsx
// ✅ Real @base-ui/react/button primitive
import { Button } from "@base-ui/react/button"

// ❌ Never hand-rolled useRender wrapper
```

### Behavior Deltas = FLAGGED, Never Patched
- Tabs manual activation
- Menu items not closing on click  
- Nav-menu 50ms delay
- Target = idiomatic Base UI matching shadcn base registry

### Honest Reporting
- Skipped/reverted files = flagged, never "migrated"
- Pre-existing failures = named as pre-existing

## Reference Files (Use These)
| File | Purpose |
|------|---------|
| `base-vs-radix.md` | Field-by-field comparison |
| `class-mapping.md` | CSS variable/rename mappings |
| `consumer-props.md` | Call-site prop changes (asChild→render, etc.) |
| `overlays.md` | Portal>Positioner>Popup; positioner FORWARD rule |
| `menus.md` | Menu family props |
| `form-controls.md` | Form family props |
| `disclosure.md` | Disclosure family |
| `display-misc.md` | Misc display components |
| `universal-patterns.md` | Imports in BOTH forms (`radix-ui` + `@radix-ui/react-*`) |
| `wrapper-shapes.md` | Exact target shapes (tooltip arrow, SubContent defaults) |

## Transformation Engine (Fallback)
When no CLI golden pair:
1. Classify wrapper: diff user's file against stock Radix for their style
2. Three-way merge: `git merge-file user.tsx radix-golden.tsx base-golden.tsx`
3. Hand-resolve conflicts with reference tables
4. **Mandatory leftover sweep** on EVERY golden-pair file:
   ```bash
   grep -n "radix-ui\|@radix-ui\|IconPlaceholder"
   ```
   - Registry reorders functions between variants → clean merge ≠ clean file

## Modes

### Legacy Styles (new-york, new-york-v4, default)
- No `base-<style>` counterpart exists
- Classification only, no replay
- Retargeting would restyle user's app → FLAG (don't fix)
- Use radix golden ONLY to detect customizations
- Transform on user's OWN file: rewire primitives, keep their classes, apply class-mapping
- At end: FLAG style name still reads as radix to CLI

## Reports
- Location: `.migration/` at project root
- Per component: `.migration/<component>.md`
- Structure:
  ```md
  # <component>
  <date, strategy, verdict>
  
  ## Changed
  <every file touched, what/why; file:line for notable>
  
  ## Leftover Scan
  grep -n "radix-ui\|@radix-ui" on this component's files
  
  ## Left Alone
  <intentionally untouched files with reason>
  
  ## Behavior Changes
  <differences that compile but act differently; flagged>
  ```
- Whole-project: `.migration/project.md` (dependency swap, app-code sweep, final build)
- **NO index file** — status derived from disk scan

## Verify
- Typecheck per file, build per batch, full build at end vs baseline
- End every run with derived count: "N wrappers remain on Radix"
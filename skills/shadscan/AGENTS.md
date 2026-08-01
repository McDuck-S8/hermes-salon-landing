# AGENTS.md — shadscan

## Purpose
Deterministic UI audits for shadcn apps — terminal, CI, and agent-integrable. Provides deterministic checks for shadcn/ui component usage, Radix UI → Base UI migration, TypeScript strictness, and accessibility compliance. Designed for CI/CD integration and agent-driven code quality gates.

## Ownership
Owner: Hermes Agent (shadcn/ui ecosystem)
Category: web-development / ui-ux
Location: D:\Portable_Soft\hermes\skills\shadscan\
Status: Active development tool

## Local Contracts
### Triggers (from SKILL.md and skill structure)
- CI/CD pipeline integration for shadcn/ui projects
- Agent-driven code quality gates (shadscan skill)
- Radix UI → Base UI migration audits
- TypeScript strict mode compliance checks
- Accessibility (a11y) auditing
- Component usage validation

### Required Tools
- Node.js / npm / pnpm / bun (for running shadscan CLI)
- TypeScript compiler (tsc) for type checking
- ESLint with shadcn/ui rules
- Git (for diff-based auditing)

### Config References
- shadscan.config.ts / .shadscanrc — main configuration
- package.json — shadcn/ui and Radix UI dependencies
- tsconfig.json — TypeScript strictness settings
- components.json — shadcn/ui component registry
- .github/workflows/ — CI integration configs for CI integration

## Work Guidance
### When to Use
- Pre-commit / pre-push hooks for shadcn/ui projects
- CI/CD pipelines for UI quality gates
- Radix UI → Base UI migration projects
- Accessibility compliance verification
- Agent-driven code reviews (via shadscan skill)
- Refactoring shadcn/ui component usage

### Common Patterns (from skill structure)
1. **Radix UI → Base UI Migration**: Use `migrate-radix-to-base` skill references in `.agents/skills/migrate-radix-to-base/`
2. **Component Addition**: Use `shadcn` skill for adding new shadcn/ui components
3. **Deterministic Audits**: Run `npx shadscan` in terminal or CI for pass/fail results
4. **TypeScript Strictness**: Enforce strict mode, no implicit any, strict null checks
5. **Accessibility**: Check ARIA attributes, focus management, color contrast

### References Directory (from skill scan)
Contains 23 reference files covering:
- Migration guides: migrate-radix-to-base.md
- Component patterns: overlays.md, menus.md, forms.md, styling.md
- Registry: registry.md, icons.md, wrapper-shapes.md
- Universal patterns: universal-patterns.md

### .agents/skills Subdirectory
Contains specialized sub-skills:
- migrate-radix-to-base — Radix UI → Base UI migration
- shadcn — shadcn/ui development skill (components, styling)

## Verification
### Test Strategy
- Check for test scripts in skill directory: `ls scripts/ tests/ evals/` → none in skill root
- Verify via:
  1. Running `npx shadscan --help` — CLI availability
  2. Running `npx shadscan audit` on a shadcn project — produces deterministic pass/fail
  3. Running in CI pipeline — exit codes for gate decisions
  4. Running migration skill: `migrate-radix-to-base` on Radix-based project

### Validation Commands
```bash
# Check shadscan CLI availability
npx shadscan --help

# Run audit on shadcn project
cd /path/to/shadcn-project
npx shadscan audit

# Run with strict mode
npx shadscan audit --strict

# Check Radix → Base migration
npx shadscan migrate --dry-run

# CI integration test (should exit 0 on pass, non-zero on fail)
npx shadscan audit --ci
```

## Child DOX Index
### References (in shadscan/references/)
| File | Purpose |
|------|---------|
| `migrate-radix-to-base.md` | Radix UI → Base UI migration guide |
| `overlays.md` | Overlay component patterns |
| `menus.md` | Menu component patterns |
| `forms.md` | Form handling patterns |
| `styling.md` | Styling conventions |
| `registry.md` | Component registry |
| `icons.md` | Icon usage patterns |
| `wrapper-shapes.md` | Wrapper component shapes |
| `universal-patterns.md` | Universal component patterns |
| `overlays.md` | Overlay primitives |
| `menus.md` | Menu components |
| `forms.md` | Form components |
| `styling.md` | Styling guidelines |
| `registry.md` | Registry management |
| `icons.md` | Icon system |
| `wrapper-shapes.md` | Wrapper patterns |
| `universal-patterns.md` | Cross-cutting patterns |
| And 7 more reference files... |

### Templates
- (none in skill directory)

### Scripts
- (none in skill directory — CLI is via npx shadscan)

### Sub-skills (.agents/skills/)
| Skill | Purpose |
|-------|---------|
| `migrate-radix-to-base` | Radix UI → Base UI migration |
| `shadcn` | shadcn/ui component development |

### Related Skills
- ui-ux-pro-max (comprehensive design system)
- design-system (token architecture, components)
- anti-slop-design (anti-AI-slop design principles)
- hallmark (anti-AI-slop design skill)
- shadcn (shadcn/ui development skill)
- web-development (general web dev)
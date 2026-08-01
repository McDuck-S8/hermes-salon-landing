# Class-Level Skill Pattern (2026-07-28)

When creating new capabilities, build as **class-level skills** with rich `SKILL.md` + `references/` directory.

## Structure
```
skills/<skill-name>/
├── SKILLS.md              # Entry point, usage modes, rules loading, evals, directory structure
├── skills-lock.json       # Version lock
├── evals/evals.json       # Test cases per category
├── agents/skills/         # Sub-skills for specialized agents
├── scripts/               # Runnable verification/probes
├── templates/             # Boilerplate scaffolding
└── references/            # 20+ markdown files for rules, patterns, mappings
    ├── topic1.md
    ├── topic2.md
    └── ...
```

## SKILL.md Must Include
- **Usage modes** (CLI, Agent, MCP, etc.)
- **Rules loading** (how agent loads references/* as enforced rules)
- **Evals** (categories + path to evals.json)
- **Directory structure** (visual tree)
- **When to use which mode** (decision table)

## References Directory
Each `references/<topic>.md` = focused rule bank for one domain:
- `styling.md` — semantic tokens, spacing, sizing
- `forms.md` — FieldGroup+Field, validation, InputGroup
- `composition.md` — Item-in-Group, full primitives, asChild/render
- `base-vs-radix.md` — asChild→render, part renames, three-way merge
- `consumer-props.md` — call-site changes for wrapper consumers
- `class-mapping.md` — data-radix→data-base, slots, CSS vars
- `universal-patterns.md` — import rewires, Portal/Positioner/Popup
- `wrapper-shapes.md` — exact target shapes (Popup wrapper)
- `overlays.md` — Dialog, Popover, Tooltip, Select, DropdownMenu
- `menus.md` — DropdownMenu, ContextMenu, Menubar, NavigationMenu
- `form-controls.md` — Checkbox, Switch, RadioGroup, Label, Slider, Tabs, Accordion
- `disclosure.md` — Accordion, Collapsible
- `display-misc.md` — Separator, ScrollArea, Toast, Avatar
- `migrate-radix-to-base.md` — full migration workflow
- `registry.md` — registry URLs, CLI commands, preset codes

## Evals
`evals/evals.json` — array of test cases per category:
```json
[
  {"name": "styling-semantic-tokens", "category": "styling", "code": "...", "expected_violation": "...", "fix": "..."},
  {"name": "migration-aschild-to-render", "category": "migration", "code": "...", "expected_violation": "...", "fix": "..."}
]
```

## Sub-Skills (agents/skills/)
```
agents/skills/
├── shadcn/SKILL.md              # General shadcn/ui development
└── migrate-radix-to-base/SKILL.md # Radix → Base UI migration
```

## Version Lock
`skills-lock.json` — simple version map:
```json
{"shadcn": "1.0.0", "migrate-radix-to-base": "1.0.0"}
```

## Anti-Pattern to Avoid
❌ Creating 50+ narrow one-session skills that fragment the library.
✅ One class-level skill per domain, with references + evals + sub-skills.

## Example: shadscan/
This pattern produced `shadscan/` with 26 files covering:
- **CLI mode**: `npx shadscan` / `npx shadscan migrate`
- **Agent Skills**: `shadscan/shadcn` + `shadscan/migrate-radix-to-base`
- **21 reference files** covering all shadcn/ui rules + Radix→Base migration
- **Evals** for styling, forms, composition, icons, chat, cli, migration
- **Sub-skills** for shadcn dev + Radix→Base migration
---
name: shadcn
description: shadcn/ui development skill — adding components, styling, forms, composition, icons, chat, CLI. Rules enforced via references/*.md
category: software-development
---

# shadcn — shadcn/ui Development Skill

Manages shadcn/ui components and projects — adding, searching, fixing, debugging, styling, composing UI.

## When to Use

- Adding shadcn components to a project
- Fixing styling violations (semantic tokens, spacing, sizing)
- Debugging form validation patterns
- Composing complex UI from primitives
- Chat/messaging interfaces
- CLI operations (presets, component docs)

## Rules (Enforced)

All rules defined in `references/*.md`:

| Rule File | Domain |
|-----------|--------|
| `styling.md` | Semantic tokens, spacing, sizing, truncate, overlay stacking |
| `forms.md` | FieldGroup+Field, validation, InputGroup, ToggleGroup |
| `composition.md` | Item-in-Group, full Card/Dialog/Select, asChild/render, use components |
| `icons.md` | data-icon, no sizing, pass as objects |
| `chat.md` | MessageScroller+Bubble, streaming, attachments |
| `cli.md` | Preset decode/url/open/apply, preset resolve |

## Allowed Tools

```bash
npx shadcn@latest *
pnpm dlx shadcn@latest *
bunx --bun shadcn@latest *
```

## Principles

1. **Use existing components first** — search registry before custom
2. **Compose, don't reinvent** — Settings = Tabs + Card + Form
3. **Built-in variants first** — variant="outline", size="sm"
4. **Semantic colors** — bg-primary, text-muted-foreground (never raw)

## Critical Rules (Always Enforced)

- `space-y-*` → `flex flex-col gap-*`
- `w-* h-*` (equal) → `size-*`
- Raw colors → semantic tokens
- Form: FieldGroup + Field (not div + Label)
- Validation: `data-invalid` on Field, `aria-invalid` on control
- Icons: `data-icon="inline-start|inline-end"`, no sizing classes
- SelectItem in SelectGroup
- Dialog/Sheet/Drawer always have Title
- TabsTrigger in TabsList
- Chat: MessageScroller + Bubble (not raw divs)
- Preset codes: CLI only (`preset decode/url/open/apply/resolve`)

## Verification

Run evals: `npx shadscan eval` or agent must pass `evals/evals.json` cases.
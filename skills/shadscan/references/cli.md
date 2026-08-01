# CLI — Critical Rules

## Preset Codes
```bash
# ✅ Correct - never decode manually
npx shadcn@latest preset decode <code>
npx shadcn@latest preset url <code>
npx shadcn@latest preset open <code>

# For project-aware detection
npx shadcn@latest preset resolve

# ❌ Wrong - manual decoding
# Don't build preset URLs or decode codes yourself
```

## Applying Presets
```bash
# ✅ Existing project
npx shadcn@latest apply <code>

# ✅ New project
npx shadcn@latest init --preset <code>
```

## Always Use Project's Package Runner
```bash
# The skill reads packageManager from components.json
# Trust it over inference

# Examples:
npx shadcn@latest add button
pnpm dlx shadcn@latest add button
bunx --bun shadcn@latest add button
```

## Project Info
```bash
# Always run first to get context
npx shadcn@latest info --json

# Returns: base, style, tailwind version, aliases, installed components, packageManager
```

## Component Docs
```bash
# Get documentation and examples
npx shadcn@latest docs <component>
```
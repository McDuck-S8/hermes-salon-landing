# Registry — shadcn Component Registry Patterns

## Registry Entry Structure

```json
{
  "name": "accordion",
  "type": "registry:component",
  "files": [
    {
      "path": "components/ui/accordion.tsx",
      "content": "...",
      "type": "registry:component"
    }
  ],
  "dependencies": ["@base-ui/react/accordion"],
  "devDependencies": [],
  "registryDependencies": []
}
```

## Registry URLs

### Style-Specific Components
```
https://ui.shadcn.com/r/styles/{style}/{component}.json
```

| Style Prefix | Example |
|--------------|---------|
| `radix-<style>` | `radix-lyra`, `radix-new-york` |
| `base-<style>` | `base-lyra`, `base-new-york` |
| Legacy (no prefix) | `new-york`, `new-york-v4`, `default` |

### Examples
```bash
# Radix Lyra Accordion
curl https://ui.shadcn.com/r/styles/radix-lyra/accordion.json

# Base Lyra Accordion
curl https://ui.shadcn.com/r/styles/base-lyra/accordion.json

# Legacy New York
curl https://ui.shadcn.com/r/styles/new-york/accordion.json
```

## Preset Codes

### Decode Preset
```bash
npx shadcn@latest preset decode <code>
```

### Apply Preset
```bash
# Existing project
npx shadcn@latest apply <code>

# New project
npx shadcn@latest init --preset <code>
```

### Preset URL
```bash
npx shadcn@latest preset url <code>
```

### Resolve Preset (Project-Aware)
```bash
npx shadcn@latest preset resolve
```

## Registry Dependencies

```json
{
  "name": "data-table",
  "type": "registry:component",
  "dependencies": [
    "@tanstack/react-table",
    "lucide-react"
  ],
  "registryDependencies": [
    "table",
    "button",
    "dropdown-menu",
    "checkbox"
  ]
}
```

## Component Categories

| Category | Components |
|----------|------------|
| Forms | input, textarea, select, checkbox, switch, radio-group, label, slider, otp |
| Overlays | dialog, alert-dialog, sheet, drawer, popover, tooltip, hover-card |
| Navigation | dropdown-menu, context-menu, navigation-menu, menubar, tabs, breadcrumb, pagination |
| Data Display | table, card, badge, avatar, skeleton, separator, scroll-area |
| Feedback | toast, progress, alert |
| Layout | sidebar, resizable, collapsible, accordion |
| Other | button, switch, toggle, tooltip, hover-card, aspect-ratio, calendar, carousel, chart |

## Versioning

Registry entries include:
- `version`: component version
- `dependencies`: npm dependencies
- `registryDependencies`: other registry components required
- `files`: array of file entries with path, content, type

## Accessing Registry Programmatically

```bash
# List all components
npx shadcn@latest list

# Add component
npx shadcn@latest add button

# Add with specific style
npx shadcn@latest add button --style new-york
```
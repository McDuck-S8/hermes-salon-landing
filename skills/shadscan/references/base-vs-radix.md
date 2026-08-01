# Base UI vs Radix UI — Field Mapping Reference

## Purpose
Exact field-by-field comparison for migration. When a prop exists in both but differs, this is the authoritative mapping.

---

## Core Overlay Components

### Dialog / AlertDialog / Sheet / Drawer
| Radix Prop | Base UI Prop | Notes |
|------------|--------------|-------|
| `open` | `open` | Same |
| `onOpenChange` | `onOpenChange` | Same |
| `defaultOpen` | `defaultOpen` | Same |
| `modal` | `modal` | Same (Dialog only) |
| — | `closeOnEscape` | Base UI: explicit |
| — | `closeOnOverlayClick` | Base UI: explicit |

### Popover / Tooltip
| Radix Prop | Base UI Prop | Notes |
|------------|--------------|-------|
| `open` | `open` | Same |
| `onOpenChange` | `onOpenChange` | Same |
| `defaultOpen` | `defaultOpen` | Same |
| `side` | `side` | Same |
| `align` | `align` | Same |
| `sideOffset` | `sideOffset` | Same |
| `alignOffset` | `alignOffset` | Same |
| `avoidCollisions` | `avoidCollisions` | Same |
| `collisionPadding` | `collisionPadding` | Same |
| `hideWhenDetached` | `hideWhenDetached` | Same |
| `delayDuration` | `delayDuration` | Same (Tooltip) |
| `skipDelayDuration` | `skipDelayDuration` | Same (Tooltip) |

### DropdownMenu / ContextMenu / Select / Combobox
| Radix Prop | Base UI Prop | Notes |
|------------|--------------|-------|
| `open` | `open` | Same |
| `onOpenChange` | `onOpenChange` | Same |
| `defaultOpen` | `defaultOpen` | Same |
| `dir` | `direction` | **Renamed** — `dir` → `direction` |
| `modal` | `modal` | Same (DropdownMenu/ContextMenu) |

---

## Form Components

### Checkbox / Switch / RadioGroup / Tabs
| Radix Prop | Base UI Prop | Notes |
|------------|--------------|-------|
| `checked` | `checked` | Same |
| `onCheckedChange` | `onCheckedChange` | Same |
| `defaultChecked` | `defaultChecked` | Same |
| `disabled` | `disabled` | Same |
| `required` | `required` | Same |
| `value` | `value` | Same (RadioGroup/Select) |
| `onValueChange` | `onValueChange` | Same (RadioGroup/Select) |
| `defaultValue` | `defaultValue` | Same |
| `orientation` | `orientation` | Same (Tabs/RadioGroup) |
| `activationMode` | `activationMode` | Same (Tabs) |

### Label / Input / Textarea / SelectTrigger
| Radix Prop | Base UI Prop | Notes |
|------------|--------------|-------|
| — | `htmlFor` | Base UI: explicit on Label |
| `asChild` | `render` | **Different pattern** — see below |

---

## asChild / Render Pattern (Critical)

### Radix: `asChild`
```tsx
<Select.Trigger asChild>
  <CustomButton />
</Select.Trigger>
```

### Base UI: `render` prop
```tsx
<Select.Trigger render={({ ref, ...props }) => (
  <CustomButton ref={ref} {...props} />
)} />
```

### Mapping Table
| Radix Pattern | Base UI Pattern |
|---------------|-----------------|
| `<Component asChild>` | `<Component render={({ref, ...props}) => <Custom {...props} ref={ref} />}>` |
| `Slot` component | Not needed — use `render` directly |
| `RadixSlot` | `Render` function |

### Consumer Props (consumer-props.md)
| Radix | Base UI | Action |
|-------|---------|--------|
| `asChild` on trigger | `render` on trigger | Rewrite consumer |
| `asChild` on content | `render` on content | Rewrite consumer |
| `asChild` on item | `render` on item | Rewrite consumer |
| `asChild` on viewport | `render` on viewport | Rewrite consumer |
| `asChild` on scroll-button | `render` on scroll-button | Rewrite consumer |
| `asChild` on separator | `render` on separator | Rewrite consumer |
| `asChild` on arrow | `render` on arrow | Rewrite consumer |

---

## Overlay Architecture (Critical)

### Radix: Portal → Positioner → Content
```tsx
<Portal>
  <Positioner>
    <Content />
  </Positioner>
</Portal>
```

### Base UI: Portal → Positioner → Popup
```tsx
<Portal>
  <Positioner>
    <Popup>
      {/* Content goes here */}
    </Popup>
  </Positioner>
</Portal>
```

### Positioner FORWARD Rule (Critical)
```tsx
// Radix: Positioner forwards to Content
<Positioner>
  <Content />  // receives positioner props
</Positioner>

// Base UI: Positioner MUST forward to Popup
<Positioner>
  <Popup>  // receives positioner props
    <Content />  // your content
  </Popup>
</Positioner>

// If you don't wrap in Popup, positioning breaks!
```

### Part Renames
| Radix Part | Base UI Part | Notes |
|------------|--------------|-------|
| `Content` | `Popup` (wraps your content) | Different nesting |
| `Arrow` | `Arrow` | Same |
| `Close` | `Close` | Same |
| `Title` | `Title` | Same |
| `Description` | `Description` | Same |

---

## Select / Combobox / DropdownMenu / ContextMenu — Part Mapping

| Radix | Base UI | Notes |
|-------|---------|-------|
| `Root` | `Root` | Same |
| `Trigger` | `Trigger` | Same |
| `Value` | `Value` | Same |
| `Icon` | `Icon` | Same |
| `Content` | `Popup` + `Content` inside | **Nested differently** |
| `Viewport` | `Viewport` | Same |
| `Item` | `Item` | Same |
| `ItemText` | `ItemText` | Same |
| `ItemIndicator` | `ItemIndicator` | Same |
| `Separator` | `Separator` | Same |
| `Group` | `Group` | Same |
| `Label` | `Label` | Same |
| `Arrow` | `Arrow` | Same |
| `ScrollUpButton` | `ScrollUpButton` | Same |
| `ScrollDownButton` | `ScrollDownButton` | Same |
| `Input` | `Input` | Combobox only |

---

## Menus / Form Controls / Disclosure — Specific Mappings

### Menus (DropdownMenu, ContextMenu, Menu)
| Radix | Base UI | Notes |
|-------|---------|-------|
| `SubTrigger` | `SubTrigger` | Same |
| `SubContent` | `SubPopup` + `Content` | Nested differently |
| `SubViewport` | `SubViewport` | Same |
| `CheckboxItem` | `CheckboxItem` | Same |
| `RadioItem` | `RadioItem` | Same |
| `RadioGroup` | `RadioGroup` | Same |
| `Item` | `Item` | Same |
| `ItemText` | `ItemText` | Same |
| `ItemIndicator` | `ItemIndicator` | Same |
| `Shortcut` | `Shortcut` | Same |

### Form Controls (Checkbox, Switch, RadioGroup, Label)
| Radix | Base UI | Notes |
|-------|---------|-------|
| `Root` | `Root` | Same |
| `Item` | `Item` | RadioGroup |
| `Indicator` | `Indicator` | Same |
| `Input` | `Input` | Hidden input |

### Disclosure (Accordion, Collapsible)
| Radix | Base UI | Notes |
|-------|---------|-------|
| `Item` | `Item` | Same |
| `Trigger` | `Trigger` | Same |
| `Content` | `Content` | Same |

---

## Props That Don't Exist in Base UI (Removed)
| Radix Prop | Component | Migration |
|------------|-----------|-----------|
| `forceMount` | Various | Not needed — Base UI handles |
| `unstyled` | Various | Not applicable |
| `dir` (on non-dropdown) | — | Use `direction` on DropdownMenu/ContextMenu only |

---

## Props That Are New in Base UI
| Base UI Prop | Component | Notes |
|--------------|-----------|-------|
| `direction` | DropdownMenu, ContextMenu | Replaces `dir` |
| `closeOnEscape` | Dialog, AlertDialog, Sheet, Drawer | Explicit |
| `closeOnOverlayClick` | Dialog, AlertDialog, Sheet, Drawer | Explicit |
| `render` | All `asChild` components | Replaces `asChild` |

---

## Styling / ClassName Mapping

| Radix Pattern | Base UI Pattern |
|---------------|-----------------|
| `className` on Content/Popup | `className` on Popup/Content |
| `data-state="open/closed"` | `data-state="open/closed"` (same) |
| `data-side="top/bottom/left/right"` | `data-side` (same) |
| `data-align="start/center/end"` | `data-align` (same) |
| `data-radix-*` | `data-base-*` (prefix changed) |

---

## Quick Reference: Most Common Migrations

```tsx
// 1. Dialog/Sheet/Drawer Content
// Radix
<Dialog.Content>
  <Dialog.Title />
  <Dialog.Description />
</Dialog.Content>

// Base UI
<Dialog.Popup>
  <Dialog.Content>
    <Dialog.Title />
    <Dialog.Description />
  </Dialog.Content>
</Dialog.Popup>

// 2. Popover/Tooltip
// Radix
<Popover.Content>
  <Popover.Arrow />
</Popover.Content>

// Base UI
<Popover.Popup>
  <Popover.Content>
    <Popover.Arrow />
  </Popover.Content>
</Popover.Popup>

// 3. Select/DropdownMenu Content
// Radix
<Select.Content>
  <Select.Viewport>
    <Select.Item />
  </Select.Viewport>
</Select.Content>

// Base UI
<Select.Popup>
  <Select.Content>
    <Select.Viewport>
      <Select.Item />
    </Select.Viewport>
  </Select.Content>
</Select.Popup>

// 4. asChild → render
// Radix
<Select.Trigger asChild>
  <Button />
</Select.Trigger>

// Base UI
<Select.Trigger render={({ref, ...props}) => (
  <Button ref={ref} {...props} />
)} />
```

---

## When in Doubt
Check `node_modules/@base-ui/react/**/*.d.ts` — TypeScript definitions are the source of truth.
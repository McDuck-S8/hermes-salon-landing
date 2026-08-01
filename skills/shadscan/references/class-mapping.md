# Class Mapping — Radix UI → Base UI

## Data Attributes
| Radix | Base UI | Notes |
|-------|---------|-------|
| `data-radix-*` | `data-base-*` | Prefix change |
| `data-state="open/closed"` | `data-state="open/closed"` | Same values |
| `data-side="top/bottom/left/right"` | `data-side="top/bottom/left/right"` | Same |
| `data-align="start/center/end"` | `data-align="start/center/end"` | Same |
| `data-radix-popper-content-wrapper` | `data-base-popper-content-wrapper` | |
| `data-radix-portal` | `data-base-portal` | |

## Slot / Part Renames (Overlay Architecture)

### Radix: Portal → Positioner → Content
### Base UI: Portal → Positioner → Popup → Content

| Radix Part | Base UI Part | Notes |
|------------|--------------|-------|
| `Content` (direct in Positioner) | `Popup` (wraps Content) | **Critical nesting change** |
| `Arrow` | `Arrow` | Same |
| `Close` | `Close` | Same |
| `Title` | `Title` | Same |
| `Description` | `Description` | Same |

### Select / Combobox / DropdownMenu / ContextMenu
| Radix Part | Base UI Part | Notes |
|------------|--------------|-------|
| `Content` | `Popup` + `Content` | Nested differently |
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
| `SubTrigger` | `SubTrigger` | Same |
| `SubContent` | `SubPopup` + `Content` | Nested differently |
| `SubViewport` | `SubViewport` | Same |

### Menus
| Radix Part | Base UI Part |
|------------|--------------|
| `SubTrigger` | `SubTrigger` |
| `SubContent` | `SubPopup` + `Content` |
| `SubViewport` | `SubViewport` |
| `CheckboxItem` | `CheckboxItem` |
| `RadioItem` | `RadioItem` |
| `RadioGroup` | `RadioGroup` |

## CSS Variable Prefixes

| Radix Pattern | Base UI Pattern |
|---------------|-----------------|
| `--radix-*` | `--base-*` |
| `--radix-colors-*` | `--base-colors-*` |

## asChild → render Pattern

### Radix
```tsx
<Select.Trigger asChild>
  <Button />
</Select.Trigger>
```

### Base UI
```tsx
<Select.Trigger render={({ ref, ...props }) => (
  <Button ref={ref} {...props} />
)} />
```

## Consumer Props Mapping

| Radix Prop | Base UI Prop | Action |
|-------------|--------------|--------|
| `asChild` (any component) | `render` (same component) | Rewrite consumer |
| `dir` (DropdownMenu/ContextMenu) | `direction` | Rename |
| `dir` (others) | — | Remove (not applicable) |
| `forceMount` | — | Remove (not needed) |
| `unstyled` | — | Remove |

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
<Select.Trigger render={({ ref, ...props }) => (
  <Button ref={ref} {...props} />
)} />
```
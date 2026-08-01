# Wrapper Shapes — Exact Target Shapes for Base UI Migration

This document defines the **exact target shapes** that every migrated wrapper must match. These are the idiomatic Base UI patterns that the shadcn base registry uses.

---

## Overlay Architecture (Critical)

### Radix: Portal → Positioner → Content
### Base UI: Portal → Positioner → **Popup** → Content

```tsx
// ❌ Radix (wrong for Base UI)
<Portal>
  <Positioner>
    <Content>
      <Title />
      <Description />
    </Content>
  </Positioner>
</Portal>

// ✅ Base UI (correct)
<Portal>
  <Positioner>
    <Popup>           {/* REQUIRED - wraps Content */}
      <Content>
        <Title />
        <Description />
      </Content>
    </Popup>
  </Positioner>
</Portal>
```

**If you don't wrap in Popup, positioning breaks!**

---

## Tooltip Arrow
```tsx
// Radix
<Tooltip.Content>
  <Tooltip.Arrow />
  Content
</Tooltip.Content>

// Base UI
<Tooltip.Popup>
  <Tooltip.Content>
    <Tooltip.Arrow />
    Content
  </Tooltip.Content>
</Tooltip.Popup>
```

---

## Select / Combobox / DropdownMenu / ContextMenu

```tsx
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
```

---

## Sub Menus

```tsx
// Radix
<DropdownMenu.SubContent>
  <DropdownMenu.SubViewport>
    <DropdownMenu.Item />
  </DropdownMenu.SubViewport>
</DropdownMenu.SubContent>

// Base UI
<DropdownMenu.SubPopup>
  <DropdownMenu.Content>
    <DropdownMenu.SubViewport>
      <DropdownMenu.Item />
    </DropdownMenu.SubViewport>
  </DropdownMenu.Content>
</DropdownMenu.SubPopup>
```

---

## Menu Family (DropdownMenu, ContextMenu, Menu)

| Radix Part | Base UI Part |
|------------|--------------|
| `Content` | `Popup` + `Content` |
| `SubContent` | `SubPopup` + `Content` |
| `Viewport` | `Viewport` |
| `SubViewport` | `SubViewport` |

---

## Popover / HoverCard

```tsx
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
```

---

## Dialog / AlertDialog / Sheet / Drawer

```tsx
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
```

---

## Positioner FORWARD Rule (Critical!)

### Radix
```tsx
<Positioner>
  <Content />  {/* Positioner forwards to Content */}
</Positioner>
```

### Base UI
```tsx
<Positioner>
  <Popup>           {/* REQUIRED - receives positioner props */}
    <Content />     {/* Your content */}
  </Popup>
</Positioner>
```

**The Positioner MUST forward to Popup, not directly to your Content.** If you skip Popup, positioning breaks!

---

## Portal Usage
```tsx
// Both Radix and Base UI use Portal at the top
<Portal>
  <Positioner>
    {/* Radix: Content */}{/* Base UI: Popup > Content */}
  </Positioner>
</Portal>
```

---

## Quick Validation Checklist

After migrating a wrapper, verify:

- [ ] `Portal` → `Positioner` → **`Popup`** → `Content` (not `Portal` → `Positioner` → `Content`)
- [ ] `Popup` wraps `Content` (and `Popup` receives positioner props)
- [ ] `SubPopup` wraps `SubContent` for menus
- [ ] No direct `Content` as child of `Positioner`
- [ ] All `Content` components have their corresponding `Popup` parent

---

## Search Patterns for Audit

```bash
# Find Positioner with direct Content (wrong)
grep -rn "<Positioner>" --include="*.tsx" -A 3 | grep -B 3 "Content" | grep -v "Popup"

# Find Content without Popup parent
grep -rn "<.*\.Content" --include="*.tsx" | grep -v "Popup"

# Find Popover/Tooltip/Select Content without Popup
grep -rn "Popover\.Content\|Tooltip\.Content\|Select\.Content\|DropdownMenu\.Content" --include="*.tsx" | grep -v "Popup"
```
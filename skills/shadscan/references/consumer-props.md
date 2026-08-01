# Consumer Props — Call-Site Migration Reference

When a wrapper component migrates from Radix to Base UI, call sites that consume it often need updates. This reference lists all consumer-side changes.

---

## asChild → render (All Components)

### Wrapper Author Change
```tsx
// Radix wrapper
<Select.Trigger asChild>
  {children}
</Select.Trigger>

// Base UI wrapper
<Select.Trigger render={({ ref, ...props }) => (
  <CustomTrigger ref={ref} {...props} />
)} />
```

### Consumer Change (Call Site)
```tsx
// Before (Radix)
<SelectTrigger asChild>
  <Button>Open</Button>
</SelectTrigger>

// After (Base UI) — no change needed if wrapper handles render!
<SelectTrigger>
  <Button>Open</Button>
</SelectTrigger>

// If consumer was using asChild directly on primitive:
<Select.Primitive.Trigger asChild>
  <Button />
</Select.Primitive.Trigger>

// Base UI equivalent:
<Select.Trigger render={({ ref, ...props }) => (
  <Button ref={ref} {...props} />
)} />
```

---

## DropdownMenu / ContextMenu — dir → direction

```tsx
// Radix
<DropdownMenu dir="rtl">  // or "ltr"
  <DropdownMenuTrigger>Menu</DropdownMenuTrigger>
  <DropdownMenuContent>...</DropdownMenuContent>
</DropdownMenu>

// Base UI
<DropdownMenu direction="rtl">
  <DropdownMenuTrigger>Menu</DropdownMenuTrigger>
  <DropdownMenuContent>...</DropdownMenuContent>
</DropdownMenu>

// ContextMenu same
<ContextMenu direction="rtl">...</ContextMenu>
```

---

## Overlay Components — forceMount Removed

```tsx
// Radix
<Dialog forceMount>
  <Dialog.Trigger>Open</Dialog.Trigger>
  <Dialog.Content>...</Dialog.Content>
</Dialog>

// Base UI — no forceMount, handles automatically
<Dialog>
  <Dialog.Trigger>Open</Dialog.Trigger>
  <Dialog.Content>...</Dialog.Content>
</Dialog>

// Same for: AlertDialog, Sheet, Drawer, Popover, Tooltip, HoverCard
```

---

## unstyled Removed

```tsx
// Radix
<Select unstyled>
  ...
</Select>

// Base UI — not applicable, use className/className overrides
<Select>
  ...
</Select>
```

---

## Select / Combobox — Consumer Props

### Trigger
```tsx
// Radix
<Select.Trigger asChild>
  <CustomButton />
</Select.Trigger>

// Base UI — wrapper handles render, consumer unchanged if wrapper correct
<SelectTrigger>
  <CustomButton />
</SelectTrigger>
```

### Value / onValueChange
```tsx
// Radix
<Select value={val} onValueChange={setVal}>

// Base UI — same
<Select value={val} onValueChange={setVal}>
```

---

## Tabs — activationMode

```tsx
// Radix
<Tabs activationMode="manual">  // or "automatic"

// Base UI — same
<Tabs activationMode="manual">
```

---

## Checkbox / Switch / RadioGroup — Indicator

```tsx
// Radix
<Checkbox.Indicator>
  <CheckIcon />
</Checkbox.Indicator>

// Base UI — same
<Checkbox.Indicator>
  <CheckIcon />
</Checkbox.Indicator>
```

---

## Label — htmlFor

```tsx
// Radix — implicit via Field/Label association

// Base UI — explicit htmlFor on Label
<Label htmlFor="input-id">Label</Label>
<Input id="input-id" />
```

---

## Quick Checklist for Consumer Sweep

After migrating wrappers, search for these patterns in app code:

| Pattern | File | Action |
|---------|------|--------|
| `asChild` | *.tsx | Wrapper now uses `render` — verify consumer works without `asChild` |
| `dir=` | *.tsx | DropdownMenu/ContextMenu → `direction=` |
| `forceMount` | *.tsx | Remove |
| `unstyled` | *.tsx | Remove |
| `data-radix-` | *.tsx, *.css | → `data-base-` |
| `radix-ui` import | *.tsx | → `@base-ui/react` (in migrated wrappers) |
| `Select.Trigger` | *.tsx | Verify wrapper passes through correctly |
| `Checkbox` without `Label htmlFor` | *.tsx | Add explicit `htmlFor` |

---

## Search Commands for Audit

```bash
# Find all consumer-side asChild (should be gone)
grep -rn "asChild" --include="*.tsx" src/ components/ app/

# Find dir= on menus
grep -rn 'dir=' --include="*.tsx" src/ | grep -i dropdown

# Find forceMount
grep -rn "forceMount" --include="*.tsx" src/

# Find unstyled
grep -rn "unstyled" --include="*.tsx" src/

# Find radix imports in non-wrapper code
grep -rn "from 'radix-ui" --include="*.tsx" src/ | grep -v "ui/"
grep -rn "from '@radix-ui" --include="*.tsx" src/ | grep -v "ui/"

# Find data-radix in CSS
grep -rn "data-radix-" --include="*.css" --include="*.tsx" src/
```
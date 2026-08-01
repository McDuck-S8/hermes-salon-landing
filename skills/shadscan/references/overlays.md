# Overlays — Dialog, AlertDialog, Sheet, Drawer, Popover, Tooltip, HoverCard

## Dialog / AlertDialog / Sheet / Drawer

### Structure (Radix → Base UI)

```tsx
// Radix
<Dialog>
  <Dialog.Trigger>Open</Dialog.Trigger>
  <Dialog.Content>
    <Dialog.Title>Title</Dialog.Title>
    <Dialog.Description>Description</Dialog.Description>
    Content
  </Dialog.Content>
</Dialog>

// Base UI
<Dialog>
  <Dialog.Trigger>Open</Dialog.Trigger>
  <Dialog.Popup>
    <Dialog.Content>
      <Dialog.Title>Title</Dialog.Title>
      <Dialog.Description>Description</Dialog.Description>
      Content
    </Dialog.Content>
  </Dialog.Popup>
</Dialog>
```

### Props Mapping

| Radix Prop | Base UI Prop | Notes |
|------------|--------------|-------|
| `open` | `open` | Same |
| `onOpenChange` | `onOpenChange` | Same |
| `defaultOpen` | `defaultOpen` | Same |
| `modal` | `modal` | Dialog/AlertDialog only |
| — | `closeOnEscape` | New in Base UI |
| — | `closeOnOverlayClick` | New in Base UI |
| `forceMount` | — | Removed |

### Part Imports

```tsx
// Radix
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "@/components/ui/dialog"

// Base UI
import {
  Dialog,
  DialogTrigger,
  DialogPopup,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "@/components/ui/dialog"
```

### asChild → render

```tsx
// Radix
<Dialog.Trigger asChild>
  <Button>Open</Button>
</Dialog.Trigger>

// Base UI
<Dialog.Trigger render={({ ref, ...props }) => (
  <Button ref={ref} {...props} />
)} />
```

---

## Popover / Tooltip / HoverCard

### Structure (Radix → Base UI)

```tsx
// Radix
<Popover>
  <Popover.Trigger>Open</Popover.Trigger>
  <Popover.Content>
    <Popover.Arrow />
    Content
  </Popover.Content>
</Popover>

// Base UI
<Popover>
  <Popover.Trigger>Open</Popover.Trigger>
  <Popover.Popup>
    <Popover.Content>
      <Popover.Arrow />
      Content
    </Popover.Content>
  </Popover.Popup>
</Popover>
```

### Props Mapping

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
| `delayDuration` | `delayDuration` | Tooltip only |
| `skipDelayDuration` | `skipDelayDuration` | Tooltip only |

### Part Imports

```tsx
// Radix
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverArrow,
} from "@/components/ui/popover"

// Base UI
import {
  Popover,
  PopoverTrigger,
  PopoverPopup,
  PopoverContent,
  PopoverArrow,
} from "@/components/ui/popover"
```

### Tooltip Specific
```tsx
// Radix
<Tooltip delayDuration={200} skipDelayDuration={300}>
  <Tooltip.Trigger>Hover</Tooltip.Trigger>
  <Tooltip.Content>
    <Tooltip.Arrow />
    Tooltip text
  </Tooltip.Content>
</Tooltip>

// Base UI - same props, Popup wrapper
<Tooltip delayDuration={200} skipDelayDuration={300}>
  <Tooltip.Trigger>Hover</Tooltip.Trigger>
  <Tooltip.Popup>
    <Tooltip.Content>
      <Tooltip.Arrow />
      Tooltip text
    </Tooltip.Content>
  </Tooltip.Popup>
</Tooltip>
```

---

## Select / Combobox / DropdownMenu / ContextMenu

### Structure (Radix → Base UI)

```tsx
// Radix
<Select>
  <Select.Trigger>Select</Select.Trigger>
  <Select.Content>
    <Select.Viewport>
      <Select.Item value="a">Option A</Select.Item>
    </Select.Viewport>
  </Select.Content>
</Select>

// Base UI
<Select>
  <Select.Trigger>Select</Select.Trigger>
  <Select.Popup>
    <Select.Content>
      <Select.Viewport>
        <Select.Item value="a">Option A</Select.Item>
      </Select.Viewport>
    </Select.Content>
  </Select.Popup>
</Select>
```

### Sub Menus

```tsx
// Radix
<DropdownMenu.SubContent>
  <DropdownMenu.SubViewport>
    <DropdownMenu.Item>Sub Item</DropdownMenu.Item>
  </DropdownMenu.SubViewport>
</DropdownMenu.SubContent>

// Base UI
<DropdownMenu.SubPopup>
  <DropdownMenu.Content>
    <DropdownMenu.SubViewport>
      <DropdownMenu.Item>Sub Item</DropdownMenu.Item>
    </DropdownMenu.SubViewport>
  </DropdownMenu.Content>
</DropdownMenu.SubPopup>
```

### Part Imports

```tsx
// Radix
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectViewport,
  SelectItem,
  SelectGroup,
  SelectLabel,
  SelectSeparator,
  SelectArrow,
  SelectScrollUpButton,
  SelectScrollDownButton,
} from "@/components/ui/select"

// Base UI
import {
  Select,
  SelectTrigger,
  SelectPopup,
  SelectContent,
  SelectViewport,
  SelectItem,
  SelectGroup,
  SelectLabel,
  SelectSeparator,
  SelectArrow,
  SelectScrollUpButton,
  SelectScrollDownButton,
  SelectInput,
} from "@/components/ui/select"
```

---

## Menus (DropdownMenu, ContextMenu, Menu)

### Props

| Radix Prop | Base UI Prop | Notes |
|------------|--------------|-------|
| `dir` | `direction` | **Renamed** |
| `modal` | `modal` | Same |
| `open` | `open` | Same |
| `onOpenChange` | `onOpenChange` | Same |

### Sub Menus

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

### Part Imports

```tsx
// Radix
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuViewport,
  DropdownMenuItem,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
  DropdownMenuSubViewport,
  DropdownMenuSeparator,
  DropdownMenuLabel,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioItem,
  DropdownMenuRadioGroup,
  DropdownMenuShortcut,
} from "@/components/ui/dropdown-menu"

// Base UI
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuPopup,
  DropdownMenuContent,
  DropdownMenuViewport,
  DropdownMenuItem,
  DropdownMenuSubTrigger,
  DropdownMenuSubPopup,
  DropdownMenuSubContent,
  DropdownMenuSubViewport,
  DropdownMenuSeparator,
  DropdownMenuLabel,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioItem,
  DropdownMenuRadioGroup,
  DropdownMenuShortcut,
} from "@/components/ui/dropdown-menu"
```

---

## Summary: Popup Wrapper Required For

| Component | Radix Content | Base UI Popup + Content |
|-----------|---------------|-------------------------|
| Dialog | `DialogContent` | `DialogPopup` + `DialogContent` |
| AlertDialog | `AlertDialogContent` | `AlertDialogPopup` + `AlertDialogContent` |
| Sheet | `SheetContent` | `SheetPopup` + `SheetContent` |
| Drawer | `DrawerContent` | `DrawerPopup` + `DrawerContent` |
| Popover | `PopoverContent` | `PopoverPopup` + `PopoverContent` |
| Tooltip | `TooltipContent` | `TooltipPopup` + `TooltipContent` |
| HoverCard | `HoverCardContent` | `HoverCardPopup` + `HoverCardContent` |
| Select | `SelectContent` | `SelectPopup` + `SelectContent` |
| Combobox | `ComboboxContent` | `ComboboxPopup` + `ComboboxContent` |
| DropdownMenu | `DropdownMenuContent` | `DropdownMenuPopup` + `DropdownMenuContent` |
| ContextMenu | `ContextMenuContent` | `ContextMenuPopup` + `ContextMenuContent` |
| Popover | `PopoverContent` | `PopoverPopup` + `PopoverContent` |

### Sub Menus

| Component | Radix SubContent | Base UI SubPopup + SubContent |
|-----------|------------------|-------------------------------|
| DropdownMenu | `DropdownMenuSubContent` | `DropdownMenuSubPopup` + `DropdownMenuContent` |
| ContextMenu | `ContextMenuSubContent` | `ContextMenuSubPopup` + `ContextMenuContent` |
| Menu | `MenuSubContent` | `MenuSubPopup` + `MenuContent` |
# Universal Patterns — Radix Import Rewires & Common Transformations

## Import Rewires (Both Forms)

### Form 1: `radix-ui` (no scope)
```tsx
// Radix
import { Dialog } from "radix-ui"

// Base UI
import { Dialog } from "@base-ui/react/dialog"
```

### Form 2: `@radix-ui/react-*` (scoped)
```tsx
// Radix
import { Dialog } from "@radix-ui/react-dialog"

// Base UI
import { Dialog } from "@base-ui/react/dialog"
```

### Complete Package Mapping

| Radix Package | Base UI Package |
|---------------|-----------------|
| `radix-ui` | `@base-ui/react` (re-exports) |
| `@radix-ui/react-dialog` | `@base-ui/react/dialog` |
| `@radix-ui/react-alert-dialog` | `@base-ui/react/alert-dialog` |
| `@radix-ui/react-sheet` | `@base-ui/react/sheet` |
| `@radix-ui/react-drawer` | `@base-ui/react/drawer` |
| `@radix-ui/react-popover` | `@base-ui/react/popover` |
| `@radix-ui/react-tooltip` | `@base-ui/react/tooltip` |
| `@radix-ui/react-hover-card` | `@base-ui/react/hover-card` |
| `@radix-ui/react-select` | `@base-ui/react/select` |
| `@radix-ui/react-combobox` | `@base-ui/react/combobox` |
| `@radix-ui/react-dropdown-menu` | `@base-ui/react/dropdown-menu` |
| `@radix-ui/react-context-menu` | `@base-ui/react/context-menu` |
| `@radix-ui/react-popover` | `@base-ui/react/popover` |
| `@radix-ui/react-tabs` | `@base-ui/react/tabs` |
| `@radix-ui/react-checkbox` | `@base-ui/react/checkbox` |
| `@radix-ui/react-switch` | `@base-ui/react/switch` |
| `@radix-ui/react-radio-group` | `@base-ui/react/radio-group` |
| `@radix-ui/react-label` | `@base-ui/react/label` |
| `@radix-ui/react-slider` | `@base-ui/react/slider` |
| `@radix-ui/react-avatar` | `@base-ui/react/avatar` |
| `@radix-ui/react-dropdown-menu` | `@base-ui/react/dropdown-menu` |
| `@radix-ui/react-context-menu` | `@base-ui/react/context-menu` |
| `@radix-ui/react-menubar` | `@base-ui/react/menubar` |
| `@radix-ui/react-navigation-menu` | `@base-ui/react/navigation-menu` |
| `@radix-ui/react-tabs` | `@base-ui/react/tabs` |
| `@radix-ui/react-accordion` | `@base-ui/react/accordion` |
| `@radix-ui/react-collapsible` | `@base-ui/react/collapsible` |
| `@radix-ui/react-separator` | `@base-ui/react/separator` |
| `@radix-ui/react-scroll-area` | `@base-ui/react/scroll-area` |
| `@radix-ui/react-toast` | `@base-ui/react/toast` |
| `@radix-ui/react-aspect-ratio` | CSS `aspect-ratio` (no component) |

---

## Primitive Rewire Pattern

### Step 1: Update Imports
```tsx
// Before
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@radix-ui/react-dialog"

// After
import {
  Dialog,
  DialogTrigger,
  DialogPopup,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@base-ui/react/dialog"
```

### Step 2: Update JSX (Popup Wrapper)
```tsx
// Before
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <DialogTitle>Title</DialogTitle>
    <DialogDescription>Desc</DialogDescription>
  </DialogContent>
</Dialog>

// After
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogPopup>
    <DialogContent>
      <DialogTitle>Title</DialogTitle>
      <DialogDescription>Desc</DialogDescription>
    </DialogContent>
  </DialogPopup>
</Dialog>
```

### Step 3: asChild → render
```tsx
// Before
<Dialog.Trigger asChild>
  <Button>Open</Button>
</Dialog.Trigger>

// After
<Dialog.Trigger render={({ ref, ...props }) => (
  <Button ref={ref} {...props}>Open</Button>
)} />
```

---

## Portal + Positioner + Popup Pattern (All Overlays)

### Radix (Wrong for Base UI)
```tsx
<Portal>
  <Positioner>
    <Content>
      <Arrow />
      <Title />
    </Content>
  </Positioner>
</Portal>
```

### Base UI (Correct)
```tsx
<Portal>
  <Positioner>
    <Popup>              {/* NEW - required */}
      <Content>
        <Arrow />
        <Title />
      </Content>
    </Popup>
  </Positioner>
</Portal>
```

**Applies to:** Dialog, AlertDialog, Sheet, Drawer, Popover, Tooltip, HoverCard, DropdownMenu, ContextMenu, Select, Combobox, Popover, Select, Combobox

---

## Data Attributes

```tsx
// Radix
data-state="open"
data-side="top"
data-align="center"
data-radix-popper-content-wrapper

// Base UI
data-state="open"
data-side="top"
data-align="center"
data-base-popper-content-wrapper   // prefix changed
```

---

## CSS Variables

```css
/* Radix */
--radix-colors-...
--radix-popper-transform-origin

/* Base UI */
--base-colors-...
--base-popper-transform-origin
```

---

## Search/Replace Commands

```bash
# 1. Update imports
find . -name "*.tsx" -exec sed -i 's|from "@radix-ui/react-\([a-z-]*\)"|from "@base-ui/react/\1"|g' {} +

# 2. Add Popup wrappers (manual per component)
# Dialog, AlertDialog, Sheet, Drawer, Popover, Tooltip, HoverCard, DropdownMenu, ContextMenu, Select, Combobox, Popover

# 3. asChild -> render
find . -name "*.tsx" -exec sed -i 's/asChild/render={({ ref, ...props }) => (<Component ref={ref} {...props} \/>)} /g' {} +

# 4. data-radix -> data-base
find . -name "*.tsx" -o -name "*.css" | xargs sed -i 's/data-radix-/data-base-/g'

# 5. CSS variables
find . -name "*.css" | xargs sed -i 's/--radix-/--base-/g'
```
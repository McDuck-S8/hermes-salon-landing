# Display Misc — AspectRatio, Label, VisuallyHidden, Direction, PopoverAnchor, NavigationMenuIndicator

## AspectRatio

### No Base UI Counterpart
```tsx
// Radix
import { AspectRatio } from "@radix-ui/react-aspect-ratio"

// Migration: Use CSS aspect-ratio
// Radix
<AspectRatio ratio={16 / 9}>
  <img src="..." alt="" />
</AspectRatio>

// Base UI - CSS only
<div style={{ aspectRatio: "16 / 9" }}>
  <img src="..." alt="" />
</div>

// Or Tailwind
<div className="aspect-video">
  <img src="..." alt="" />
</div>
```

---

## Label

### Radix → Base UI
```tsx
// Radix
import { Label } from "@radix-ui/react-label"

// Base UI
import { Label } from "@base-ui/react/label"
```

### htmlFor (Explicit in Base UI)
```tsx
// Radix - implicit via Field
<Field>
  <Label>Email</Label>
  <Input />
</Field>

// Base UI - explicit htmlFor
<Label htmlFor="email">Email</Label>
<Input id="email" />
```

---

## VisuallyHidden

### Radix → Base UI
```tsx
// Radix
import { VisuallyHidden } from "@radix-ui/react-visually-hidden"

// Base UI - use CSS sr-only
// Radix
<VisuallyHidden>Screen reader text</VisuallyHidden>

// Base UI
<span className="sr-only">Screen reader text</span>

// Tailwind
<span className="sr-only">Screen reader text</span>
```

---

## Direction Provider

### Radix → Base UI
```tsx
// Radix
import { DirectionProvider } from "@radix-ui/react-direction"

// Base UI
import { DirectionProvider } from "@base-ui/react/direction"
```

### Props
```tsx
// Radix
<DirectionProvider dir="rtl">
  <App />
</DirectionProvider>

// Base UI - same
<DirectionProvider direction="rtl">
  <App />
</DirectionProvider>
```

### Consumer Components
```tsx
// Radix
<Popover dir="rtl">...</Popover>
<DropdownMenu dir="rtl">...</DropdownMenu>

// Base UI
<Popover direction="rtl">...</Popover>
<DropdownMenu direction="rtl">...</DropdownMenu>
```

---

## PopoverAnchor / NavigationMenuIndicator

### No Base UI Counterpart (Flag, Don't Fix)

```tsx
// Radix
import { PopoverAnchor } from "@radix-ui/react-popover"
import { NavigationMenuIndicator } from "@radix-ui/react-navigation-menu"

// Migration: Inert passthrough + flag in report

// PopoverAnchor - inert passthrough
const PopoverAnchor = ({ children, ...props }) => (
  <span {...props}>{children}</span>
)

// NavigationMenuIndicator - inert passthrough
const NavigationMenuIndicator = ({ children, ...props }) => (
  <span {...props}>{children}</span>
)
```

### Report Entry
```markdown
## Left Alone
- `PopoverAnchor` — not a Radix primitive, inert passthrough
- `NavigationMenuIndicator` — no Base UI equivalent, inert passthrough
```
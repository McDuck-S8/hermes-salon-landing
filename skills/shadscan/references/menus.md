# Menus — DropdownMenu, ContextMenu, Menubar, NavigationMenu

## DropdownMenu / ContextMenu

### dir → direction (Critical)
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

### Overlay Structure (Popup Wrapper)
```tsx
// Radix
<DropdownMenu>
  <DropdownMenuTrigger>Menu</DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuViewport>
      <DropdownMenuItem>Item</DropdownMenuItem>
    </DropdownMenuViewport>
  </DropdownMenuContent>
</DropdownMenu>

// Base UI
<DropdownMenu>
  <DropdownMenuTrigger>Menu</DropdownMenuTrigger>
  <DropdownMenuPopup>
    <DropdownMenuContent>
      <DropdownMenuViewport>
        <DropdownMenuItem>Item</DropdownMenuItem>
      </DropdownMenuViewport>
    </DropdownMenuContent>
  </DropdownMenuPopup>
</DropdownMenu>
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

### Part Mapping
| Radix Part | Base UI Part |
|------------|--------------|
| `Content` | `Popup` + `Content` |
| `SubContent` | `SubPopup` + `Content` |
| `Viewport` | `Viewport` |
| `SubViewport` | `SubViewport` |
| `Trigger` | `Trigger` |
| `Item` | `Item` |
| `ItemText` | `ItemText` |
| `ItemIndicator` | `ItemIndicator` |
| `Separator` | `Separator` |
| `Group` | `Group` |
| `Label` | `Label` |
| `Arrow` | `Arrow` |
| `ScrollUpButton` | `ScrollUpButton` |
| `ScrollDownButton` | `ScrollDownButton` |
| `Shortcut` | `Shortcut` |
| `CheckboxItem` | `CheckboxItem` |
| `RadioItem` | `RadioItem` |
| `RadioGroup` | `RadioGroup` |

### asChild → render
```tsx
// Radix
<DropdownMenu.Trigger asChild>
  <Button>Menu</Button>
</DropdownMenu.Trigger>

// Base UI
<DropdownMenu.Trigger render={({ ref, ...props }) => (
  <Button ref={ref} {...props}>Menu</Button>
)} />
```

## Menubar / NavigationMenu

### Imports
```tsx
// Radix
import {
  Menubar,
  MenubarTrigger,
  MenubarContent,
  MenubarItem,
  MenubarSeparator,
  MenubarArrow,
  MenubarGroup,
  MenubarLabel,
  MenubarShortcut,
} from "@radix-ui/react-menubar"

import {
  NavigationMenu,
  NavigationMenuTrigger,
  NavigationMenuContent,
  NavigationMenuLink,
  NavigationMenuIndicator,
  NavigationMenuViewport,
} from "@radix-ui/react-navigation-menu"

// Base UI
import {
  Menubar,
  MenubarTrigger,
  MenubarPopup,
  MenubarContent,
  MenubarItem,
  MenubarSeparator,
  MenubarArrow,
  MenubarGroup,
  MenubarLabel,
  MenubarShortcut,
} from "@base-ui/react/menubar"

import {
  NavigationMenu,
  NavigationMenuTrigger,
  NavigationMenuContent,
  NavigationMenuLink,
  NavigationMenuIndicator,
  NavigationMenuViewport,
} from "@base-ui/react/navigation-menu"
```

### Menubar Structure (Popup Wrapper)
```tsx
// Radix
<Menubar>
  <MenubarTrigger>File</MenubarTrigger>
  <MenubarContent>
    <MenubarItem>New</MenubarItem>
    <MenubarSeparator />
    <MenubarItem>Open</MenubarItem>
  </MenubarContent>
</Menubar>

// Base UI
<Menubar>
  <MenubarTrigger>File</MenubarTrigger>
  <MenubarPopup>
    <MenubarContent>
      <MenubarItem>New</MenubarItem>
      <MenubarSeparator />
      <MenubarItem>Open</MenubarItem>
    </MenubarContent>
  </MenubarPopup>
</Menubar>
```

### NavigationMenu (No Popup Wrapper)
```tsx
// Radix & Base UI — same structure
<NavigationMenu>
  <NavigationMenuTrigger>Products</NavigationMenuTrigger>
  <NavigationMenuContent>
    <NavigationMenuLink>Product A</NavigationMenuLink>
    <NavigationMenuLink>Product B</NavigationMenuLink>
  </NavigationMenuContent>
  <NavigationMenuViewport />
</NavigationMenu>

// Note: NavigationMenu does NOT get Popup wrapper in Base UI
```

### Menubar Part Mapping
| Radix Part | Base UI Part |
|------------|--------------|
| `Content` | `Popup` + `Content` |
| `Item` | `Item` |
| `Separator` | `Separator` |
| `Arrow` | `Arrow` |
| `Group` | `Group` |
| `Label` | `Label` |
| `Shortcut` | `Shortcut` |

### NavigationMenu Part Mapping
| Radix Part | Base UI Part |
|------------|--------------|
| `Trigger` | `Trigger` |
| `Content` | `Content` (no Popup) |
| `Link` | `Link` |
| `Indicator` | `Indicator` |
| `Viewport` | `Viewport` |
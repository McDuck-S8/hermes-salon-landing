# Icons — Critical Rules

## Icons in Buttons
```tsx
// ✅ Correct - data-icon for positioning
<Button>
  <SearchIcon data-icon="inline-start" />
  Search
</Button>

<Button>
  Settings
  <ChevronDownIcon data-icon="inline-end" />
</Button>

// ❌ Wrong - sizing classes on icons
<Button>
  <SearchIcon className="w-4 h-4" />
  Search
</Button>
```

## Icon Sizing
- **Never** add `size-*`, `w-* h-*` to icons inside components
- Components handle icon sizing via CSS (e.g., `Button` sets `size-4`)
- Pass icons as objects: `icon={SearchIcon}`, not string keys

## Icons as Objects
```tsx
// ✅ Correct
<Button>
  <SearchIcon data-icon="inline-start" />
  Search
</Button>

// ❌ Wrong - string lookup
<Button icon="search">Search</Button>
```

## No Icons Where Not Needed
- Don't add decorative icons to every button
- Use icons when they convey meaning (navigation, actions, status)
- Empty states, loading states, success states = appropriate icon use
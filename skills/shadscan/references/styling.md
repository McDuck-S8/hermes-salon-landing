# Styling & Tailwind — Critical Rules

## Semantic Tokens Only
- Use `bg-primary`, `text-muted-foreground`, `border-border`, `bg-background`
- **Never** raw colors: `bg-blue-500`, `text-gray-700`, `border-red-300`
- Dark mode works automatically via semantic tokens

## Conditional Classes
```tsx
// ✅ Correct
cn("base-classes", condition && "conditional-classes")

// ❌ Wrong
className={condition ? "base conditional" : "base"}
className={`base ${condition ? "conditional" : ""}`}
```

## Spacing
```tsx
// ✅ Correct
<div className="flex flex-col gap-4">

// ❌ Wrong
<div className="space-y-4">
```

## Equal Dimensions
```tsx
// ✅ Correct
<Avatar className="size-10" />

// ❌ Wrong
<Avatar className="w-10 h-10" />
```

## Truncate Shorthand
```tsx
// ✅ Correct
<p className="truncate">

// ❌ Wrong
<p className="overflow-hidden text-ellipsis whitespace-nowrap">
```

## Overlay Stacking
```tsx
// ✅ Correct - components handle their own z-index
<Dialog><DialogContent>...</DialogContent></Dialog>

// ❌ Wrong - manual z-index
<DialogContent className="z-50">
```

## Typography
- Use component variants: `variant="outline"`, `variant="ghost"`, `size="sm"`
- Don't override component colors/typography via className
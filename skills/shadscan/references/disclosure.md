# Disclosure — Accordion, Collapsible

## Accordion

### Radix → Base UI
```tsx
// Radix
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@radix-ui/react-accordion"

// Base UI
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@base-ui/react/accordion"
```

### Structure (Same)
```tsx
<Accordion type="single" value={val} onValueChange={setVal}>
  <AccordionItem value="item-1">
    <AccordionTrigger>Is it accessible?</AccordionTrigger>
    <AccordionContent>
      Yes, it follows WAI-ARIA patterns.
    </AccordionContent>
  </AccordionItem>
</Accordion>
```

### Props (Same)
| Prop | Radix | Base UI |
|------|-------|---------|
| `type` ("single" | "multiple") | ✅ | ✅ |
| `value` | ✅ | ✅ |
| `onValueChange` | ✅ | ✅ |
| `defaultValue` | ✅ | ✅ |
| `disabled` | ✅ | ✅ |
| `orientation` | ✅ | ✅ |

---

## Collapsible

### Radix → Base UI
```tsx
// Radix
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@radix-ui/react-collapsible"

// Base UI
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@base-ui/react/collapsible"
```

### Structure (Same)
```tsx
<Collapsible open={open} onOpenChange={setOpen}>
  <CollapsibleTrigger>Toggle</CollapsibleTrigger>
  <CollapsibleContent>Content</CollapsibleContent>
</Collapsible>
```

### Props (Same)
| Prop | Radix | Base UI |
|------|-------|---------|
| `open` | ✅ | ✅ |
| `onOpenChange` | ✅ | ✅ |
| `defaultOpen` | ✅ | ✅ |
| `disabled` | ✅ | ✅ |
# Parameters (Zod Schema) Reference

Reference: https://www.remotion.dev/docs/parameters

## Install
```bash
npm install zod
```

## Basic Schema
```tsx
import { z } from "zod";
import { zColor } from "remotion";

export const Schema = z.object({
  title: z.string().min(1).max(50),
  color: zColor(),
  count: z.number().int().min(1).max(100),
  enabled: z.boolean().default(true),
  options: z.enum(["a", "b", "c"]).optional(),
});
```

## Pass to Composition
```tsx
<Composition
  id="ParamVideo"
  component={MyComp}
  schema={Schema}
  defaultProps={{ title: "Hello", color: "#0066ff", count: 5 }}
/>
```

## In Component
```tsx
import { getInputProps } from "remotion";

const MyComp = () => {
  const props = getInputProps<z.infer<typeof Schema>>();
  // props.title, props.color, props.count are typed
  return <Text color={props.color}>{props.title}</Text>;
};
```

## zColor
```tsx
import { zColor } from "remotion";

zColor() // validates hex, rgb, hsl, named colors
```

## Complex Types
```tsx
z.object({
  gradient: z.object({
    from: zColor(),
    to: zColor(),
    angle: z.number().default(90),
  }),
  texts: z.array(z.object({
    text: z.string(),
    position: z.object({ x: z.number(), y: z.number() }),
  })),
})
```

## Studio Visual Editor
- When schema is passed, Studio shows visual editor
- Sliders for numbers
- Color pickers for zColor
- Dropdowns for enums
- Checkboxes for booleans

## TypeScript
```ts
import { z } from "zod";

type Props = z.infer<typeof Schema>;
// Props = { title: string; color: string; count: number; enabled: boolean; options?: "a" | "b" | "c" }
```
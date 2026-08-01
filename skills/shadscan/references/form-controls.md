# Form Controls — Input, Textarea, Select, Combobox, InputOTP, Slider, Toggle, ToggleGroup

## Input / Textarea

### Radix → Base UI
```tsx
// Radix (via shadcn wrappers)
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

// Base UI
import { Input } from "@base-ui/react/input"
import { Textarea } from "@base-ui/react/textarea"
```

### Props (Same)
| Prop | Radix | Base UI |
|------|-------|---------|
| `value` | ✅ | ✅ |
| `onChange` | ✅ | ✅ |
| `defaultValue` | ✅ | ✅ |
| `disabled` | ✅ | ✅ |
| `required` | ✅ | ✅ |
| `placeholder` | ✅ | ✅ |
| `type` | ✅ | ✅ |

---

## Select

### Radix → Base UI
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
  SelectScrollUpButton,
  SelectScrollDownButton,
} from "@radix-ui/react-select"

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
  SelectScrollUpButton,
  SelectScrollDownButton,
  SelectInput,
} from "@base-ui/react/select"
```

### Structure Change
```tsx
// Radix
<Select>
  <SelectTrigger>Select</SelectTrigger>
  <SelectContent>
    <SelectViewport>
      <Select.Item value="a">Option A</Select.Item>
    </SelectViewport>
  </SelectContent>
</Select>

// Base UI
<Select>
  <SelectTrigger>Select</SelectTrigger>
  <SelectPopup>
    <SelectContent>
      <SelectViewport>
        <Select.Item value="a">Option A</Select.Item>
      </SelectViewport>
    </SelectContent>
  </SelectPopup>
</Select>
```

---

## Combobox

### Radix → Base UI
```tsx
// Radix
import { Combobox, ComboboxTrigger, ComboboxContent, ComboboxInput, ComboboxItem } from "@radix-ui/react-combobox"

// Base UI
import { Combobox, ComboboxTrigger, ComboboxPopup, ComboboxContent, ComboboxInput, ComboboxItem } from "@base-ui/react/combobox"
```

### Structure Change
```tsx
// Radix
<Combobox>
  <ComboboxTrigger>Search</ComboboxTrigger>
  <ComboboxContent>
    <ComboboxInput />
    <ComboboxItem value="a">Option A</Combobox.Item>
  </ComboboxContent>
</Combobox>

// Base UI
<Combobox>
  <ComboboxTrigger>Search</ComboboxTrigger>
  <ComboboxPopup>
    <ComboboxContent>
      <ComboboxInput />
      <Combobox.Item value="a">Option A</Combobox.Item>
    </ComboboxContent>
  </ComboboxPopup>
</Combobox>
```

---

## InputOTP

```tsx
// Radix
import { InputOTP, InputOTPGroup, InputOTPSlot, InputOTPSeparator } from "@radix-ui/react-input-otp"

// Base UI
import { InputOTP, InputOTPGroup, InputOTPSlot, InputOTPSeparator } from "@base-ui/react/input-otp"
```

### Structure (Same)
```tsx
<InputOTP maxLength={6} onValueChange={setValue}>
  <InputOTPGroup>
    <InputOTPSlot index={0} />
    <InputOTPSlot index={1} />
    <InputOTPSeparator />
    <InputOTPSlot index={2} />
    <InputOTPSlot index={3} />
  </InputOTPGroup>
</InputOTP>
```

---

## Slider

```tsx
// Radix
import { Slider } from "@radix-ui/react-slider"

// Base UI
import { Slider } from "@base-ui/react/slider"
```

### Props (Same)
| Prop | Radix | Base UI |
|------|-------|---------|
| `value` (number[]) | ✅ | ✅ |
| `onValueChange` | ✅ | ✅ |
| `defaultValue` | ✅ | ✅ |
| `min` | ✅ | ✅ |
| `max` | ✅ | ✅ |
| `step` | ✅ | ✅ |
| `orientation` | ✅ | ✅ |
| `disabled` | ✅ | ✅ |

---

## Toggle / ToggleGroup

```tsx
// Radix
import { Toggle, ToggleGroup, ToggleGroupItem } from "@radix-ui/react-toggle"

// Base UI
import { Toggle, ToggleGroup, ToggleGroupItem } from "@base-ui/react/toggle"
```

### Structure (Same)
```tsx
<ToggleGroup type="multiple" value={val} onValueChange={setVal}>
  <ToggleGroupItem value="bold"><BoldIcon /></ToggleGroupItem>
  <ToggleGroupItem value="italic"><ItalicIcon /></ToggleGroupItem>
</ToggleGroup>

<Toggle>Single</Toggle>
```

---

## Search Commands for Migration

```bash
# Find all Radix form imports
grep -rn "from \"@radix-ui/react-\(input\|select\|combobox\|input-otp\|slider\|toggle\)" --include="*.tsx" src/

# Find Select.Content without Popup
grep -rn "Select\.Content" --include="*.tsx" src/ | grep -v "Popup"

# Find Combobox.Content without Popup
grep -rn "Combobox\.Content" --include="*.tsx" src/ | grep -v "Popup"
```
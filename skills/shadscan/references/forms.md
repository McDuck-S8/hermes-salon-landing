# Forms & Inputs — Critical Rules

## Field Structure
```tsx
// ✅ Correct
<FieldGroup>
  <Field>
    <FieldLabel htmlFor="email">Email</FieldLabel>
    <Input id="email" />
    <FieldDescription>Your email address</FieldDescription>
  </Field>
</FieldGroup>

// ❌ Wrong - raw div + Label
<div className="space-y-2">
  <Label htmlFor="email">Email</Label>
  <Input id="email" />
</div>
```

## Validation
```tsx
// ✅ Correct - data-invalid on Field, aria-invalid on control
<Field data-invalid>
  <FieldLabel>Email</FieldLabel>
  <Input aria-invalid />
  <FieldDescription>Invalid email.</FieldDescription>
</Field>

// Disabled state
<Field data-disabled>
  <Input disabled />
</Field>
```

## Input Groups
```tsx
// ✅ Correct
<InputGroup>
  <InputGroupAddon>$</InputGroupAddon>
  <InputGroupInput />
</InputGroup>

// ❌ Wrong - raw Input with div wrapper
<div className="flex">
  <span>$</span>
  <Input />
</div>
```

## Option Sets (2-7 choices)
```tsx
// ✅ Correct - ToggleGroup
<ToggleGroup type="multiple" value={value} onValueChange={setValue}>
  <ToggleGroupItem value="a">Option A</ToggleGroupItem>
  <ToggleGroupItem value="b">Option B</ToggleGroupItem>
</ToggleGroup>

// ❌ Wrong - manual Button loop with active state
{options.map(opt => (
  <Button 
    key={opt} 
    variant={active === opt ? "default" : "outline"}
    onClick={() => setActive(opt)}
  >
    {opt}
  </Button>
))}
```

## Checkboxes/Radios Grouping
```tsx
// ✅ Correct
<FieldSet>
  <FieldLegend>Options</FieldLegend>
  <div className="space-y-2">
    {items.map(item => (
      <Field key={item.id}>
        <Field>
          <Checkbox id={item.id} value={item.value} />
          <FieldLabel htmlFor={item.id}>{item.label}</FieldLabel>
        </Field>
      </Field>
    ))}
  </div>
</FieldSet>

// ❌ Wrong - raw div with heading
<div>
  <h3>Options</h3>
  {items.map(item => (
    <label key={item.id}>
      <Checkbox value={item.value} />
      {item.label}
    </label>
  ))}
</div>
```

## Button in Input
```tsx
// ✅ Correct
<InputGroup>
  <InputGroupAddon>
    <Button>Submit</Button>
  </InputGroupAddon>
  <Input />
</InputGroup>
```
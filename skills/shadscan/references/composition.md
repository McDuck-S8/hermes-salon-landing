# Component Structure & Composition — Critical Rules

## Items Always Inside Their Group
```tsx
// ✅ Correct
<Select>
  <SelectTrigger>...</SelectTrigger>
  <SelectContent>
    <SelectGroup>
      <SelectLabel>Category</SelectLabel>
      <SelectItem value="a">Option A</SelectItem>
      <SelectItem value="b">Option B</SelectItem>
    </SelectGroup>
  </SelectContent>
</Select>

// ❌ Wrong - SelectItem outside SelectGroup
<SelectContent>
  <SelectItem value="a">Option A</SelectItem>
</SelectContent>
```

## DropdownMenu
```tsx
// ✅ Correct
<DropdownMenu>
  <DropdownMenuTrigger>Actions</DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuGroup>
      <DropdownMenuLabel>Actions</DropdownMenuLabel>
      <DropdownMenuItem>Edit</DropdownMenuItem>
      <DropdownMenuItem>Delete</DropdownMenuItem>
    </DropdownMenuGroup>
  </DropdownMenuContent>
</DropdownMenu>

// ❌ Wrong - item directly in content
<DropdownMenuContent>
  <DropdownMenuItem>Edit</DropdownMenuItem>
</DropdownMenuContent>
```

## Command
```tsx
// ✅ Correct
<Command>
  <CommandInput placeholder="Search..." />
  <CommandList>
    <CommandGroup>
      <CommandItem>Results...</CommandItem>
    </CommandGroup>
    <CommandEmpty>No results.</CommandEmpty>
  </CommandList>
</Command>
```

## Tabs
```tsx
// ✅ Correct
<Tabs defaultValue="a">
  <TabsList>
    <TabsTrigger value="a">Tab A</TabsTrigger>
    <TabsTrigger value="b">Tab B</TabsTrigger>
  </TabsList>
  <TabsContent value="a">Content A</TabsContent>
  <TabsContent value="b">Content B</TabsContent>
</Tabs>

// ❌ Wrong - trigger directly in Tabs
<Tabs>
  <TabsTrigger value="a">Tab A</TabsTrigger>
</Tabs>
```

## Dialog / Sheet / Drawer
```tsx
// ✅ Correct - always include Title
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Title Required</DialogTitle>
      <DialogDescription>Description</DialogDescription>
    </DialogHeader>
    <DialogContent>Body</DialogContent>
    <DialogFooter>Actions</DialogFooter>
  </DialogContent>
</Dialog>

// ❌ Wrong - missing DialogTitle
<DialogContent>
  <p>Content without title</p>
</DialogContent>
```

## Card — Full Composition
```tsx
// ✅ Correct
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Main content</CardContent>
  <CardFooter>Actions</CardFooter>
</Card>

// ❌ Wrong - everything in CardContent
<Card>
  <CardContent>
    <h3>Title</h3>
    <p>Description</p>
    <div>Main content</div>
    <button>Action</button>
  </CardContent>
</Card>
```

## asChild / render for Custom Triggers
```tsx
// Radix (asChild)
<SelectTrigger asChild>
  <Button>Custom Trigger</Button>
</SelectTrigger>

// Base UI (render)
<SelectTrigger render={({ open, ref }) => (
  <Button ref={ref} aria-expanded={open}>Custom</Button>
)} />
```

## Use Components, Not Custom Markup
```tsx
// ✅ Correct
<Alert variant="destructive"><AlertTitle>Error</AlertTitle><AlertDescription>...</AlertDescription></Alert>
<Empty>No data</Empty>
<Skeleton className="h-4 w-3/4" />
<Separator />
<Badge variant="secondary">+20%</Badge>
<Toast /> via sonner toast()

// ❌ Wrong - hand-rolled
<div className="border-l-4 border-red-500 p-4 bg-red-50">Error</div>
<div className="animate-pulse h-4 bg-gray-200" />
<hr className="border-t" />
<span className="px-2 py-1 bg-gray-100 rounded">+20%</span>
```
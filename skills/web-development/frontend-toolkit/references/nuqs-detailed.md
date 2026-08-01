# nuqs — Detailed Reference

## Core API

### Basic Usage
```tsx
import { useQueryState, parseAsString } from 'nuqs'

function SearchBar() {
  const [query, setQuery] = useQueryState('q', parseAsString)
  return (
    <input 
      value={query ?? ''} 
      onChange={e => setQuery(e.target.value)} 
    />
  )
}
```

### Built-in Parsers
- `parseAsString` — string (default)
- `parseAsNumber` — number
- `parseAsBoolean` — boolean
- `parseAsJson` — JSON object
- `parseAsArrayOf` — array of items
- `parseAsIsoDateTime` — ISO date string

### Multiple Params
```tsx
import { useQueryStates, parseAsString, parseAsNumber } from 'nuqs'

const [filters, setFilters] = useQueryStates({
  q: parseAsString,
  page: parseAsNumber.withDefault(1),
  sort: parseAsString.withDefault('newest')
})
```

### History Control
```tsx
// Replace current history entry (default)
setQuery('new-value')

// Append to history (browser back works)
setQuery('new-value', { history: 'push' })
```

### Server Components (RSC)
```tsx
// Server component — read search params
import { getQueryState } from 'nuqs/server'

export default async function Page({ searchParams }) {
  const query = await getQueryState(searchParams, 'q', parseAsString)
  // ...
}
```

### Shallow vs Deep Updates
```tsx
// Shallow (default) — only URL changes, no server re-render
setQuery('value')

// Deep — triggers server re-render for RSC
setQuery('value', { shallow: false })
```

### Custom Parsers
```tsx
import { createParser } from 'nuqs'

const parseAsColor = createParser({
  parse: (value) => value.startsWith('#') ? value : null,
  serialize: (value) => value
})

const [color, setColor] = useQueryState('color', parseAsColor)
```

### Testing
```tsx
import { useQueryState } from 'nuqs/testing'

// In test
const [query, setQuery] = useQueryState('q', parseAsString)
```

## Compatibility
- Next.js App Router ✓
- Next.js Pages Router ✓
- React SPA ✓
- Remix ✓
- React Router ✓
- TanStack Router ✓

## Adopters
AutoGPT, Dify, shadcn-ui, Supabase, LobeHub, Sentry, Discord.js, Uniswap, Vercel examples

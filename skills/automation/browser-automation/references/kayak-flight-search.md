# Kayak Flight Search — BrowserClaw Recipe

## Complete Working Example

```python
import asyncio

async def search_flights(origin: str, destination: str, date: str):
    """Search flights on Kayak via BrowserClaw."""
    
    # 1. Create new tab
    result = await mcp__browserclaw__tabs(action="new", url="https://www.kayak.com/flights")
    page = result["page"]
    
    # 2. Handle cookie consent
    await mcp__browserclaw__snapshot(page=page)
    # Click "Accept all" - find ref in snapshot
    await mcp__browserclaw__act(page=page, kind="click", ref="<accept-all-ref>")
    
    # 3. Fill origin
    await mcp__browserclaw__snapshot(page=page)
    await mcp__browserclaw__act(page=page, kind="fill", ref="<origin-ref>", value=origin)
    await mcp__browserclaw__act(page=page, kind="press", key="Enter")
    
    # 4. Fill destination
    await mcp__browserclaw__snapshot(page=page)
    await mcp__browserclaw__act(page=page, kind="fill", ref="<dest-ref>", value=destination)
    await mcp__browserclaw__act(page=page, kind="press", key="Enter")
    
    # 5. Select departure date
    await mcp__browserclaw__snapshot(page=page)
    # Find date ref via grep or visual inspection
    await mcp__browserclaw__act(page=page, kind="click", ref="<date-ref>")
    
    # 6. Click search
    await mcp__browserclaw__act(page=page, kind="click", ref="<search-ref>")
    
    # 7. Wait for results
    await mcp__browserclaw__wait(page=page, for="time", value=10000)
    
    # 8. Extract results
    await mcp__browserclaw__snapshot(page=page)
    content = await mcp__browserclaw__read(page=page, format="markdown")
    
    # 9. Parse prices (grep for $ amounts)
    prices = await mcp__browserclaw__grep(page=page, pattern=r"\$\d{1,3}(?:,\d{3})*", over="content")
    
    return {
        "origin": origin,
        "destination": destination,
        "date": date,
        "results": content,
        "prices": prices
    }

# Usage
results = await search_flights("SFO", "NYC", "2025-07-18")
print(f"Found {len(results['prices'])} price points")
```

## Ref Discovery Tips

Use `grep` to find element refs dynamically:

```python
# Find origin input
await mcp__browserclaw__snapshot(page=page)
origin_refs = await mcp__browserclaw__grep(page=page, pattern="origin|from|where from", over="ax")

# Find destination input
dest_refs = await mcp__browserclaw__grep(page=page, pattern="destination|to|where to", over="ax")

# Find search button
search_refs = await mcp__browserclaw__grep(page=page, pattern="search|find flights", over="ax")

# Find calendar day
day_refs = await mcp__browserclaw__grep(page=page, pattern="18|19|20", over="ax")
```

## Error Handling

```python
try:
    results = await search_flights("SFO", "NYC", "2025-07-18")
except Exception as e:
    # Screenshot for debugging
    await mcp__browserclaw__screenshot(page=page, fullPage=True, annotate=True)
    raise
```
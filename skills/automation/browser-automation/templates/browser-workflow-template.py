# BrowserClaw Workflow Template

## Standard Page Interaction Template

```python
async def interact_with_page(page: int, actions: list[dict]):
    """
    Execute a sequence of actions on a page.
    
    actions = [
        {"kind": "snapshot"},  # Always start with snapshot
        {"kind": "click", "ref": "e1"},
        {"kind": "fill", "ref": "e2", "value": "text"},
        {"kind": "press", "key": "Enter"},
        {"kind": "wait", "for": "selector", "value": ".results"},
        {"kind": "snapshot"},
        {"kind": "read", "format": "markdown"},
    ]
    """
    for action in actions:
        if action["kind"] == "snapshot":
            await mcp__browserclaw__snapshot(page=page)
        elif action["kind"] == "click":
            await mcp__browserclaw__act(page=page, kind="click", ref=action["ref"])
        elif action["kind"] == "fill":
            await mcp__browserclaw__act(page=page, kind="fill", ref=action["ref"], value=action["value"])
        elif action["kind"] == "press":
            await mcp__browserclaw__act(page=page, kind="press", key=action["key"])
        elif action["kind"] == "wait":
            await mcp__browserclaw__wait(page=page, for=action["for"], value=action.get("value"))
        elif action["kind"] == "read":
            return await mcp__browserclaw__read(page=page, format=action.get("format", "markdown"))
        elif action["kind"] == "grep":
            return await mcp__browserclaw__grep(page=page, pattern=action["pattern"], over=action.get("over", "content"))
```

## Form Filling Template

```python
async def fill_form(page: int, fields: dict[str, str], submit_ref: str):
    """Fill multiple form fields and submit."""
    for label, value in fields.items():
        # Find field by label text
        await mcp__browserclaw__snapshot(page=page)
        refs = await mcp__browserclaw__grep(page=page, pattern=label, over="ax")
        if refs:
            # Parse ref from grep result
            field_ref = parse_ref_from_grep(refs[0])
            await mcp__browserclaw__act(page=page, kind="fill", ref=field_ref, value=value)
            await mcp__browserclaw__act(page=page, kind="press", key="Tab")
    
    await mcp__browserclaw__act(page=page, kind="click", ref=submit_ref)
```

## Data Extraction Template

```python
async def extract_table_data(page: int, selector_pattern: str) -> list[dict]:
    """Extract structured data from tables or lists."""
    await mcp__browserclaw__snapshot(page=page)
    content = await mcp__browserclaw__read(page=page, format="markdown")
    
    # Parse markdown tables
    lines = content.split("\n")
    headers = None
    rows = []
    
    for line in lines:
        if "|" in line and not line.strip().startswith("|---"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if headers is None:
                headers = cells
            else:
                rows.append(dict(zip(headers, cells)))
    
    return rows
```

## Screenshot + Annotate for Debugging

```python
async def debug_screenshot(page: int, filename: str = "debug"):
    """Take annotated screenshot for debugging."""
    result = await mcp__browserclaw__screenshot(
        page=page,
        fullPage=True,
        annotate=True,
        format="png"
    )
    # result contains screenshot_path
    return result["screenshot_path"]
```

## Navigation with Wait

```python
async def navigate_and_wait(page: int, url: str, wait_for: str = None):
    """Navigate and wait for content."""
    await mcp__browserclaw__navigate(page=page, action="url", url=url)
    if wait_for:
        await mcp__browserclaw__wait(page=page, for="selector", value=wait_for)
    else:
        await mcp__browserclaw__wait(page=page, for="time", value=3000)
```
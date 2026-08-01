# YAML/Structured-Format Injection Prevention

## The Problem

Building YAML frontmatter (or TOML/JSON/CSV) via string concatenation or f-strings
with user-controlled values creates injection vectors. Crafted input can:
- Break out of quoted strings via backslash (`\`)
- Inject new YAML keys via colon-space sequences (`key: value`)
- Break YAML lines via embedded newlines (`\n`)

## The Fix Pattern

Use a sanitization helper that escapes the three dangerous characters before interpolation:

```python
def sanitize_yaml_field(s):
    """Replace YAML-dangerous characters to prevent injection via crafted input."""
    if not s:
        return s
    s = s.replace("\\", "\\\\")   # backslash (escape char in YAML quoted strings)
    s = s.replace("\n", "\\n")    # newlines (would break YAML lines)
    s = s.replace(":", "\\:")     # colons (YAML key separator in bare scalars)
    return s
```

Apply to every user-controlled field before inserting into the YAML template:

```python
# BEFORE (vulnerable):
fm += f"type: {category}\n"
fm += f'title: "{content[:80]}"\n'
fm += f"resource: {source}\n"
fm += f"verification_method: {verification_method}\n"

# AFTER (safe):
fm += f"type: {sanitize_yaml_field(category)}\n"
safe_title = sanitize_yaml_field(content[:80].replace('"', "'"))
fm += f'title: "{safe_title}"\n'
fm += f"resource: {sanitize_yaml_field(source)}\n"
fm += f"verification_method: {sanitize_yaml_field(verification_method)}\n"
```

## Affected Fields

In a typical YAML frontmatter builder, these are user-controlled:
- `title` / content excerpt     → used in double-quoted scalar
- `category` / `concept_type`   → used as bare scalar after `type:`
- `tags` list items             → used as bare scalars in `- tag` form
- `source` / `resource`         → used as bare scalar after `resource:`
- `verification_method`         → used as bare scalar
- `expiration_date`             → used as bare scalar

## Verification

Test with a crafted payload containing all three dangerous characters:

```python
result = okf_make_frontmatter(
    content='test\ninjected: true',
    tags='injected: true,back\\slash',
    source='evil: source\nhack',
    category='bad: category\ninject',
)
# Verify that the frontmatter section (between --- markers)
# contains only escaped variants of these characters
fm_part = result.split('---')[1]
assert ': true' not in fm_part or '\\: true' in fm_part  # colon escaped
assert '\\n' in fm_part  # newline turned to literal \n
```

## Adapting to Other Formats

- **JSON**: use `json.dumps()` — never build JSON via string concatenation
- **TOML**: use `tomli_w.dumps()` — or escape `\`, `\n`, `"` for quoted strings
- **CSV**: use `csv.writer` with `quoting=csv.QUOTE_ALL` — or escape `"` → `""`, commas, newlines
- **SQL**: use parameterized queries — never f-string interpolation into SQL

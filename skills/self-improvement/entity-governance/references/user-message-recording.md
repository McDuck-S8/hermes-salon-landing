# Recording User Messages to Knowledge Cube

## Why
Users reference themselves and their identity in chat messages, but these messages never enter the Knowledge Cube (KC). Entity Engine can't track user identity because user data isn't in any KC table. This makes the user look like a "phantom" entity with 0 mentions.

## Pattern: record_user_to_kc.py

```python
# Record a user message as a KC experience
def record_user_message(message, source="user_chat"):
    conn = sqlite3.connect(KC_DB)
    content = f"[user:{user_name}] {message}"
    conn.execute('''
        INSERT OR IGNORE INTO experiences 
        (ts, content, raw_text, hash, axis_domain, axis_outcome, source, tags)
        VALUES (?, ?, ?, ?, ?, ?, 'success', ?, ?)
    ''', (now, content, message, sha256(content)[:16], 
          'user_communication', source, 
          json.dumps(["user_message", f"user:{user_name}"])))
    conn.commit()
    conn.close()
```

### Key details:
- **Hash dedup** — SHA256[:16] prevents duplicate entries
- **Tag structure** — `user:{user_name}` tag enables EE matching when syncing
- **Content prefix** — `[user:{user_name}]` prefix makes the name searchable in text
- **axis_domain** — `user_communication` separates user messages from system events
- **source** — identifies the origin channel (user_chat, telegram, etc.)

## Principal Identity Setup

The first message to record should be a **principal fact** that establishes the user as system owner:

```json
{
    "content": "Alexander (Александр) is the principal and owner of the entire Hermes system. The system serves him. He is NOT a phantom entity.",
    "tags": ["principal", "owner", "identity"],
    "domain": "system_knowledge"
}
```

This ensures:
1. The user's name appears in KC at least once → EE can count it
2. A `is_owner_of` relationship can be created in EE
3. The system "knows" who the principal is in durable storage

## Sync After Recording

After each user message recording, run EE sync:

```python
# Sync EE mention counts from ALL KC text sources
def sync_ee_from_kc():
    # Read all KC text (experiences, kc_entries, kc_fts)
    # For each entity, count name occurrences in text
    # Batch-update mention_count in EE
    pass  # See sync_ee_kc.py for full implementation
```

## Cron Registration

Regular sync ensures identity tracking stays current:

```bash
# Every hour: sync EE mentions from KC
cronjob action=create name="EE-KC Sync" schedule="every 1h" \
    prompt="Sync Entity Engine mention_counts from all KC text sources" \
    script="scripts/record_user_to_kc.py --sync"
```

## Entity Quality Gating

Not all entities deserve tracking. Generic words (known, unknown, pattern, time, error) dominate naive substring matching. Filter:

```sql
SELECT id, name FROM entities 
WHERE LENGTH(name) >= 3 
  AND type_id NOT IN (SELECT id FROM entity_types WHERE name = 'Концепция')
```

## Pitfalls

1. **User name in chat vs system references** — user messages rarely contain the user's own name ("сделай это" not "Александр, сделай это"). The `[user:{name}]` content prefix solves this.
2. **Hash collisions** — SHA256[:16] is sufficient for dedup but not cryptographic; OK for internal use
3. **Session persistence** — messages only exist during the current session; recording must happen in real-time during interaction
4. **Over-recording** — avoid recording every keystroke; record substantive user messages (commands, corrections, decisions)

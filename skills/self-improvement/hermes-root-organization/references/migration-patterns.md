# Installation Migration Reference

## Old Installation Locations (known)
1. `D:\Users\Asus\Загрузки\Hermes-USB-Portable-main\Hermes-USB-Portable-main\` — USB portable
2. `D:\Portable_Soft\hermes-usb-portable-main\` — old local install

## What Was Migrated (2026-06-26)

### Successfully migrated:
- `memories/MEMORY.md` — NEVER DELETE rule, v2rayN config, event-driven preference
- `memories/USER.md` — direct action style, POLICY 8, no "how to use" instructions
- `.env` tokens — already existed in current installation

### Blocked by user:
- KC dimensions (4 entries) — user blocked terminal command
- state.db — user blocked access

### Not found in old installation:
- Custom scripts (data/scripts/) — delegation hallucinated, directory empty
- Salon-bot config — not at expected path
- Plugins — only Python runtime files

## Verification Checklist for Future Migrations
- [ ] User provided explicit path (don't assume)
- [ ] `ls` the old directory yourself (don't trust delegation)
- [ ] Compare old vs current before overwriting
- [ ] Ask user before modifying KC or state.db
- [ ] Merge memories with patch (additive, not replacement)

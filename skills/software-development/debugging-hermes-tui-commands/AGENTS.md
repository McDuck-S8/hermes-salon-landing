# AGENTS.md — debugging-hermes-tui-commands

## Purpose
Debug Hermes TUI slash commands spanning three layers: Python command registry, tui_gateway JSON-RPC bridge, and Ink/TypeScript frontend. Diagnoses issues like missing autocomplete entries, CLI-vs-TUI command discrepancies, config persistence without UI updates, and cross-layer debugging.

## Ownership
Owner: Hermes Agent
Category: software-development / debugging
Version: 1.1.0
Platforms: Linux, macOS, Windows
Status: Active (stale since 2026-06-03, 44 days stale as of 2026-07-24)
Updated by: auto_patch_g009

## Local Contracts
### Triggers (from SKILL.md metadata)
- Missing slash commands in TUI autocomplete (works in CLI)
- Commands work in CLI but not in TUI
- Config persists but UI doesn't update
- JSON-RPC communication failures between Python and TypeScript layers
- TypeScript/Python interop debugging

### Required Tools
- Python debugger (debugpy)
- Node.js inspector (--inspect)
- TypeScript compiler (tsc) for type checking
- JSON-RPC protocol knowledge
- Hermes source: `hermes-agent/`, `hermes-webui/`, `gateway-service/`

### Config References
- config.yaml — Hermes configuration (persistence layer)
- hermes-agent/commands/ — Python command registry
- tui_gateway/ — JSON-RPC bridge service
- hermes-webui/ — Ink/TypeScript frontend
- pyproject.toml / package.json — build configs

## Work Guidance
### When to Use
- Slash command missing from TUI autocomplete but present in CLI
- Command executes in CLI but fails/does nothing in TUI
- Configuration changes persist but TUI state doesn't refresh
- Debugging Python ↔ TypeScript communication via tui_gateway
- TypeScript type errors in Hermes webui components
- Python command registration issues

### Common Patterns (from SKILL.md and domain knowledge)
1. **Missing autocomplete**: Check command registration in Python registry → tui_gateway command list → Ink frontend command palette
2. **CLI works, TUI fails**: Trace JSON-RPC request/response in tui_gateway logs; check TypeScript command handler
3. **Config persists but UI stale**: Verify config.yaml watch/reload in tui_gateway → WebSocket push to frontend
4. **Cross-layer debugging**: 
   - Python: `python -m debugpy --listen 5678 -m hermes`
   - TypeScript: `npm run dev -- --inspect` in hermes-webui
   - Gateway: Check tui_gateway logs for JSON-RPC traffic

### Three-Layer Architecture
| Layer | Technology | Location | Debug Entry |
|-------|-----------|----------|-------------|
| Commands | Python | hermes-agent/commands/ | debugpy port 5678 |
| Gateway | JSON-RPC | tui_gateway/ | logs + ws proxy |
| Frontend | Ink/TS | hermes-webui/ | node --inspect |

## Verification
### Test Strategy
- Check for test scripts in skill directory: `ls scripts/ tests/ evals/` → none exist
- Verify fixes by:
  1. Starting Hermes TUI and testing slash command autocomplete
  2. Running same command via CLI and TUI — compare behavior
  3. Checking tui_gateway logs for JSON-RPC errors
  4. Running TypeScript type check: `cd hermes-webui && npx tsc --noEmit`
  5. Running Python type check: `cd hermes-agent && python -m pyright`

### Validation Commands
```bash
# Start Hermes with debugpy for Python layer
cd D:/Portable_Soft/hermes/hermes-agent
python -m debugpy --listen 5678 --wait-for-client -m hermes

# Start tui_gateway with debug logging
cd D:/Portable_Soft/hermes/tui_gateway
python -m tui_gateway --debug

# Start webui with Node inspector
cd D:/Portable_Soft/hermes/hermes-webui
npm run dev -- --inspect

# TypeScript type check
cd D:/Portable_Soft/hermes/hermes-webui
npx tsc --noEmit

# Python type check (if pyright available)
cd D:/Portable_Soft/hermes/hermes-agent
python -m pyright

# Check command registry
cd D:/Portable_Soft/hermes/hermes-agent
python -c "from hermes.commands import registry; print([c.name for c in registry.commands])"

# Test JSON-RPC manually
echo '{"jsonrpc":"2.0","method":"commands.list","id":1}' | nc localhost 8765
```

## Child DOX Index
### References
- (none in skill directory)

### Templates
- (none in skill directory)

### Scripts
- (none in skill directory)

### Related Skills
- python-debugpy — Python debugging with debugpy
- node-inspect-debugger — Node.js inspector debugging
- systematic-debugging — General debugging methodology
- hermes-agent — Hermes Agent configuration and debugging
- hermes-s6-container-supervision — Container supervision for Hermes services
- debugging-toolkit — Unified debugging toolkit for Hermes
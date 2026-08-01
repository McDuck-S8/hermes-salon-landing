# Persona System — Integration with Mark-XLVIII

Source: `D:/Portable_Soft/hermes/Mark-XLVIII/main.py` and `config/__init__.py`

## Mark-XLVIII Language-Aware Address Pattern

From `main.py` line 72 and `config/__init__.py`:
> "The system prompt now enforces: **Turkish → efendim**, **English → sir**, never mixed. Mark XLVII's prompt said 'Always call sir to user' which caused JARVIS to say 'sir' mid-Turkish sentence. Fixed."

This is a **persona-level language rule** — each persona should handle address terms correctly.

## Session State Reset on Persona Switch

Mark-XLVIII resets all transient flags on new Gemini session connection. For Hermes:
- **Persona switch** = soft session boundary
- Should trigger `reset_session_transient()` (clears interrupt/vision flags)
- Persona config persists in `persistent_state`

## Integration Points

| Component | Integration |
|-----------|-------------|
| `autonomous_agent.py` | Load persona config at startup; apply temperature, tools_priority |
| `self_system.py` | `--heal` triggers persona-aware reset |
| `forge-dynamic-tools` | Inject persona directives into forge prompt |
| `session-state-isolation` | `reset_session_transient()` on persona switch |

## Persona Config Structure (from `config.yaml` agent.personalities)

```yaml
personas:
  arbitrage:
    system_prompt: "..."
    tone: "direct, concise"
    style: "arbitrageur"
    temperature: 0.2
  sales:
    system_prompt: "..."
    tone: "persuasive, consultative"
    style: "sales"
    temperature: 0.5
```

## Files
- `scripts/persona_system.py` — Main implementation with 4 personas
- `cache/active_persona.json` — Persistent storage
- This reference: `references/mark-xlviii-integration.md`
# touchdesigner-mcp — Skill

## Purpose
Control a running TouchDesigner instance via twozero MCP — create operators, set parameters, wire connections, execute Python, build real-time visuals. 36 native tools. Free plugin (no payment/license — confirmed April 2026).

## Ownership
Hermes Agent

## Local Contracts
- **Triggers**: User requests TouchDesigner control, real-time visuals, generative art, audio-reactive, VJ, installation, GLSL work via MCP
- **Required tools**: Hermes MCP tools (td_* tools), terminal for setup script
- **Config**: config.yaml in skill dir (optional)
- **Required scripts**: `scripts/setup.sh` (automated setup)
- **Required environment**: TouchDesigner running with twozero.tox installed, MCP enabled on port 40404

## Work Guidance
**When to use**: When user asks to control TouchDesigner via MCP, create operators, set parameters, wire connections, execute Python, build real-time visuals, audio-reactive setups, GLSL shaders, VJ setups, installations.

**Critical Rules (MANDATORY)**:
1. **NEVER guess parameter names.** Call `td_get_par_info` for the op type FIRST. Training data is wrong for TD 2025.32.
2. **If `tdAttributeError` fires, STOP.** Call `td_get_operator_info` on the failing node before continuing.
3. **NEVER hardcode absolute paths** in script callbacks. Use `me.parent()` / `scriptOp.parent()`.
4. **Prefer native MCP tools over `td_execute_python`.** Use `td_create_operator`, `td_set_operator_pars`, `td_get_errors` etc. Only fall back to `td_execute_python` for complex multi-step logic.
5. **Call `td_get_hints` before building.** It returns patterns specific to the op type you're working with.

**Workflow**:
1. **Discover** (before building anything):
   - Call `td_get_par_info` with op_type for each type you plan to use
   - Call `td_get_hints` with the topic you're building (e.g., "glsl", "audio reactive", "feedback")
   - Call `td_get_focus` to see where the user is and what's selected
   - Call `td_get_network` to see what already exists

2. **Clean + Build** (split into SEPARATE MCP calls):
   - Use `td_create_operator` for each node (handles viewport positioning automatically)
   - For bulk creation or wiring, use `td_execute_python` — destroying and recreating same-named nodes in one call causes "Invalid OP object" errors

3. **Set Parameters**:
   - Prefer native tool `td_set_operator_pars` (validates params, won't crash)
   - For expressions or modes, use `td_execute_python`

4. **Wire**:
   - Use `td_execute_python` — no native wire tool exists

5. **Verify**:
   - `td_get_errors(path="/project1", recursive=true)`
   - `td_get_perf()`
   - `td_get_operator_info(path="/project1/out", detail="full")`

6. **Display / Capture**:
   - `td_get_screenshot(path="/project1/out")`
   - Or open window via script (windowCOMP)

**Key Implementation Rules**:
- GLSL time: No `uTDCurrentTime` in GLSL TOP. Use Values page, then set expression via script
- Feedback TOP: Use `top` parameter reference, not direct input wire. "Not enough sources" resolves after first cook. "Cook dependency loop" warning is expected.
- Resolution: Non-Commercial caps at 1280×1280. Use `outputresolution = 'custom'`.
- Large shaders: Write GLSL to `/tmp/file.glsl`, then use `td_write_dat` or `td_execute_python` to load.
- Vertex/Point access (TD 2025.32): `point.P[0]`, `point.P[1]`, `point.P[2]` — NOT `.x`, `.y`, `.z`.
- Extensions: `ext0object` format is `"op('./datName').module.ClassName(me)"` in CONSTANT mode. After editing extension code with `td_write_dat`, call `td_reinit_extension`.
- Script callbacks: ALWAYS use relative paths via `me.parent()` / `scriptOp.parent()`.
- Cleaning nodes: Always `list(root.children)` before iterating + `child.valid` check.

**Audio-Reactive GLSL (Proven Recipe)**:
Correct signal chain: AudioFileIn CHOP → AudioSpectrum CHOP (FFT=512, outputmenu=setmanually, outlength=256, timeslice=ON) → Math CHOP (gain=10) → CHOP to TOP (dataformat=r, layout=rowscropped) → GLSL TOP input 1. Constant TOP (rgba32float, time) → GLSL TOP input 0. Critical: TimeSlice must stay ON, set Output Length manually to 256, DO NOT use Lag/Filter CHOP for spectrum smoothing (timeslice expansion problem), smoothing belongs in GLSL shader via temporal lerp with feedback texture.

**Recording/Exporting Video**:
Use MovieFileOut TOP via `td_execute_python`. Codec: `prores` (preferred on macOS) or `mjpa` as fallback. H.264/H.265/AV1 require Commercial license. Before recording: verify FPS > 0 via `td_get_perf`, verify shader output not black via `td_get_screenshot`, cue audio first then delay recording by 3 frames, set output path before starting record.

**Related skills**: native-mcp, ascii-video, manim-video, hermes-video

## Verification
- Load SKILL.md and validate frontmatter
- Run `bash scripts/setup.sh` to verify automated setup works
- Verify `td_get_par_info` and `td_get_hints` MCP tools respond
- Check `references/` directory has 21 reference files
- Verify `scripts/setup.sh` exists and is executable
- Test MCP connection: `nc -z 127.0.0.1 40404 && echo "twozero MCP: READY"`

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (21 files: 3d-scene.md, animation.md, audio-reactive.md, dat-scripting.md, external-data.md, geometry-comp.md, glsl.md, layout-compositor.md, mcp-tools.md, midi-osc.md, network-patterns.md, operators.md, operator-tips.md, panel-ui.md, particles.md, pitfalls.md, postfx.md, projection-mapping.md, python-api.md, replicator.md, troubleshooting.md) |
| `scripts/` | Executable helpers (1 file: setup.sh - automated setup script) |
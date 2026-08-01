# Google Stitch MCP — Design Resource

Google Stitch (stitch.withgoogle.com) is a free AI UI/UX design tool (~400 credits/day). Its MCP server gives direct access to generate, analyze, and export designs from the agent.

## Two MCP Server Implementations

### 1. stitch-mcp (npm, 1.3.2) — GCP ADC auth

```
npx -y stitch-mcp
```
Needs `GOOGLE_CLOUD_PROJECT` env var + `gcloud auth application-default login`.
Works with Google Cloud ADC.

### 2. oogleyskr/stitch-mcp-server (clone + build) — STITCH_API_KEY

```
git clone https://github.com/oogleyskr/stitch-mcp-server.git
cd stitch-mcp-server
npm install && npm run build
```
Needs `STITCH_API_KEY` env var. **This is what we use.** 44 tools across 9 categories.

## Hermes Config

```bash
hermes mcp add stitch --command node \
  --env STITCH_API_KEY=your-key \
  --args /path/to/stitch-mcp-server/dist/index.js
```

## 44 Available Tools

| Category | Tools |
|----------|-------|
| Upstream proxy | list_projects, get_project, list_screens, get_screen, generate_screen_from_text, edit_screens, generate_variants |
| Code | get_screen_code, get_screen_image, build_site, list_tools |
| Workspace | get_workspace_project, set_workspace_project, clear_workspace_project |
| Design | extract_design_context, apply_design_context, generate_design_tokens, generate_responsive_variant, batch_generate_screens, generate_from_template |
| Analysis | analyze_accessibility, compare_designs, extract_components, design_diff |
| Export | generate_style_guide, export_design_system, suggest_trending_design, export_all_screens |
| Codegen | screen_to_react |
| Integration | screen_to_plane_issue |
| Advanced | screen_to_tailwind_config, screen_to_css_variables, validate_design_system, generate_dark_mode, generate_component_variants, project_summary |
| Project CRUD | create_project, delete_project |
| Design systems | upload_design_md, create_design_system, create_design_system_from_design_md, update_design_system, list_design_systems, apply_design_system |

## Usage Pattern

```python
# 1. Generate a design from text prompt
# (via Stitch MCP tool: generate_screen_from_text)

# 2. Extract design context from existing screen
# (via Stitch MCP tool: extract_design_context)

# 3. Generate variants or apply trends
# (via Stitch MCP tool: suggest_trending_design)

# 4. Export code
# (via Stitch MCP tool: screen_to_react, screen_to_css_variables)
```

Best used when stuck on design direction after 2+ user rejections. Generate 3-5 reference screens at once via `batch_generate_screens` rather than one-by-one.

Free quota: ~400 credits/day, ~350/month depending on usage pattern.

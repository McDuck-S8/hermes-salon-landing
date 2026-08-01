# Headroom + LLMLingua Integration for Hermes Autonomous Proactivity

## Overview
Full-stack context compression to fix timeout issues and enable free models to handle large contexts.

## Components

### Headroom (chopratejas/headroom)
- **Purpose**: Compress tool outputs, logs, RAG chunks, files before LLM
- **Compression**: 60-95% fewer tokens, same answers
- **Modes**: Library + Proxy + MCP server
- **CLI**: `headroom wrap <command>`, `headroom mcp install`
- **Features**: Reversible, 6 algorithms, local-first, cross-agent memory via `headroom learn`

### LLMLingua (microsoft/LLMLingua)
- **Purpose**: Compress prompts (system + user + RAG) before LLM
- **LLMLingua-2**: BERT-level encoder, task-agnostic, up to 20x compression
- **LongLLMLingua**: Long contexts (meetings, code, CoT)
- **RAG improvement**: +21.4% performance at 1/4 tokens

## Synergy: Full Stack Compression
```
Hermes Agent → tool outputs, logs, RAG
    ↓
[Headroom] → 60-95% compression (tool outputs, logs, files)
    ↓
[LLMLingua-2] → 4-20x compression (prompts, RAG, system prompt)
    ↓
[Free LLM] → fast, cheap, quality preserved
```

## Integration Points

### 1. LLM Analyst Wrapper (Immediate Fix)
```bash
# Wrap the cron job script
headroom wrap python scripts/llm_analyst.py
```
- Fixes 120s timeout by compressing context before LLM
- Use direct opencode.exe path: `D:/npm-global/node_modules/opencode-ai/bin/opencode.exe`

### 2. MCP Server (All Agents)
```bash
headroom mcp install
```
- Adds compression layer to all agents via MCP
- Automatic for any agent using MCP tools

### 3. LLMLingua-2 in Proactive Executor
```python
# In proactive_executor.py Phase 2.5 before analyze_with_llm()
from llmlingua import PromptCompressor

compressor = PromptCompressor(
    model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank"
)
compressed = compressor.compress_prompt(
    prompt=huge_prompt_from_knowledge_cube,
    rate=0.25,  # 4x compression
    target_token=2000
)
# Use compressed.prompt for LLM call
```

### 4. Headroom Learn (Auto-Pattern Learning)
```bash
headroom learn
```
- Automatically learns compression patterns from usage
- Improves compression over time

## Configuration

### config.yaml additions
```yaml
# Headroom settings
headroom:
  enabled: true
  wrap_llm_analyst: true
  mcp_enabled: true

# LLMLingua settings
llmlingua:
  model: "microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank"
  compression_rate: 0.25  # 4x
  target_tokens: 2000
```

## Installation
```bash
# In Hermes venv
D:/Portable_Soft/hermes/hermes-agent/venv/Scripts/python.exe -m pip install headroom llmlingua
```

## Verification
1. `headroom wrap python scripts/llm_analyst.py` — should run without timeout
2. `python -c "from llmlingua import PromptCompressor; print('OK')"` — LLMLingua loads
3. `headroom mcp install` — MCP server registered

## Benefits for Hermes
| Problem | Solution |
|---------|----------|
| llm_analyst timeout (120s) | Headroom compresses context → fits in free model limits |
| Free model context limits | LLMLingua compresses prompts 4-20x |
| Token costs | 60-95% + 4-20x = massive savings |
| RAG quality | LLMLingua improves RAG +21.4% at 1/4 tokens |
| Cross-agent memory | Headroom learn + MCP sharing |

## Next Steps
1. Install in venv (resolve pip conflicts)
2. Test `headroom wrap python scripts/llm_analyst.py` 
3. Add LLMLingua-2 to proactive_executor.py
4. Install MCP server
4. Verify end-to-end proactivity loop
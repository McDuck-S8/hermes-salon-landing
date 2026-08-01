# AI-Agent Infrastructure Stack — $0 Budget (2026-06-29)

**Source:** WEba_2Nf19Y video + fabric research
**Status:** UNVERIFIED — requires integration testing

## 10-Tool Production Stack

| # | Tool | Repo | Role in Arbitrage/Agency | Priority | Integration Point |
|---|------|------|--------------------------|----------|-------------------|
| 1 | **Instructor** | https://github.com/jxnl/instructor | Structured LLM outputs, Pydantic validation | 🔥 HIGH | `goal_executor.py`, `rd_processor.py`, `dev_processor.py`, `auto_poster.py` |
| 2 | **LiteLLM** | https://github.com/BerriAI/litellm | Unified API for 100+ providers, fallback, routing | 🔥 HIGH | `config.yaml` providers, `hermes_bootstrap.py` health check |
| 3 | **Outlines** | https://github.com/dottxt-ai/outlines | Guided generation, regex/JSON/grammar enforcement | 🔥 HIGH | Schema validation for all LLM outputs |
| 4 | **Crawl4AI** | https://github.com/unclecode/crawl4ai | LLM-friendly crawler, markdown extraction | 🔥 HIGH | `web_surfer.py` replacement |
| 5 | **DSPy** | https://github.com/stanfordnlp/dspy | Declarative LM programs, prompt optimization | MEDIUM | Prompt optimization for conversion |
| 6 | **Qdrant** | https://github.com/qdrant/qdrant | Vector DB, semantic search | MEDIUM | `knowledge_cube.py` backend |
| 7 | **Ollama** | https://github.com/ollama/ollama | Local LLM runner (Qwen, Llama, Gemma) | 🔥 HIGH | `hermes_bootstrap.py` fallback |
| 8 | **Langfuse** | https://github.com/langfuse/langfuse | LLM observability, tracing, eval | MEDIUM | `cron/scheduler.py` tracing |
| 9 | **Marker** | https://github.com/VikParuchuri/marker | PDF → Markdown (OLM + LLM) | HIGH | `document-processing` skill |
| 10 | **Chonkie** | https://github.com/chonkie-ai/chonkie | Semantic chunking for RAG | MEDIUM | `knowledge_cube.py` chunking |

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HERMES AGENT CORE                         │
├─────────────────────────────────────────────────────────────┤
│  config.yaml → LiteLLM (provider routing + fallback)        │
│  hermes_bootstrap.py → Ollama health check                  │
├─────────────────────────────────────────────────────────────┤
│  WEB SURFER LAYER                                           │
│  web_surfer.py → Crawl4AI (replaces requests + BS4)         │
├─────────────────────────────────────────────────────────────┤
│  KNOWLEDGE CUBE LAYER                                       │
│  knowledge_cube.py → Qdrant (vector) + Chonkie (chunking)   │
├─────────────────────────────────────────────────────────────┤
│  STRUCTURED OUTPUT LAYER                                    │
│  Instructor + Outlines → All LLM calls validated            │
│  - goal_executor: goal schema                               │
│  - rd_processor: research schema                            │
│  - dev_processor: dev task schema                           │
│  - auto_poster: post schema                                 │
├─────────────────────────────────────────────────────────────┤
│  OBSERVABILITY LAYER                                        │
│  cron/scheduler.py → Langfuse tracing                       │
│  - tokens, costs, latency per job                           │
│  - A/B prompt comparison                                    │
├─────────────────────────────────────────────────────────────┤
│  DOCUMENT PROCESSING LAYER                                  │
│  document-processing skill → Marker (PDF → Markdown)        │
│  - PDF offers, TZ, contracts → structured data              │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Steps

### Phase 1: Core Infrastructure (Week 1)
- [ ] Add LiteLLM to config.yaml as primary provider router
- [ ] Install Ollama, pull Qwen2.5-7B, Llama3.1-8B
- [ ] Add Ollama health check to `hermes_bootstrap.py`
- [ ] Test provider fallback chain: OpenRouter → Groq → DeepSeek → Ollama

### Phase 2: Structured Output (Week 1-2)
- [ ] Add Instructor + Outlines to `requirements.txt`
- [ ] Define Pydantic schemas for all agent outputs
- [ ] Wrap `goal_executor`, `rd_processor`, `dev_processor` with validation
- [ ] Test schema enforcement on 10 real runs

### Phase 3: Knowledge Cube Upgrade (Week 2)
- [ ] Deploy Qdrant (Docker: `qdrant/qdrant`)
- [ ] Migrate `knowledge_cube.py` from SQLite FTS5 → Qdrant
- [ ] Add Chonkie for semantic chunking
- [ ] Benchmark: search latency, relevance

### Phase 4: Web Surfer Upgrade (Week 2-3)
- [ ] Replace `web_surfer.py` requests+BS4 with Crawl4AI
- [ ] Test on 20 competitor landing pages
- [ ] Compare extraction quality vs old method

### Phase 5: Observability (Week 3)
- [ ] Deploy Langfuse (Docker compose)
- [ ] Instrument `cron/scheduler.py` with tracing
- [ ] Add A/B prompt testing framework

### Phase 6: Document Processing (Week 3-4)
- [ ] Integrate Marker into `document-processing` skill
- [ ] Test on 10 PDF offers/contracts
- [ ] Build pipeline: PDF → Markdown → Instructor → structured data

## Cost Analysis (Monthly)

| Component | Cost | Notes |
|-----------|------|-------|
| LiteLLM | $0 | Self-hosted |
| Ollama | $0 | Local GPU/CPU |
| Qdrant | $0 | Self-hosted (1M vectors free) |
| Langfuse | $0 | Self-hosted (100K traces/mo free) |
| Crawl4AI | $0 | Local |
| Instructor/Outlines/DSPy/Marker/Chonkie | $0 | Python packages |
| **Total** | **$0** | **Production-ready AI stack** |

## Free API Fallback Chain (via LiteLLM)

```yaml
# config.yaml
providers:
  openrouter:
    api_base: "https://openrouter.ai/api/v1"
    models: ["google/gemini-flash-1.5", "anthropic/claude-3.5-sonnet"]
  groq:
    api_base: "https://api.groq.com/openai/v1"
    models: ["llama-3.1-70b-versatile", "gemma2-9b-it"]
  deepseek:
    api_base: "http://localhost:9655/v1"
    models: ["deepseek-chat", "deepseek-reasoner"]
  ollama:
    api_base: "http://localhost:11434/v1"
    models: ["qwen2.5:7b", "llama3.1:8b", "gemma2:9b"]
```

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Free API rate limits | HIGH | MEDIUM | LiteLLM auto-fallback, Ollama local |
| Qdrant memory usage | MEDIUM | LOW | Monitor, limit vector dims |
| Crawl4AI blocks | MEDIUM | MEDIUM | Rotate user agents, add delays |
| Schema validation breaks LLM flow | LOW | HIGH | Start with warn-only mode |
| Langfuse storage growth | LOW | LOW | Retention policies, sampling |

## Quick Verification Commands

```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Test Qdrant
curl http://localhost:6333/collections

# Test LiteLLM
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "ollama/qwen2.5:7b", "messages": [{"role": "user", "content": "test"}]}'

# Test Crawl4AI
python -c "import crawl4ai; print(crawl4ai.__version__)"

# Test Instructor
python -c "import instructor; print('OK')"
```

## Related Files

- `ARBITRAGE_WORKSHOP.md` — AI-АРСЕНАЛ 2026 section (lines 358-390)
- `earning-with-ai` skill — AI-AGENT ИНФРАСТРУКТУРА $0 section
- `references/pinterest-google-flow-arbitrage-2026-06-29.md` — Pinterest scheme
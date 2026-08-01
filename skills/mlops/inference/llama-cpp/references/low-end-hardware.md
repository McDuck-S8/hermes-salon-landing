# Model Selection for Low-End Hardware

A practical guide for choosing GGUF models when GPU VRAM is limited (≤2GB) and CPU is low-power (i3-6006U class).

## Hardware Profile: Typical Low-End Laptop

| Component | Specification | Impact on LLM |
|---|---|---|
| CPU | Intel i3-6006U (2C/4T, 2.0GHz) | Slow CPU-only inference. 2 physical threads usable |
| RAM | 32 GB DDR4 | Plenty. Can run up to 9B models in Q4 |
| GPU | GeForce 940MX (2GB VRAM, Maxwell gen) | Too old/small for meaningful offload. Treat as CPU-only |
| OS | Windows 11 | llama.cpp runs well; prefer MSYS2 or WSL |

**Key insight:** With 2GB VRAM on a Maxwell GPU (compute 5.0), GPU offload is not viable. The CPU has only 2 cores. Inference will be slow — optimize for model quality per token, not tokens per second.

## Model Size Recommendations

Based on 32 GB system RAM and CPU-only inference:

| Model Size | RAM Usage (Q4_K_M) | Tokens/sec (i3-6006U) | Use Case |
|---|---|---|---|
| **1.5B** (Qwen2.5-1.5B) | ~1 GB | 10-15 tok/s | Fast chat, simple queries, classification |
| **3B** (Qwen2.5-3B / Llama-3.2-3B) | ~2 GB | 5-8 tok/s | General chat, basic tool calling ✅ BEST BALANCE |
| **7B** (Qwen2.5-7B / Mistral-7B) | ~4.5 GB | 1-2 tok/s | Complex reasoning, but painfully slow |
| **8B+** (Llama-3.1-8B / Qwen2.5-9B) | ~5-6 GB | <1 tok/s | Too slow for interactive use |

**Recommended: Qwen2.5-3B-Instruct Q4_K_M** — tool calling support, strong instruction following, small RAM footprint, active maintenance.

## Quantization Guide

| Quant | Size vs Q4_K_M | Quality | When to Use |
|---|---|---|---|
| Q4_K_M | 1.0× (baseline) | Good | Default choice |
| Q5_K_M | ~1.2× | Better | If model + cache fits in RAM |
| Q3_K_M | ~0.8× | Fair | When RAM is tight (<8 GB) |
| IQ4_NL | ~1.0× | Good | Alternative to Q4_K_M |

## Setting Up on Windows (CPU-only)

```bash
# Option A: winget
winget install llama.cpp

# Option B: git + cmake (no GPU flags)
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build --config Release

# Verify
build/bin/Release/llama-cli.exe -hf Qwen/Qwen2.5-3B-Instruct-GGUF:Q4_K_M -p "Hello" -n 32
```

### Server Mode (OpenAI-compatible)

```bash
build/bin/Release/llama-server.exe \
    -hf bartowski/Qwen2.5-3B-Instruct-GGUF:Q4_K_M \
    -c 4096 --port 8080 -t 2 -ngl 0

# Test
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}],"max_tokens":64}'
```

**CPU-only flags:** `-t 2` (use physical core count), `-ngl 0` (zero GPU), `--mlock` (lock in RAM).

## Hermes Integration

In `config.yaml`:
```yaml
providers:
  custom:
    local-llama:
      api: http://localhost:8080/v1
      default_model: Qwen2.5-3B-Instruct
```

Enable via `hermes model` → Custom → local-llama. Set as fallback:
```yaml
fallback_providers:
  - provider: custom
    name: local-llama
```

## Pitfalls

- **Hyperthreading:** i3-6006U has 2C/4T. `-t 4` can be SLOWER than `-t 2` due to cache contention. Benchmark both.
- **GPU offload worse than none** on Maxwell (900 series) with <4GB. Use `-ngl 0`.
- **Windows Defender** scans large GGUF files on first access. Add exclusion for model cache dir.
- **Firewall:** llama-server on Windows prompts for firewall access on first start.
- **Model download** path: `%USERPROFILE%\.cache\llama.cpp\`. Ensure 5+ GB free on system drive.

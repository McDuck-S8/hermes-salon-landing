# Handling Thinking/Reasoning Model Responses

Models from different providers return reasoning content in different field names.
The voice loop must handle all three formats.

## API Response Shapes

### Format 1: `reasoning_content` (Qwen 3.5+, DeepSeek-R1 via LM Studio)

```json
{
  "choices": [{
    "message": {
      "content": "",
      "reasoning_content": "Thinking process...\n\nThe actual answer here..."
    }
  }]
}
```

### Format 2: `reasoning` (mimo-v2.5-free and some opencode.ai/zen models)

```json
{
  "choices": [{
    "message": {
      "content": null,
      "reasoning": "The user is greeting me..."
    }
  }]
}
```

### Format 3: `reasoning_details` (xiaomi/mimo models via opencode.ai)

```json
{
  "choices": [{
    "message": {
      "content": null,
      "reasoning": "...",
      "reasoning_details": [
        {"type": "reasoning.text", "text": "Step 1 thinking..."},
        {"type": "reasoning.text", "text": "Final answer is here."}
      ]
    }
  }]
}
```

## Safe Parsing (current implementation in jarvis_voice_loop.py)

```python
msg = result["choices"][0]["message"]
content = (msg.get("content") or "").strip()
if not content:
    content = (msg.get("reasoning") or "").strip()
if not content:
    content = (msg.get("reasoning_content") or "").strip()
if not content and "reasoning_details" in msg:
    details = msg["reasoning_details"]
    if isinstance(details, list) and len(details):
        # Take the last reasoning step (most likely the actual answer)
        content = details[-1].get("text", "") if isinstance(details[-1], dict) else ""
# Final fallback — don't leave the user hanging
return content if content else "Я слушаю, Сэр."
```

## Why models do this

- **Qwen 3.5+** (qwen3.5-4b, qwen3-coder-30b-a3b): thinking mode is on by default.
  The model thinks before answering and puts reasoning in `reasoning_content`,
  the final answer in `content`. But sometimes `content` is empty if the model
  stops early or the thinking consumed all tokens.
- **DeepSeek-R1 / DeepSeek-v4**: similar pattern. `content` may be empty.
- **opencode.ai/zen models** (mimo-v2.5-free, deepseek-v4-flash-free): return
  `content: null` and put all text in `reasoning` or `reasoning_details`.
  These are free models, no API key needed.

## Related pitfalls

- `reasoning_content`/`reasoning` may contain markdown, thinking markers, or meta-commentary.
  For TTS output, strip thinking markers before speaking.
- Models with `max_tokens` too low may fill the budget with reasoning and leave
  empty content. Increase `max_tokens` or reduce reasoning via system prompt.
- Russian system prompt: when using Russian TTS, the system prompt MUST be in
  Russian. English-prompted Qwen models may think in English and produce empty
  Russian content.
- **default empty response**: if ALL fields are empty (which shouldn't happen
  with a working model), return a neutral fallback like "Я слушаю, Сэр." rather
  than crashing or leaving the user with dead air.
- Always check `reasoning_details[-1].text` (last detail item) — that's typically
  the final answer, not the thinking itself.

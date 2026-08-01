# Pollinations.ai — Session Test Results (2026-07-15)

## Test 1: GET endpoint (no key, no signup)

```
curl "https://image.pollinations.ai/prompt/test%20image?width=512&height=512&seed=1"
```

- **HTTP 200**
- **Content-Type: image/jpeg**
- **Size: 53,640 bytes**
- **Time: ~3-5 seconds**

## Test 2: Portrait generation

```
https://image.pollinations.ai/prompt/beautiful%20ethereal%20fantasy%20woman%20portrait?width=768&height=1024&seed=42&model=flux
```

- **HTTP 200**
- **Size: 91,635 bytes**
- **Model: flux** (default)

## Test 3: Batch generation (3 images via generate.py)

All 3/3 successful through `urllib.request` (Python):

| # | Seed | Size | Style | Model |
|---|------|------|-------|-------|
| 1 | 145301 | 108 KB | fantasy | flux |
| 2 | 8979 | 104 KB | fantasy | flux |
| 3 | 389292 | 87 KB | fantasy | flux |

## Quirks

- **Timeout**: anime-style prompt timed out once via curl (30s). Second attempt with same seed worked.
- **Full prompts yield better results**: 50-100 character prompts produce coherent outputs. Short (<20 chars) prompts produce generic results.
- **No safety filter by default**: `safe` param defaults to off. Explicit `?safe=false` or omit.
- **No rate limiting observed**: 3 sequential requests completed without throttling.

## Python code snippet (verified working)

```python
import urllib.request, urllib.parse

prompt = "Your prompt here"
encoded = urllib.parse.quote(prompt)
url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1024&seed={seed}&model=flux"

req = urllib.request.Request(url, headers={"User-Agent": "Hermes-Agent/1.0"})
with urllib.request.urlopen(req, timeout=60) as resp:
    data = resp.read()
    with open("output.jpg", "wb") as f:
        f.write(data)
```

## Production notes

- For AI OFM (adult content generation): `safe` param default is OFF, but individual models may refuse explicit prompts. Flux handles fantasy/anime/editorial portraits well.
- For higher reliability: use `gen.pollinations.ai` POST endpoint with an API key (free tier available at enter.pollinations.ai).
- Empty size URL returns 1024x1024 default.

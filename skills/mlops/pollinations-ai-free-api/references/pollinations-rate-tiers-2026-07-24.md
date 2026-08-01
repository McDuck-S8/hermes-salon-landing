# Pollinations Rate Limit Tiers (Session-Tested, 2026-07-24)

## Test Results

### Tier 1: 1-2 images
- Delay: 10-20s between requests
- Timeout: 60-75s per request
- Result: ✅ Success (avatar 22KB, cover 64KB)
- Working command:
  ```python
  timeout 90 python -c "
  import urllib.request, urllib.parse
  prompt='your prompt here'
  encoded=urllib.parse.quote(prompt)
  url=f'https://image.pollinations.ai/prompt/{encoded}?width=1024&height=768&model=flux&nologo=true&seed=100'
  req=urllib.request.Request(url, headers={'User-Agent': 'Hermes-Agent/1.0'})
  with urllib.request.urlopen(req, timeout=75) as resp:
      data=resp.read()
      print(f'OK: {len(data)} bytes')
  "
  ```

### Tier 2: 3-4 images
- Delay: 20-30s between requests
- Timeout: 90s per request
- Result: ⚠️ Mixed — first 2 succeed, 3rd-4th timeout at 180s total script limit
- Lesson: Don't batch 4 images in a single script with terminal timeout 180s

### Tier 3: 5+ images
- NOT TESTED — likely requires POST API with key
- Use `gen.pollinations.ai` with API key for mass generation

## File Size Observations
- flux model at 1024×768: 57KB-87KB JPEG
- Lower resolution = faster generation (768×768 tested at 28KB)
- nologo=true recommended for channel content

## Common Failures
- HTTP 429: Too Many Requests — wait 60s before retry
- Exit 124 (timeout): Increase terminal timeout to 120-180s for single image
- SSL errors: Not observed with this endpoint (unlike youtube.com)

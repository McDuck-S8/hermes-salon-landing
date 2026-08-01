# Network Constraints on This Machine

All external HTTPS requests must go through the SOCKS5 proxy at `127.0.0.1:10806`.

## Per-Tool Configuration

### Git
```bash
git -c http.proxy=socks5://127.0.0.1:10806 push origin gh-pages
```

### curl
```bash
curl --proxy socks5://127.0.0.1:10806 https://example.com
```

### Python requests
```python
proxies = {'https': 'socks5://127.0.0.1:10806'}
requests.get(url, proxies=proxies, timeout=10)
```

### gh CLI
Respects `HTTPS_PROXY` environment variable:
```bash
export HTTPS_PROXY=socks5://127.0.0.1:10806
gh api /repos/...
```

### yt-dlp
```bash
yt-dlp --proxy socks5://127.0.0.1:10806 ...
```

### Node.js / gh CLI
```bash
export HTTPS_PROXY=socks5://127.0.0.1:10806
gh api /repos/...
```

### Docker
```dockerfile
ENV HTTPS_PROXY=socks5://127.0.0.1:10806
```

## Verification
```bash
# Test proxy works
curl --proxy socks5://127.0.0.1:10806 https://api.github.com/repos/McDuck-S8/hermes-salon-landing
```

## Common Failures When Proxy Missing
- `curl: (7) Failed to connect to api.github.com port 443`
- `git push` hangs or fails with SSL error
- `requests.exceptions.ProxyError`
- `gh api` hangs indefinitely
# HTTP→SOCKS5 Bridge (scripts/http_to_socks_proxy.py)

## Purpose
Bypass httpcore's broken SOCKS5 transport in long-lived async processes (like Hermes gateway).

## How it works
- Listens on HTTP `127.0.0.1:10807` (configurable via `HTTP_PROXY_PORT`)
- Accepts HTTP CONNECT requests (what httpx sends for HTTPS URLs)
- Establishes SOCKS5 tunnel to `127.0.0.1:10806` (configurable via `SOCKS_PROXY_PORT`)
- Bridges raw TCP data bidirectionally using `select()` + threads
- TLS passthrough is transparent because it's raw bytes

## Usage
```bash
# Start bridge (background)
python scripts/http_to_socks_proxy.py &

# Or with custom ports
HTTP_PROXY_PORT=8118 SOCKS_PROXY_PORT=10806 python scripts/http_to_socks_proxy.py &
```

## Config
```yaml
# config.yaml — use HTTP proxy, not SOCKS5
telegram:
  proxy_url: "http://127.0.0.1:10807"
```

## Why raw sockets (not asyncio streams)?
Asyncio StreamReader reads ahead into internal buffers, which corrupts TLS ClientHello bytes when relaying through a tunnel. Raw socket.recv() + select() is byte-transparent.

## Dependencies
None — Python stdlib only (socket, select, struct, threading).

## Running as a service
Start before gateway. Gateway expects the bridge to be listening on port 10807.
If bridge dies, gateway will get RemoteProtocolError until bridge restarts.

# Money4Band Native 💰

Run multiple bandwidth-sharing apps for passive income — **without Docker**.

Pure Python, native processes, no containers needed.

## Supported Apps

| App | Status | How it works |
|-----|--------|-------------|
| Honeygain | ✅ Native runner | Share bandwidth → earn credits |
| EarnApp | ✅ Native runner | Share bandwidth → earn USD |
| PacketStream | ✅ Native runner | Sell bandwidth → earn USD |
| Pawns.app | ✅ Native runner | Share bandwidth → earn USD |
| Traffmonetizer | ✅ Native runner | Share traffic → earn crypto |
| Peer2Profit | ✅ Native runner | Share bandwidth → earn crypto |
| Bitping | ✅ Native runner | Share connection → earn crypto |
| Grass | 🔄 Coming soon | Browser extension |

## Quick Start

```bash
# Install dependencies
pip install pyyaml aiohttp

# Run setup wizard (enter your API tokens)
python cli.py setup

# Check status
python cli.py status

# Start all apps
python cli.py start

# Start with web dashboard
python cli.py dashboard
```

## Configuration

Edit `config.yaml`:

```yaml
apps:
  honeygain:
    enabled: true
    email: "your@email.com"
    password: "your-password"
    
  earnapp:
    enabled: true
    redeem_code: "your-redeem-code"

  # Optional: global proxy for all apps
global:
  proxy: socks5://127.0.0.1:1080
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `python cli.py status` | Show all apps status |
| `python cli.py start` | Start all enabled apps |
| `python cli.py start honeygain` | Start specific app |
| `python cli.py stop` | Stop all apps |
| `python cli.py setup` | Interactive setup wizard |
| `python cli.py dashboard` | Start web dashboard |

## Architecture

```
money4band-native/
├── config.yaml      # All configurations
├── cli.py           # CLI interface
├── manager.py       # Process orchestrator
├── runner.py        # Base app runner
├── apps.py          # Per-app runners
├── dashboard.py     # Web dashboard (aiohttp)
├── data/            # App data and logs
└── logs/            # Process logs
```

## Why Native?

- **No Docker overhead** — no VM, no daemon, no images
- **Direct access** — files, network, system resources
- **Lighter** — just Python + native binaries
- **Easier debugging** — logs in plain text, processes in task manager
- **Windows-friendly** — works natively on Windows without Docker Desktop

## How it Works

1. Each app runs as a native subprocess (or Python module)
2. Manager monitors health via process polling
3. Auto-restarts crashed apps
4. Web dashboard shows real-time status
5. All apps share the same config file

## License

MIT

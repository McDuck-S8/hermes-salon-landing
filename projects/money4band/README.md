# Bandwidth Sharing Launcher

A unified Python launcher for managing multiple bandwidth sharing applications on Windows without Docker.

## Overview

This tool helps you manage and monitor multiple bandwidth sharing apps that generate passive income by sharing your unused internet bandwidth. All apps run natively on Windows without requiring Docker.

## Supported Applications

| App | Status | Expected Earnings |
|-----|--------|-------------------|
| Honeygain | ✅ Supported | $5-10/month |
| EarnApp | ✅ Supported | $5-10/month |
| PacketStream | ✅ Supported | $0.50-2/month |
| Repocket | ✅ Supported | $1-3/month |
| Earnfm | ✅ Supported | $0.50-1/month |
| Bitping | ✅ Supported | $1-5/month |
| PacketShare | ✅ Supported | $0.30-1/month |
| IPRoyal Pawns | ✅ Supported | $0.50-2/month |
| Grass | ✅ Supported | Points (crypto) |

**Total Expected Monthly Earnings: $10-20/month (conservative)**

## Prerequisites

- Windows 10/11
- Python 3.7+ installed
- Stable internet connection
- Separate accounts for each bandwidth sharing service

## Installation

### 1. Install Bandwidth Sharing Apps

Download and install each app from their official websites:

- **Honeygain**: https://www.honeygain.com/download-app
- **EarnApp**: https://earnapp.com/
- **PacketStream**: https://app.packetstream.io
- **Repocket**: https://repocket.com/download-app
- **Earnfm**: https://earn.fm/download
- **Bitping**: https://bitping.com/earn
- **PacketShare**: https://www.packetshare.io
- **IPRoyal Pawns**: https://pawns.app/downloads
- **Grass**: https://www.grass.io/download

### 2. Configure the Launcher

Edit `launcher_config.json` to enable/disable specific apps:

```json
{
  "auto_start": true,
  "check_interval": 300,
  "apps_enabled": {
    "honeygain": true,
    "earnapp": true,
    "packetstream": true,
    "repocket": true,
    "earnfm": true,
    "bitping": true,
    "packetshare": true,
    "iproyal_pawns": true,
    "grass": true
  }
}
```

## Usage

### Command Line Interface

```bash
# Start all apps
python bandwidth_launcher.py start

# Start specific app
python bandwidth_launcher.py start honeygain

# Stop all apps
python bandwidth_launcher.py stop

# Stop specific app
python bandwidth_launcher.py stop earnapp

# Show status
python bandwidth_launcher.py status

# Monitor apps (auto-restart crashed apps)
python bandwidth_launcher.py monitor

# Show installation instructions
python bandwidth_launcher.py install
```

### Interactive Mode

Run without arguments for interactive menu:

```bash
python bandwidth_launcher.py
```

### Background Monitoring

To run the launcher in the background with auto-restart:

```bash
python bandwidth_launcher.py monitor
```

This will:
- Check every 5 minutes (configurable)
- Restart any crashed applications
- Log all activity to `bandwidth_launcher.log`

## Configuration

### launcher_config.json

| Setting | Description | Default |
|---------|-------------|---------|
| `auto_start` | Start apps automatically on launcher start | `true` |
| `check_interval` | Monitor check interval in seconds | `300` (5 min) |
| `log_level` | Logging level | `INFO` |
| `apps_enabled` | Enable/disable specific apps | All `true` |

### Custom App Paths

If apps are installed in non-standard locations, you can manually set the executable path in the launcher by modifying the `discover_apps()` method or by creating a custom config file.

## Logging

All activity is logged to:
- **Console**: Real-time output
- **File**: `bandwidth_launcher.log`

## Troubleshooting

### App Not Found

If the launcher can't find an app:
1. Check if the app is installed
2. Verify the executable name matches (e.g., `Honeygain.exe`)
3. Run `python bandwidth_launcher.py install` for download links

### App Won't Start

1. Check if the app is already running (use Task Manager)
2. Run the app manually first to complete initial setup
3. Check Windows Firewall settings
4. Verify internet connection

### High CPU/Memory Usage

1. Reduce the number of active apps
2. Increase `check_interval` in config
3. Use the `stop` command to pause specific apps

## Security Considerations

- All apps share bandwidth only, not personal data
- Use separate email accounts for each service
- Monitor network usage if on metered connection
- Consider using a dedicated device for maximum earnings

## Expected Earnings

### Conservative Estimate
- **Single device**: $10-15/month
- **Multiple devices**: $20-30/month

### Optimization Tips
1. Run apps 24/7 for maximum earnings
2. Use a stable, high-speed internet connection
3. Enable all apps for diverse income streams
4. Check for referral bonuses (many apps offer 10-25% of referrals' earnings)

## Files

- `bandwidth_launcher.py` - Main launcher script
- `launcher_config.json` - Configuration file
- `COMPARISON_TABLE.md` - Detailed app comparison
- `README.md` - This file
- `bandwidth_launcher.log` - Runtime logs (generated)

## License

MIT License - Free to use and modify.

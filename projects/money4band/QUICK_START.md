# Quick Start Guide - Bandwidth Sharing Launcher

## Step 1: Install Bandwidth Sharing Apps

Download and install these apps (all work natively on Windows):

### Must-Have (Highest Earnings)
1. **EarnApp** - https://earnapp.com/ (~$9/month)
2. **Honeygain** - https://www.honeygain.com/download-app (~$9/month)

### Recommended (Good Earnings)
3. **Bitping** - https://bitping.com/earn (~$1-5/month)
4. **Repocket** - https://repocket.com/download-app (~$1-3/month)

### Optional (Supplemental Income)
5. **PacketStream** - https://app.packetstream.io (~$0.50-2/month)
6. **IPRoyal Pawns** - https://pawns.app/downloads (~$0.50-2/month)
7. **Earnfm** - https://earn.fm/download (~$0.50-1/month)
8. **PacketShare** - https://www.packetshare.io (~$0.30-1/month)
9. **Grass** - https://www.grass.io/download (Points/crypto)

## Step 2: Create Accounts

For each app:
1. Visit the website
2. Sign up with email
3. Complete initial setup
4. Note your login credentials

## Step 3: Run the Launcher

### Option A: Using Batch File (Easiest)
Double-click `launcher.bat` in the project folder.

### Option B: Using Command Line
```bash
cd D:\Portable_Soft\hermes\projects\money4band
python bandwidth_launcher.py
```

### Option C: Using Python Directly
```bash
python bandwidth_launcher.py start    # Start all apps
python bandwidth_launcher.py status   # Check status
python bandwidth_launcher.py monitor  # Auto-restart crashed apps
```

## Step 4: Configure Auto-Start

To start apps automatically when Windows boots:

1. Press `Win + R`, type `shell:startup`, press Enter
2. Create a shortcut to `launcher.bat` in this folder
3. Right-click the shortcut, select Properties
4. Add arguments: `start monitor`

## Step 5: Monitor Earnings

### Check Status
```bash
python bandwidth_launcher.py status
```

### View Logs
Open `bandwidth_launcher.log` to see activity.

### Monitor Dashboard
Run in monitor mode to auto-restart crashed apps:
```bash
python bandwidth_launcher.py monitor
```

## Expected Earnings

| Scenario | Monthly Earnings |
|----------|------------------|
| Conservative (1 device) | $10-15 |
| Optimistic (1 device) | $20-30 |
| Multiple devices | $30-50+ |

## Tips for Maximum Earnings

1. **Run 24/7** - Keep apps running all the time
2. **Stable Internet** - Use reliable, high-speed connection
3. **Multiple Devices** - Use old phones/computers too
4. **Enable All Apps** - Diversify income streams
5. **Check Referrals** - Many apps offer 10-25% referral bonuses

## Troubleshooting

### App Not Starting
- Run the app manually first to complete setup
- Check Windows Firewall settings
- Verify internet connection

### Low Earnings
- Ensure apps are running 24/7
- Check if your region has high demand (US/EU best)
- Enable all available apps

### Launcher Not Finding Apps
- Use `python bandwidth_launcher.py install` for download links
- Manually set paths in `launcher_config.json`

## Files in This Project

- `bandwidth_launcher.py` - Main launcher script
- `launcher.bat` - Windows batch file for easy running
- `launcher_config.json` - Configuration file
- `COMPARISON_TABLE.md` - Detailed app comparison
- `QUICK_START.md` - This file
- `README.md` - Full documentation
- `bandwidth_launcher.log` - Runtime logs (generated)

## Need Help?

1. Check the `bandwidth_launcher.log` for errors
2. Run `python bandwidth_launcher.py status` to see what's running
3. Visit each app's website for app-specific support

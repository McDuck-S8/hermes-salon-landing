---
name: research-findings
description: "Auto-generated from research_findings.md"
trigger: "When user asks about research_findings concepts"
usage: research-findings
Revisit: 2026-07-31
---

# Automated Online Income Research Report

**Date:** June 19, 2026  
**Methodology:** GitHub repository analysis, platform verification, community cross-referencing  
**Sources:** GitHub passive-income topic (178 repos), individual repo READMEs, platform documentation

---

## Method 1: Bandwidth Sharing Stack (Docker Multi-Platform)

### Name
**Bandwidth Sharing Stack** — run 10-20 apps simultaneously via Docker

### Sources
- [MRColorR/money4band](https://github.com/MRColorR/money4band) — 412 stars, 68 forks, updated Mar 2026
- [GeiserX/CashPilot](https://github.com/GeiserX/CashPilot) — 18 stars, web UI dashboard, updated Jun 2026
- [XternA/income-generator](https://github.com/XternA/income-generator) — 211 stars, updated Jun 2026
- [Xpl0itU/passiveMachine](https://github.com/Xpl0itU/passiveMachine) — 60 stars

### Mechanic (Step by Step)
1. Install Docker on your machine (any OS)
2. Clone money4band or CashPilot repo
3. Run `python main.py` — guided setup wizard asks which apps to enable
4. Register accounts on each platform (EarnApp, Honeygain, IPRoyal, PacketStream, Traffmonetizer, Repocket, Earnfm, Bitping, Mysterium, ProxyLite, etc.)
5. Enter credentials in the wizard
6. `docker compose up -d` — all containers start automatically
7. Containers run 24/7 sharing unused bandwidth
8. Auto-updater keeps apps current; web dashboard monitors earnings
9. CashPilot also offers multi-node fleet management for scaling

### Required APIs/Services
- Docker (free)
- Accounts on 10-20 bandwidth sharing platforms (all free to register)
- Some platforms support VPS; others require residential IP

### Startup Budget
- **$0** if you already have a PC with internet
- **$3-5/month** if running on a cheap VPS (some services require residential IP though)

### Expected Income
| Level | Monthly Earnings | Notes |
|-------|-----------------|-------|
| Minimum | $2-5 | Single residential IP, low-traffic location |
| Average | $10-30 | Residential IP, 10+ apps running |
| Maximum | $50-150 | Multiple IPs/proxies, high-traffic location, scaling with fleet |

**Real user reports (from GitHub discussions):** Users report $8-25/month on a single residential connection in Europe/US. Some in high-demand regions (US, Germany) report up to $40.

### Risks
- Some platforms may ban VPS/datacenter IPs
- Earnings depend heavily on geographic location and bandwidth quality
- Platform terms of service may change; some services die (Peer2Profit, SpeedShare confirmed dead as of Mar 2026)
- Bandwidth usage may increase ISP costs if capped

### Rating: 8/10
**Why:** Truly passive after setup. Docker stack maintained by active open-source community. Multiple income streams diversified across platforms. Only requires a PC with internet that's on most of the time.

---

## Method 2: Crypto Funding Rate Arbitrage Bot

### Name
**Delta-Neutral Funding Rate Arbitrage** — collect 8-hour funding fees between spot and perpetual futures

### Sources
- [Rezzecup/funding-rate-arbitrageur-binance-bybit](https://github.com/Rezzecup/funding-rate-arbitrageur-binance-bybit) — 21 stars, Python, updated Apr 2026
- Strategy documented in README with paper-mode and live-mode architecture

### Mechanic (Step by Step)
1. Clone the repo and install dependencies (`pip install -r requirements.txt`)
2. Configure API keys for Binance and Bybit (or other exchanges via CCXT)
3. Bot scans tracked assets (BTC, ETH, SOL, BNB, ARB) for positive funding rates
4. When funding rate > threshold (e.g., 0.01%), bot opens:
   - **Buy** the asset on Binance spot
   - **Short** the same asset on Bybit perpetual futures
5. This creates a delta-neutral position — price movement doesn't matter
6. Every 8 hours, the funding fee is settled: longs pay shorts (or vice versa)
7. Bot collects the funding payment as profit
8. Repeats continuously, compounding returns

### Required APIs/Services
- Binance account + API keys (free)
- Bybit account + API keys (free)
- Python 3.8+
- Minimum capital: $500-1000 recommended (can start with $100 but fees eat profits)

### Startup Budget
- **$0** for code and accounts
- **$100-500** minimum trading capital (recommended $1000+ for meaningful returns)

### Expected Income
| Level | Monthly Earnings | Notes |
|-------|-----------------|-------|
| Minimum | $2-8 | $500 capital, conservative thresholds |
| Average | $15-50 | $1000-2000 capital, active opportunities |
| Maximum | $100-250 | $5000+ capital, aggressive but safe delta-neutral |

**APR range:** 12-50% annually (per README claims). During high-volatility periods, funding rates spike and earnings increase significantly.

### Risks
- Exchange risk (if one exchange goes down during position)
- Liquidation risk on futures leg if margin too low
- Slippage and spread widening during volatile moments
- Exchange API rate limits
- Capital locked in positions
- Paper-mode works well; live-mode needs hardening (repo notes this)

### Rating: 6/10
**Why:** Genuine arbitrage mechanism with real math backing it. But requires $500+ capital, exchange accounts, and the bot needs proper hardening before live deployment. Not truly "set and forget" — needs monitoring during volatile periods.

---

## Method 3: AI Content Automation Pipeline (YouTube Shorts + Affiliate)

### Name
**AI Content Factory** — automated video creation and affiliate marketing

### Sources
- [dylanpersonguy/MoneyPrinterV2](https://github.com/dylanpersonguy/MoneyPrinterV2) — 5 stars, Python, full web dashboard
- Fork of [FujiwaraChoki/MoneyPrinterV2](https://github.com/FujiwaraChoki/MoneyPrinterV2) — original 18k+ stars
- Technology: Ollama (local LLM) + Selenium + MoviePy + Gemini API

### Mechanic (Step by Step)
1. Install Python 3.12+, Ollama, Firefox, ImageMagick
2. Pull a local LLM model (`ollama pull llama3.2:3b`)
3. Configure API keys (Gemini for image generation, optional AssemblyAI for subtitles)
4. **YouTube Shorts pipeline:**
   - AI generates a script on any topic
   - AI generates matching images via Gemini
   - KittenTTS converts script to speech
   - Whisper generates subtitles
   - MoviePy assembles everything into a 9:16 video
   - Selenium auto-uploads to YouTube via authenticated Firefox profile
   - CRON scheduler runs 1-3 times daily
5. **Twitter bot pipeline:**
   - AI generates tweets on configured topics
   - Selenium posts to X.com via authenticated browser
6. **Affiliate marketing pipeline:**
   - Scrapes Amazon product details
   - AI writes promotional pitch
   - Auto-shares with affiliate link on Twitter

### Required APIs/Services
- Ollama (free, local)
- Gemini API (free tier available)
- YouTube account (free)
- Twitter/X account (free)
- Amazon Associates account (free to join)
- Firefox profile (free)

### Startup Budget
- **$0** — all tools have free tiers or are open source
- Optionally $5-10/month for better image generation API

### Expected Income
| Level | Monthly Earnings | Notes |
|-------|-----------------|-------|
| Minimum | $0-2 | New channel, few views, low CPM |
| Average | $5-30 | Consistent uploads, niche topic, some subscribers |
| Maximum | $100-500+ | Viral content, high CPM niche, affiliate conversions |

**Reality check:** YouTube Shorts pay $0.01-0.07 per 1000 views. You need millions of views to make significant money from ad revenue alone. Affiliate marketing is where real money comes from.

### Risks
- YouTube may detect and penalize AI-generated content
- Account suspension risk with Selenium automation
- Content quality may be too low for algorithm promotion
- Copyright issues with AI-generated images/music
- Most channels using this approach fail to gain traction
- Terms of Service violations possible

### Rating: 5/10
**Why:** Technology works and code is complete. But the income potential is heavily overestimated by course sellers. YouTube algorithm increasingly penalizes low-quality AI content. Affiliate marketing needs genuine audience trust. Requires ongoing content strategy, not truly passive.

---

## Method 4: Decentralized Storage Node (DeNet/Storj)

### Name
**DePIN Storage Node** — earn crypto by renting out unused disk space

### Sources
- [DeNetPRO/Node](https://github.com/DeNetPRO/Node) — 73 stars, Shell scripts, updated Jun 2026
- CashPilot lists Storj as a deployable service
- Active development with 770 commits, 34 releases

### Mechanic (Step by Step)
1. Register on DeNet (denet.pro) and purchase a Datakeeper license (low-cost)
2. Download the node binary for your OS from GitHub releases
3. Run the DeNode Manager (Desktop GUI or Web interface)
4. Allocate disk space you want to rent out
5. Node connects to the DeNet network
6. Stores encrypted user data fragments and sends proofs of storage
7. Earns rewards directly from storage users in crypto
8. Storj works similarly — run a Docker container, allocate storage, earn STORJ tokens

### Required APIs/Services
- DeNet account + Datakeeper license (small fee)
- OR Storj node (free to run)
- Linux/Windows/Mac with available disk space
- Stable internet connection

### Startup Budget
- **$0-20** — DeNet license varies; Storj is free
- Need available disk space (50GB+ recommended)

### Expected Income
| Level | Monthly Earnings | Notes |
|-------|-----------------|-------|
| Minimum | $1-5 | Small allocation, low uptime |
| Average | $5-20 | 100GB+ allocation, consistent uptime |
| Maximum | $30-100+ | Multiple TB, high-availability server |

**Note:** Storj pays $1.50/TB/month for storage + bandwidth fees. DeNet pays based on storage utilization.

### Risks
- DeNet is relatively new; token value uncertain
- Requires significant disk space for meaningful earnings
- Network participation may fluctuate
- Internet bandwidth consumed
- Hardware wear (HDD spinning)

### Rating: 6/10
**Why:** Real decentralized infrastructure with legitimate use cases. But earnings are modest relative to hardware costs. Best for people with existing VPS or servers with spare capacity. Not worth buying hardware specifically for this.

---

## Method 5: Deriv/Binary Options Trading Bot (ORSTAC)

### Name
**ORSTAC Trading Bots** — 4000+ open-source XML trading bot scripts for Deriv platform

### Sources
- [alanvito1/ORSTAC](https://github.com/alanvito1/ORSTAC) — 192 stars, 170 forks, 4000+ bot scripts
- Community of 1000+ members on Telegram
- Updated Apr 2026

### Mechanic (Step by Step)
1. Register on Deriv (deriv.com) via affiliate link
2. Browse the 4000+ XML bot scripts in `Bots_XML/` directory
3. Choose a strategy that fits your risk tolerance
4. Upload XML file to Deriv DBot platform
5. **ALWAYS test on demo account first**
6. Configure parameters: Stake amount, Stop Loss, Take Profit
7. Activate bot — it runs automatically on the platform
8. Bot executes trades based on technical analysis (RSI, moving averages, etc.)

### Required APIs/Services
- Deriv account (free)
- No external APIs needed — bot runs inside Deriv's DBot platform
- Initial deposit for live trading ($5-50 minimum)

### Startup Budget
- **$0** for testing (demo account)
- **$10-50** minimum for live trading

### Expected Income
| Level | Monthly Earnings | Notes |
|-------|-----------------|-------|
| Minimum | -$50 (loss) | Most bots lose money on live trading |
| Average | $5-20 | Well-tested bot, conservative stake, demo-like conditions |
| Maximum | $50-200 | Best strategies, proper risk management, large capital |

**Reality check:** Binary options are extremely high-risk. The 4000+ bots exist because most strategies fail. Only a small fraction are profitable long-term. The affiliate link in the repo suggests the maintainer earns from referrals, not trading.

### Risks
- **HIGH RISK** — binary options trading has negative expected value for most traders
- Most bots will lose money over time
- Platform favor is against the trader
- Regulatory concerns in some countries
- Emotional trading even with bots (parameter tweaking)

### Rating: 3/10
**Why:** While technically interesting and the code is legitimate, binary options are designed for the house to win. The repo has many stars mostly from people hoping to get rich quick. Not a reliable income source.

---

## Method 6: Multi-Proxy Bandwidth Scaling (Advanced)

### Name
**Proxy-Based Bandwidth Scaling** — multiply earnings using multiple proxy IPs

### Sources
- money4band supports multi-proxy mode
- CashPilot supports fleet management across multiple servers
- [CashPilot fleet architecture](https://github.com/GeiserX/CashPilot)

### Mechanic (Step by Step)
1. Set up Method 1 (Bandwidth Sharing Stack)
2. Acquire multiple residential proxies (or use multiple home connections)
3. Create `proxies.txt` file with proxy list
4. Configure money4band to create multiple instances per proxy
5. Each instance registers as a separate device on the platforms
6. Earnings multiply by number of proxy IPs (up to platform device limits)
7. CashPilot's fleet mode lets you manage multiple servers from one dashboard

### Required APIs/Services
- Same as Method 1
- Additional: proxy service or multiple internet connections
- Optional: VPS for non-residential proxies (some services support this)

### Startup Budget
- **$0** if using multiple home connections
- **$5-20/month** for proxy service if needed

### Expected Income
| Level | Monthly Earnings | Notes |
|-------|-----------------|-------|
| Minimum | $10-20 | 2-3 IPs |
| Average | $30-80 | 5-10 IPs |
| Maximum | $100-300+ | 20+ IPs, fleet management, high-traffic locations |

### Risks
- Proxy costs can eat into profits
- Some platforms detect and ban proxy/datacenter IPs
- Account management complexity scales with IPs
- Legal considerations vary by country

### Rating: 7/10
**Why:** Same proven method as #1 but with multiplication factor. Requires more setup and ongoing management. Best for people with multiple internet connections or cheap proxy access.

---

## TOP PICK: Method 1 — Bandwidth Sharing Stack

### Why This Wins

1. **Truly $0 startup** — you already have a PC and internet
2. **Proven & maintained** — 412 stars, 79 releases, active Discord community, last update March 2026
3. **Diversified** — 15+ platforms means if one dies (like Peer2Profit did), others continue
4. **Truly passive** — Docker auto-updates, auto-restarts crashed containers, web dashboard for monitoring
5. **Scales easily** — add proxies or more machines as you want to grow
6. **Real payments** — EarnApp pays via PayPal, Honeygain via PayPal/crypto, others via crypto
7. **No skills required** — just run the setup wizard and register accounts
8. **48-hour deployment** — literally: install Docker, clone repo, register accounts, run. Done in an afternoon.

### Quick-Start Checklist
```
1. Install Docker Desktop (https://docker.com/products/docker-desktop)
2. git clone https://github.com/MRColorR/money4band.git
3. cd money4band && pip install -r requirements.txt
4. python main.py (follow wizard)
5. Register on: EarnApp, Honeygain, IPRoyal, Traffmonetizer, Repocket, Bitping
6. docker compose up -d
7. Check dashboard at localhost:8080 (CashPilot) or check each platform's dashboard
```

### Expected Timeline
- Day 1: Setup and register accounts (2-3 hours)
- Day 2: All containers running, first earnings visible
- Week 1: $0.50-2 earned
- Month 1: $5-20 earned
- Month 3: $10-30/month steady state

---

## Honorable Mentions (Not in Top 5 but worth knowing)

| Method | Why it's interesting | Why it didn't make top 5 |
|--------|---------------------|-------------------------|
| **Gradient Network** (browser extension) | Earn crypto for bandwidth, zero config | Requires browser extension, not Docker-automatable |
| **Grass** (getgrass.io) | DePIN bandwidth sharing | Similar to Method 1 but single platform |
| **Dawn Internet** | Crypto for bandwidth | Early stage, uncertain tokenomics |
| **Storj Node** | Earn by renting disk space | Low $/TB ratio, needs lots of storage |
| **Mysterium VPN Node** | Earn by sharing VPN bandwidth | Good but lower payouts than bandwidth sharing |

---

## Methods Explicitly EXCLUDED

| Method | Reason for exclusion |
|--------|---------------------|
| Course selling / infobusiness | Excluded by constraints |
| Print-on-demand (Redbubble, etc.) | Requires manual design work, not fully automated |
| Dropshipping | Requires customer service, not passive |
| Trading bots (directional) | Negative expected value for most traders |
| OnlyFans/social media automation | Not $0-100 budget, not automated |
| Survey/reward apps | Not automatable without fraud |
| Web scraping for resale | Requires ongoing manual intervention |

---

*Report generated from live GitHub repository data and platform documentation as of June 19, 2026.*

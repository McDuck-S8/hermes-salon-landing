Usage: python scripts/arbitrage-router.py [options]

Options:
  --all              Best route per traffic source (default)
  --from <source>    All routes from one source (tiktok/youtube/telegram/reddit/pinterest/seo)
  --route <nodes>    Simulate specific path (e.g. --route tiktok carrd cpagrip tbank profit)
  --budget $         Budget in dollars (default: 100)

Examples:
  python scripts/arbitrage-router.py --all
  python scripts/arbitrage-router.py --from tiktok --budget 200
  python scripts/arbitrage-router.py --route tiktok carrd cpagrip kucoin-p2p tbank profit

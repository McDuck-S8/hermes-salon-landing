#!/usr/bin/env python
"""Test Headroom compression on Hermes conversation data."""

import sys
import json
from pathlib import Path

# Add headroom to path
sys.path.insert(0, "D:/Portable_Soft/hermes/tools/headroom")

try:
    from headroom import compress
    print("✅ Headroom imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Trying to install dependencies...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", "D:/Portable_Soft/hermes/tools/headroom"], capture_output=True)
    from headroom import compress
    print("✅ Headroom installed and imported")

# Test with sample conversation
messages = [
    {
        "role": "system",
        "content": "You are Hermes, an autonomous arbitrageur AI agent. You find price differences and execute trades."
    },
    {
        "role": "user",
        "content": "Найди арбитражные возможности на крипто биржах"
    },
    {
        "role": "assistant",
        "content": """I'll search for arbitrage opportunities across crypto exchanges.

Let me check prices on multiple exchanges:

1. Binance: BTC/USDT = $67,450.23
2. OKX: BTC/USDT = $67,512.45
3. Bybit: BTC/USDT = $67,389.12
4. Gate.io: BTC/USDT = $67,601.89

Analysis:
- Spread between lowest (Bybit) and highest (Gate.io): $212.77
- Percentage spread: 0.315%
- After fees (0.1% each side): 0.315% - 0.2% = 0.115% profit

Recommendation:
- Buy on Bybit at $67,389.12
- Sell on Gate.io at $67,601.89
- Profit per BTC: ~$77.12 after fees
- Risk: Price movement during transfer (10-30 minutes)

This is a valid arbitrage opportunity with positive expected value."""
    },
    {
        "role": "user",
        "content": "Сделай это"
    }
]

# Compress
print("\n📊 Compressing conversation...")
result = compress(messages, model="gpt-4o")

print(f"\n📈 Results:")
print(f"  Original tokens: ~{sum(len(m['content'].split()) * 1.3 for m in messages):.0f}")
print(f"  Compression ratio: {result.compression_ratio:.2%}")
print(f"  Tokens saved: {result.tokens_saved}")

print(f"\n📄 Compressed messages:")
for i, msg in enumerate(result.messages):
    content = msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content']
    print(f"  [{i}] {msg['role']}: {content[:100]}...")

print("\n✅ Test complete!")

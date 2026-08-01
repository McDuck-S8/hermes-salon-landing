#!/usr/bin/env python3
"""
Crypto Price Monitor — проверяет цены через бесплатные API
Показывает: цену, изменение за 24ч, разницу между биржами

Использование:
    python price_monitor.py                # все монеты
    python price_monitor.py BTC ETH SOL    # конкретные монеты
    python price_monitor.py --arb          # поиск арбитражных возможностей
"""

import sys
import json
import urllib.request
import urllib.error
from datetime import datetime


# Free APIs (no key required)
COINGECKO_API = "https://api.coingecko.com/api/v3"
BINANCE_API = "https://api.binance.com/api/v3"


def get_coingecko_prices(coins: list) -> dict:
    """Get prices from CoinGecko."""
    ids = ",".join(coins)
    url = f"{COINGECKO_API}/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"CoinGecko error: {e}")
        return {}


def get_binance_prices(symbols: list) -> dict:
    """Get prices from Binance."""
    results = {}
    for sym in symbols:
        url = f"{BINANCE_API}/ticker/24hr?symbol={sym}USDT"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                results[sym] = {
                    "price": float(data["lastPrice"]),
                    "change_24h": float(data["priceChangePercent"]),
                    "volume": float(data["volume"]),
                    "high": float(data["highPrice"]),
                    "low": float(data["lowPrice"])
                }
        except Exception as e:
            print(f"Binance error for {sym}: {e}")
    return results


def check_arbitrage机会(coins: list):
    """Check for price differences between exchanges."""
    print("\n🔍 ПРОВЕРКА АРБИТРАЖНЫХ ВОЗМОЖНОСТЕЙ")
    print("=" * 60)
    
    # Get Binance prices
    binance = get_binance_prices([c.upper() for c in coins])
    
    # Get CoinGecko prices
    cg_ids = {
        "btc": "bitcoin", "eth": "ethereum", "sol": "solana",
        "xrp": "ripple", "doge": "dogecoin", "ada": "cardano",
        "dot": "polkadot", "avax": "avalanche-2", "matic": "matic-network"
    }
    cg_names = [cg_ids.get(c.lower(), c.lower()) for c in coins]
    coingecko = get_coingecko_prices(cg_names)
    
    print(f"\n{'Монета':<8} {'Binance':>12} {'CoinGecko':>12} {'Разница':>10} {'Статус':<10}")
    print("-" * 55)
    
    for coin in coins:
        sym = coin.upper()
        cg_name = cg_ids.get(coin.lower(), coin.lower())
        
        b_price = binance.get(sym, {}).get("price", 0)
        cg_price = coingecko.get(cg_name, {}).get("usd", 0)
        
        if b_price and cg_price:
            diff = abs(b_price - cg_price) / max(b_price, cg_price) * 100
            
            if diff > 1:
                status = "🔥 АРБИТРАЖ"
            elif diff > 0.5:
                status = "⚠️  СЛЕДИТЬ"
            else:
                status = "✅ НОРМА"
            
            print(f"{sym:<8} ${b_price:>10,.2f} ${cg_price:>10,.2f} {diff:>8.2f}% {status}")
        else:
            print(f"{sym:<8} {'н/д':>12} {'н/д':>12} {'н/д':>10} ❌ НЕТ ДАННЫХ")
    
    print("\n💡 Арбитраж = разница > 1% после учёта комиссий (~0.1-0.2%)")
    print("   На практике: разница > 2% = реальная возможность")


def main():
    # Default coins
    default_coins = ["btc", "eth", "sol", "xrp", "doge"]
    
    args = sys.argv[1:]
    
    if "--arb" in args:
        coins = [a for a in args if a != "--arb"]
        if not coins:
            coins = default_coins
        check_arbitrage机会(coins)
        return
    
    if args:
        coins = [a.lower() for a in args if not a.startswith("-")]
    else:
        coins = default_coins
    
    print("=" * 60)
    print(f"  📊 CRYPTO PRICE MONITOR — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # Get prices from both sources
    cg_ids = {
        "btc": "bitcoin", "eth": "ethereum", "sol": "solana",
        "xrp": "ripple", "doge": "dogecoin", "ada": "cardano",
        "dot": "polkadot", "avax": "avalanche-2", "matic": "matic-network"
    }
    
    cg_names = [cg_ids.get(c, c) for c in coins]
    coingecko = get_coingecko_prices(cg_names)
    binance = get_binance_prices([c.upper() for c in coins])
    
    print(f"\n{'Монета':<8} {'Цена':>12} {'Изм. 24ч':>10} {'Объём 24ч':>15} {'Источник':<10}")
    print("-" * 60)
    
    for coin in coins:
        sym = coin.upper()
        cg_name = cg_ids.get(coin, coin)
        
        # Prefer Binance (more accurate), fallback to CoinGecko
        if sym in binance:
            b = binance[sym]
            price = b["price"]
            change = b["change_24h"]
            vol = b["volume"]
            src = "Binance"
        elif cg_name in coingecko:
            cg = coingecko[cg_name]
            price = cg["usd"]
            change = cg.get("usd_24h_change", 0)
            vol = cg.get("usd_24h_vol", 0)
            src = "CoinGecko"
        else:
            print(f"{sym:<8} {'н/д':>12} {'н/д':>10} {'н/д':>15} ❌ НЕТ ДАННЫХ")
            continue
        
        # Format volume
        if vol > 1e9:
            vol_str = f"${vol/1e9:.1f}B"
        elif vol > 1e6:
            vol_str = f"${vol/1e6:.1f}M"
        elif vol > 1e3:
            vol_str = f"${vol/1e3:.1f}K"
        else:
            vol_str = f"${vol:.0f}"
        
        # Change indicator
        if change > 5:
            chg = f"🟢 +{change:.1f}%"
        elif change > 0:
            chg = f"🟢 +{change:.1f}%"
        elif change > -5:
            chg = f"🔴 {change:.1f}%"
        else:
            chg = f"🔴 {change:.1f}%"
        
        print(f"{sym:<8} ${price:>10,.2f} {chg:>10} {vol_str:>15} {src:<10}")
    
    print(f"\n💰 Данные на: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💡 Для арбитража: python price_monitor.py --arb")


if __name__ == "__main__":
    main()

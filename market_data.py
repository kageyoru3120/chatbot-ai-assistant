import requests
from datetime import datetime

# ============================================
# COINGECKO API - GRATIS, NO API KEY NEEDED
# ============================================

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

def get_crypto_price(coin_id="bitcoin", vs_currency="usd"):
    """Ambil harga real-time crypto dari CoinGecko"""
    try:
        url = f"{COINGECKO_BASE}/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": vs_currency,
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true",
            "include_last_updated_at": "true"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if coin_id not in data:
            return {"error": f"Coin '{coin_id}' tidak ditemukan"}
        
        coin_data = data[coin_id]
        
        return {
            "coin_id": coin_id,
            "symbol": coin_id.upper(),
            "price": coin_data.get(f"{vs_currency}", 0),
            "change_24h": coin_data.get(f"{vs_currency}_24h_change", 0),
            "volume_24h": coin_data.get(f"{vs_currency}_24h_vol", 0),
            "market_cap": coin_data.get(f"{vs_currency}_market_cap", 0),
            "last_updated": datetime.now().isoformat(),
            "source": "CoinGecko"
        }
        
    except Exception as e:
        return {"error": str(e)}

def get_trending_coins():
    """Ambil 7 coin yang lagi trending"""
    try:
        url = f"{COINGECKO_BASE}/search/trending"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        trending = []
        for coin in data.get("coins", [])[:7]:
            item = coin.get("item", {})
            trending.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "symbol": item.get("symbol"),
                "market_cap_rank": item.get("market_cap_rank"),
                "thumb": item.get("thumb")
            })
        
        return trending
        
    except Exception as e:
        return {"error": str(e)}

def get_coin_list():
    """Daftar coin populer yang tersedia"""
    return {
        "Bitcoin": "bitcoin",
        "Ethereum": "ethereum",
        "Solana": "solana",
        "BNB": "binancecoin",
        "XRP": "ripple",
        "Cardano": "cardano",
        "Dogecoin": "dogecoin",
        "Avalanche": "avalanche-2",
        "Chainlink": "chainlink",
        "Polygon": "matic-network",
        "Litecoin": "litecoin",
        "Polkadot": "polkadot",
        "TRON": "tron",
        "Uniswap": "uniswap",
        "Shiba Inu": "shiba-inu"
    }

def get_coin_ohlc(coin_id="bitcoin", vs_currency="usd", days=7):
    """Ambil data OHLC untuk chart (7 hari terakhir)"""
    try:
        url = f"{COINGECKO_BASE}/coins/{coin_id}/ohlc"
        params = {
            "vs_currency": vs_currency,
            "days": days
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if isinstance(data, dict) and "error" in data:
            return {"error": data["error"]}
        
        # Format: [timestamp, open, high, low, close]
        return data
        
    except Exception as e:
        return {"error": str(e)}

# ============================================
# CONTOH PENGGUNAAN
# ============================================
if __name__ == "__main__":
    # Test ambil harga BTC
    print("=== Harga Bitcoin ===")
    result = get_crypto_price("bitcoin")
    print(result)
    
    print("\n=== Trending Coins ===")
    trending = get_trending_coins()
    print(trending)
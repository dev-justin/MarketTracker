import requests

def get_crypto_prices(symbols):
    """
    Get current prices for specified crypto symbols using CoinGecko API
    """
    # CoinGecko uses lowercase IDs
    symbol_mapping = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'DOGE': 'dogecoin'
    }
    
    prices = {}
    base_url = "https://api.coingecko.com/api/v3"
    
    try:
        for symbol in symbols:
            coin_id = symbol_mapping.get(symbol)
            if not coin_id:
                continue
                
            response = requests.get(
                f"{base_url}/simple/price",
                params={
                    "ids": coin_id,
                    "vs_currencies": "usd"
                }
            )
            response.raise_for_status()
            data = response.json()
            prices[symbol] = data[coin_id]["usd"]
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching prices: {e}")
        return {}
        
    return prices 
import ccxt

def get_crypto_prices(symbols):
    """
    Get current prices for specified crypto symbols
    """
    exchange = ccxt.binance()
    prices = {}
    
    for symbol in symbols:
        ticker = exchange.fetch_ticker(f"{symbol}/USDT")
        prices[symbol] = ticker['last']
    
    return prices 
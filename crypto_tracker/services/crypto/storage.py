import json
from config.settings import AppConfig


class CryptoStorage:

    def __init__(self):
        self.coins = []

    def add_coin(self, coin):
        """Add a coin (id, name, image, is_favorite) to the storage."""
        with open(AppConfig.CRYPTO_STORAGE_FILE, 'w') as f:
            json.dump(coin, f)


    def get_coins(self):
        return self.coins
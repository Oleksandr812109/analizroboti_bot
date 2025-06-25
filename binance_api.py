from binance.client import Client
import logging

logger = logging.getLogger(__name__)

class BinanceAPI:
    def __init__(self, api_key, api_secret, testnet=True):
        """
        Клас для роботи з Binance API (Futures).
        Args:
            api_key (str): Ваш API ключ Binance.
            api_secret (str): Ваш секретний ключ Binance.
            testnet (bool): Використовувати testnet чи основну мережу.
        """
        self.client = Client(api_key, api_secret)
        if testnet:
            self.client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"
        logger.info(f"BinanceAPI ініціалізовано (testnet={testnet})")

    def get_futures_filled_orders(self, symbol=None):
        """
        Отримати закриті (filled) ордери на Binance Futures.

        Args:
            symbol (str, optional): Тікер торгової пари, наприклад 'BTCUSDT'. Якщо None, повертає всі угоди.

        Returns:
            list: Список словників з інформацією про угоди.
        """
        try:
            if symbol:
                orders = self.client.futures_account_trades(symbol=symbol)
            else:
                orders = self.client.futures_account_trades()
            logger.info(f"Знайдено {len(orders)} ордер(ів) на Binance Futures.")
            return orders
        except Exception as e:
            logger.error(f"Помилка при отриманні ордерів з Binance: {e}", exc_info=True)
            return []

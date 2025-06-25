import os
import logging

def load_config():
    # Читання з .env або змінних середовища
    return {
        "BINANCE_API_KEY": os.environ.get("BINANCE_API_KEY", ""),
        "BINANCE_API_SECRET": os.environ.get("BINANCE_API_SECRET", ""),
    }

# Рівень логування (можна через змінну оточення LOG_LEVEL)
LOG_LEVEL = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)

# Прапорець для тестової мережі (Binance Futures Testnet)
USE_TESTNET = os.environ.get("BINANCE_USE_TESTNET", "1") == "1"  # За замовчуванням True (1)

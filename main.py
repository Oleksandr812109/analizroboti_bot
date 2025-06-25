from config import load_config, LOG_LEVEL, USE_TESTNET
from binance_api import BinanceAPI
from data_processor import process_orders
from excel_exporter import export_to_excel
import logging
import os
from datetime import datetime

def setup_logging():
    if not os.path.exists("logs"):
        os.makedirs("logs")
    log_filename = f"logs/bot_{datetime.now().strftime('%Y-%m-%d')}.log"
    logging.basicConfig(
        filename=log_filename,
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)s: %(message)s",
    )
    # Логи також у консоль
    console = logging.StreamHandler()
    console.setLevel(LOG_LEVEL)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    # Мінімум логів від сторонніх бібліотек
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("binance").setLevel(logging.WARNING)

def main():
    setup_logging()
    logging.info("Binance Futures Order Tracker: запуск...")

    # 1. Завантаження конфігурації
    config = load_config()
    api_key = config.get("BINANCE_API_KEY")
    api_secret = config.get("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        logging.critical("API_KEY або API_SECRET не знайдено в конфігурації. Перевірте config.py або .env.")
        return

    # 2. Ініціалізація Binance API (з урахуванням testnet)
    try:
        binance = BinanceAPI(api_key, api_secret, testnet=USE_TESTNET)
        logging.info(f"Binance API ініціалізовано (testnet={USE_TESTNET})")
    except Exception as e:
        logging.critical(f"Помилка ініціалізації Binance API: {e}")
        return

    # 3. Збір даних про ордери та позиції
    try:
        logging.info("Збір історії ф'ючерсних угод...")
        orders = binance.get_futures_filled_orders()
    except Exception as e:
        logging.error(f"Помилка при отриманні історії угод: {e}")
        return

    try:
        logging.info("Збір відкритих позицій...")
        positions = binance.get_futures_open_positions()
    except Exception as e:
        logging.error(f"Помилка при отриманні позицій: {e}")
        return

    # 4. Перевірка наявності даних
    if not orders and not positions:
        logging.warning("Немає даних для обробки: не знайдено ні ордерів, ні позицій.")
        return
    if not orders:
        logging.info("Не знайдено виконаних ордерів (filled orders).")
    if not positions:
        logging.info("Не знайдено відкритих позицій.")

    # 5. Обробка даних
    processed_data = process_orders(orders, positions)
    if not processed_data:
        logging.warning("Після обробки немає даних для експорту. Завершення роботи.")
        return

    # 6. Експорт у Excel
    filename = f"Binance_Futures_Trades_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    try:
        export_to_excel(processed_data, filename)
        logging.info(f"Звіт збережено у {filename}")
    except Exception as e:
        logging.error(f"Помилка при експорті у Excel: {e}")

if __name__ == "__main__":
    main()

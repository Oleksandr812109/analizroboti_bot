import logging
from binance_api import BinanceAPI
from data_processor import process_orders
from excel_exporter import export_to_excel
from google_sheets_exporter import export_to_gsheets

def main():
    # 1. Налаштування логування
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # 2. Введіть свої ключі Binance API
    api_key = "d819d92b03fa3d8c61ff4c4835908ec4afde53fc64ac6df6235c5b332fbef930"
    api_secret = "007055837e544dfb38e99582a2b00626164602a168aa939eb5943adb293bf727"
    use_testnet = True  # Змініть на False для реального акаунту

    # 3. Параметри експорту
    export_to_excel_flag = True
    export_to_gsheets_flag = False

    excel_filename = "Futures_Trades_Report.xlsx"
    excel_sheet_name = "Futures Trades Report"

    gsheets_spreadsheet_name = "Binance Futures Trades"  # Назва Google таблиці
    gsheets_worksheet_name = "Futures Trades Report"
    gsheets_creds_path = "service_account.json"

    # 4. Ініціалізація Binance API
    binance = BinanceAPI(api_key, api_secret, testnet=use_testnet)

    # 5. Отримати закриті угоди (userTrades)
    orders = binance.get_futures_filled_orders()
    if not orders:
        logging.info("Не знайдено жодної угоди для обробки.")
        return

    # 6. Обробити дані
    processed_df = process_orders(orders)

    # 7. Експорт у Excel
    if export_to_excel_flag:
        export_to_excel(processed_df, excel_filename, sheet_name=excel_sheet_name)

    # 8. Експорт у Google Sheets
    if export_to_gsheets_flag:
        try:
            export_to_gsheets(
                processed_df,
                spreadsheet_name=gsheets_spreadsheet_name,
                worksheet_name=gsheets_worksheet_name,
                creds_json_path=gsheets_creds_path,
                clear_existing_data=True
            )
        except Exception as e:
            logging.error("Помилка при експорті у Google Sheets. Перевірте логи для деталей.")

    logging.info("Завершено!")

if __name__ == "__main__":
    main()

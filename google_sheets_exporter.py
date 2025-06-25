import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
import logging

def export_to_gsheets(
    data_frame: pd.DataFrame,
    spreadsheet_name: str,
    worksheet_name: str = "Futures Trades Report",
    creds_json_path: str = "service_account.json",
    clear_existing_data: bool = True
):
    """
    Експортує DataFrame у Google Sheets.

    Args:
        data_frame (pd.DataFrame): Дані для експорту.
        spreadsheet_name (str): Назва Google Sheets документа (має вже існувати).
        worksheet_name (str): Назва листа у таблиці (буде створено, якщо не існує).
        creds_json_path (str): Шлях до JSON-файлу з ключами сервісного акаунта.
            (Докладніше: створіть сервісний акаунт через Google Cloud Console,
            активуйте Google Sheets API, додайте credentials файл, і додайте email сервісного акаунта 
            як редактора до Google таблиці.)
        clear_existing_data (bool): Якщо True — очистити аркуш перед експортом.
    """
    if data_frame.empty:
        logging.warning("DataFrame порожній. Нічого експортувати в Google Sheets.")
        return

    try:
        gc = gspread.service_account(filename=creds_json_path)
        sh = gc.open(spreadsheet_name)

        try:
            worksheet = sh.worksheet(worksheet_name)
            if clear_existing_data:
                worksheet.clear()
                logging.info(f"Очищено існуючий лист '{worksheet_name}'.")
        except gspread.exceptions.WorksheetNotFound:
            num_rows = data_frame.shape[0] + 1  # +1 для заголовка
            num_cols = data_frame.shape[1]
            worksheet = sh.add_worksheet(
                title=worksheet_name, 
                rows=num_rows + 10,  # запас
                cols=num_cols + 5    # запас
            )
            logging.info(f"Створено новий лист '{worksheet_name}' з розміром {num_rows+10}x{num_cols+5}.")

        set_with_dataframe(worksheet, data_frame, include_index=False)
        logging.info(f"Дані успішно експортовані до Google Sheets: '{spreadsheet_name}' / '{worksheet_name}'")

    except gspread.exceptions.SpreadsheetNotFound:
        logging.error(f"Google Sheets документ '{spreadsheet_name}' не знайдено. Перевірте назву та дозволи.")
        raise
    except gspread.exceptions.APIError as e:
        logging.error(f"Помилка API Google Sheets: {e.args[0]}. Перевірте дозволи сервісного акаунта або ліміти API.", exc_info=True)
        raise
    except Exception as e:
        logging.error(f"Непередбачена помилка експорту до Google Sheets: {e}", exc_info=True)
        raise

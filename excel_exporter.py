import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

def export_to_excel(data_frame: pd.DataFrame, filename: str, sheet_name: str = "Futures Trades Report"):
    """
    Експортує DataFrame з обробленими даними в Excel-файл.

    Args:
        data_frame (pd.DataFrame): DataFrame, що містить дані для експорту.
        filename (str): Назва Excel-файлу для збереження (наприклад, "report.xlsx").
        sheet_name (str): Назва листа в Excel-файлі.
    """
    if data_frame.empty:
        logger.warning("DataFrame порожній. Нічого експортувати в Excel.")
        return

    try:
        # Перевірка та створення директорії для збереження звітів
        output_dir = "reports"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Створено директорію для звітів: {output_dir}")

        full_path = os.path.join(output_dir, filename)

        # Експорт DataFrame у Excel
        with pd.ExcelWriter(full_path, engine="openpyxl") as writer:
            data_frame.to_excel(writer, sheet_name=sheet_name, index=False)

            # Автоматично підлаштовуємо ширину колонок під вміст (опціонально)
            worksheet = writer.sheets[sheet_name]
            for idx, col in enumerate(data_frame.columns, 1):
                max_len = max(
                    data_frame[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2  # Додаємо запас
                worksheet.column_dimensions[chr(64 + idx)].width = max_len

        logger.info(f"Дані успішно експортовані до {full_path}")

    except PermissionError:
        logger.error(f"Відмова у доступі: Неможливо записати файл {full_path}. Перевірте дозволи.")
        raise
    except IOError as e:
        logger.error(f"Помилка вводу/виводу під час запису файлу {full_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Непередбачена помилка під час експорту в Excel: {e}", exc_info=True)
        raise

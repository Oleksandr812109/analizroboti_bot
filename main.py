import logging
from binance_api import BinanceAPI
from data_processor import process_orders
from excel_exporter import export_to_excel
from google_sheets_exporter import export_to_gsheets

import os
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.message import EmailMessage
import time

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ======= НАЛАШТУВАННЯ =======

# Email config (заповніть свої значення!)
FROM_EMAIL = "your@gmail.com"  # Gmail-відправник
APP_PASSWORD = "your_app_password"  # App password Gmail
TO_EMAIL = "oleksandr.agro81@gmail.com"  # Отримувач

# Звіт
EXCEL_FILENAME = "Futures_Trades_Report.xlsx"
EXCEL_SHEET_NAME = "Futures Trades Report"
REPORT_PATH = os.path.join(os.getcwd(), EXCEL_FILENAME)

# Binance API ключі (заповніть свої значення!)
API_KEY = "d819d92b03fa3d8c61ff4c4835908ec4afde53fc64ac6df6235c5b332fbef930"
API_SECRET = "007055837e544dfb38e99582a2b00626164602a168aa939eb5943adb293bf727"
USE_TESTNET = True

# Google Sheets (не змінюйте якщо не використовуєте)
EXPORT_TO_GSHEETS_FLAG = False
GSHEETS_SPREADSHEET_NAME = "Binance Futures Trades"
GSHEETS_WORKSHEET_NAME = "Futures Trades Report"
GSHEETS_CREDS_PATH = "service_account.json"

# Telegram бот
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"  # <-- Вставте свій токен

# ============================

def generate_report():
    logging.info("Генерація звіту...")
    binance = BinanceAPI(API_KEY, API_SECRET, testnet=USE_TESTNET)
    orders = binance.get_futures_filled_orders()
    if not orders:
        logging.info("Не знайдено жодної угоди для обробки.")
        return None
    processed_df = process_orders(orders)
    export_to_excel(processed_df, EXCEL_FILENAME, sheet_name=EXCEL_SHEET_NAME)
    if EXPORT_TO_GSHEETS_FLAG:
        try:
            export_to_gsheets(
                processed_df,
                spreadsheet_name=GSHEETS_SPREADSHEET_NAME,
                worksheet_name=GSHEETS_WORKSHEET_NAME,
                creds_json_path=GSHEETS_CREDS_PATH,
                clear_existing_data=True
            )
        except Exception as e:
            logging.error("Помилка при експорті у Google Sheets: %s", e)
    logging.info("Звіт збережено у %s", EXCEL_FILENAME)
    return REPORT_PATH

def send_report_email(report_path, from_email, app_password, to_email):
    logging.info("Відправляю звіт на пошту %s", to_email)
    msg = EmailMessage()
    msg["Subject"] = "Щоденний звіт Binance Futures"
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content("Доброго дня! У вкладенні щоденний звіт.")

    with open(report_path, "rb") as f:
        file_data = f.read()
        filename = os.path.basename(report_path)
        msg.add_attachment(
            file_data,
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_email, app_password)
        smtp.send_message(msg)
    logging.info("Звіт відправлено на пошту!")

def scheduled_job():
    logging.info("Виконую планове надсилання звіту...")
    report_path = generate_report()
    if report_path:
        send_report_email(report_path, FROM_EMAIL, APP_PASSWORD, TO_EMAIL)
    else:
        logging.info("Звіт не згенеровано, email не відправлено.")

async def send_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Запит на відправку звіту вручну через Telegram...")
    report_path = generate_report()
    if report_path:
        try:
            send_report_email(report_path, FROM_EMAIL, APP_PASSWORD, TO_EMAIL)
            await update.message.reply_text("Звіт відправлено на пошту!")
        except Exception as e:
            await update.message.reply_text(f"Помилка при надсиланні email: {e}")
    else:
        await update.message.reply_text("Виникла помилка: не вдалося згенерувати звіт.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_job, "cron", hour=8, minute=0)
    scheduler.start()
    logging.info("Планувальник для щоденного звіту запущено.")

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Запуск планувальника
    start_scheduler()

    # Запуск Telegram-бота
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("send_report", send_report_command))
    logging.info("Telegram-бот запущений та чекає команду /send_report")
    app.run_polling()

    # Основний цикл (залишаємо, якщо потрібно ще щось у фоновому режимі)
    # while True:
    #     time.sleep(60)

if __name__ == "__main__":
    main()

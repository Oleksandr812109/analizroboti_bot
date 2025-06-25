import smtplib
from email.message import EmailMessage
import os

def send_report_email(report_path, from_email, app_password, to_email):
    msg = EmailMessage()
    msg['Subject'] = 'Щоденний звіт'
    msg['From'] = from_email
    msg['To'] = to_email
    msg.set_content('Доброго дня! У вкладенні щоденний звіт.')

    # Вкладення
    with open(report_path, 'rb') as f:
        file_data = f.read()
        filename = os.path.basename(report_path)
        msg.add_attachment(
            file_data,
            maintype='application',
            subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=filename
        )

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(from_email, app_password)
        smtp.send_message(msg)

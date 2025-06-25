from apscheduler.schedulers.background import BackgroundScheduler
from email_utils import send_report_email

def start_scheduler(from_email, app_password, to_email, report_path):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_report_email,
        'cron',
        hour=8,
        minute=0,
        args=[report_path, from_email, app_password, to_email]
    )
    scheduler.start()
    return scheduler

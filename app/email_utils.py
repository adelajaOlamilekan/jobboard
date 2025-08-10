from fastapi import BackgroundTasks
from .config import settings
import smtplib
from email.message import EmailMessage

def send_email_sync(to_email: str, subject: str, html_content: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg.set_content(html_content, subtype="html")
    # simple SMTP - replace with SendGrid or other provider in prod
    if not settings.SMTP_HOST:
        print("SMTP not configured, email content:", html_content)
        return
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
        s.starttls()
        s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        s.send_message(msg)

def send_email_background(background_tasks: BackgroundTasks, to_email: str, subject: str, html_content: str):
    background_tasks.add_task(send_email_sync, to_email, subject, html_content)

import smtplib
from credentials import password, sender_email
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from models import models
from time import time


def send_email(subject, body, sender, user_addr, password) -> None:
    '''
    Sends email from sender account to user address via gmail using SMTP connection.
    '''
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = user_addr
    smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, user_addr, msg.as_string())
    smtp_server.quit()


def check_deadlines() -> None:
    '''
    Query returing all tasks with deadlines in the next 24 hours that havent had reminders send and sends them.
    '''
    tomorrow = datetime.now() + timedelta(days=1)
    for task in models.session.query(models.Task).filter((models.Task.deadline.isnot(None)) & (models.Task.deadline <= tomorrow) & (models.Task.reminder_sent == False)):
        deadline = task.deadline.strftime("%d/%m/%Y")
        subject = "A gentle reminder"
        body = f"This is a gentle reminder that on {deadline} you have the task with the description: '{task.description}',\nwhich is tomorrow!"
        user = models.session.query(models.User).filter(models.User.id == task.user_id).all()[0]
        send_success = send_email(subject=subject, body=body, sender=sender_email, user_addr=user.user_email, password=password)
        if send_success:
            task.reminder_sent = True
            models.session.commit()
            logger(task_id=task.id, success="sent")
        logger(task_id=task.id, success="error")


def logger(task_id, success) -> None:
    '''
    Logs whenever an email reminder is sent.
    '''
    timestamp = int(time() * 1000000)
    data_to_log = f'{timestamp} : {success} : {task_id}\n'
    with open(f"/var/log/{datetime.today().strftime('%Y-%m-%d')}-draft_log.txt", "a") as log_file:
        log_file.write(data_to_log)


if __name__ == "__main__":
    check_deadlines()
from datetime import datetime, timedelta
from draft_manager import DraftManager
from models import models
from time import time


draft_manager = DraftManager()


def check_deadlines():
    '''
    Query returing all tasks with deadlines in the next 24 hours that havent had reminders send and sends them.
    '''
    tomorrow = datetime.now() + timedelta(days=1)
    for task in models.session.query(models.Task).filter((models.Task.deadline.isnot(None)) & (models.Task.deadline <= tomorrow) & (models.Task.draft_sent == False)):
        send_success = DraftManager.send_draft(task.draft_id)
        if send_success:
            task.draft_sent = True
            models.session.commit()
            logger(task_id=task.task_id, draft_id=task.draft_id, success="sent")
        logger(task_id=task.task_id, draft_id=task.draft_id, success="error")


def logger(task_id, draft_id, success):
    '''
    Logs whenever a draft is sent as an email.
    '''
    timestamp = int(time() * 1000000)
    data_to_log = f'{timestamp} : {success} : {task_id} : {draft_id}\n'
    with open(f'/var/log/{datetime.today().strftime("%Y-%m-%d")}-draft_log.txt', 'a') as log_file:
        log_file.write(data_to_log)


if __name__ == "__main__":
    check_deadlines()

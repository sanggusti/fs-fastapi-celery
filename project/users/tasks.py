import random
from celery import shared_task
import requests

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def divide(x, y):
    # from celery.contrib import rdb

    # rdb.set_trace()

    import time

    time.sleep(4)
    return x / y


@shared_task
def sample_task(email):
    from project.users.views import api_call

    api_call(email)


@shared_task(bind=True)
def task_process_notification(self):
    try:
        if not random.choice([0, 1]):
            # mimic random error
            raise Exception()

        #  block the I/O
        requests.post("https://httpbin.org/delay/5")
    except Exception as e:
        logger.error("exception raised, it would be retry after 5 seconds")
        raise self.retry(exc=e, countdown=5)

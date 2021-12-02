import random
import requests
import logging

from asgiref.sync import async_to_sync
from celery import shared_task
from celery.utils.log import get_task_logger
from celery.signals import task_postrun, after_setup_logger
from celery.utils.log import get_task_logger
from project.database import db_context

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


# using task retry decorator from celery built-in
@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 7, "countdown": 5},
)
def task_process_notification(self):
    if not random.choice([0, 1]):
        # mimic random error
        raise Exception()

    #  block the I/O
    requests.post("https://httpbin.org/delay/5")


@task_postrun.connect
def task_postrun_handler(task_id, **kwargs):
    from project.ws.views import update_celery_task_status

    async_to_sync(update_celery_task_status)(task_id)

    from project.ws.views import update_celery_task_status_socketio

    update_celery_task_status_socketio(task_id)


@shared_task(name="task_schedule_work")
def task_schedule_work():
    logger.info("task_schedule_work run")


@shared_task(name="default:dynamic_example_one")
def dynamic_example_one():
    logger.info("Example one")


@shared_task(name="low_priority:dynamic_example_two")
def dynamic_example_two():
    logger.info("Example two")


@shared_task(name="high_priority:dynamic_example_three")
def dynamic_example_three():
    logger.info("Example three")


@shared_task()
def task_send_welcome_email(user_pk):
    from project.users.models import User

    with db_context() as session:
        user = session.query(User).get(user_pk)
        logger.info(f"Sending welcome email to {user.email} {user.id}")


@shared_task()
def task_test_logger():
    logger.info("test")


@shared_task(bind=True)
def task_add_subscribe(self, user_pk):
    with db_context() as session:
        try:
            from project.users.models import User

            user = session.query(User).get(user_pk)
            requests.post(
                "https://httpbin.org/delay/5",
                data={"email": user.email},
            )
        except Exception as exc:
            raise self.retry(exc=exc)


@after_setup_logger.connect()
def on_after_setup_logger(logger, **kwargs):
    formatter = logger.handlers[0].formatter
    file_handler = logging.FileHandler("celery.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

from celery import shared_task


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

from celery import shared_task


@shared_task
def divide(x, y):
    # from celery.contrib import rdb

    # rdb.set_trace()

    import time

    time.sleep(4)
    return x / y

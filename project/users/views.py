import logging
import random
from string import ascii_lowercase

import requests
from celery.result import AsyncResult
from fastapi import FastAPI, Request, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import users_router
from .schemas import UserBody
from .tasks import sample_task, task_process_notification, task_send_welcome_email
from .models import User
from project.database import get_db_session


logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="project/users/templates")


def api_call(email: str):
    # used for testing a failed api call
    if random.choice([0, 1]):
        raise Exception("random processing error")

    # used for simulating a call to a third party api
    requests.post("https://httpbin.org/delay/5")


def random_username():
    username = "".join([random.choice(ascii_lowercase) for i in range(5)])
    return username


@users_router.get("/form/")
def form_example_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@users_router.post("/form/")
def form_example_post(user: UserBody):
    task = sample_task.delay(user.email)
    return JSONResponse({"task_id": task.task_id})


@users_router.get("/task_status/")
def task_status(task_id: str):
    task = AsyncResult(task_id)
    if task.state == "FAILURE":
        error = str(task.result)
        response = {
            "state": task.state,
            "error": error,
        }
    else:
        response = {
            "state": task.state,
        }
    return JSONResponse(response)


@users_router.post("/webhook_test/")
def webhook_test():
    if not random.choice([0, 1]):
        # mimic random error
        raise Exception("random processing error")

    # blocking process
    requests.post("https://httpbin.org/delay/5")
    return "pong"


@users_router.post("/webhook_test_2/")
def webhook_test_2(request: Request):
    task = task_process_notification.delay()
    print(task.id)
    return "pong"


@users_router.get("/form_ws/")
def form_ws_example(request: Request):
    return templates.TemplateResponse("form_ws.html", {"request": request})


@users_router.get("/form_socketio/")
def form_socketio_example(request: Request):
    return templates.TemplateResponse("form_socketio.html", {"request": request})


@users_router.get("/transaction_celery/")
def transaction_celery(session: Session = Depends(get_db_session)):
    try:
        username = random_username()
        user = User(
            username=f"{username}",
            email=f"{username}@test.com",
        )
        session.add(user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise

    logger.info(f"user {user.id} {user.username} is persistent now")
    task_send_welcome_email.delay(user.id)
    return {"message": "done"}

# fs-fastapi-celery
A definitive guide to Celery and FastApi

-- Via PR#2

Adding redis, celery and flower job, assuming already run redis image in docker, description on how to run:

```bash
poetry install

# first terminal: run celery
celery -A main.celery worker --loglevel=info

# second terminal: run flower
celery -A main.celery fower --port=5555

# third terminal: execute python tasks
python
>>> from main import app, divide
>>> task = divide.delay(1,2)
```

Check the tasks in terminal if you want to check via celery or for more interactive go to `localhost:5555` to task tab

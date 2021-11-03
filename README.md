# fs-fastapi-celery
A definitive guide to Celery and FastApi

## How to run the app

Via docker-compose

```bash
docker-compose build
docker-compose up -d
```

Via Locally

```bash
poetry install

# run redis image in daemon mode
docker run -p 6379:6379 --name some-redis -d redis

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

from unittest import mock

import requests
from project.users import tasks
from project.users.factories import UserFactory

from project.users.models import User


def test_pytest_setup(client, db_session):
    # test view
    response = client.get("/users/form/")
    assert response.status_code == 200

    # test db
    user = User(username="test", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    assert user.id


def test_view_with_eager_model(client, db_session, settings, monkeypatch):
    mock_requests_post = mock.MagicMock()
    monkeypatch.setattr(requests, "post", mock_requests_post)
    monkeypatch.setattr(settings, "CELERY_TASK_ALWAYS_EAGER", True, raising=False)

    user_name = "gustiwinata"
    user_email = f"{user_name}@accordbox.com"
    response = client.post(
        "/users/user_subscribe/",
        json={"email": user_email, "username": user_name},
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "send task to Celery successfully",
    }

    mock_requests_post.assert_called_once_with(
        "https://httpbin.org/delay/5", data={"email": user_email}
    )


def test_user_subscribe_view(client, db_session, settings, monkeypatch, user_factory):
    user = user_factory.build()
    task_add_subscribe = mock.MagicMock(name="task_add_subscribe")
    task_add_subscribe.return_value = mock.MagicMock(task_id="task_id")
    monkeypatch.setattr(tasks.task_add_subscribe, "delay", task_add_subscribe)

    response = client.post(
        "/users/user_subscribe/", json={"email": user.email, "username": user.username}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "send task to Celery successfully",
    }

    # query from the db again
    user = db_session.query(User).filter_by(username=user.username).first()
    task_add_subscribe.assert_called_with(user.id)

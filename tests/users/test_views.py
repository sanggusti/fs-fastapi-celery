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

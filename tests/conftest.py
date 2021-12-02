import os

import pytest
from sqlalchemy.orm import session

os.environ["FASTAPI_CONFIG"] = "testing"  # noqa


@pytest.fixture
def settings():
    from project.config import settings as _settings

    return _settings


@pytest.fixture
def app(settings):
    from project import create_app

    app = create_app()
    return app


@pytest.fixture()
def db_session(app):
    from project.database import Base, engine, SessionLocal

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(app):
    from fastapi.testclient import TestClient

    yield TestClient(app)

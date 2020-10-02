import pytest

from app.factory import create_app


@pytest.fixture()
def client(app):
    client = app.test_client()
    return client


@pytest.fixture()
def app():
    app = create_app('app.config.TestingConfig')
    return app

"""
Shared pytest fixtures.

The vision services are deliberately NOT exercised here — loading MediaPipe
would add seconds per test and would need real photographs of real people
committed to the repo. Route tests stub the analysis functions instead; the
geometry and colour maths are unit-tested directly against synthetic inputs.
"""
import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db as _db
from app.models.user import User


@pytest.fixture
def app():
    """A Flask app bound to a fresh in-memory database."""
    app = create_app(TestConfig)

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def user(app):
    """A persisted user account."""
    u = User(email="tester@example.com")
    u.set_password("password123")
    _db.session.add(u)
    _db.session.commit()
    return u


@pytest.fixture
def auth(client, user):
    """Authorization header for `user`."""
    response = client.post(
        "/api/auth/login",
        json={"email": "tester@example.com", "password": "password123"},
    )
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

"""Authentication route behaviour."""
import pytest

from app.models.token_blocklist import TokenBlocklist


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_register_returns_token_and_user(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "new@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["access_token"]
    assert body["user"]["email"] == "new@example.com"
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_register_normalises_email_case(client):
    client.post(
        "/api/auth/register",
        json={"email": "MixedCase@Example.com", "password": "password123"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "mixedcase@example.com", "password": "password123"},
    )
    assert response.status_code == 200


def test_register_rejects_duplicate_email(client, user):
    response = client.post(
        "/api/auth/register",
        json={"email": "tester@example.com", "password": "password123"},
    )
    assert response.status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "not-an-email", "password": "password123"},
        {"email": "", "password": "password123"},
        {"email": "ok@example.com", "password": "short1"},
        {"email": "ok@example.com", "password": "nodigitshere"},
        {"email": "ok@example.com", "password": "12345678"},
    ],
)
def test_register_rejects_bad_input(client, payload):
    assert client.post("/api/auth/register", json=payload).status_code == 422


def test_register_rejects_non_json_body(client):
    assert client.post("/api/auth/register", data="nope").status_code == 400


def test_login_succeeds_with_correct_password(client, user):
    response = client.post(
        "/api/auth/login",
        json={"email": "tester@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert response.get_json()["access_token"]


def test_login_rejects_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        json={"email": "tester@example.com", "password": "wrongpassword1"},
    )
    assert response.status_code == 401


def test_login_rejects_unknown_email_the_same_way(client):
    """An unknown account must not be distinguishable from a bad password."""
    response = client.post(
        "/api/auth/login",
        json={"email": "ghost@example.com", "password": "password123"},
    )
    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid email or password"


def test_password_is_hashed_not_stored(client, db):
    client.post(
        "/api/auth/register",
        json={"email": "hash@example.com", "password": "password123"},
    )
    from app.models.user import User

    stored = User.find_by_email("hash@example.com")
    assert stored.password_hash != "password123"
    assert stored.check_password("password123")
    assert not stored.check_password("password124")


def test_me_requires_a_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_returns_the_caller(client, auth):
    response = client.get("/api/auth/me", headers=auth)
    assert response.status_code == 200
    assert response.get_json()["user"]["email"] == "tester@example.com"


def test_logout_revokes_the_token(client, auth):
    assert client.post("/api/auth/logout", headers=auth).status_code == 200
    assert client.get("/api/auth/me", headers=auth).status_code == 401


def test_logout_persists_the_revocation(client, auth, db):
    """
    The blocklist must be durable — it used to be a module-level set, so a
    restart silently un-revoked every token that had been logged out.
    """
    client.post("/api/auth/logout", headers=auth)

    row = TokenBlocklist.query.one()
    assert row.jti
    assert row.expires_at is not None


def test_logout_twice_is_not_an_error(client, auth):
    client.post("/api/auth/logout", headers=auth)
    # Second call is rejected because the token is already revoked, not 500.
    assert client.post("/api/auth/logout", headers=auth).status_code == 401

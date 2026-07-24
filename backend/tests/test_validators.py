"""Input validation helpers."""
import pytest

from app.utils.validators import validate_email, validate_password


@pytest.mark.parametrize(
    "email",
    [
        "user@example.com",
        "first.last@sub.example.co.uk",
        "user+tag@example.io",
    ],
)
def test_accepts_valid_emails(email):
    assert validate_email(email) is None


@pytest.mark.parametrize(
    "email",
    [
        None,
        "",
        "   ",
        "no-at-sign",
        "no@domain",
        "@example.com",
        "spaces in@example.com",
        "two@@example.com",
    ],
)
def test_rejects_invalid_emails(email):
    assert validate_email(email) is not None


@pytest.mark.parametrize(
    "password",
    ["password1", "aB3xxxxx", "correct-horse-9"],
)
def test_accepts_valid_passwords(password):
    assert validate_password(password) is None


@pytest.mark.parametrize(
    ("password", "reason"),
    [
        (None, "missing"),
        ("", "empty"),
        ("short1", "under 8 characters"),
        ("alphabetsonly", "no digit"),
        ("12345678", "no letter"),
    ],
)
def test_rejects_weak_passwords(password, reason):
    assert validate_password(password) is not None, reason

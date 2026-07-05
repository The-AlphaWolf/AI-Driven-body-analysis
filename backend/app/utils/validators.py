"""
Input validation helpers.
"""
import re

# Minimum 8 chars, at least one letter and one digit
_PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email: str | None) -> str | None:
    """Return an error message if the email is invalid, else None."""
    if not email or not email.strip():
        return "Email is required"
    if not _EMAIL_RE.match(email.strip()):
        return "Invalid email format"
    return None


def validate_password(password: str | None) -> str | None:
    """Return an error message if the password is weak, else None."""
    if not password:
        return "Password is required"
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not _PASSWORD_RE.match(password):
        return "Password must contain at least one letter and one digit"
    return None

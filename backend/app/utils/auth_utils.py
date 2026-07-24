"""
JWT authentication helpers.

Revoked tokens live in the database (see TokenBlocklist) so a logout is not
undone by a restart, and is seen consistently by every gunicorn worker.
"""
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.token_blocklist import TokenBlocklist


def revoke_token(jti: str, expires_at: datetime | None = None) -> None:
    """Record a token's JTI as revoked (logout)."""
    if expires_at is None:
        expires_at = datetime.now(timezone.utc)

    db.session.add(TokenBlocklist(jti=jti, expires_at=expires_at))
    try:
        db.session.commit()
    except IntegrityError:
        # Already revoked — logging out twice is not an error.
        db.session.rollback()


def is_token_revoked(jwt_payload: dict) -> bool:
    """Check whether a token has been revoked."""
    jti = jwt_payload.get("jti")
    if not jti:
        return False
    return db.session.query(
        TokenBlocklist.query.filter_by(jti=jti).exists()
    ).scalar()


def prune_expired_tokens() -> int:
    """
    Drop blocklist rows for tokens that have expired on their own.

    Returns the number of rows removed.
    """
    now = datetime.now(timezone.utc)
    removed = TokenBlocklist.query.filter(TokenBlocklist.expires_at < now).delete()
    db.session.commit()
    return removed

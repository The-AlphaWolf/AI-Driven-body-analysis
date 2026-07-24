"""
Revoked JWT storage.

Kept in the database rather than a process-local set so that logging out
actually sticks across restarts, redeploys, and multiple gunicorn workers.
"""
from datetime import datetime, timezone

from app.extensions import db


class TokenBlocklist(db.Model):
    """A JWT that has been revoked via logout."""

    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
    revoked_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    # When the token would have expired anyway — rows past this are prunable.
    expires_at = db.Column(db.DateTime, nullable=False, index=True)

    def __repr__(self):
        return f"<TokenBlocklist {self.jti}>"

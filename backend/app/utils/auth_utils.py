"""
JWT authentication helpers.
"""
from datetime import datetime, timezone

# In-memory blocklist for revoked tokens.
# In production, replace with Redis for persistence across restarts.
_blocklist: set[str] = set()


def revoke_token(jti: str) -> None:
    """Add a token's JTI to the blocklist (logout)."""
    _blocklist.add(jti)


def is_token_revoked(jwt_payload: dict) -> bool:
    """Check whether a token has been revoked."""
    return jwt_payload.get("jti") in _blocklist

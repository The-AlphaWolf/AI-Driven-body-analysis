"""
User model for authentication and account management.
"""
import uuid
from datetime import datetime, timezone

from app.extensions import db, bcrypt


class User(db.Model):
    """Registered user account."""

    __tablename__ = "users"

    id = db.Column(
        db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationship to analyses
    analyses = db.relationship(
        "Analysis", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    feedback = db.relationship(
        "Feedback", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        """Hash and store a plaintext password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    @classmethod
    def find_by_email(cls, email: str):
        """Look up a user by email address."""
        return cls.query.filter_by(email=email).first()

    def to_dict(self) -> dict:
        """Serialize user to a JSON-safe dictionary (no password)."""
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<User {self.email}>"

"""
Analysis model for storing style analysis results.
"""
import secrets
import uuid
from datetime import datetime, timezone

from app.extensions import db


class Analysis(db.Model):
    """A single style analysis result tied to a user."""

    __tablename__ = "analyses"

    id = db.Column(
        db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False, index=True
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # ── Face analysis results ──────────────────────────────────────────
    face_shape = db.Column(db.String(50), nullable=True)
    face_confidence = db.Column(db.Float, nullable=True)

    # ── Skin tone analysis results ─────────────────────────────────────
    skin_depth = db.Column(db.String(50), nullable=True)
    skin_undertone = db.Column(db.String(50), nullable=True)
    skin_hex_color = db.Column(db.String(7), nullable=True)
    skin_confidence = db.Column(db.Float, nullable=True)
    skin_low_confidence_flag = db.Column(db.Boolean, default=False)

    # ── Body shape analysis results ────────────────────────────────────
    body_shape = db.Column(db.String(50), nullable=True)
    body_confidence = db.Column(db.Float, nullable=True)

    # ── Recommendations (flexible JSON payload) ────────────────────────
    recommendations = db.Column(db.JSON, nullable=True)

    # ── Public sharing ─────────────────────────────────────────────────
    # Null until the owner explicitly shares. Anyone holding the token can
    # read the analysis, so it is a long random value, not a guessable id.
    share_token = db.Column(db.String(43), nullable=True, unique=True, index=True)
    shared_at = db.Column(db.DateTime, nullable=True)

    # ── Thumbnail for history display ──────────────────────────────────
    # Stored inline as JPEG bytes (~8KB) so history survives redeploys on
    # hosts with an ephemeral filesystem (Hugging Face Spaces, Render free).
    thumbnail = db.Column(db.LargeBinary, nullable=True)

    # Deleting an analysis takes its feedback with it — a verdict on a
    # recommendation is meaningless once the analysis that produced it is gone.
    # The ORM does the cascade rather than delegating to the database:
    # SQLite does not enforce ON DELETE without a per-connection pragma, so
    # passive_deletes would silently orphan rows in development and tests.
    # The FK still carries ON DELETE CASCADE as a backstop on Postgres.
    feedback = db.relationship(
        "Feedback", backref="analysis", lazy="dynamic",
        cascade="all, delete-orphan",
    )

    @classmethod
    def get_by_user(cls, user_id: str, page: int = 1, per_page: int = 12):
        """Paginated list of analyses for a user, newest first."""
        return cls.query.filter_by(user_id=user_id).order_by(
            cls.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

    @classmethod
    def get_by_id_and_user(cls, analysis_id: str, user_id: str):
        """Fetch a single analysis, enforcing ownership."""
        return cls.query.filter_by(id=analysis_id, user_id=user_id).first()

    @classmethod
    def get_by_share_token(cls, token: str):
        """Fetch a publicly shared analysis. No ownership check by design."""
        if not token:
            return None
        return cls.query.filter_by(share_token=token).first()

    def enable_sharing(self) -> str:
        """Mint a share token, or return the existing one."""
        if not self.share_token:
            self.share_token = secrets.token_urlsafe(32)
            self.shared_at = datetime.now(timezone.utc)
        return self.share_token

    def disable_sharing(self) -> None:
        """Revoke the share link. Any circulating URL stops working."""
        self.share_token = None
        self.shared_at = None

    def to_summary_dict(self) -> dict:
        """Compact representation for history list view."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "face_shape": self.face_shape,
            "body_shape": self.body_shape,
            "skin_depth": self.skin_depth,
            "skin_undertone": self.skin_undertone,
            "skin_hex_color": self.skin_hex_color,
            "thumbnail_url": f"/api/history/{self.id}/thumbnail" if self.thumbnail else None,
        }

    def to_full_dict(self, public: bool = False) -> dict:
        """
        Complete representation for detail view.

        The public form is what a share link exposes. It deliberately omits
        the photo and the internal id: a shared style report should not hand
        a stranger the subject's face, and the id is the owner's handle for
        routes that only ownership should reach.
        """
        payload = {
            "id": None if public else self.id,
            "created_at": self.created_at.isoformat(),
            "face_analysis": {
                "shape": self.face_shape,
                "confidence": self.face_confidence,
            } if self.face_shape else None,
            "skin_analysis": {
                "depth": self.skin_depth,
                "undertone": self.skin_undertone,
                "hex_color": self.skin_hex_color,
                "confidence": self.skin_confidence,
                "low_confidence_flag": self.skin_low_confidence_flag,
            } if self.skin_depth else None,
            "body_analysis": {
                "shape": self.body_shape,
                "confidence": self.body_confidence,
            } if self.body_shape else None,
            "recommendations": self.recommendations,
        }

        if not public:
            payload["thumbnail_url"] = (
                f"/api/history/{self.id}/thumbnail" if self.thumbnail else None
            )
            payload["share_token"] = self.share_token
            payload["shared_at"] = self.shared_at.isoformat() if self.shared_at else None

        return payload

    def __repr__(self):
        return f"<Analysis {self.id} user={self.user_id}>"

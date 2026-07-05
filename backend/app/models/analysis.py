"""
Analysis model for storing style analysis results.
"""
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

    # ── Thumbnail for history display ──────────────────────────────────
    thumbnail_path = db.Column(db.String(500), nullable=True)

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

    def to_summary_dict(self) -> dict:
        """Compact representation for history list view."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "face_shape": self.face_shape,
            "body_shape": self.body_shape,
            "skin_depth": self.skin_depth,
            "skin_undertone": self.skin_undertone,
            "thumbnail_url": f"/api/history/{self.id}/thumbnail" if self.thumbnail_path else None,
        }

    def to_full_dict(self) -> dict:
        """Complete representation for detail view."""
        return {
            "id": self.id,
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
            "thumbnail_url": f"/api/history/{self.id}/thumbnail" if self.thumbnail_path else None,
        }

    def __repr__(self):
        return f"<Analysis {self.id} user={self.user_id}>"

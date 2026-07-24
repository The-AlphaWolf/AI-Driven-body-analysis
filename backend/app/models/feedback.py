"""
User feedback on individual recommendations.

This is the training signal the README's "upgrade the engine to a trained
model" plan depends on: which recommendations a real person kept and which
they rejected, joined to the attributes that produced them.

A recommendation has no id of its own — it is generated on the fly from the
rules dataset — so a row is keyed by (analysis, category, recommendation
text). That text is stable because it comes verbatim from style_rules.json.
"""
import uuid
from datetime import datetime, timezone

from app.extensions import db

VERDICTS = ("like", "dislike")


class Feedback(db.Model):
    """One user's verdict on one recommendation within one analysis."""

    __tablename__ = "feedback"
    __table_args__ = (
        db.UniqueConstraint(
            "analysis_id", "category", "recommendation", name="uq_feedback_target"
        ),
    )

    id = db.Column(
        db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False, index=True
    )
    analysis_id = db.Column(
        db.String(36),
        db.ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category = db.Column(db.String(50), nullable=False)
    recommendation = db.Column(db.String(255), nullable=False)
    verdict = db.Column(db.String(10), nullable=False)

    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @classmethod
    def for_analysis(cls, analysis_id: str, user_id: str) -> dict[str, str]:
        """
        Verdicts for one analysis, keyed by "category::recommendation".

        Returned as a lookup so the client can render each card's state
        without an N+1 of requests.
        """
        rows = cls.query.filter_by(analysis_id=analysis_id, user_id=user_id).all()
        return {f"{r.category}::{r.recommendation}": r.verdict for r in rows}

    @classmethod
    def saved_for_user(cls, user_id: str, page: int = 1, per_page: int = 20):
        """Paginated list of everything the user has liked, newest first."""
        return (
            cls.query.filter_by(user_id=user_id, verdict="like")
            .order_by(cls.updated_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "category": self.category,
            "recommendation": self.recommendation,
            "verdict": self.verdict,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self):
        return f"<Feedback {self.verdict} {self.category}/{self.recommendation}>"

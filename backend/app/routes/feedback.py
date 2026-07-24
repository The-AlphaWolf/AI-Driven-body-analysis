"""
Feedback routes: record and read verdicts on individual recommendations.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.analysis import Analysis
from app.models.feedback import Feedback, VERDICTS

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("/analysis/<analysis_id>", methods=["PUT"])
@jwt_required()
def set_feedback(analysis_id):
    """
    Record a verdict on one recommendation.

    Request body: { "category": "...", "recommendation": "...",
                    "verdict": "like" | "dislike" | null }

    A null verdict clears any existing feedback, so the same call toggles a
    button off. Idempotent — sending the same verdict twice is a no-op.
    """
    user_id = get_jwt_identity()

    if not Analysis.get_by_id_and_user(analysis_id, user_id):
        return jsonify({"error": "Analysis not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    category = (data.get("category") or "").strip()
    recommendation = (data.get("recommendation") or "").strip()
    verdict = data.get("verdict")

    if not category or not recommendation:
        return jsonify({"error": "category and recommendation are required"}), 422

    if verdict is not None and verdict not in VERDICTS:
        return jsonify({
            "error": f"verdict must be one of {', '.join(VERDICTS)}, or null to clear"
        }), 422

    existing = Feedback.query.filter_by(
        analysis_id=analysis_id,
        category=category,
        recommendation=recommendation,
    ).first()

    if verdict is None:
        if existing:
            db.session.delete(existing)
            db.session.commit()
        return jsonify({"feedback": None}), 200

    if existing:
        existing.verdict = verdict
    else:
        existing = Feedback(
            user_id=user_id,
            analysis_id=analysis_id,
            category=category,
            recommendation=recommendation,
            verdict=verdict,
        )
        db.session.add(existing)

    db.session.commit()
    return jsonify({"feedback": existing.to_dict()}), 200


@feedback_bp.route("/analysis/<analysis_id>", methods=["GET"])
@jwt_required()
def get_feedback(analysis_id):
    """
    All verdicts for one analysis, keyed by "category::recommendation".

    Returns: { "feedback": { "colors::Camel": "like", ... } }
    """
    user_id = get_jwt_identity()

    if not Analysis.get_by_id_and_user(analysis_id, user_id):
        return jsonify({"error": "Analysis not found"}), 404

    return jsonify({"feedback": Feedback.for_analysis(analysis_id, user_id)}), 200


@feedback_bp.route("/saved", methods=["GET"])
@jwt_required()
def list_saved():
    """
    Everything the user has liked, across every analysis.

    Query params: ?page=1&per_page=20
    """
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 50)

    pagination = Feedback.saved_for_user(user_id, page=page, per_page=per_page)

    return jsonify({
        "saved": [f.to_dict() for f in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    }), 200

"""
History routes: list, view, and delete past analyses.
"""
import os
from flask import Blueprint, jsonify, request, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.analysis import Analysis

history_bp = Blueprint("history", __name__)


@history_bp.route("", methods=["GET"])
@jwt_required()
def list_analyses():
    """
    List the current user's past analyses (paginated).

    Query params: ?page=1&per_page=12
    Returns: { "analyses": [...], "total": N, "page": P, "pages": M }
    """
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 12, type=int)
    per_page = min(per_page, 50)  # Cap page size

    pagination = Analysis.get_by_user(user_id, page=page, per_page=per_page)

    return jsonify({
        "analyses": [a.to_summary_dict() for a in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    }), 200


@history_bp.route("/<analysis_id>", methods=["GET"])
@jwt_required()
def get_analysis(analysis_id):
    """
    Get full details of a specific analysis.

    Returns: { "analysis": { ... } }
    """
    user_id = get_jwt_identity()
    analysis = Analysis.get_by_id_and_user(analysis_id, user_id)

    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    return jsonify({"analysis": analysis.to_full_dict()}), 200


@history_bp.route("/<analysis_id>", methods=["DELETE"])
@jwt_required()
def delete_analysis(analysis_id):
    """
    Delete an analysis (only the owner can delete).

    Returns: { "message": "Analysis deleted" }
    """
    user_id = get_jwt_identity()
    analysis = Analysis.get_by_id_and_user(analysis_id, user_id)

    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    # Clean up thumbnail file if it exists
    if analysis.thumbnail_path and os.path.exists(analysis.thumbnail_path):
        try:
            os.remove(analysis.thumbnail_path)
        except OSError:
            pass  # Non-critical, continue with deletion

    db.session.delete(analysis)
    db.session.commit()

    return jsonify({"message": "Analysis deleted"}), 200


@history_bp.route("/<analysis_id>/thumbnail", methods=["GET"])
@jwt_required()
def get_thumbnail(analysis_id):
    """
    Serve the thumbnail image for an analysis.

    Returns the JPEG image file.
    """
    user_id = get_jwt_identity()
    analysis = Analysis.get_by_id_and_user(analysis_id, user_id)

    if not analysis or not analysis.thumbnail_path:
        return jsonify({"error": "Thumbnail not found"}), 404

    if not os.path.exists(analysis.thumbnail_path):
        return jsonify({"error": "Thumbnail file missing"}), 404

    return send_file(analysis.thumbnail_path, mimetype="image/jpeg")

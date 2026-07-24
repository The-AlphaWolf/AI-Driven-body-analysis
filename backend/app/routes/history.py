"""
History routes: list, view, and delete past analyses.
"""
import io

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.analysis import Analysis
from app.services.report import build_style_report, report_filename

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

    if not analysis or not analysis.thumbnail:
        return jsonify({"error": "Thumbnail not found"}), 404

    response = send_file(
        io.BytesIO(analysis.thumbnail),
        mimetype="image/jpeg",
        download_name=f"{analysis.id}.jpg",
    )
    response.headers["Cache-Control"] = "private, max-age=86400"
    return response


@history_bp.route("/<analysis_id>/report.pdf", methods=["GET"])
@jwt_required()
def download_report(analysis_id):
    """Download an analysis as a printable PDF style report."""
    user_id = get_jwt_identity()
    analysis = Analysis.get_by_id_and_user(analysis_id, user_id)

    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    return send_file(
        io.BytesIO(build_style_report(analysis)),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=report_filename(analysis),
    )


@history_bp.route("/<analysis_id>/share", methods=["POST"])
@jwt_required()
def enable_share(analysis_id):
    """
    Create a public link for an analysis.

    Idempotent — calling it again returns the existing token rather than
    invalidating a link the owner may have already sent to someone.

    Returns: { "share_token": "...", "share_path": "/s/<token>" }
    """
    user_id = get_jwt_identity()
    analysis = Analysis.get_by_id_and_user(analysis_id, user_id)

    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    token = analysis.enable_sharing()
    db.session.commit()

    return jsonify({
        "share_token": token,
        "share_path": f"/s/{token}",
        "shared_at": analysis.shared_at.isoformat(),
    }), 200


@history_bp.route("/<analysis_id>/share", methods=["DELETE"])
@jwt_required()
def disable_share(analysis_id):
    """Revoke the public link. Any URL already sent out stops working."""
    user_id = get_jwt_identity()
    analysis = Analysis.get_by_id_and_user(analysis_id, user_id)

    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    analysis.disable_sharing()
    db.session.commit()

    return jsonify({"message": "Sharing disabled"}), 200

"""
Public routes for shared analyses.

Everything here is unauthenticated and reachable by anyone holding a share
token, so it exposes the redacted form of an analysis only — no photo, no
internal id, no feedback.
"""
import io

from flask import Blueprint, jsonify, send_file

from app.models.analysis import Analysis
from app.services.report import build_style_report, report_filename

public_bp = Blueprint("public", __name__)


@public_bp.route("/<share_token>", methods=["GET"])
def get_shared_analysis(share_token):
    """
    Read a shared analysis.

    Returns: { "analysis": { ... } } with the photo and owner ids removed.
    """
    analysis = Analysis.get_by_share_token(share_token)
    if not analysis:
        return jsonify({"error": "This link is not valid or has been revoked"}), 404

    return jsonify({"analysis": analysis.to_full_dict(public=True)}), 200


@public_bp.route("/<share_token>/report.pdf", methods=["GET"])
def get_shared_report(share_token):
    """Download the shared analysis as a PDF."""
    analysis = Analysis.get_by_share_token(share_token)
    if not analysis:
        return jsonify({"error": "This link is not valid or has been revoked"}), 404

    return send_file(
        io.BytesIO(build_style_report(analysis)),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=report_filename(analysis),
    )

"""
Analysis routes: upload photos and run the style analysis pipeline.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.analysis import Analysis
from app.utils.image_utils import validate_image, preprocess_image, make_thumbnail
from app.services.face_analysis import analyze_face
from app.services.skin_analysis import analyze_skin_tone
from app.services.body_analysis import analyze_body
from app.services.recommendation import generate_recommendations

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/analyze", methods=["POST"])
@jwt_required()
def analyze():
    """
    Run a full style analysis on uploaded photos.

    Accepts multipart/form-data with:
      - face_image (optional): Photo of face for shape + skin tone analysis
      - body_image (optional): Full-body photo for body proportion analysis
    At least one image is required.

    Returns the complete analysis result with recommendations.
    """
    user_id = get_jwt_identity()

    face_file = request.files.get("face_image")
    body_file = request.files.get("body_image")

    if not face_file and not body_file:
        return jsonify({"error": "At least one image (face or body) is required"}), 422

    # ── Validate uploaded files ────────────────────────────────────────
    if face_file:
        face_err = validate_image(face_file)
        if face_err:
            return jsonify({"error": f"Face image: {face_err}"}), 422

    if body_file:
        body_err = validate_image(body_file)
        if body_err:
            return jsonify({"error": f"Body image: {body_err}"}), 422

    # ── Run analysis pipeline ──────────────────────────────────────────
    face_result = None
    skin_result = None
    body_result = None

    if face_file:
        face_image = preprocess_image(face_file.read())
        if face_image is None:
            return jsonify({"error": "Could not decode face image"}), 422

        face_result = analyze_face(face_image)
        if face_result and face_result.get("shape"):
            skin_result = analyze_skin_tone(face_image)

    if body_file:
        body_image = preprocess_image(body_file.read())
        if body_image is None:
            return jsonify({"error": "Could not decode body image"}), 422

        body_result = analyze_body(body_image)

    # ── Check that at least one analysis succeeded ─────────────────────
    if not face_result and not body_result:
        return jsonify({
            "error": "Analysis failed",
            "message": "Could not detect a face or body in the uploaded image(s). "
                       "Please upload clear, well-lit photos.",
        }), 422

    # ── Generate recommendations ───────────────────────────────────────
    recommendations = generate_recommendations(
        face_result=face_result,
        skin_result=skin_result,
        body_result=body_result,
    )

    # ── Build thumbnail from first available image ─────────────────────
    thumb_source = face_image if face_file else body_image
    thumbnail = make_thumbnail(thumb_source) if thumb_source is not None else None

    # ── Persist to database ────────────────────────────────────────────
    analysis = Analysis(
        user_id=user_id,
        face_shape=face_result.get("shape") if face_result else None,
        face_confidence=face_result.get("confidence") if face_result else None,
        skin_depth=skin_result.get("depth") if skin_result else None,
        skin_undertone=skin_result.get("undertone") if skin_result else None,
        skin_hex_color=skin_result.get("hex_color") if skin_result else None,
        skin_confidence=skin_result.get("confidence") if skin_result else None,
        skin_low_confidence_flag=skin_result.get("low_confidence_flag", False) if skin_result else False,
        body_shape=body_result.get("shape") if body_result else None,
        body_confidence=body_result.get("confidence") if body_result else None,
        recommendations=recommendations,
        thumbnail=thumbnail,
    )

    db.session.add(analysis)
    db.session.commit()

    return jsonify({
        "analysis": analysis.to_full_dict(),
    }), 201

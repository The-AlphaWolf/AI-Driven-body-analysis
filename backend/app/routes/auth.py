"""
Authentication routes: register, login, profile, logout.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)

from app.extensions import db
from app.models.user import User
from app.utils.validators import validate_email, validate_password
from app.utils.auth_utils import revoke_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user account.

    Request body: { "email": "...", "password": "..." }
    Returns: { "access_token": "...", "user": { ... } }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # ── Validate inputs ────────────────────────────────────────────────
    email_err = validate_email(email)
    if email_err:
        return jsonify({"error": email_err}), 422

    pwd_err = validate_password(password)
    if pwd_err:
        return jsonify({"error": pwd_err}), 422

    # ── Check for existing user ────────────────────────────────────────
    if User.find_by_email(email):
        return jsonify({"error": "An account with this email already exists"}), 409

    # ── Create user ────────────────────────────────────────────────────
    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)

    return jsonify({
        "access_token": access_token,
        "user": user.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate and receive a JWT.

    Request body: { "email": "...", "password": "..." }
    Returns: { "access_token": "...", "user": { ... } }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 422

    user = User.find_by_email(email)
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=user.id)

    return jsonify({
        "access_token": access_token,
        "user": user.to_dict(),
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    Get the current authenticated user's profile.

    Requires: Authorization: Bearer <token>
    Returns: { "user": { ... } }
    """
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user.to_dict()}), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Revoke the current JWT (logout).

    Requires: Authorization: Bearer <token>
    Returns: { "message": "Successfully logged out" }
    """
    jti = get_jwt()["jti"]
    revoke_token(jti)
    return jsonify({"message": "Successfully logged out"}), 200

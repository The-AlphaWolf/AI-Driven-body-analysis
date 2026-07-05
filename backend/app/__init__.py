"""
Flask application factory.
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS

from app.config import Config
from app.extensions import db, migrate, bcrypt, jwt


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Initialize extensions ──────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)

    # ── Ensure upload directories exist ────────────────────────────────
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["THUMBNAIL_FOLDER"], exist_ok=True)

    # ── Register blueprints ────────────────────────────────────────────
    from app.routes.auth import auth_bp
    from app.routes.analysis import analysis_bp
    from app.routes.history import history_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(analysis_bp, url_prefix="/api/analysis")
    app.register_blueprint(history_bp, url_prefix="/api/history")

    # ── JWT blocklist check ────────────────────────────────────────────
    from app.utils.auth_utils import is_token_revoked

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return is_token_revoked(jwt_payload)

    # ── Global error handlers ──────────────────────────────────────────
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "message": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "message": "Resource not found"}), 404

    @app.errorhandler(413)
    def payload_too_large(e):
        return jsonify({"error": "File too large", "message": "Maximum file size is 10MB"}), 413

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({"error": "Unprocessable entity", "message": str(e)}), 422

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error", "message": "Something went wrong"}), 500

    # ── Health check ───────────────────────────────────────────────────
    @app.route("/api/health")
    def health_check():
        return jsonify({"status": "healthy", "service": "StyleSense AI API"})

    return app

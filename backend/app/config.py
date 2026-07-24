"""
Application configuration loaded from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()

DEV_SECRET = "dev-secret-change-me"


class Config:
    """Base configuration."""

    ENV = os.getenv("FLASK_ENV", "development")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///stylesense_dev.db"
    )
    # Render and Heroku hand out 'postgres://' but SQLAlchemy requires 'postgresql://'
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Managed Postgres (Neon and friends) drops idle connections; recycle before
    # the pool hands out a socket the server has already closed.
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", DEV_SECRET)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 86400))  # 24h
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Upload — images are processed in memory and never written to disk
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))  # 10MB

    # CORS
    CORS_ORIGINS = [
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        if o.strip()
    ]

    @classmethod
    def validate(cls) -> None:
        """
        Refuse to serve production traffic with development defaults.

        A shipped default JWT secret means anyone who has read the repo can
        mint a valid token for any account, so this is a hard failure rather
        than a warning.
        """
        if cls.ENV != "production":
            return

        if cls.JWT_SECRET_KEY == DEV_SECRET:
            raise RuntimeError(
                "JWT_SECRET_KEY is still the development default. Set a real "
                "secret before running in production: "
                'python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )

        if cls.SQLALCHEMY_DATABASE_URI.startswith("sqlite:"):
            raise RuntimeError(
                "DATABASE_URL is unset, so the app would run on a local SQLite "
                "file that the host wipes on every redeploy. Point it at Postgres."
            )


class TestConfig(Config):
    """Configuration for the test suite."""

    ENV = "testing"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    JWT_SECRET_KEY = "test-secret-not-used-outside-tests"

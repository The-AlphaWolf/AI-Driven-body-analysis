"""Configuration guards."""
import importlib

import dotenv
import pytest


def reload_config(monkeypatch, **env):
    """Re-import the config module with a given environment."""
    for key in (
        "FLASK_ENV",
        "JWT_SECRET_KEY",
        "DATABASE_URL",
        "CORS_ORIGINS",
    ):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    # load_dotenv must not resurrect the developer's local .env here. The patch
    # goes on the dotenv module rather than on app.config, because reloading
    # app.config re-runs its `from dotenv import load_dotenv` and would rebind
    # the real function straight back over a patched attribute — which made
    # these guards silently pass only on machines with no .env file.
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *a, **k: None)

    import app.config

    return importlib.reload(app.config)


def test_development_tolerates_defaults(monkeypatch):
    config = reload_config(monkeypatch)
    config.Config.validate()  # does not raise


def test_production_rejects_the_default_jwt_secret(monkeypatch):
    config = reload_config(
        monkeypatch,
        FLASK_ENV="production",
        DATABASE_URL="postgresql://u:p@host/db",
    )
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        config.Config.validate()


def test_production_rejects_sqlite(monkeypatch):
    """SQLite on an ephemeral host means every redeploy wipes the accounts."""
    config = reload_config(
        monkeypatch, FLASK_ENV="production", JWT_SECRET_KEY="a-real-secret-value"
    )
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        config.Config.validate()


def test_production_accepts_a_real_configuration(monkeypatch):
    config = reload_config(
        monkeypatch,
        FLASK_ENV="production",
        JWT_SECRET_KEY="a-real-secret-value",
        DATABASE_URL="postgresql://u:p@host/db",
    )
    config.Config.validate()


def test_legacy_postgres_scheme_is_normalised(monkeypatch):
    """Render and Heroku hand out postgres://, which SQLAlchemy 2 rejects."""
    config = reload_config(monkeypatch, DATABASE_URL="postgres://u:p@host/db")
    assert config.Config.SQLALCHEMY_DATABASE_URI.startswith("postgresql://")


def test_cors_origins_are_split_and_trimmed(monkeypatch):
    config = reload_config(
        monkeypatch, CORS_ORIGINS="https://a.example , https://b.example"
    )
    assert config.Config.CORS_ORIGINS == ["https://a.example", "https://b.example"]

"""
Shared extension instances.

Instantiated here (outside the app factory) to avoid circular imports
between models and the app factory. Each extension is initialized with
the app in create_app() via init_app().
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()

"""
WSGI entry point for the Flask application.
Used by Gunicorn in production and `flask run` in development.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

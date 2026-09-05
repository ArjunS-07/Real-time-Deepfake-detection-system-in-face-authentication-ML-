"""
Flask entrypoint — registers all route blueprints and initializes the DB.
"""
from flask import Flask
from flask_cors import CORS

from routes.webcam_routes import webcam_bp
from routes.upload_routes import upload_bp
from routes.health_routes import health_bp
from db.database import init_db
from utils.logger import get_logger

logger = get_logger(__name__)


def create_app():
    app = Flask(__name__)
    CORS(app)  # allow the Streamlit frontend (different origin/port) to call this API

    app.register_blueprint(health_bp)
    app.register_blueprint(webcam_bp)
    app.register_blueprint(upload_bp)  # placeholder, returns 501 (v2)

    init_db()
    logger.info("Flask app created and DB initialized.")
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

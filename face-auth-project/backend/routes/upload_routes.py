"""
Upload path — real vs AI-generated image/video detection.
PLACEHOLDER ONLY. This is v2 scope; not being built yet.
"""
from flask import Blueprint, jsonify

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/predict/upload", methods=["POST"])
def predict_upload():
    return jsonify({
        "error": "Upload path is not implemented yet (planned for v2).",
    }), 501

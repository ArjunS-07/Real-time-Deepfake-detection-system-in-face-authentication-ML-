"""
Webcam liveness / deepfake detection routes — BUILD NOW (Phase 2/3 core path).

Flow:
  1. Frontend opens a session:      POST /predict/session/start
  2. Frontend streams frames to:    POST /predict/frame           (repeated)
  3. Frontend finalizes with:       POST /predict/session/finalize
     -> runs fusion engine on the session's aggregated scores, logs to DB.

Frames are analyzed per-call (mock or real engines), accumulated in the
in-memory session, and only fused into a final REAL/SPOOF decision once
enough frames have been collected — this matches the "biological cue"
signals (blink, landmark coherence) which need a short sequence, not a
single frame, to mean anything.
"""
import base64
import io
import os
import time

from flask import Blueprint, request, jsonify
from PIL import Image

from engines.preprocessing import detect_and_align, normalize
from engines.texture_analysis import analyze_texture
from engines.biological_cues import analyze_blink_sequence
from engines.landmark_coherence import analyze_landmark_coherence
from engines.fusion import fuse
from session import session_manager
from db.database import log_frame_score, log_final_prediction, log_captured_sample
from utils.logger import get_logger

webcam_bp = Blueprint("webcam", __name__)
logger = get_logger(__name__)

# Captured frame images are saved here for future retraining.
# Gitignored — these are real user face images, never commit them.
CAPTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "captured_frames")
os.makedirs(CAPTURE_DIR, exist_ok=True)


def _save_frame_image(session_id: str, image: Image.Image, is_final: bool) -> str:
    """Saves the frame to disk and returns its path (relative, for DB storage)."""
    tag = "final" if is_final else f"{int(time.time() * 1000)}"
    filename = f"{session_id}_{tag}.jpg"
    full_path = os.path.join(CAPTURE_DIR, filename)
    image.save(full_path, format="JPEG")
    return full_path


def _decode_image(b64_string: str) -> Image.Image:
    image_bytes = base64.b64decode(b64_string.split(",")[-1])
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


@webcam_bp.route("/predict/session/start", methods=["POST"])
def start_session():
    session_id = session_manager.create_session()
    return jsonify({"session_id": session_id}), 200


@webcam_bp.route("/predict/frame", methods=["POST"])
def predict_frame():
    data = request.get_json(silent=True)
    if not data or "image" not in data or "session_id" not in data:
        return jsonify({"error": "Requires 'session_id' and 'image' (base64)"}), 400

    session_id = data["session_id"]

    try:
        image = _decode_image(data["image"])
    except Exception as e:
        return jsonify({"error": f"Invalid image payload: {str(e)}"}), 400

    face_crop, landmarks = detect_and_align(image)
    if face_crop is None:
        return jsonify({"error": "No face detected in frame"}), 422

    face_crop = normalize(face_crop)

    texture_score = analyze_texture(face_crop)
    # Single-frame placeholders for sequence-based engines; the real signal
    # comes from finalize_session() aggregating across frames.
    landmark_confidence = analyze_landmark_coherence([landmarks] if landmarks else [])
    blink_score = analyze_blink_sequence([landmarks] if landmarks else [], None)

    scores = {
        "texture_score": texture_score,
        "landmark_confidence": landmark_confidence,
        "blink_score": blink_score,
    }

    import numpy as np
    green_val = float(np.mean(np.array(face_crop)[:, :, 1])) if face_crop else None
    frame_count = session_manager.add_frame(session_id, scores, landmarks, green_val)
    log_frame_score(session_id, frame_count, scores)

    # Keep the most recent raw frame in memory (not yet saved to disk) so
    # finalize_session() can persist one representative image alongside
    # the final decision, rather than saving every single frame.
    session_manager.set_last_raw_frame(session_id, image)

    return jsonify({
        "session_id": session_id,
        "frame_count": frame_count,
        "frame_scores": scores,
    }), 200


@webcam_bp.route("/predict/session/finalize", methods=["POST"])
def finalize_session():
    data = request.get_json(silent=True)
    if not data or "session_id" not in data:
        return jsonify({"error": "Requires 'session_id'"}), 400

    start = time.time()
    session_id = data["session_id"]

    result = session_manager.finalize_session(session_id)
    if result is None:
        return jsonify({
            "error": "Session not found or has too few frames to finalize."
        }), 400

    aggregated_scores, frame_count, last_raw_frame = result

    fusion_score, disagreement, decision = fuse(
        aggregated_scores["texture_score"],
        aggregated_scores["landmark_confidence"],
        aggregated_scores["blink_score"],
    )

    # Persist one representative image + the model's own decision for this
    # session, so it becomes a candidate for future training once reviewed.
    if last_raw_frame is not None:
        image_path = _save_frame_image(session_id, last_raw_frame, is_final=True)
        log_captured_sample(
            session_id=session_id,
            image_path=image_path,
            frame_index=frame_count,
            is_final_frame=True,
            scores=aggregated_scores,
            fusion_score=fusion_score,
            decision=decision,
        )

    latency_ms = round((time.time() - start) * 1000, 2)

    response = {
        "session_id": session_id,
        "frame_count": frame_count,
        "engines": aggregated_scores,
        "disagreement": disagreement,
        "fusion_score": fusion_score,
        "decision": decision,
        "latency_ms": latency_ms,
    }

    log_final_prediction(session_id, frame_count, response)
    logger.info("Session %s finalized: %s (score=%s)", session_id, decision, fusion_score)

    return jsonify(response), 200
"""
In-memory session manager for webcam liveness checks.

A "session" accumulates per-frame engine scores over a short capture
window (e.g. a few seconds of webcam frames), then finalizes into a
single aggregated decision. Sessions expire automatically after
SESSION_TIMEOUT_SECONDS of inactivity.

NOTE: in-memory only — fine for a single-process dev/demo backend.
Move to Redis or a DB-backed store before any multi-worker deployment.
"""
import time
import uuid
import threading

SESSION_TIMEOUT_SECONDS = 60
MIN_FRAMES_TO_FINALIZE = 5

_sessions = {}
_lock = threading.Lock()


def create_session() -> str:
    session_id = str(uuid.uuid4())
    with _lock:
        _sessions[session_id] = {
            "created_at": time.time(),
            "last_seen": time.time(),
            "frames": [],  # list of {texture_score, landmark_confidence, blink_score}
            "landmarks": [],  # list of per-frame landmark sets (for coherence/blink engines)
            "greens": [],  # list of per-frame mean green channel values
            "last_raw_frame": None,
        }
    return session_id


def _purge_expired():
    now = time.time()
    expired = [
        sid for sid, s in _sessions.items()
        if now - s["last_seen"] > SESSION_TIMEOUT_SECONDS
    ]
    for sid in expired:
        del _sessions[sid]


def add_frame(session_id: str, scores: dict, landmarks=None, green_val=None):
    with _lock:
        _purge_expired()
        if session_id not in _sessions:
            _sessions[session_id] = {
                "created_at": time.time(),
                "last_seen": time.time(),
                "frames": [],
                "landmarks": [],
                "greens": [],
                "last_raw_frame": None,
            }
        _sessions[session_id]["frames"].append(scores)
        _sessions[session_id].setdefault("landmarks", []).append(landmarks)
        if green_val is not None:
            _sessions[session_id].setdefault("greens", []).append(green_val)
        _sessions[session_id]["last_seen"] = time.time()
        return len(_sessions[session_id]["frames"])


def set_last_raw_frame(session_id: str, image):
    """Keeps a reference to the most recent raw PIL image for this session
    (in memory only — not saved to disk here), so finalize can persist a
    single representative image alongside the final decision."""
    with _lock:
        if session_id in _sessions:
            _sessions[session_id]["last_raw_frame"] = image


def get_last_raw_frame(session_id: str):
    with _lock:
        session = _sessions.get(session_id)
        return session["last_raw_frame"] if session else None


def get_session(session_id: str):
    with _lock:
        return _sessions.get(session_id)


def finalize_session(session_id: str):
    """
    Aggregates per-frame scores and evaluates multi-frame biological and
    landmark coherence on the collected sequence for the fusion engine.
    Returns None if session doesn't exist or has too few frames.
    """
    with _lock:
        session = _sessions.get(session_id)
        if not session or len(session["frames"]) < MIN_FRAMES_TO_FINALIZE:
            return None

        frames = session["frames"]
        n = len(frames)
        landmarks_seq = session.get("landmarks", [])
        greens_seq = session.get("greens", [])

        # Import sequence engines
        from engines.landmark_coherence import analyze_landmark_coherence
        from engines.biological_cues import analyze_blink_sequence

        texture_score = round(sum(f["texture_score"] for f in frames) / n, 4)
        landmark_confidence = analyze_landmark_coherence(landmarks_seq)
        blink_score = analyze_blink_sequence(landmarks_seq, greens_seq)

        aggregated = {
            "texture_score": texture_score,
            "landmark_confidence": landmark_confidence,
            "blink_score": blink_score,
        }
        frame_count = n
        last_raw_frame = session.get("last_raw_frame")
        # Clean up session after finalizing
        del _sessions[session_id]
        return aggregated, frame_count, last_raw_frame
"""SQLite connection handling and logging helpers."""
import sqlite3
import os
from datetime import datetime

from utils.logger import get_logger

logger = get_logger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "logs.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    logger.info("Database initialized at %s", DB_PATH)


def log_frame_score(session_id: str, frame_index: int, scores: dict):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO frame_scores
        (session_id, frame_index, timestamp, texture_score, landmark_confidence, blink_score)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            frame_index,
            datetime.utcnow().isoformat(),
            scores["texture_score"],
            scores["landmark_confidence"],
            scores["blink_score"],
        ),
    )
    conn.commit()
    conn.close()


def log_final_prediction(session_id: str, frame_count: int, result: dict):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO predictions
        (session_id, timestamp, frame_count, texture_score, landmark_confidence,
         blink_score, disagreement, fusion_score, decision, latency_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            datetime.now().astimezone().isoformat(),
            frame_count,
            result["engines"]["texture_score"],
            result["engines"]["landmark_confidence"],
            result["engines"]["blink_score"],
            result["disagreement"],
            result["fusion_score"],
            result["decision"],
            result["latency_ms"],
        ),
    )
    conn.commit()
    conn.close()


def log_captured_sample(
    session_id: str,
    image_path: str,
    frame_index: int,
    is_final_frame: bool,
    scores: dict,
    fusion_score,
    decision,
):
    """
    Stores a reference to a saved frame image alongside the model's own
    decision. `verified_label` is intentionally left NULL here — it should
    only be filled in later via a review step, before the row is used
    for training. See schema.sql for why.
    """
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO captured_samples
        (session_id, image_path, frame_index, is_final_frame,
         texture_score, landmark_confidence, blink_score,
         fusion_score, decision, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            image_path,
            frame_index,
            1 if is_final_frame else 0,
            scores.get("texture_score"),
            scores.get("landmark_confidence"),
            scores.get("blink_score"),
            fusion_score,
            decision,
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_unverified_samples(limit: int = 100):
    """Samples awaiting human review before they can be used for training."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM captured_samples WHERE verified_label IS NULL ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def set_verified_label(sample_id: int, verified_label: str):
    """Call this once a human (or a future trusted process) confirms the true label."""
    conn = get_connection()
    conn.execute(
        "UPDATE captured_samples SET verified_label = ? WHERE id = ?",
        (verified_label, sample_id),
    )
    conn.commit()
    conn.close()


def get_training_ready_samples(limit: int = 1000):
    """Only samples with a verified_label are eligible for training."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM captured_samples
        WHERE verified_label IS NOT NULL AND used_for_training = 0
        ORDER BY id ASC LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_recent_predictions(limit: int = 50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
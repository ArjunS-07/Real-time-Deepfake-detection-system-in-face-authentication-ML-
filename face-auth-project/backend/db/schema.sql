-- Prediction log: one row per finalized webcam session (aggregated result)
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    frame_count INTEGER,
    texture_score REAL,
    landmark_confidence REAL,
    blink_score REAL,
    disagreement REAL,
    fusion_score REAL,
    decision TEXT,
    latency_ms REAL
);

-- Optional: raw per-frame scores, useful for debugging/model iteration
CREATE TABLE IF NOT EXISTS frame_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    frame_index INTEGER,
    timestamp TEXT NOT NULL,
    texture_score REAL,
    landmark_confidence REAL,
    blink_score REAL
);

-- Captured samples: stores a reference to the saved image + the model's own
-- decision, so real usage can become future training data.
--
-- IMPORTANT: `decision` is the MODEL'S OWN prediction, not verified ground
-- truth. Do NOT feed rows into training where verified_label IS NULL —
-- retraining directly on unverified self-predictions risks the model
-- reinforcing its own mistakes over time. `verified_label` is filled in
-- later (manual review, or a future confidence-gated auto-accept rule)
-- before a row is eligible for training.
CREATE TABLE IF NOT EXISTS captured_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    image_path TEXT NOT NULL,          -- path to saved frame image on disk
    frame_index INTEGER,
    is_final_frame INTEGER DEFAULT 0,  -- 1 = the representative/last frame of the session
    texture_score REAL,
    landmark_confidence REAL,
    blink_score REAL,
    fusion_score REAL,
    decision TEXT,                     -- model's own prediction: "REAL" or "SPOOF"
    verified_label TEXT DEFAULT NULL,  -- ground truth, filled in later ("real"/"spoof"), NULL until reviewed
    used_for_training INTEGER DEFAULT 0,
    timestamp TEXT NOT NULL
);
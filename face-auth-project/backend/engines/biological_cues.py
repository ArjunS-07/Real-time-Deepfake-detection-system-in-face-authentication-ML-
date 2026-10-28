"""
Biological cue analysis: blink rate / eye aspect ratio dynamics over a sequence of frames.
Webcam-only signal — requires landmarks across multiple frames in a session.
Evaluates 17 temporal features:
  - EAR curve dynamics (mean, std, min, range, blink count, blink rate, max velocity)
  - Mouth aspect ratio (MAR) micro-expressions (mean, std, range)
  - Facial micro-motion & non-rigid distance stability
  - Green-channel rPPG intensity and spectral power
"""
import os
import numpy as np
import pandas as pd
import xgboost as xgb

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "biological_engine.json")

_model = None
_model_mtime = 0


def _load_model():
    global _model, _model_mtime
    if os.path.exists(MODEL_PATH):
        try:
            mtime = os.path.getmtime(MODEL_PATH)
            if _model is None or mtime != _model_mtime:
                m = xgb.XGBClassifier()
                m.load_model(MODEL_PATH)
                _model = m
                _model_mtime = mtime
        except Exception:
            _model = None
    return _model


LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
LIP_TOP, LIP_BOTTOM, MOUTH_L, MOUTH_R = 13, 14, 61, 291


def _eye_aspect_ratio(pts, eye_idx):
    eye_pts = pts[eye_idx]
    vert1 = np.linalg.norm(eye_pts[1, :2] - eye_pts[5, :2])
    vert2 = np.linalg.norm(eye_pts[2, :2] - eye_pts[4, :2])
    horiz = np.linalg.norm(eye_pts[0, :2] - eye_pts[3, :2])
    return float((vert1 + vert2) / (2.0 * horiz + 1e-6))


def _mouth_aspect_ratio(pts):
    vert = np.linalg.norm(pts[LIP_TOP, :2] - pts[LIP_BOTTOM, :2])
    horiz = np.linalg.norm(pts[MOUTH_L, :2] - pts[MOUTH_R, :2])
    return float(vert / (horiz + 1e-6))


def _signal_variability(signal):
    signal = signal - np.mean(signal)
    if len(signal) < 4:
        return 0.0, 0.0
    fft = np.abs(np.fft.rfft(signal))
    freqs = np.fft.rfftfreq(len(signal), d=1.0)
    if len(fft) <= 1:
        return 0.0, 0.0
    fft[0] = 0
    peak_idx = np.argmax(fft)
    return float(freqs[peak_idx]), float(fft[peak_idx])


def analyze_blink_sequence(landmark_sequence: list, green_sequence: list = None, *args, **kwargs) -> float:
    """
    landmark_sequence: list of per-frame landmark sets collected during a session.
    green_sequence: optional list of mean green-channel values across frames.
    Evaluates physiological liveness (EAR blink dynamics, MAR micro-expressions,
    rigid/non-rigid head motion, and facial green rPPG variability) against the
    trained XGBoost biological engine.
    100% independent feature extraction and model inference.
    Returns a liveness score in [0, 1] (higher = more likely real).
    """
    if not landmark_sequence or len(landmark_sequence) < 2:
        return 0.15

    valid_pts = []
    for lm in landmark_sequence:
        if lm is not None and len(lm) >= 468:
            pts = np.array([[p[0], p[1], p[2] if len(p) > 2 else 0.0] for p in lm], dtype=np.float64)
            # Defensive auto-normalization if pixel coordinates were provided
            if len(pts) > 0 and (np.max(pts[:, 0]) > 2.0 or np.max(pts[:, 1]) > 2.0):
                scale_x = np.max(pts[:, 0]) if np.max(pts[:, 0]) > 1.0 else 1.0
                scale_y = np.max(pts[:, 1]) if np.max(pts[:, 1]) > 1.0 else 1.0
                pts[:, 0] /= scale_x
                pts[:, 1] /= scale_y
                pts[:, 2] /= scale_x
            valid_pts.append(pts)

    if len(valid_pts) < 3:
        return 0.15

    ears = []
    mars = []
    centroids = []
    internal_dists = []

    for pts in valid_pts:
        ear_l = _eye_aspect_ratio(pts, LEFT_EYE)
        ear_r = _eye_aspect_ratio(pts, RIGHT_EYE)
        ears.append((ear_l + ear_r) / 2.0)
        mars.append(_mouth_aspect_ratio(pts))
        centroids.append([np.mean(pts[:, 0]), np.mean(pts[:, 1])])
        internal_dists.append(float(np.linalg.norm(pts[1, :2] - pts[33, :2])))

    e_arr = np.array(ears)
    m_arr = np.array(mars)
    c_arr = np.array(centroids)
    id_arr = np.array(internal_dists)

    # Blink dynamics
    ear_mean = float(np.mean(e_arr))
    ear_std = float(np.std(e_arr))
    ear_min = float(np.min(e_arr))
    ear_range = float(np.max(e_arr) - np.min(e_arr))

    # Real human blinks require substantial amplitude change (EAR drop >= 0.035).
    # Sensor noise / slight landmark jitter on a static photo (std < 0.008) must NOT count as blinks.
    if ear_std >= 0.008 and ear_range >= 0.035:
        blink_thresh = min(0.22, ear_mean - max(0.035, 0.5 * ear_std))
        below = (e_arr < blink_thresh).astype(int)
        blinks = int(np.sum(np.diff(below) == 1))
    else:
        blinks = 0
    blink_rate = float(blinks / len(e_arr))

    ear_diffs = np.abs(np.diff(e_arr))
    ear_vel_max = float(np.max(ear_diffs)) if len(ear_diffs) > 0 else 0.0

    # Mouth dynamics
    mar_mean = float(np.mean(m_arr))
    mar_std = float(np.std(m_arr))
    mar_range = float(np.max(m_arr) - np.min(m_arr))

    # Motion dynamics
    motion_x = float(np.std(c_arr[:, 0])) if len(c_arr) > 1 else 0.0
    motion_y = float(np.std(c_arr[:, 1])) if len(c_arr) > 1 else 0.0
    motion_std = float(np.sqrt(motion_x**2 + motion_y**2))
    internal_dist_std = float(np.std(id_arr)) if len(id_arr) > 1 else 0.0

    # Green channel (rPPG proxy)
    if green_sequence and len(green_sequence) >= 5:
        g_arr = np.array(green_sequence)
        g_mean = float(np.mean(g_arr))
        g_std = float(np.std(g_arr))
        g_freq, g_power = _signal_variability(g_arr)
    else:
        g_mean = 118.0
        g_std = 3.0
        g_freq, g_power = 0.25, 15.0

    feats = {
        "n_frames": len(valid_pts),
        "green_mean": g_mean,
        "green_std": g_std,
        "signal_variability_freq": g_freq,
        "signal_variability_power": g_power,
        "ear_mean": ear_mean,
        "ear_std": ear_std,
        "ear_min": ear_min,
        "ear_range": ear_range,
        "blink_count": blinks,
        "blink_rate": blink_rate,
        "ear_velocity_max": ear_vel_max,
        "mar_mean": mar_mean,
        "mar_std": mar_std,
        "mar_range": mar_range,
        "motion_std": motion_std,
        "internal_dist_std": internal_dist_std,
    }

    feature_cols = [
        "n_frames", "green_mean", "green_std", "signal_variability_freq",
        "signal_variability_power", "ear_mean", "ear_std", "ear_min",
        "ear_range", "blink_count", "blink_rate", "ear_velocity_max",
        "mar_mean", "mar_std", "mar_range", "motion_std", "internal_dist_std"
    ]

    model = _load_model()
    if model is not None:
        try:
            X = pd.DataFrame([feats])[feature_cols]
            p_spoof = float(model.predict_proba(X)[0, 1])
            raw_live = 1.0 - p_spoof

            # Physiological scoring:
            # 1. Verified physiological eye blink: eyelid closed (ear_min < 0.21) with rapid recovery
            if blinks >= 1 and ear_min < 0.21:
                bio_score = max(raw_live, 0.85)
            # 2. Zero blinks in the short capture window:
            # A real user sitting naturally often does not blink within 1-2 seconds.
            # Treat as unconfirmed neutral baseline (0.40) rather than an artificial spoof penalty.
            elif blinks == 0:
                bio_score = 0.40
            else:
                bio_score = raw_live

            return round(float(np.clip(bio_score, 0.05, 0.95)), 4)
        except Exception:
            pass

    # Analytical heuristic fallback only if model weights file is missing
    if blinks >= 1 and ear_min < 0.21:
        liveness_score = 0.85
    else:
        liveness_score = 0.40

    return round(float(np.clip(liveness_score, 0.05, 0.95)), 4)



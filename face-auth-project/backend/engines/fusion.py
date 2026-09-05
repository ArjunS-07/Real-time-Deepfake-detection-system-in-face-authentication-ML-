"""
Disagreement-aware fusion engine.

Stage A: rule-based disagreement detection (std dev across engine scores).
Stage B: escalation-rule stacking classifier trained on [engine scores + disagreement feature]
         loaded from models/fusion_model.joblib.
"""
import os
import joblib
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "fusion_model.joblib")

_fusion_data = None

def _load_fusion():
    global _fusion_data
    if _fusion_data is None and os.path.exists(MODEL_PATH):
        try:
            _fusion_data = joblib.load(MODEL_PATH)
        except Exception:
            _fusion_data = None
    return _fusion_data


def _disagreement(scores: list) -> float:
    mean_score = sum(scores) / len(scores)
    variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
    return round(variance ** 0.5, 4)


def fuse(texture_score: float, landmark_confidence: float, blink_score: float):
    """
    Returns (fusion_score, disagreement, decision) where decision is "REAL" or "SPOOF".
    Higher scores in [0, 1] represent higher confidence of bona fide (real) user.
    """
    scores = [texture_score, landmark_confidence, blink_score]
    disagreement = _disagreement(scores)

    data = _load_fusion()
    if data is not None:
        try:
            low = data.get("low", 0.3)
            high = data.get("high", 0.7)
            escalation_model = data.get("escalation_model")

            tex_spoof = 1.0 - texture_score
            lm_spoof = 1.0 - landmark_confidence
            bio_spoof = 1.0 - blink_score

            if tex_spoof < low or tex_spoof > high or escalation_model is None:
                final_spoof = tex_spoof
            else:
                X = pd.DataFrame([{
                    "texture_prob": tex_spoof,
                    "landmark_prob": lm_spoof,
                    "has_landmark": 1.0,
                    "bio_prob": bio_spoof,
                    "has_bio": 1.0,
                }])
                final_spoof = float(escalation_model.predict_proba(X)[0, 1])

            fusion_score = round(max(0.0, min(1.0, 1.0 - final_spoof)), 4)
            decision = "REAL" if fusion_score >= 0.5 else "SPOOF"
            return fusion_score, disagreement, decision
        except Exception:
            pass

    # Stage A rule-based fallback
    mean_score = sum(scores) / len(scores)
    fusion_score = round(mean_score - (disagreement * 0.5), 4)
    decision = "REAL" if fusion_score >= 0.5 else "SPOOF"
    return fusion_score, disagreement, decision


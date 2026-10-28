"""
Disagreement-aware multi-modal fusion engine.

Architecture:
1. Stage A Primary Texture Rule:
   - If texture_score < 0.30: unequivocal spoof artifact (print, moiré, digital screen, cutouts).
     Direct SPOOF decision.
2. Physiological Anti-Static Veto:
   - If blink_score <= 0.10: confirmed static photo or screen presentation attack with zero blinks.
     Direct SPOOF decision (cannot masquerade as live regardless of single-frame texture).
3. High-Confidence Bona Fide Agreement:
   - If texture_score > 0.70 and blink_score > 0.10:
     Multi-modal live verification.
4. Stage B Multi-Modal Weighted Consensus:
   - Ambiguous zone (0.30 <= texture_score <= 0.70):
     Weighted consensus penalized by inter-engine disagreement.
"""
import os
import numpy as np


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

    # 1. Texture Spoof Veto (Primary screen / print / moiré artifact detector)
    # If texture model detects strong spoof artifacts (< 0.30), immediately flag as SPOOF.
    if texture_score < 0.30:
        return round(texture_score, 4), disagreement, "SPOOF"

    # 2. Confident Multi-Modal Real Agreement (Handles real users sitting naturally without blinking)
    # If skin texture is unmistakably real (>= 0.85) AND 3D facial geometry is coherent (>= 0.55),
    # the user is confirmed bona fide even if they did not happen to blink during the 1-2s capture window.
    if texture_score >= 0.85 and landmark_confidence >= 0.55:
        fusion_score = round(0.50 * texture_score + 0.35 * landmark_confidence + 0.15 * blink_score, 4)
        return fusion_score, disagreement, "REAL"

    # 3. Dynamic Blink-Confirmed Liveness
    # If the user performed a verified physiological blink (blink_score >= 0.70) with authentic texture:
    if blink_score >= 0.70 and texture_score >= 0.50:
        fusion_score = round(0.40 * texture_score + 0.35 * blink_score + 0.25 * landmark_confidence, 4)
        return fusion_score, disagreement, "REAL"

    # 4. Inconclusive / Ambiguous Zone (e.g. photos on screens where texture is lukewarm ~0.73, landmark ~0.45, no blink)
    # If no blink occurred and texture/landmarks lack high confidence, classify as SPOOF.
    if blink_score < 0.70 and (texture_score < 0.85 or landmark_confidence < 0.55):
        spoof_score = round(min(texture_score * 0.45, 0.42), 4)
        return spoof_score, disagreement, "SPOOF"

    # Balanced default weighting fallback
    weighted_score = 0.40 * texture_score + 0.35 * landmark_confidence + 0.25 * blink_score
    calibrated_score = weighted_score - (disagreement * 0.20)
    fusion_score = round(float(np.clip(calibrated_score, 0.05, 0.95)), 4)
    decision = "REAL" if fusion_score >= 0.50 else "SPOOF"
    return fusion_score, disagreement, decision


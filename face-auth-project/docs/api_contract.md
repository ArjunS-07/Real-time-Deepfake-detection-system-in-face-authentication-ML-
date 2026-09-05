# API Contract — Webcam Liveness Path

Base URL: `http://localhost:5000` (local) / set via `BACKEND_URL` env var in deployment.

## GET /health
Returns `{"status": "ok", "service": "face-auth-backend"}`.

## POST /predict/session/start
Starts a new liveness-check session.
**Response:** `{"session_id": "<uuid>"}`

## POST /predict/frame
Analyzes a single frame and adds it to a session.
**Request:**
```json
{"session_id": "<uuid>", "image": "<base64 JPEG>"}
```
**Response (200):**
```json
{"session_id": "<uuid>", "frame_count": 3, "frame_scores": {"texture_score": 0.87, "landmark_confidence": 0.91, "blink_score": 0.76}}
```
**Errors:** `400` missing fields, `422` no face detected.

## POST /predict/session/finalize
Aggregates all frames in a session and returns the fused decision.
**Request:** `{"session_id": "<uuid>"}`
**Response (200):**
```json
{
  "session_id": "<uuid>",
  "frame_count": 8,
  "engines": {"texture_score": 0.85, "landmark_confidence": 0.9, "blink_score": 0.8},
  "disagreement": 0.04,
  "fusion_score": 0.83,
  "decision": "REAL",
  "latency_ms": 12.3
}
```
**Errors:** `400` session not found / too few frames.

## POST /predict/upload  (v2 — placeholder)
Returns `501 Not Implemented`. Reserved for the upload real-vs-AI-generated path.

---
Label set: `decision` ∈ {`"REAL"`, `"SPOOF"`}. Do not introduce new label
strings without updating this doc and both frontend pages.

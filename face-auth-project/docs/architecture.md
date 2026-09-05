# Architecture Overview

Two Hugging Face Spaces: Streamlit frontend + Dockerized Flask backend, communicating over HTTP with CORS.

## Webcam liveness path (current scope)
1. Frontend opens a session (`/predict/session/start`)
2. Streamlit captures frames via `streamlit-webrtc`, sends each to `/predict/frame`
3. Each frame runs: preprocessing (MediaPipe align) -> texture analysis (EfficientNet/ONNX)
   -> landmark coherence -> blink/bio-cue scoring
4. After enough frames, `/predict/session/finalize` aggregates scores and runs the
   fusion engine:
   - **Stage A**: rule-based disagreement detection (std dev of engine scores)
   - **Stage B**: sklearn stacking classifier on [scores + disagreement]
5. Result + scores logged to SQLite (`backend/logs.db`)

## Upload path (v2, not built yet)
Real vs. AI-generated image/video detection. Routes and frontend page exist as
placeholders only.

## Model swap points
All ML logic is isolated behind `backend/engines/*.py`. Each falls back to a
mock score if its trained artifact isn't present in `backend/models/`, so the
API and frontend never need to change when real models are dropped in.

# Architecture Overview

Two Hugging Face Spaces: Streamlit frontend + Dockerized Flask backend, communicating over HTTP with CORS.

## Webcam liveness path (current scope)
1. Frontend opens a session (`/predict/session/start`)
2. Streamlit captures frames via `streamlit-webrtc`, sends each to `/predict/frame`
3. Each frame runs:
   - Preprocessing: face alignment and ROI crop via MediaPipe FaceMesh
   - Texture analysis: MobileNetV3-Small (`texture_engine.pt`, PyTorch/CUDA) screening for moiré, print, and specular artifacts (Stage A fast-path)
   - Landmark coherence: 20 scale-invariant 3D geometric & PCA planarity features via XGBoost (`landmark_engine.json`)
   - Biological cues buffer: frame-to-frame accumulator collecting EAR blink traces, MAR dynamics, and green-channel rPPG proxies across the session
4. After sufficient frames (minimum 5-10 frames), `/predict/session/finalize` evaluates accumulated temporal dynamics with the biological engine (`biological_engine.json`) and invokes the fusion engine:
   - **Stage A (Fast Path)**: If Texture is highly confident ($P_{spoof} < 0.30$ or $> 0.70$), trust texture alone in ~15.7 ms.
   - **Stage B (Multi-Modal Stacking Escalation)**: If Texture is ambiguous ($0.30 \le P_{spoof} \le 0.70$, ~2.6% of requests), execute stacking meta-classifier (`fusion_model.joblib`) over $[P_{texture}, P_{landmark}, \mathbb{I}_{landmark}, P_{bio}, \mathbb{I}_{bio}]$ to produce the final decision.
5. Result + scores logged to SQLite (`backend/logs.db`)

## Upload path (v2, not built yet)
Real vs. AI-generated image/video detection. Routes and frontend page exist as placeholders only.

## Model swap points & Production Artifacts
All ML logic is isolated behind `backend/engines/*.py`:
- `backend/models/texture_engine.pt`: MobileNetV3-Small (95.03% test accuracy, 0.9789 ROC-AUC, 6.74% ACER)
- `backend/models/landmark_engine.json`: 3D FaceMesh XGBoost (74.09% test accuracy, 0.6905 ROC-AUC, 35.82% ACER)
- `backend/models/biological_engine.json`: Temporal Dynamics XGBoost (92.26% video accuracy, 0.9816 ROC-AUC, 7.88% ACER)
- `backend/models/fusion_model.joblib`: Escalation Stacking Meta-Model (95.11% test accuracy, 0.9788 ROC-AUC, 7.08% ACER)

Each falls back to a deterministic heuristic/mock calculation if its trained artifact is not present in `backend/models/`, ensuring the full REST API and frontend function smoothly in development and testing.

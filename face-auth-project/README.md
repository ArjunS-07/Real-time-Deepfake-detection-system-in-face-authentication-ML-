# 🛡️ Real-Time Face Authentication & Deepfake Detection

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask%20REST%20API-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit%20WebRTC-red.svg)](https://streamlit.io/)
[![PyTorch](https://img.shields.io/badge/Framework-PyTorch-orange.svg)](https://pytorch.org/)
[![MediaPipe](https://img.shields.io/badge/Landmarks-MediaPipe%20FaceMesh-teal.svg)](https://developers.google.com/mediapipe)
[![Docker](https://img.shields.io/badge/Deployment-Docker%20Compose-blue.svg)](https://www.docker.com/)

A multi-modal biometric authentication and anti-spoofing system designed to detect print attacks, screen replay attacks, 3D masks, and deepfakes in real-time video streams. 

The system leverages a decoupled client-server microservice architecture with a Streamlit WebRTC frontend, a Flask inference backend, and a tri-engine biometric verification pipeline orchestrated by a disagreement-aware fusion classifier.

---

## 📑 Table of Contents
- [System Architecture](#-system-architecture)
- [Multi-Engine Detection Pipeline](#-multi-engine-detection-pipeline)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Option A: Local Development](#option-a-local-development)
  - [Option B: Docker Compose](#option-b-docker-compose)
- [API Reference](#-api-reference)
- [Model Artifacts & Inference Fallbacks](#-model-artifacts--inference-fallbacks)
- [Security & Data Privacy](#-security--data-privacy)
- [Roadmap](#-roadmap)

---

## 🏛 System Architecture

The project is structured as two independent services communicating over asynchronous HTTP REST endpoints:

```
                  ┌─────────────────────────────────────────┐
                  │          Streamlit Frontend             │
                  │   - WebRTC webcam frame capture         │
                  │   - Session orchestrator & UI gauges    │
                  └────────────────────┬────────────────────┘
                                       │
                      Base64 Frames    │  HTTP REST (CORS)
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │           Flask Backend API             │
                  │   - Session Manager (in-memory buffer)  │
                  │   - SQLite Audit Logger                 │
                  └────────────────────┬────────────────────┘
                                       │
      ┌────────────────────────────────┼────────────────────────────────┐
      │                                │                                │
      ▼                                ▼                                ▼
┌──────────────┐             ┌────────────────────┐            ┌─────────────────┐
│Engine 1:     │             │Engine 2:           │            │Engine 3:        │
│Texture       │             │3D Landmark         │            │Biological Cues  │
│Analysis      │             │Coherence           │            │& Eye Dynamics   │
│(MobileNetV3) │             │(FaceMesh 468-pts)  │            │(Blink / EAR)    │
└──────┬───────┘             └─────────┬──────────┘            └────────┬────────┘
       │                               │                                │
       └───────────────────────┬───────┴────────────────────────────────┘
                               ▼
            ┌───────────────────────────────────────────┐
            │        Disagreement-Aware Fusion          │
            │   - Stage A: Inter-engine variance check  │
            │   - Stage B: Escalation classifier        │
            │   - Final Decision: [REAL / SPOOF]        │
            └───────────────────────────────────────────┘
```

---

## 🔍 Multi-Engine Detection Pipeline

1. **Texture Analysis Engine (`texture_analysis.py`)**
   - Evaluates micro-texture anomalies, print grid artifacts, moiré patterns, paper reflections, and screen boundary contrasts using PyTorch (MobileNetV3-Small).
   - Generates a normalized real-vs-spoof confidence score in $[0, 1]$.

2. **3D Landmark Coherence Engine (`landmark_coherence.py`)**
   - Tracks 468 3D facial landmarks via Google MediaPipe FaceMesh.
   - Measures planar flatness vs. genuine 3D facial depth, nose-to-jaw spatial vectors, and cross-frame head-pose consistency to expose 2D paper and screen spoofs.

3. **Biological & Eye Dynamics Engine (`biological_cues.py`)**
   - Computes real-time Eye Aspect Ratio (EAR) curves across rolling frame windows.
   - Detects natural involuntary blinking and temporal physiological dynamics, preventing static photo attacks.

4. **Disagreement-Aware Fusion Engine (`fusion.py`)**
   - **Stage A**: Rule-based standard deviation analysis across engine confidences to detect anomalous divergence between models.
   - **Stage B**: Multi-feature escalation classifier (`fusion_model.joblib`) trained on engine scores and disagreement metrics to synthesize a final robust verdict (`REAL` vs. `SPOOF`).

---

## 📂 Repository Structure

```text
face-auth-project/
├── backend/
│   ├── app.py                     # Flask application factory & entrypoint
│   ├── requirements.txt           # Backend dependencies
│   ├── Dockerfile                 # Container specification
│   ├── .env.example               # Environment template
│   ├── db/
│   │   └── database.py            # SQLite schema, frame logging, audit trail
│   ├── engines/
│   │   ├── preprocessing.py       # Face detection, crop alignment & normalization
│   │   ├── texture_analysis.py    # PyTorch MobileNetV3 micro-texture engine
│   │   ├── landmark_coherence.py  # MediaPipe 3D landmark geometry analyzer
│   │   ├── biological_cues.py     # Temporal blink & physiological cues analyzer
│   │   └── fusion.py              # Stacking fusion & disagreement resolution
│   ├── models/                    # Model weights directory (gitignored)
│   │   └── README.md              # Model artifact specifications
│   ├── routes/
│   │   ├── health_routes.py       # API liveness & healthcheck endpoint
│   │   ├── webcam_routes.py       # Session lifecycle & frame inference routes
│   │   └── upload_routes.py       # Offline forensic analysis routes (v2)
│   ├── session/
│   │   └── session_manager.py     # In-memory rolling frame session state
│   └── utils/
│       └── logger.py              # Standardized logging utility
├── frontend/
│   ├── app.py                     # Streamlit landing page & status probe
│   ├── requirements.txt           # Frontend dependencies
│   ├── .streamlit/
│   │   └── config.toml            # UI theme configuration
│   └── pages/
│       ├── 1_webcam.py            # Real-time WebRTC camera authentication page
│       └── 2_upload.py            # Media file forensic inspection page (v2)
├── docs/
│   ├── architecture.md            # In-depth architectural blueprint
│   ├── api_contract.md            # REST payload specifications
│   └── evaluation_report.md       # Benchmarks, APCER, BPCER metrics
├── docker-compose.yml             # Multi-service local deployment manifest
├── .gitignore                     # Git tracking exclusions
└── README.md                      # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or 3.11
- Webcam / video capture device
- Git
- (Optional) Docker & Docker Compose

---

### Option A: Local Development

#### 1. Start Backend API

```powershell
# Open Terminal 1
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1       # On Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Launch Flask server
python app.py
```
> The backend server will start on **`http://localhost:5000`**.

#### 2. Start Frontend UI

```powershell
# Open Terminal 2
cd frontend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1       # On Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit dashboard
streamlit run app.py
```
> The frontend application will open on **`http://localhost:8501`**. Navigate to **"1 webcam"** in the sidebar to test authentication.

---

### Option B: Docker Compose

You can launch both services in isolated containers with a single command:

```bash
docker compose up --build
```

- Frontend: `http://localhost:8501`
- Backend API: `http://localhost:5000`

---

## 📡 API Reference

### Health Check
- **`GET /health`**
  - Response: `{"status": "ok", "service": "face-auth-backend"}`

### Session Lifecycle
- **`POST /predict/session/start`**
  - Initializes a new verification session.
  - Response: `{"session_id": "<uuid>"}`

- **`POST /predict/frame`**
  - Processes a single incoming video frame in Base64 format.
  - Body:
    ```json
    {
      "session_id": "<uuid>",
      "image": "data:image/jpeg;base64,..."
    }
    ```
  - Response:
    ```json
    {
      "session_id": "<uuid>",
      "frame_count": 5,
      "frame_scores": {
        "texture_score": 0.8921,
        "landmark_confidence": 0.9412,
        "blink_score": 0.7845
      }
    }
    ```

- **`POST /predict/session/finalize`**
  - Aggregates temporal frame sequence, computes disagreement, and runs the fusion classifier.
  - Body: `{"session_id": "<uuid>"}`
  - Response:
    ```json
    {
      "session_id": "<uuid>",
      "frame_count": 12,
      "engines": {
        "texture_score": 0.8845,
        "landmark_confidence": 0.9120,
        "blink_score": 0.8401
      },
      "disagreement": 0.0382,
      "fusion_score": 0.8914,
      "decision": "REAL",
      "latency_ms": 142.6
    }
    ```

---

## 🧠 Model Artifacts & Inference Fallbacks

Trained weights are placed in `backend/models/`:
- `texture_engine.pt` — PyTorch MobileNetV3-Small checkpoint
- `landmark_engine.json` — XGBoost landmark geometry model
- `biological_engine.json` — Biological cues & temporal dynamics model
- `fusion_model.joblib` — Multi-engine escalation classifier

> **Zero-Dependency Fallback:** If trained weights are not present in `backend/models/`, each engine automatically falls back to an internal heuristic/mock mode. This allows the full end-to-end integration and UI flow to be tested immediately without downloading heavy weights.

---

## 🔒 Security & Data Privacy

- **Biometric Data Protection**: Raw facial video frames and session captures are saved only in local runtime directories (`backend/data/`) and are strictly excluded from version control via `.gitignore`.
- **Decoupled Architecture**: Biometric feature extraction runs entirely on the backend; the client frontend receives only aggregate confidence metrics.
- **Audit Trails**: All verification results and timestamps are logged to an internal SQLite database (`backend/logs.db`) for tamper-evident review.

---

## 🗺️ Roadmap
- [x] Real-time webcam liveness pipeline (Phase 1 & 2)
- [x] Multi-engine fusion (Texture + 3D Landmark + Biological cues)
- [x] Streamlit WebRTC live feed integration
- [x] Dockerized container deployment
- [ ] **Phase 3 (v2)**: Deepfake forensic inspection for uploaded media files (images/videos)
- [ ] rPPG (remote photoplethysmography) pulse-rate estimation for enhanced liveness

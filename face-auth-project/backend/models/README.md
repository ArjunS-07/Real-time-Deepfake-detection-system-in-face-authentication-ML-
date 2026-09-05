# Backend Models Directory

Trained model artifacts are placed in this directory (excluded from git via `.gitignore`):

| File | Type | Engine | Description |
| :--- | :--- | :--- | :--- |
| `texture_engine.pt` | PyTorch checkpoint | `engines/texture_analysis.py` | MobileNetV3-Small texture anomaly classifier |
| `landmark_engine.json` | XGBoost model | `engines/landmark_coherence.py` | 3D FaceMesh geometric coherence model |
| `biological_engine.json` | Config / Model | `engines/biological_cues.py` | Temporal EAR & blink dynamics evaluator |
| `fusion_model.joblib` | Scikit-learn bundle | `engines/fusion.py` | Stage B escalation stacking classifier |

### Mock / Heuristic Fallbacks
If any model file is absent from this folder, its corresponding engine script in `engines/` automatically falls back to an internal heuristic/mock calculation. This ensures the full REST API and Streamlit UI can be exercised for development and end-to-end integration testing even before model weights are provided.

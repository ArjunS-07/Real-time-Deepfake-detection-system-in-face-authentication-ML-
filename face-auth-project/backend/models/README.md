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

---

### Upgraded Model Specifications & Benchmark Metrics

| Model Artifact | Algorithm | Input Modality & Features | Test Accuracy | ROC-AUC | ACER (ISO/IEC 30107-3) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `texture_engine.pt` | MobileNetV3-Small | Specular & print moiré artifacts (224×224 normalized RGB) | 95.03% | 0.9789 | 6.74% |
| `landmark_engine.json` | XGBoost (Hist) | 20 scale-invariant 3D FaceMesh features (3D PCA planarity, IOD-normalized depths, surface normals, MAR, EAR) | 74.09% | 0.6905 | 35.82% |
| `biological_engine.json` | XGBoost (Hist) | 17 multi-frame temporal biometrics (EAR blink dynamics, MAR micro-motion, rPPG green signal power, head micro-tremor) | 92.26% (video sequences) / 87.41% (full test set) | 0.9816 (video sequences) / 0.7126 (full test set) | 7.88% (video sequences) / 31.86% (full test set) |
| `fusion_model.joblib` | LogisticRegressionCV | Escalation-rule stacking meta-model on multi-modal probabilities | 95.11% | 0.9788 | 7.08% |


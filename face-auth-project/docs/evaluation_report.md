# Biometric Evaluation Report: Presentation Attack Detection (PAD)

This evaluation report summarizes empirical benchmarks, ISO/IEC 30107-3 compliance metrics, and comparative architecture results computed on the preprocessed face crop dataset using the NVIDIA GeForce RTX 2050 GPU pipeline.

For the exhaustive academic analysis, convergence plots, and failure state studies, refer to the full document:  
👉 [TRAINING_AND_EVALUATION_REPORT.md](file:///d:/MAJOR_PROJECT/face-auth-project/docs/TRAINING_AND_EVALUATION_REPORT.md)

---

## 1. Train/Test Split Sensitivity Analysis

Benchmarks computed on MobileNetV3-Small across three canonical evaluation splits:

| Split Ratio | Test Accuracy | ROC-AUC | Precision | Recall (Spoof) | F1-Score | APCER (Spoof $\rightarrow$ Live) | BPCER (Live $\rightarrow$ Spoof) | ACER (Average Error) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **50:50** | 68.50% | 0.7925 | 86.40% | 45.20% | 59.32% | 54.80% | 8.20% | 31.50% |
| **75:25** | 85.60% | 0.9280 | 92.80% | 78.50% | 85.06% | 21.50% | 7.30% | 14.40% |
| **80:20 [Production]** | **92.25%** | **0.9703** | **93.33%** | **91.00%** | **92.15%** | **9.00%** | **6.50%** | **7.75%** |
| **85:15** | 81.33% | 0.9340 | 97.00% | 64.67% | 77.60% | 35.33% | 2.00% | 18.67% |

- **Optimal Configuration**: **80:20 Split** minimizes the Average Classification Error Rate (**ACER = 7.75%**) while securing high spoof sensitivity (**Recall = 91.00%**).

---

## 2. Model Architecture Comparison

Evaluated on the optimal 80:20 test split under identical hardware constraints:

| Architecture | Model Size | GPU Latency | Test Accuracy | ROC-AUC | APCER | BPCER | ACER | Production Decision |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **MobileNetV3-Small** | **1.52 M** | **24.27 ms** | **92.25%** | **0.9703** | **9.00%** | **6.50%** | **7.75%** | **Selected (Optimal Trade-off)** |
| **ResNet-18** | 11.18 M | 10.12 ms | 74.00% | 0.8994 | 51.00% | 1.00% | 26.00% | Excluded (High APCER / Underfit) |
| **Custom Lightweight CNN** | 0.10 M | 2.24 ms | 64.50% | 0.8444 | 69.00% | 2.00% | 35.50% | Excluded (Insufficient Capacity) |

---

## 3. Multi-Modal System Benchmark & Tri-Engine Evaluation

Evaluated across the official held-out test split (**2,636 identity-isolated crops**, 915 unique subjects):

| Authentication Engine | Underlying Architecture | Primary Biometric Modality | Test Accuracy | ROC-AUC | Spoof Recall | APCER ↓ | BPCER ↓ | ACER ↓ | Latency | Operational Decision |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Model 1: Texture Engine** | MobileNetV3-Small | Specular & Moiré Artifacts | 95.03% | 0.9789 | 96.08% | 3.92% | 9.55% | 6.74% | 15.7 ms | **ACTIVE (Stage A Fast-Path) ★** |
| **Model 2: Landmark Engine** | XGBoost (468 Mesh + 3D PCA) | 3D Depth & Facial Symmetry | 74.09% | 0.6905 | 79.99% | 20.01% | 51.63% | 35.82% | 6.3 ms | **ACTIVE (Stage B Secondary)** |
| **Model 3: Biological Engine (Video Sequences)** | XGBoost (17 Temporal Dynamics) | rPPG Pulse & Blink Dynamics | 92.26% | 0.9816 | 92.71% | 7.29% | 8.46% | 7.88% | 18.5 ms | **ACTIVE (Video Verification)** |
| *(Biological Full Set w/ Neutral Prior)* | XGBoost + Image Neutral Fallback | Static Prior + Sequence Cues | 87.41% | 0.7126 | 98.88% | 1.12% | 62.60% | 31.86% | 18.5 ms | *Evaluation Benchmark* |
| **Model 4: Multi-Modal Fusion** | Stacking Meta-Model | Tri-Engine Escalation Fusion | **95.11%** | **0.9788** | **96.41%** | **3.59%** | **10.57%** | **7.08%** | **16.3 ms** | **SELECTED (Full Pipeline) ★** |

- **Upgraded Accuracy**: 3D Landmark Coherence accuracy increased from 69.16% to **74.09%** (ROC-AUC up to **0.6905**, ACER reduced to **35.82%**) via 20 scale-invariant geometric & PCA planarity features. Biological cues test accuracy reached **92.26%** on video sequences with an ROC-AUC of **0.9816** and an ACER of **7.88%** (session-level classification achieved **90.41%** accuracy with ACER **9.55%**).
- **Security Gain**: Multi-Modal Fusion lowers APCER from 3.92% to **3.59%** (higher spoof attack interception rate) while preserving low latency (16.3 ms average).
- **Escalation Strategy**: 97.4% of authentication requests resolve immediately on the fast path; only 2.6% of ambiguous cases trigger Stage B sensor fusion.

---

## 4. High-Resolution Documentation Figures

All figures are generated in [`docs/figures/`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/):
- **Split Benchmark Graphic Table**: [`table1_split_benchmark.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/table1_split_benchmark.png)
- **Epoch Convergence Graphic Table**: [`table2_epoch_convergence.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/table2_epoch_convergence.png)
- **Data Preprocessing & Normalization Pipeline**: [`diagram3_preprocessing_pipeline.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/diagram3_preprocessing_pipeline.png)
- **Architecture Comparison Graphic Table**: [`table4_architecture_comparison.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/table4_architecture_comparison.png)
- **Loss Progression Curves**: [`fig1_loss_epochs.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/fig1_loss_epochs.png)
- **Accuracy & AUC Convergence**: [`fig2_accuracy_epochs.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/fig2_accuracy_epochs.png)
- **Multi-Split ROC Curves**: [`fig3_roc_splits.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/fig3_roc_splits.png)
- **Metrics Bar Chart Across Splits**: [`fig4_metrics_barchart.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/fig4_metrics_barchart.png)
- **Latency vs Accuracy Trade-off**: [`fig5_model_comparison.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/fig5_model_comparison.png)
- **Optimal Split Confusion Matrix**: [`fig6_confusion_matrix.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/fig6_confusion_matrix.png)
- **Multi-Modal Benchmark Graphic Table**: [`table5_multimodal_benchmark.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/table5_multimodal_benchmark.png)
- **Multi-Modal Escalation Architecture Flowchart**: [`diagram8_multimodal_decision_flow.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/diagram8_multimodal_decision_flow.png)
- **Multi-Modal ROC Curves Comparison**: [`fig7_multimodal_roc_comparison.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/fig7_multimodal_roc_comparison.png)
- **Multi-Modal Biometric Metrics Bar Chart**: [`fig8_multimodal_metrics_comparison.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/fig8_multimodal_metrics_comparison.png)
- **Landmark 3D Geometry Feature Importance**: [`fig9_landmark_feature_importance.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/fig9_landmark_feature_importance.png)
- **Biological Cues Feature Importance**: [`fig10_biological_feature_importance.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/fig10_biological_feature_importance.png)
- **Production Fusion Confusion Matrix**: [`fig11_fusion_confusion_matrix.png`](file:///d:/MAJOR_PROJECT/face-auth-project/docs/figures/fig11_fusion_confusion_matrix.png)

---

## 5. Reproducibility & Exported Metrics

Metrics JSON data is archived at:  
- **Texture Experiments**: [`face-auth-project/training/report_metrics.json`](file:///d:/MAJOR_PROJECT/face-auth-project/training/report_metrics.json)  
- **Multi-Modal Suite**: [`face-auth-project/training/multimodal_report_metrics.json`](file:///d:/MAJOR_PROJECT/face-auth-project/training/multimodal_report_metrics.json)

To re-run the benchmark suites:
```powershell
# 1. Texture split & epoch benchmarking
& "d:\MAJOR_PROJECT\mpenv\Scripts\python.exe" -u "d:\MAJOR_PROJECT\face-auth-project\training\run_report_experiments.py"

# 2. Multi-Modal 4-engine evaluation
& "d:\MAJOR_PROJECT\mpenv\Scripts\python.exe" -u "d:\MAJOR_PROJECT\face-auth-project\training\run_multimodal_experiments.py"

# 3. Figure rendering
& "d:\MAJOR_PROJECT\mpenv\Scripts\python.exe" "d:\MAJOR_PROJECT\face-auth-project\training\generate_multimodal_figures.py"
```

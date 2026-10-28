"""
Streamlit Front Page / System Portal.
Presents system architecture and provides direct access to Real-Time Camera Verification.
"""
import os
import streamlit as st

DEFAULT_BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000")
st.session_state["backend_url"] = DEFAULT_BACKEND_URL

st.set_page_config(
    page_title="Biometric Face Authentication",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Global Base Styling */
    .stApp {
        background: #0e1117;
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Container constraints */
    .block-container {
        max-width: 960px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }

    /* Hero Section */
    .hero-tag {
        display: inline-block;
        padding: 4px 12px;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 4px;
        color: #60a5fa;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 0.8rem;
        text-transform: uppercase;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.25;
        margin-bottom: 0.6rem;
    }
    .hero-sub {
        font-size: 1rem;
        color: #94a3b8;
        line-height: 1.6;
        margin-bottom: 1.6rem;
        max-width: 800px;
    }

    /* Feature Cards */
    .card-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin: 1.5rem 0;
    }
    .feature-card {
        background: #161b24;
        border: 1px solid #232a36;
        border-radius: 10px;
        padding: 1.3rem 1.4rem;
        transition: border-color 0.2s ease;
    }
    .feature-card:hover {
        border-color: #3b82f6;
    }
    .card-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 0.4rem;
    }
    .card-desc {
        font-size: 0.86rem;
        color: #94a3b8;
        line-height: 1.5;
        margin: 0;
    }

    /* Callout Box */
    .callout-box {
        background: #131720;
        border: 1px solid #232a36;
        border-left: 3px solid #3b82f6;
        border-radius: 6px;
        padding: 1rem 1.3rem;
        margin: 1.6rem 0;
    }
    .callout-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 0.2rem;
    }
    .callout-desc {
        font-size: 0.85rem;
        color: #94a3b8;
        line-height: 1.5;
        margin: 0;
    }

    /* Metrics Bar */
    .spec-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 1.2rem;
    }
    .spec-pill {
        background: #161b24;
        border: 1px solid #232a36;
        border-radius: 4px;
        padding: 6px 12px;
        font-size: 0.8rem;
        color: #cbd5e1;
    }
    .spec-pill strong {
        color: #f8fafc;
    }

    /* Sidebar Clean Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0e14;
        border-right: 1px solid #1c222e;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Hero Header
st.markdown('<span class="hero-tag">Biometric Security</span>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Face Authentication & Anti-Spoofing</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">'
    'Real-time presentation attack detection integrating micro-texture screening, '
    '3D facial geometry coherence, and involuntary biological temporal signals.'
    '</div>',
    unsafe_allow_html=True,
)

# Primary Call to Action
col1, col2 = st.columns([1, 2])
with col1:
    st.page_link(
        "pages/1_webcam.py",
        label="Open Real-Time Camera",
        help="Launch real-time camera verification",
    )

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# 3 Modality Feature Cards
st.markdown(
    """
    <div class="card-grid">
        <div class="feature-card">
            <div class="card-title">1. Micro-Texture Analysis</div>
            <p class="card-desc">
                Screens face crops with MobileNetV3-Small to identify specular screen reflections,
                print moiré artifacts, and display color-banding in real time.
            </p>
        </div>
        <div class="feature-card">
            <div class="card-title">2. 3D Landmark Geometry</div>
            <p class="card-desc">
                Extracts 468 facial depth landmarks to evaluate facial depth relief, nose protrusion,
                and planarity against flat photo printouts and screen replays.
            </p>
        </div>
        <div class="feature-card">
            <div class="card-title">3. Biological Temporal Cues</div>
            <p class="card-desc">
                Measures natural eye-aspect-ratio (EAR) blink transitions, lip micro-motion,
                and facial skin chrominance (rPPG pulse variation) across video frames.
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Architecture Callout
st.markdown(
    """
    <div class="callout-box">
        <div class="callout-title">Multi-Modal Fusion Architecture</div>
        <p class="callout-desc">
            The system processes authentic traffic instantaneously through the fast-path screening layer.
            Ambiguous edge cases automatically escalate to multi-modal stacking fusion to ensure high
            accuracy and defense against presentation attacks.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Benchmark Summary
st.markdown(
    """
    <div class="spec-grid">
        <span class="spec-pill">Evaluation Standard: <strong>ISO/IEC 30107-3</strong></span>
        <span class="spec-pill">Overall Accuracy: <strong>95.11%</strong></span>
        <span class="spec-pill">Spoof Recall: <strong>96.41%</strong></span>
        <span class="spec-pill">Average Latency: <strong>16.3 ms</strong></span>
    </div>
    """,
    unsafe_allow_html=True,
)

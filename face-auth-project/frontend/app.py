"""
Streamlit entrypoint / landing page.
Actual pages live in pages/1_webcam.py (live path, build now)
and pages/2_upload.py (placeholder, v2).
"""
import os
import requests
import streamlit as st

DEFAULT_BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000")

st.set_page_config(
    page_title="Face Auth Project",
    page_icon="🛡️",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #0f172a 0%, #111827 100%); color: #e5e7eb; }
    .hero-title { font-size: 2.2rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.2rem; }
    .hero-sub { color: #94a3b8; font-size: 1rem; margin-bottom: 2rem; }
    .card {
        background: #1e293b; border: 1px solid #334155; border-radius: 12px;
        padding: 1.2rem 1.4rem; margin-bottom: 1rem;
    }
    .card h4 { margin: 0 0 0.4rem 0; color: #f1f5f9; }
    .card p { margin: 0; color: #94a3b8; font-size: 0.9rem; }
    .conn-ok { color: #4ade80; font-weight: 600; }
    .conn-bad { color: #f87171; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="hero-title">🛡️ Face Authentication & Deepfake Detection</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Capstone project — webcam liveness path (active) '
    'and upload detection path (planned, v2)</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="card">
        <h4>🎥 Webcam Liveness Check</h4>
        <p>Real-time liveness &amp; deepfake detection via webcam. Open the
        "1 webcam" page from the sidebar to try it.</p>
    </div>
    <div class="card">
        <h4>📤 Upload Detection (v2)</h4>
        <p>Real vs. AI-generated image/video detection. Placeholder — not built yet.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()
st.markdown("### ⚙️ Backend Connection")
backend_url = st.text_input("Backend URL", value=DEFAULT_BACKEND_URL, key="backend_url")

if st.button("Check connection"):
    try:
        r = requests.get(f"{backend_url}/health", timeout=3)
        if r.status_code == 200:
            st.markdown('<span class="conn-ok">● Connected</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="conn-bad">● Backend responded with an error</span>', unsafe_allow_html=True)
    except requests.exceptions.RequestException:
        st.markdown('<span class="conn-bad">● Not reachable</span>', unsafe_allow_html=True)

st.caption("Use the sidebar to navigate to the webcam page.")

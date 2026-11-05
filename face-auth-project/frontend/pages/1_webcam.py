"""
Webcam liveness check page — Native Instant Hardware Camera.
Multi-modal biometric verification with single-screen zero-scroll dashboard layout.
"""
import os
import streamlit as st
import streamlit.components.v1 as components

DEFAULT_BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000")
backend_url = st.session_state.get("backend_url", DEFAULT_BACKEND_URL)

st.set_page_config(
    page_title="Real-Time Verification",
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

    /* Prevent vertical scrolling and enforce single-screen fit */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
    }

    /* Tight container constraints to fit standard laptop/desktop viewports */
    .block-container {
        max-width: 1140px !important;
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    /* Minimize Streamlit default top bar */
    header[data-testid="stHeader"] {
        height: 1.6rem !important;
        background: transparent !important;
    }

    /* Compact Header Bar */
    .page-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #1c222e;
    }
    .header-title-box {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .page-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
    }
    .page-badge {
        font-size: 0.7rem;
        font-weight: 600;
        background: #1e293b;
        color: #38bdf8;
        border: 1px solid #334155;
        padding: 2px 7px;
        border-radius: 4px;
        letter-spacing: 0.4px;
    }
    .page-sub {
        font-size: 0.8rem;
        color: #8b949e;
        margin: 0;
    }

    /* Clean Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0b0e14;
        border-right: 1px solid #1c222e;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-header">
        <div class="header-title-box">
            <span class="page-title">Real-Time Verification</span>
            <span class="page-badge">Tri-Engine PAD</span>
        </div>
        <div class="page-sub">Webcam-based multi-modal biometric presentation attack detection</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Embedded Native Instant Camera with side-by-side single-screen dashboard
components.html(
    f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8"/>
      <style>
        * {{
          box-sizing: border-box;
        }}
        body {{
          margin: 0;
          padding: 0;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          color: #f0f3f6;
          background: transparent;
          overflow: hidden;
        }}

        /* 2-Column Balanced Dashboard Grid */
        .dashboard-grid {{
          display: grid;
          grid-template-columns: 380px 1fr;
          gap: 16px;
          align-items: start;
        }}

        /* Left Column: Camera Feed */
        .camera-col {{
          display: flex;
          flex-direction: column;
        }}
        .video-box {{
          position: relative;
          width: 100%;
          aspect-ratio: 4 / 3;
          background: #090c10;
          border-radius: 10px;
          overflow: hidden;
          border: 1px solid #232a36;
        }}
        video {{
          width: 100%;
          height: 100%;
          object-fit: cover;
          display: block;
          transform: scaleX(-1);
          background: #090c10;
        }}

        /* Subtle Face Framing Guide */
        .face-guide {{
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 135px;
          height: 175px;
          border: 2px dashed rgba(59, 130, 246, 0.45);
          border-radius: 50% 50% 45% 45%;
          pointer-events: none;
        }}
        .live-tag {{
          position: absolute;
          top: 8px;
          left: 8px;
          background: rgba(14, 17, 23, 0.85);
          border: 1px solid #232a36;
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 0.68rem;
          font-weight: 600;
          color: #10b981;
          display: flex;
          align-items: center;
          gap: 5px;
          letter-spacing: 0.5px;
        }}
        .live-dot {{
          width: 5px;
          height: 5px;
          background: #10b981;
          border-radius: 50%;
          animation: pulse 1.8s infinite;
        }}
        @keyframes pulse {{
          0% {{ opacity: 1; }}
          50% {{ opacity: 0.3; }}
          100% {{ opacity: 1; }}
        }}

        /* Button Controls */
        .btn-grid {{
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 8px;
          margin: 10px 0 6px 0;
        }}
        .btn {{
          width: 100%;
          padding: 8px 12px;
          border-radius: 6px;
          font-size: 0.85rem;
          font-weight: 600;
          cursor: pointer;
          text-align: center;
          transition: background 0.15s ease, border-color 0.15s ease;
          border: 1px solid transparent;
        }}
        .btn-primary {{
          background: #2563eb;
          color: #ffffff;
          border-color: #3b82f6;
        }}
        .btn-primary:hover:not(:disabled) {{
          background: #1d4ed8;
          border-color: #60a5fa;
        }}
        .btn-secondary {{
          background: #161b24;
          color: #c9d1d9;
          border-color: #232a36;
        }}
        .btn-secondary:hover:not(:disabled) {{
          background: #212631;
          color: #f0f3f6;
          border-color: #30363d;
        }}
        .btn:disabled {{
          opacity: 0.45;
          cursor: not-allowed;
        }}

        /* Progress Bar & Status */
        .progress-track {{
          width: 100%;
          height: 4px;
          background: #161b24;
          border-radius: 4px;
          overflow: hidden;
          margin: 4px 0 4px 0;
        }}
        .progress-fill {{
          height: 100%;
          width: 0%;
          background: #3b82f6;
          border-radius: 4px;
          transition: width 0.3s ease;
        }}
        .status-box {{
          font-size: 0.76rem;
          color: #8b949e;
          text-align: center;
          min-height: 18px;
          line-height: 1.3;
        }}

        /* Right Column: Biometric Results & Multi-Engine Dashboard */
        .biometric-col {{
          display: flex;
          flex-direction: column;
        }}

        /* Decision Banner */
        .decision-banner {{
          background: #161b24;
          border: 1px solid #232a36;
          border-radius: 8px;
          padding: 10px 14px;
          margin-bottom: 10px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-left: 4px solid #64748b;
          transition: border-left 0.3s ease;
        }}
        .decision-banner.real {{
          border-left: 4px solid #10b981;
        }}
        .decision-banner.spoof {{
          border-left: 4px solid #f43f5e;
        }}
        .decision-banner.scanning {{
          border-left: 4px solid #3b82f6;
        }}
        .decision-banner.standby {{
          border-left: 4px solid #64748b;
        }}

        .decision-text-group {{
          display: flex;
          flex-direction: column;
        }}
        .decision-eyebrow {{
          font-size: 0.65rem;
          font-weight: 700;
          color: #64748b;
          letter-spacing: 0.5px;
        }}
        .decision-title {{
          font-size: 1.1rem;
          font-weight: 700;
          letter-spacing: 0.5px;
          line-height: 1.2;
        }}
        .decision-title.real {{ color: #10b981; }}
        .decision-title.spoof {{ color: #f43f5e; }}
        .decision-title.scanning {{ color: #60a5fa; }}
        .decision-title.standby {{ color: #94a3b8; }}

        .fusion-box {{
          display: flex;
          flex-direction: column;
          align-items: center;
        }}
        .fusion-label {{
          font-size: 0.68rem;
          color: #8b949e;
          font-weight: 600;
        }}
        .fusion-val {{
          font-size: 1.2rem;
          font-weight: 700;
          color: #f0f3f6;
          line-height: 1.1;
        }}
        .decision-badge {{
          padding: 3px 10px;
          border-radius: 4px;
          font-size: 0.72rem;
          font-weight: 700;
          letter-spacing: 0.5px;
        }}
        .decision-badge.real {{
          background: rgba(16, 185, 129, 0.15);
          color: #10b981;
          border: 1px solid rgba(16, 185, 129, 0.3);
        }}
        .decision-badge.spoof {{
          background: rgba(244, 63, 94, 0.15);
          color: #f43f5e;
          border: 1px solid rgba(244, 63, 94, 0.3);
        }}
        .decision-badge.scanning {{
          background: rgba(59, 130, 246, 0.15);
          color: #60a5fa;
          border: 1px solid rgba(59, 130, 246, 0.3);
        }}
        .decision-badge.standby {{
          background: rgba(100, 116, 139, 0.15);
          color: #94a3b8;
          border: 1px solid rgba(100, 116, 139, 0.3);
        }}

        /* Graphical Score Grid */
        .score-grid {{
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 10px;
          margin-bottom: 10px;
        }}
        .score-card {{
          background: #161b24;
          border: 1px solid #232a36;
          border-radius: 8px;
          padding: 10px 6px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }}
        .gauge-svg {{
          width: 76px;
          height: 76px;
        }}
        .gauge-bg {{
          fill: none;
          stroke: #212631;
          stroke-width: 8;
        }}
        .gauge-ring {{
          fill: none;
          stroke-width: 8;
          stroke-linecap: round;
          stroke-dasharray: 251.33;
          stroke-dashoffset: 251.33;
          transform: rotate(-90deg);
          transform-origin: 50% 50%;
          transition: stroke-dashoffset 0.6s ease, stroke 0.4s ease;
        }}
        .gauge-pct {{
          font-size: 16px;
          font-weight: 700;
          fill: #f0f3f6;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        .gauge-num {{
          font-size: 10px;
          font-weight: 500;
          fill: #8b949e;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        .engine-label {{
          font-size: 0.8rem;
          font-weight: 600;
          color: #f0f3f6;
          margin-top: 6px;
          text-align: center;
        }}
        .engine-sub {{
          font-size: 0.68rem;
          color: #64748b;
          text-align: center;
        }}

        /* Summary Bar */
        .summary-bar {{
          display: flex;
          justify-content: space-between;
          background: #131720;
          border: 1px solid #232a36;
          border-radius: 6px;
          padding: 6px 12px;
          font-size: 0.74rem;
          color: #8b949e;
          margin-bottom: 8px;
        }}
        .summary-bar strong {{
          color: #f0f3f6;
        }}

        /* Architecture Info Note */
        .audit-note {{
          background: #11151e;
          border: 1px solid #1c222e;
          border-radius: 6px;
          padding: 7px 10px;
          font-size: 0.72rem;
          color: #64748b;
          display: flex;
          align-items: center;
          gap: 6px;
          line-height: 1.35;
        }}
        .audit-note strong {{
          color: #94a3b8;
        }}

        @media (max-width: 780px) {{
          .dashboard-grid {{
            grid-template-columns: 1fr;
          }}
        }}
      </style>
    </head>
    <body>
      <div class="dashboard-grid">
        <!-- Left Column: Camera Feed & Controls -->
        <div class="camera-col">
          <div class="video-box">
            <video id="webcam-vid" autoplay playsinline muted></video>
            <div class="face-guide"></div>
            <div class="live-tag">
              <span class="live-dot"></span> LIVE FEED
            </div>
          </div>

          <div class="btn-grid">
            <button id="start-btn" class="btn btn-primary" onclick="startCheck()">Start Verification</button>
            <button class="btn btn-secondary" onclick="resetCheck()">Reset</button>
          </div>

          <div class="progress-track">
            <div id="prog-bar" class="progress-fill"></div>
          </div>
          <div id="status-box" class="status-box">Ready. Position face inside the guide and click Start.</div>
        </div>

        <!-- Right Column: Biometric Analysis Dashboard -->
        <div class="biometric-col" id="result-section">
          <!-- Decision Banner -->
          <div id="decision-banner" class="decision-banner standby">
            <div class="decision-text-group">
              <span class="decision-eyebrow">VERIFICATION VERDICT</span>
              <div class="decision-title standby" id="decision-title">STANDBY</div>
            </div>
            <div class="fusion-box">
              <span class="fusion-label">Fusion Score</span>
              <span class="fusion-val" id="val-fusion">--</span>
            </div>
            <div id="decision-badge" class="decision-badge standby">READY</div>
          </div>

          <!-- Multi-Engine Circular Score Cards -->
          <div class="score-grid">
            <!-- Texture Engine -->
            <div class="score-card">
              <svg class="gauge-svg" viewBox="0 0 100 100">
                <circle class="gauge-bg" cx="50" cy="50" r="40" />
                <circle id="ring-tex" class="gauge-ring" cx="50" cy="50" r="40" stroke="#2d3748" />
                <text x="50" y="46" text-anchor="middle" dominant-baseline="central" class="gauge-pct" id="pct-tex">0%</text>
                <text x="50" y="62" text-anchor="middle" dominant-baseline="central" class="gauge-num" id="val-tex">0.00</text>
              </svg>
              <div class="engine-label">Texture Engine</div>
              <div class="engine-sub">MobileNetV3</div>
            </div>

            <!-- Landmark Engine -->
            <div class="score-card">
              <svg class="gauge-svg" viewBox="0 0 100 100">
                <circle class="gauge-bg" cx="50" cy="50" r="40" />
                <circle id="ring-lm" class="gauge-ring" cx="50" cy="50" r="40" stroke="#2d3748" />
                <text x="50" y="46" text-anchor="middle" dominant-baseline="central" class="gauge-pct" id="pct-lm">0%</text>
                <text x="50" y="62" text-anchor="middle" dominant-baseline="central" class="gauge-num" id="val-lm">0.00</text>
              </svg>
              <div class="engine-label">Landmark Engine</div>
              <div class="engine-sub">468-pt Mesh</div>
            </div>

            <!-- Biological Engine -->
            <div class="score-card">
              <svg class="gauge-svg" viewBox="0 0 100 100">
                <circle class="gauge-bg" cx="50" cy="50" r="40" />
                <circle id="ring-bio" class="gauge-ring" cx="50" cy="50" r="40" stroke="#2d3748" />
                <text x="50" y="46" text-anchor="middle" dominant-baseline="central" class="gauge-pct" id="pct-bio">0%</text>
                <text x="50" y="62" text-anchor="middle" dominant-baseline="central" class="gauge-num" id="val-bio">0.00</text>
              </svg>
              <div class="engine-label">Biological Engine</div>
              <div class="engine-sub">Blink Dynamics</div>
            </div>
          </div>

          <!-- Summary Bar -->
          <div class="summary-bar">
            <span>Consensus Disagreement: <strong id="val-disagree">--</strong></span>
            <span>Frames Analyzed: <strong id="val-frames">0 / 8</strong></span>
          </div>

          <!-- Architecture Info Note -->
          <div class="audit-note">
            <span>🛡️ <strong>Tri-Engine PAD Architecture:</strong> MobileNetV3 micro-texture &bull; 3D planar coherence &bull; Involuntary blink dynamics.</span>
          </div>
        </div>
      </div>

      <script>
        const BACKEND_URL = "{backend_url}";
        const FRAMES_TO_COLLECT = 8;
        const CIRCUMFERENCE = 251.33;

        const videoEl = document.getElementById("webcam-vid");
        const startBtn = document.getElementById("start-btn");
        const statusBox = document.getElementById("status-box");
        const progBar = document.getElementById("prog-bar");
        const resultSec = document.getElementById("result-section");
        let isProcessing = false;

        // Initialize hardware camera
        navigator.mediaDevices.getUserMedia({{
          video: {{ width: {{ ideal: 640 }}, height: {{ ideal: 480 }}, facingMode: "user" }},
          audio: false
        }})
        .then(stream => {{
          videoEl.srcObject = stream;
          statusBox.textContent = "Ready. Position face inside the guide and click Start.";
        }})
        .catch(err => {{
          statusBox.textContent = "Camera access error: " + err.message;
        }});

        function resetGauges() {{
          ["tex", "lm", "bio"].forEach(key => {{
            const ring = document.getElementById("ring-" + key);
            const pctEl = document.getElementById("pct-" + key);
            const valEl = document.getElementById("val-" + key);
            if (ring) {{
              ring.style.strokeDashoffset = CIRCUMFERENCE;
              ring.style.stroke = "#2d3748";
            }}
            if (pctEl) pctEl.textContent = "0%";
            if (valEl) valEl.textContent = "0.00";
          }});
        }}

        function setGauge(ringId, pctId, valId, score) {{
          const num = Math.max(0.0, Math.min(1.0, score));
          const ring = document.getElementById(ringId);
          const pctEl = document.getElementById(pctId);
          const valEl = document.getElementById(valId);

          const offset = CIRCUMFERENCE * (1.0 - num);
          if (ring) {{
            ring.style.strokeDashoffset = offset;
            if (num >= 0.70) {{
              ring.style.stroke = "#10b981"; // Emerald
            }} else if (num >= 0.40) {{
              ring.style.stroke = "#f59e0b"; // Amber
            }} else {{
              ring.style.stroke = "#f43f5e"; // Rose
            }}
          }}

          if (pctEl) pctEl.textContent = Math.round(num * 100) + "%";
          if (valEl) valEl.textContent = num.toFixed(2);
        }}

        async function startCheck() {{
          if (isProcessing) return;
          isProcessing = true;
          startBtn.disabled = true;

          // Transition to scanning state
          const banner = document.getElementById("decision-banner");
          const title = document.getElementById("decision-title");
          const badge = document.getElementById("decision-badge");
          banner.className = "decision-banner scanning";
          title.className = "decision-title scanning";
          title.textContent = "ANALYZING...";
          badge.className = "decision-badge scanning";
          badge.textContent = "SCANNING";
          document.getElementById("val-fusion").textContent = "...";
          document.getElementById("val-disagree").textContent = "...";
          document.getElementById("val-frames").textContent = "0 / " + FRAMES_TO_COLLECT;

          progBar.style.width = "5%";
          statusBox.textContent = "Starting session...";

          let sessionId = null;
          try {{
            const res = await fetch(BACKEND_URL + "/predict/session/start", {{ method: "POST" }});
            if (!res.ok) throw new Error("Backend HTTP " + res.status);
            const data = await res.json();
            sessionId = data.session_id;
            statusBox.textContent = "Capturing frames...";
          }} catch (e) {{
            statusBox.textContent = "Unable to reach authentication backend (" + e.message + ").";
            banner.className = "decision-banner standby";
            title.className = "decision-title standby";
            title.textContent = "OFFLINE";
            badge.className = "decision-badge spoof";
            badge.textContent = "ERROR";
            document.getElementById("val-fusion").textContent = "--";
            startBtn.disabled = false;
            isProcessing = false;
            return;
          }}

          // Capture and send frames
          const canvas = document.createElement("canvas");
          canvas.width = 640;
          canvas.height = 480;
          const ctx = canvas.getContext("2d");

          for (let i = 1; i <= FRAMES_TO_COLLECT; i++) {{
            ctx.save();
            ctx.translate(canvas.width, 0);
            ctx.scale(-1, 1);
            ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
            ctx.restore();

            const b64 = canvas.toDataURL("image/jpeg", 0.85);

            try {{
              await fetch(BACKEND_URL + "/predict/frame", {{
                method: "POST",
                headers: {{ "Content-Type": "application/json" }},
                body: JSON.stringify({{ session_id: sessionId, image: b64 }})
              }});
            }} catch (e) {{
              console.warn("Frame send warning:", e);
            }}

            const pct = Math.round((i / FRAMES_TO_COLLECT) * 88);
            progBar.style.width = pct + "%";
            statusBox.textContent = "Capturing frame " + i + " of " + FRAMES_TO_COLLECT + "...";
            document.getElementById("val-frames").textContent = i + " / " + FRAMES_TO_COLLECT;

            await new Promise(r => setTimeout(r, 400));
          }}

          // Finalize session
          statusBox.textContent = "Evaluating multi-modal score...";
          progBar.style.width = "95%";

          try {{
            const finalizeRes = await fetch(BACKEND_URL + "/predict/session/finalize", {{
              method: "POST",
              headers: {{ "Content-Type": "application/json" }},
              body: JSON.stringify({{ session_id: sessionId }})
            }});

            if (!finalizeRes.ok) throw new Error("Finalize HTTP " + finalizeRes.status);
            const result = await finalizeRes.json();
            displayFinalResult(result);
            progBar.style.width = "100%";
            statusBox.textContent = "Verification complete.";
          }} catch (e) {{
            statusBox.textContent = "Session finalization error: " + e.message;
            banner.className = "decision-banner spoof";
            title.className = "decision-title spoof";
            title.textContent = "ERROR";
            badge.className = "decision-badge spoof";
            badge.textContent = "FAILED";
          }} finally {{
            startBtn.disabled = false;
            isProcessing = false;
          }}
        }}

        function displayFinalResult(result) {{
          const decision = (result.decision || "UNKNOWN").toUpperCase();
          const isReal = decision === "REAL";

          const banner = document.getElementById("decision-banner");
          const title = document.getElementById("decision-title");
          const badge = document.getElementById("decision-badge");

          if (isReal) {{
            banner.className = "decision-banner real";
            title.className = "decision-title real";
            title.textContent = "AUTHENTIC";
            badge.className = "decision-badge real";
            badge.textContent = "PASS";
          }} else {{
            banner.className = "decision-banner spoof";
            title.className = "decision-title spoof";
            title.textContent = "SPOOF ATTACK";
            badge.className = "decision-badge spoof";
            badge.textContent = "REJECTED";
          }}

          const engines = result.engines || {{}};
          const tex = parseFloat(engines.texture_score || 0);
          const lm = parseFloat(engines.landmark_confidence || 0);
          const bio = parseFloat(engines.blink_score || 0);

          // Update individual graphical circular gauges
          setGauge("ring-tex", "pct-tex", "val-tex", tex);
          setGauge("ring-lm", "pct-lm", "val-lm", lm);
          setGauge("ring-bio", "pct-bio", "val-bio", bio);

          // Update Fusion & Summary
          const fusionScore = result.fusion_score !== undefined ? parseFloat(result.fusion_score) : 0;
          document.getElementById("val-fusion").textContent = (fusionScore * 100).toFixed(1) + "%";

          const disagree = result.disagreement !== undefined ? parseFloat(result.disagreement) : 0;
          document.getElementById("val-disagree").textContent = disagree.toFixed(3);
          document.getElementById("val-frames").textContent = (result.frame_count || FRAMES_TO_COLLECT) + " / " + FRAMES_TO_COLLECT;
        }}

        function resetCheck() {{
          progBar.style.width = "0%";
          statusBox.textContent = "Ready. Position face inside the guide and click Start.";
          const banner = document.getElementById("decision-banner");
          const title = document.getElementById("decision-title");
          const badge = document.getElementById("decision-badge");
          banner.className = "decision-banner standby";
          title.className = "decision-title standby";
          title.textContent = "STANDBY";
          badge.className = "decision-badge standby";
          badge.textContent = "READY";
          document.getElementById("val-fusion").textContent = "--";
          document.getElementById("val-disagree").textContent = "--";
          document.getElementById("val-frames").textContent = "0 / " + FRAMES_TO_COLLECT;
          resetGauges();
          startBtn.disabled = false;
          isProcessing = false;
        }}

        // Initialize default idle state
        resetGauges();
      </script>
    </body>
    </html>
    """,
    height=415,
    scrolling=False,
)

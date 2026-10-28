"""
Webcam liveness check page — Native Instant Hardware Camera.
Multi-modal biometric verification with graphical circular score gauges.
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

    /* Container constraints */
    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Clean Header */
    .page-header {
        margin-bottom: 1.5rem;
    }
    .page-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.3rem;
    }
    .page-sub {
        font-size: 0.92rem;
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
        <div class="page-title">Real-Time Verification</div>
        <div class="page-sub">Webcam-based multi-modal authentication</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Embedded Native Instant Camera with graphical circular score representations
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
        }}

        /* Camera Viewport */
        .camera-container {{
          max-width: 520px;
          margin: 0 auto;
        }}
        .video-box {{
          position: relative;
          width: 100%;
          background: #090c10;
          border-radius: 12px;
          overflow: hidden;
          border: 1px solid #232a36;
        }}
        video {{
          width: 100%;
          height: auto;
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
          width: 200px;
          height: 260px;
          border: 2px dashed rgba(59, 130, 246, 0.4);
          border-radius: 50% 50% 45% 45%;
          pointer-events: none;
        }}
        .live-tag {{
          position: absolute;
          top: 12px;
          left: 12px;
          background: rgba(14, 17, 23, 0.8);
          border: 1px solid #232a36;
          padding: 3px 10px;
          border-radius: 4px;
          font-size: 0.72rem;
          font-weight: 600;
          color: #10b981;
          display: flex;
          align-items: center;
          gap: 6px;
          letter-spacing: 0.5px;
        }}
        .live-dot {{
          width: 6px;
          height: 6px;
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
          gap: 10px;
          margin: 14px 0 8px 0;
        }}
        .btn {{
          width: 100%;
          padding: 10px 16px;
          border-radius: 6px;
          font-size: 0.9rem;
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
          margin: 10px 0 6px 0;
        }}
        .progress-fill {{
          height: 100%;
          width: 0%;
          background: #3b82f6;
          border-radius: 4px;
          transition: width 0.3s ease;
        }}
        .status-box {{
          font-size: 0.82rem;
          color: #8b949e;
          text-align: center;
          min-height: 20px;
          margin-bottom: 8px;
        }}

        /* Results Display */
        #result-section {{
          margin-top: 22px;
        }}

        /* Decision Banner */
        .decision-banner {{
          background: #161b24;
          border: 1px solid #232a36;
          border-radius: 8px;
          padding: 16px 20px;
          margin-bottom: 16px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }}
        .decision-banner.real {{
          border-left: 4px solid #10b981;
        }}
        .decision-banner.spoof {{
          border-left: 4px solid #f43f5e;
        }}
        .decision-title {{
          font-size: 1.15rem;
          font-weight: 700;
          letter-spacing: 0.5px;
        }}
        .decision-title.real {{
          color: #10b981;
        }}
        .decision-title.spoof {{
          color: #f43f5e;
        }}
        .fusion-box {{
          display: flex;
          align-items: baseline;
          gap: 6px;
        }}
        .fusion-label {{
          font-size: 0.82rem;
          color: #8b949e;
        }}
        .fusion-val {{
          font-size: 1.25rem;
          font-weight: 700;
          color: #f0f3f6;
        }}
        .decision-badge {{
          padding: 4px 12px;
          border-radius: 4px;
          font-size: 0.8rem;
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

        /* Graphical Score Grid (Engine Name + Score Meter) */
        .score-grid {{
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
          margin-bottom: 14px;
        }}
        .score-card {{
          background: #161b24;
          border: 1px solid #232a36;
          border-radius: 8px;
          padding: 16px 12px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }}
        .gauge-svg {{
          width: 90px;
          height: 90px;
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
          font-size: 18px;
          font-weight: 700;
          fill: #f0f3f6;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        .gauge-num {{
          font-size: 11px;
          font-weight: 500;
          fill: #8b949e;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        .engine-label {{
          font-size: 0.88rem;
          font-weight: 600;
          color: #f0f3f6;
          margin-top: 10px;
          text-align: center;
        }}

        /* Summary Footnote */
        .summary-bar {{
          display: flex;
          justify-content: space-around;
          background: #131720;
          border: 1px solid #232a36;
          border-radius: 6px;
          padding: 8px 14px;
          font-size: 0.8rem;
          color: #8b949e;
        }}
        .summary-bar strong {{
          color: #f0f3f6;
        }}

        @media (max-width: 640px) {{
          .score-grid {{
            grid-template-columns: 1fr;
          }}
        }}
      </style>
    </head>
    <body>
      <div class="camera-container">
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

      <!-- Result Section (Graphical Biometric Representation) -->
      <div id="result-section" style="display: none;">
        <!-- Decision Banner -->
        <div id="decision-banner" class="decision-banner real">
          <div class="decision-title real" id="decision-title">AUTHENTIC</div>
          <div class="fusion-box">
            <span class="fusion-label">Fusion Score:</span>
            <span class="fusion-val" id="val-fusion">0.00</span>
          </div>
          <div id="decision-badge" class="decision-badge real">PASS</div>
        </div>

        <!-- Graphical Score Cards (Engine Name + Score Meter) -->
        <div class="score-grid">
          <!-- Texture Engine -->
          <div class="score-card">
            <svg class="gauge-svg" viewBox="0 0 100 100">
              <circle class="gauge-bg" cx="50" cy="50" r="40" />
              <circle id="ring-tex" class="gauge-ring" cx="50" cy="50" r="40" stroke="#10b981" />
              <text x="50" y="46" text-anchor="middle" dominant-baseline="central" class="gauge-pct" id="pct-tex">0%</text>
              <text x="50" y="62" text-anchor="middle" dominant-baseline="central" class="gauge-num" id="val-tex">0.00</text>
            </svg>
            <div class="engine-label">Texture Engine</div>
          </div>

          <!-- Landmark Engine -->
          <div class="score-card">
            <svg class="gauge-svg" viewBox="0 0 100 100">
              <circle class="gauge-bg" cx="50" cy="50" r="40" />
              <circle id="ring-lm" class="gauge-ring" cx="50" cy="50" r="40" stroke="#10b981" />
              <text x="50" y="46" text-anchor="middle" dominant-baseline="central" class="gauge-pct" id="pct-lm">0%</text>
              <text x="50" y="62" text-anchor="middle" dominant-baseline="central" class="gauge-num" id="val-lm">0.00</text>
            </svg>
            <div class="engine-label">Landmark Engine</div>
          </div>

          <!-- Biological Engine -->
          <div class="score-card">
            <svg class="gauge-svg" viewBox="0 0 100 100">
              <circle class="gauge-bg" cx="50" cy="50" r="40" />
              <circle id="ring-bio" class="gauge-ring" cx="50" cy="50" r="40" stroke="#10b981" />
              <text x="50" y="46" text-anchor="middle" dominant-baseline="central" class="gauge-pct" id="pct-bio">0%</text>
              <text x="50" y="62" text-anchor="middle" dominant-baseline="central" class="gauge-num" id="val-bio">0.00</text>
            </svg>
            <div class="engine-label">Biological Engine</div>
          </div>
        </div>

        <!-- Summary Bar -->
        <div class="summary-bar">
          <span>Engine Consensus: <strong id="val-disagree">0.00</strong></span>
          <span>Frames Analyzed: <strong id="val-frames">8</strong></span>
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

        async function startCheck() {{
          if (isProcessing) return;
          isProcessing = true;
          startBtn.disabled = true;
          resultSec.style.display = "none";
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
          }} finally {{
            startBtn.disabled = false;
            isProcessing = false;
          }}
        }}

        function setGauge(ringId, pctId, valId, score) {{
          const num = Math.max(0.0, Math.min(1.0, score));
          const ring = document.getElementById(ringId);
          const pctEl = document.getElementById(pctId);
          const valEl = document.getElementById(valId);

          const offset = CIRCUMFERENCE * (1.0 - num);
          ring.style.strokeDashoffset = offset;

          pctEl.textContent = Math.round(num * 100) + "%";
          valEl.textContent = num.toFixed(2);

          // Color threshold
          if (num >= 0.70) {{
            ring.style.stroke = "#10b981"; // Emerald
          }} else if (num >= 0.40) {{
            ring.style.stroke = "#f59e0b"; // Amber
          }} else {{
            ring.style.stroke = "#f43f5e"; // Rose
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
          document.getElementById("val-frames").textContent = result.frame_count || FRAMES_TO_COLLECT;

          resultSec.style.display = "block";
        }}

        function resetCheck() {{
          progBar.style.width = "0%";
          statusBox.textContent = "Ready. Position face inside the guide and click Start.";
          resultSec.style.display = "none";
          startBtn.disabled = false;
          isProcessing = false;
        }}
      </script>
    </body>
    </html>
    """,
    height=860,
    scrolling=False,
)

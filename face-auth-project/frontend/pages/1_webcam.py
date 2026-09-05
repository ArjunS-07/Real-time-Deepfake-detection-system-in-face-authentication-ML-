"""
Webcam liveness check page — Native Instant Camera (Option A).

Flow:
  1. User clicks "Start liveness check" -> POST /predict/session/start
  2. Webcam frames are captured via browser hardware video and sent to
     POST /predict/frame at a fixed interval, accumulating in the session.
  3. Once enough frames are collected, POST /predict/session/finalize
     runs the fusion engine and returns the final REAL/SPOOF decision.
"""
import os
import streamlit as st
import streamlit.components.v1 as components

DEFAULT_BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000")

st.set_page_config(page_title="Webcam Liveness Check", page_icon="🎥", layout="centered")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #0f172a 0%, #111827 100%); color: #e5e7eb; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎥 Webcam Liveness Check")
st.caption("Look at the camera and click Start — a few seconds of frames will be analyzed.")

with st.sidebar:
    backend_url = st.text_input(
        "Backend URL", value=st.session_state.get("backend_url", DEFAULT_BACKEND_URL)
    )
    st.session_state["backend_url"] = backend_url

# Embedded Native Instant Camera with exact original Streamlit card & engine scores display
components.html(
    f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8"/>
      <style>
        body {{
          margin: 0;
          padding: 0;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          color: #e5e7eb;
          background: transparent;
        }}
        .video-box {{
          position: relative;
          width: 100%;
          max-width: 520px;
          margin: 0 auto;
          background: #0b1120;
          border-radius: 12px;
          overflow: hidden;
          border: 1px solid #334155;
        }}
        video {{
          width: 100%;
          height: auto;
          display: block;
          transform: scaleX(-1);
          background: #020617;
        }}
        .btn-grid {{
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin: 14px 0 10px 0;
        }}
        .st-btn {{
          width: 100%;
          padding: 10px 16px;
          background: #1e293b;
          color: #f8fafc;
          border: 1px solid #475569;
          border-radius: 8px;
          font-size: 0.95rem;
          font-weight: 600;
          cursor: pointer;
          text-align: center;
          transition: background 0.2s, border-color 0.2s;
        }}
        .st-btn:hover:not(:disabled) {{
          background: #334155;
          border-color: #94a3b8;
        }}
        .st-btn-primary {{
          background: #0284c7;
          border-color: #38bdf8;
        }}
        .st-btn-primary:hover:not(:disabled) {{
          background: #0369a1;
          border-color: #0ea5e9;
        }}
        .st-btn:disabled {{
          opacity: 0.5;
          cursor: not-allowed;
        }}
        .status-box {{
          font-size: 0.9rem;
          color: #94a3b8;
          text-align: center;
          margin: 8px 0;
          min-height: 22px;
        }}
        .progress-track {{
          width: 100%;
          height: 8px;
          background: #1e293b;
          border-radius: 999px;
          overflow: hidden;
          margin: 10px 0;
        }}
        .progress-fill {{
          height: 100%;
          width: 0%;
          background: #ff4b4b;
          transition: width 0.3s ease;
        }}
        .card {{
          background: #1e293b;
          border: 1px solid #334155;
          border-radius: 12px;
          padding: 1.1rem 1.3rem;
          margin: 1rem 0;
        }}
        .card h4 {{
          margin: 0 0 0.6rem 0;
          color: #cbd5e1;
          font-size: 0.9rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }}
        .badge {{
          display: inline-block;
          padding: 0.35rem 0.9rem;
          border-radius: 999px;
          font-weight: 700;
          font-size: 1.1rem;
        }}
        .badge-real {{
          background: rgba(34, 197, 94, 0.15);
          color: #4ade80;
          border: 1px solid rgba(34, 197, 94, 0.4);
        }}
        .badge-spoof {{
          background: rgba(239, 68, 68, 0.15);
          color: #f87171;
          border: 1px solid rgba(239, 68, 68, 0.4);
        }}
        .engine-score-row {{
          margin: 12px 0 16px 0;
        }}
        .engine-score-label {{
          display: flex;
          justify-content: space-between;
          font-size: 0.9rem;
          color: #e5e7eb;
          margin-bottom: 6px;
        }}
        .engine-progress-bar {{
          width: 100%;
          height: 10px;
          background: #0f172a;
          border-radius: 999px;
          overflow: hidden;
        }}
        .engine-progress-fill {{
          height: 100%;
          background: #ff4b4b;
          border-radius: 999px;
          transition: width 0.4s ease;
        }}
        .metrics-grid {{
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
          margin-top: 14px;
          margin-bottom: 24px;
        }}
        .metric-card {{
          background: #1e293b;
          border: 1px solid #334155;
          border-radius: 10px;
          padding: 12px 14px;
        }}
        .metric-title {{
          font-size: 0.8rem;
          color: #94a3b8;
          margin-bottom: 4px;
        }}
        .metric-value {{
          font-size: 1.5rem;
          font-weight: 700;
          color: #f8fafc;
        }}
      </style>
    </head>
    <body>
      <div class="video-box">
        <video id="webcam-vid" autoplay playsinline muted></video>
      </div>

      <div class="btn-grid">
        <button id="start-btn" class="st-btn st-btn-primary" onclick="startCheck()">▶ Start liveness check</button>
        <button class="st-btn" onclick="resetCheck()">↺ Reset</button>
      </div>

      <div class="progress-track">
        <div id="prog-bar" class="progress-fill"></div>
      </div>
      <div id="status-box" class="status-box">Camera active. Click Start when ready.</div>

      <!-- Result section (appears exactly like original Streamlit card) -->
      <div id="result-section" style="display: none;">
        <div class="card">
          <h4>Final Decision</h4>
          <span id="decision-badge" class="badge">--</span>
        </div>

        <div class="card">
          <h4>Engine Scores (session average)</h4>

          <div class="engine-score-row">
            <div class="engine-score-label">
              <span>Texture Analysis (MobileNetV3): <strong id="val-texture">0.00</strong></span>
            </div>
            <div class="engine-progress-bar">
              <div id="bar-texture" class="engine-progress-fill" style="width: 0%;"></div>
            </div>
          </div>

          <div class="engine-score-row">
            <div class="engine-score-label">
              <span>Landmark Coherence (MediaPipe): <strong id="val-landmark">0.00</strong></span>
            </div>
            <div class="engine-progress-bar">
              <div id="bar-landmark" class="engine-progress-fill" style="width: 0%;"></div>
            </div>
          </div>

          <div class="engine-score-row">
            <div class="engine-score-label">
              <span>Blink / Bio Cue Score: <strong id="val-blink">0.00</strong></span>
            </div>
            <div class="engine-progress-bar">
              <div id="bar-blink" class="engine-progress-fill" style="width: 0%;"></div>
            </div>
          </div>
        </div>

        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-title">Fusion Score</div>
            <div id="val-fusion" class="metric-value">--</div>
          </div>
          <div class="metric-card">
            <div class="metric-title">Disagreement (σ)</div>
            <div id="val-disagree" class="metric-value">--</div>
          </div>
          <div class="metric-card">
            <div class="metric-title">Frames Used</div>
            <div id="val-frames" class="metric-value">8</div>
          </div>
        </div>
      </div>

      <script>
        const BACKEND_URL = "{backend_url}";
        const FRAMES_TO_COLLECT = 8;
        const videoEl = document.getElementById("webcam-vid");
        const startBtn = document.getElementById("start-btn");
        const statusBox = document.getElementById("status-box");
        const progBar = document.getElementById("prog-bar");
        const resultSec = document.getElementById("result-section");
        let isProcessing = false;

        // Instant hardware camera initialization (<500ms)
        navigator.mediaDevices.getUserMedia({{
          video: {{ width: {{ ideal: 640 }}, height: {{ ideal: 480 }}, facingMode: "user" }},
          audio: false
        }})
        .then(stream => {{
          videoEl.srcObject = stream;
          statusBox.textContent = "Camera ready. Click Start to begin verification.";
        }})
        .catch(err => {{
          statusBox.textContent = "Camera error: " + err.message;
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
            if (!res.ok) throw new Error("Backend error (" + res.status + ")");
            const data = await res.json();
            sessionId = data.session_id;
            statusBox.textContent = "Session started: " + sessionId.substring(0, 8) + "...";
          }} catch (e) {{
            statusBox.textContent = "Could not start session — is the backend running? (" + e.message + ")";
            startBtn.disabled = false;
            isProcessing = false;
            return;
          }}

          // Capture and send 8 frames
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
              console.warn("Frame send error:", e);
            }}

            const pct = Math.round((i / FRAMES_TO_COLLECT) * 90);
            progBar.style.width = pct + "%";
            statusBox.textContent = "Collecting frames: " + i + "/" + FRAMES_TO_COLLECT;

            await new Promise(r => setTimeout(r, 450));
          }}

          // Finalize session
          statusBox.textContent = "Running fusion engine...";
          progBar.style.width = "95%";

          try {{
            const finalizeRes = await fetch(BACKEND_URL + "/predict/session/finalize", {{
              method: "POST",
              headers: {{ "Content-Type": "application/json" }},
              body: JSON.stringify({{ session_id: sessionId }})
            }});

            const result = await finalizeRes.json();
            displayFinalResult(result);
            progBar.style.width = "100%";
            statusBox.textContent = "Verification complete.";
          }} catch (e) {{
            statusBox.textContent = "Finalize failed: " + e.message;
          }} finally {{
            startBtn.disabled = false;
            isProcessing = false;
          }}
        }}

        function displayFinalResult(result) {{
          const decision = result.decision || "UNKNOWN";
          const isReal = decision === "REAL";
          const badge = document.getElementById("decision-badge");
          badge.textContent = decision;
          badge.className = "badge " + (isReal ? "badge-real" : "badge-spoof");

          const engines = result.engines || {{}};
          const tex = parseFloat(engines.texture_score || 0);
          const lm = parseFloat(engines.landmark_confidence || 0);
          const bio = parseFloat(engines.blink_score || 0);

          // Update texture score & bar
          document.getElementById("val-texture").textContent = tex.toFixed(2);
          document.getElementById("bar-texture").style.width = Math.min(Math.max(tex * 100, 0), 100) + "%";

          // Update landmark score & bar
          document.getElementById("val-landmark").textContent = lm.toFixed(2);
          document.getElementById("bar-landmark").style.width = Math.min(Math.max(lm * 100, 0), 100) + "%";

          // Update blink score & bar
          document.getElementById("val-blink").textContent = bio.toFixed(2);
          document.getElementById("bar-blink").style.width = Math.min(Math.max(bio * 100, 0), 100) + "%";

          // Metrics
          document.getElementById("val-fusion").textContent = (result.fusion_score !== undefined ? result.fusion_score.toFixed(2) : "--");
          document.getElementById("val-disagree").textContent = (result.disagreement !== undefined ? result.disagreement.toFixed(2) : "--");
          document.getElementById("val-frames").textContent = result.frame_count || 8;

          resultSec.style.display = "block";
        }}

        function resetCheck() {{
          progBar.style.width = "0%";
          statusBox.textContent = "Ready for new check.";
          resultSec.style.display = "none";
          startBtn.disabled = false;
          isProcessing = false;
        }}
      </script>
    </body>
    </html>
    """,
    height=1080,
    scrolling=False,
)

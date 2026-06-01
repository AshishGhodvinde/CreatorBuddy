import streamlit as st
import sqlite3
from config import init_database, DATABASE_PATH
from ui import render_trend_tab, render_studio_tab, render_analytics_tab

st.set_page_config(
    page_title="CreatorBuddy AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

try:
    db_path = init_database()
except Exception as e:
    st.error(f"Database initialization failed: {e}")
    st.stop()

for key, default in {
    "discovered_trends":    [],
    "selected_trend":       None,
    "viral_package":        None,
    "generated_video_path": None,
    "virality_report":      None,
    "active_tab":           "trends",
    "show_history":         False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
  --ink:          #111111;
  --bg-cream:     #F4F0EA;
  --surface:      #FFFFFF;
  --border-soft:  #E5E2DC;
  --border-hard:  #111111;
  --text-1:       #111111;
  --text-2:       #4A5568;
  --text-3:       #9CA3AF;
  --accent:       #FFD25A;
  --accent-2:     #60A5FA;
  --lime:         #4ADE80;
  --red:          #FB7171;
  --font-display: 'Syne', sans-serif;
  --font-sans:    'Space Grotesk', sans-serif;
  --r-sm:  6px;
  --r-md:  12px;
  --r-lg:  16px;
}

#MainMenu, footer, header              { visibility: hidden !important; }
div[data-testid="stToolbar"]          { display: none !important; }
div[data-testid="stDecoration"]       { display: none !important; }
div[data-testid="stStatusWidget"]     { display: none !important; }
[data-testid="collapsedControl"]      { display: none !important; }
section[data-testid="stSidebar"]      { display: none !important; }

.stApp, [data-testid="stAppViewContainer"] {
  background-color: #F4F0EA !important;
  background-image: 
    linear-gradient(rgba(17, 17, 17, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(17, 17, 17, 0.02) 1px, transparent 1px),
    radial-gradient(circle, #C8C2B8 1px, transparent 1px) !important;
  background-size: 80px 80px, 80px 80px, 20px 20px !important;
  font-family: var(--font-sans) !important;
}
.main .block-container {
  padding: 0 2.5rem 5rem !important;
  max-width: 1440px;
  margin: 0 auto;
}

html, body, h1, h2, h3, h4, h5, h6,
p, span, div, label, input, textarea, button, option, select {
  font-family: var(--font-sans) !important;
  color: var(--text-1) !important;
}
h1, h2, h3 {
  font-family: var(--font-display) !important;
  font-weight: 800 !important;
  letter-spacing: -0.02em;
}
label[data-testid="stWidgetLabel"] > div > p {
  color: var(--text-2) !important;
  font-size: 0.82rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.06em !important;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0px); }
  50%       { transform: translateY(-8px); }
}
@keyframes logoGlow {
  0%, 100% { filter: drop-shadow(0 0 20px rgba(255,210,90,0.3)); }
  50%       { filter: drop-shadow(0 0 50px rgba(255,210,90,0.6)) drop-shadow(0 0 80px rgba(251,113,113,0.25)); }
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulseDot {
  0%,100% { box-shadow: 0 0 0 0 rgba(74,222,128,0.4); }
  50%     { box-shadow: 0 0 0 6px rgba(74,222,128,0); }
}

.cb-hero {
  text-align: center;
  padding: 2.8rem 0 1.6rem;
}
.cb-wordmark {
  font-family: var(--font-display) !important;
  font-size: clamp(3.2rem, 7vw, 5.2rem);
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.04em;
  background: linear-gradient(135deg, #FFD25A 0%, #FB7171 55%, #60A5FA 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: inline-block;
  animation: logoFloat 4s ease-in-out infinite, logoGlow 3s ease-in-out infinite;
  cursor: default;
  user-select: none;
}
.cb-tagline {
  font-family: var(--font-sans) !important;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-3) !important;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  margin: 10px 0 16px;
  animation: fadeUp 0.7s ease 0.3s both;
}
.cb-live-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: rgba(74,222,128,0.07);
  border: 1px solid rgba(74,222,128,0.2);
  border-radius: 50px;
  padding: 5px 16px;
  animation: fadeUp 0.7s ease 0.5s both;
}
.cb-live-dot {
  display: inline-block;
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--lime);
  animation: pulseDot 2s ease-in-out infinite;
}
.cb-live-text {
  font-size: 0.62rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #4ADE80 !important;
}

.cb-nav-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0;
  background: var(--surface);
  border: 2px solid #111111 !important;
  border-radius: 14px;
  padding: 6px;
  max-width: 100% !important;
  margin: 0 auto 2rem;
  box-shadow: 4px 4px 0px #111111 !important;
  animation: fadeUp 0.6s ease 0.15s both;
}

div.stButton > button {
  font-family: var(--font-sans) !important;
  font-size: 0.88rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.03em !important;
  padding: 9px 22px !important;
  border-radius: 10px !important;
  height: auto !important;
  width: 100% !important;
  background: #FFFFFF !important;
  color: var(--text-1) !important;
  border: 2px solid #111111 !important;
  box-shadow: 3px 3px 0px #111111 !important;
  transition: all 0.15s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
  margin: 0 !important;
}
div.stButton > button:hover {
  transform: translate(-1.5px, -1.5px) !important;
  box-shadow: 4.5px 4.5px 0px #111111 !important;
  background: #FFFFFF !important;
  color: var(--text-1) !important;
}
div.stButton > button:active {
  transform: translate(1.5px, 1.5px) !important;
  box-shadow: 1.5px 1.5px 0px #111111 !important;
}

div.stButton > button[data-testid="stBaseButton-primary"],
div.stButton > button[class*="primary"] {
  background: var(--accent) !important;
  color: var(--text-1) !important;
  font-weight: 800 !important;
  border: 2px solid #111111 !important;
  box-shadow: 3px 3px 0px #111111 !important;
}
div.stButton > button[data-testid="stBaseButton-primary"]:hover,
div.stButton > button[class*="primary"]:hover {
  background: var(--accent) !important;
  transform: translate(-1.5px, -1.5px) !important;
  box-shadow: 4.5px 4.5px 0px #111111 !important;
}

.cb-history-btn div.stButton > button {
  font-size: 0.76rem !important;
  font-weight: 700 !important;
  padding: 7px 18px !important;
  border-radius: 50px !important;
  background: #FFFFFF !important;
  border: 2px solid #111111 !important;
  color: var(--text-2) !important;
  box-shadow: 2px 2px 0px #111111 !important;
  width: auto !important;
}
.cb-history-btn div.stButton > button:hover {
  color: var(--text-1) !important;
  transform: translate(-1px, -1px) !important;
  box-shadow: 3px 3px 0px #111111 !important;
  background: #FFFFFF !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
  background:    var(--surface) !important;
  border:        2px solid #111111 !important;
  border-radius: var(--r-lg) !important;
  box-shadow:    4px 4px 0px #111111 !important;
  transition:    all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
  transform:   translate(-2px, -2px) !important;
  box-shadow:  6px 6px 0px #111111 !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
textarea {
  background:    #FFFFFF !important;
  border:        2px solid #111111 !important;
  border-radius: var(--r-md) !important;
  color:         var(--text-1) !important;
  font-family:   var(--font-sans) !important;
  box-shadow:    2px 2px 0px #111111 !important;
  transition:    all 0.15s ease !important;
}
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="input"]  > div:focus-within,
textarea:focus {
  border-color: var(--accent) !important;
  transform: translate(-1px, -1px) !important;
  box-shadow: 3px 3px 0px #111111 !important;
}
ul[role="listbox"] {
  background: #FFFFFF !important;
  border: 2px solid #111111 !important;
  border-radius: var(--r-md) !important;
  box-shadow: 4px 4px 0px #111111 !important;
}
li[role="option"] {
  background: #FFFFFF !important;
  color: var(--text-1) !important;
  font-weight: 600 !important;
  transition: background 0.15s !important;
}
li[role="option"]:hover {
  background: var(--accent) !important;
}

.cb-label {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-2);
  margin: 14px 0 8px;
  font-family: var(--font-sans);
}
.cb-divider {
  width: 100%;
  height: 1px;
  background: linear-gradient(to right, transparent, var(--border-soft), transparent);
  margin: 6px 0 20px;
}
div[data-testid="stProgressBar"] > div > div {
  background: linear-gradient(90deg, var(--accent), var(--red)) !important;
  border-radius: 4px !important;
}
div[data-testid="stMetricValue"] {
  font-family: var(--font-display) !important;
  font-size: 2.4rem !important;
  font-weight: 800 !important;
  color: var(--text-1) !important;
}

.cb-history-drawer {
  background: var(--surface);
  border: 2px solid #111111 !important;
  border-radius: var(--r-lg);
  padding: 20px 24px;
  margin-bottom: 20px;
  box-shadow: 4px 4px 0px #111111 !important;
  animation: fadeUp 0.3s ease;
}
.cb-history-item {
  background: var(--bg-cream);
  border: 2px solid #111111 !important;
  border-radius: 10px;
  padding: 12px 14px;
  box-shadow: 2px 2px 0px #111111 !important;
  transition: all 0.15s ease;
}
.cb-history-item:hover {
  border-color: var(--accent) !important;
  transform: translate(-1px, -1px) !important;
  box-shadow: 3px 3px 0px #111111 !important;
}

.cb-decor-sparkle {
  position: absolute;
  font-size: 3rem;
  opacity: 0.08;
  z-index: 0;
  pointer-events: none;
  animation: floatDecor 8s ease-in-out infinite;
  user-select: none;
}
.cb-decor-1 { top: 12%; left: 4%; animation-delay: 0s; }
.cb-decor-2 { top: 62%; left: 6%; animation-delay: 2s; font-size: 4rem; }
.cb-decor-3 { top: 18%; right: 4%; animation-delay: 4s; }
.cb-decor-4 { top: 68%; right: 5%; animation-delay: 6s; font-size: 3.5rem; }

@keyframes floatDecor {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50%       { transform: translateY(-15px) rotate(8deg); }
}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D5D0C9; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #B0AAA0; }
</style>

<div class="cb-decor-sparkle cb-decor-1">✨</div>
<div class="cb-decor-sparkle cb-decor-2">🎬</div>
<div class="cb-decor-sparkle cb-decor-3">💡</div>
<div class="cb-decor-sparkle cb-decor-4">📈</div>
""", unsafe_allow_html=True)

h_left, h_center, h_right = st.columns([0.8, 3.4, 0.8])
with h_center:
    st.markdown("""
    <div class="cb-hero" style="text-align: center; padding: 2rem 0 1.2rem;">
      <div class="cb-wordmark">CreatorBuddy</div>
      <p class="cb-tagline" style="margin-top: 8px;">Autonomous AI Viral Reel Agent &nbsp;·&nbsp; Powered by Gemini 2.5</p>
      <div class="cb-live-badge" style="margin-top: 4px;">
        <span class="cb-live-dot"></span>
        <span class="cb-live-text">Live Connection</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
with h_right:
    st.markdown("<div style='height: 2.3rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="cb-history-btn" style="text-align: right;">', unsafe_allow_html=True)
    history_label = "Hide History" if st.session_state["show_history"] else "Past Runs"
    btn_history = st.button(history_label, key="nav_history", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="cb-nav-wrap" id="cb-nav">', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    btn_trends = st.button(
        "Trend Discovery",
        key="nav_trends",
        use_container_width=True,
        type="primary" if st.session_state["active_tab"] == "trends" else "secondary"
    )
with c2:
    btn_studio = st.button(
        "Creator Studio",
        key="nav_studio",
        use_container_width=True,
        type="primary" if st.session_state["active_tab"] == "studio" else "secondary"
    )
with c3:
    btn_analytics = st.button(
        "Performance",
        key="nav_analytics",
        use_container_width=True,
        type="primary" if st.session_state["active_tab"] == "analytics" else "secondary"
    )
st.markdown('</div>', unsafe_allow_html=True)

if btn_trends:
    st.session_state["active_tab"] = "trends"
    st.rerun()
elif btn_studio:
    st.session_state["active_tab"] = "studio"
    st.rerun()
elif btn_analytics:
    st.session_state["active_tab"] = "analytics"
    st.rerun()
elif btn_history:
    st.session_state["show_history"] = not st.session_state["show_history"]
    st.rerun()

st.markdown("<div class='cb-divider'></div>", unsafe_allow_html=True)

if st.session_state["show_history"]:
    def fetch_generation_history():
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT c.id, t.topic, t.niche, t.score as trend_score,
                       c.script, c.ig_caption, c.li_post, c.video_path,
                       c.virality_score, c.visual_keywords, t.timestamp, t.id as trend_id
                FROM content c
                INNER JOIN trends t ON c.trend_id = t.id
                ORDER BY c.id DESC
            """)
            cols = [col[0] for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception:
            return []
        finally:
            conn.close()

    history = fetch_generation_history()

    st.markdown('<div class="cb-history-drawer">', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:0.7rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; '
        'color:var(--text-2); margin:0 0 14px;">Past Runs</p>',
        unsafe_allow_html=True
    )

    if not history:
        st.markdown(
            '<p style="font-size:0.82rem; color:var(--text-3); text-align:center; padding:16px 0;">No runs yet. Compile your first blueprint to see history here.</p>',
            unsafe_allow_html=True
        )
    else:
        cols = st.columns(min(len(history[:5]), 5))
        for i, item in enumerate(history[:5]):
            with cols[i]:
                st.markdown(
                    f'<div class="cb-history-item">'
                    f'<p style="font-size:0.6rem; font-weight:800; color:var(--text-3); margin:0 0 4px; text-transform:uppercase; letter-spacing:0.06em;">Run #{item["id"]} · {item["niche"]}</p>'
                    f'<p style="font-size:0.78rem; font-weight:700; color:var(--text-1); margin:0 0 6px; line-height:1.3;">'
                    f'{item["topic"][:42]}{"…" if len(item["topic"]) > 42 else ""}</p>'
                    f'<p style="font-size:0.7rem; color:var(--lime); margin:0; font-weight:700;">Score: {item["virality_score"]}/100</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if st.button("Restore", key=f"restore_{item['id']}", use_container_width=True):
                    kw_str  = item.get("visual_keywords", "")
                    visuals = [k.strip() for k in kw_str.split("|") if k.strip()] if kw_str else [
                        "Technology Innovation", "Digital Transformation", "Future of Work"
                    ]
                    st.session_state.selected_trend = {
                        "id": item["trend_id"], "topic": item["topic"],
                        "niche": item["niche"],  "score": item["trend_score"],
                        "timestamp": item["timestamp"]
                    }
                    st.session_state.viral_package = {
                        "script": item["script"], "linkedin_post": item["li_post"],
                        "instagram_caption": item["ig_caption"], "visual_keywords": visuals
                    }
                    st.session_state.generated_video_path = item["video_path"]
                    from core.predictor import ViralityPredictorModel
                    st.session_state.virality_report = ViralityPredictorModel().predict_content_virality(item["script"])
                    st.session_state["active_tab"] = "analytics"
                    st.toast(f"Restored Run #{item['id']}", icon="✅")
                    st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    _, reset_col = st.columns([5, 1])
    with reset_col:
        if st.button("Reset Workspace", key="reset_ws", use_container_width=True):
            for k in ["discovered_trends", "selected_trend", "viral_package",
                      "generated_video_path", "virality_report"]:
                st.session_state[k] = [] if k == "discovered_trends" else None
            st.session_state["active_tab"] = "trends"
            st.session_state["show_history"] = False
            st.toast("Workspace reset", icon="🧹")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state["active_tab"] == "trends":
    render_trend_tab()
elif st.session_state["active_tab"] == "studio":
    render_studio_tab()
elif st.session_state["active_tab"] == "analytics":
    render_analytics_tab()

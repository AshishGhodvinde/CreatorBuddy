import sqlite3
import streamlit as st
from datetime import datetime
from core.intake import TrendDiscoveryEngine
from config import DATABASE_PATH

NICHE_STYLES = {
    "ai":             {"color": "#818CF8", "bg": "rgba(129,140,248,0.05)"},
    "technology":     {"color": "#38BDF8", "bg": "rgba(56,189,248,0.05)"},
    "business":       {"color": "#0D9488", "bg": "rgba(13,148,136,0.05)"},
    "startups":       {"color": "#F59E0B", "bg": "rgba(245,158,11,0.05)"},
    "finance":        {"color": "#10B981", "bg": "rgba(16,185,129,0.05)"},
    "creator economy":{"color": "#8B5CF6", "bg": "rgba(139,92,246,0.05)"},
    "sports":         {"color": "#F87171", "bg": "rgba(248,113,113,0.05)"},
    "entertainment":  {"color": "#C084FC", "bg": "rgba(192,132,252,0.05)"},
    "politics":       {"color": "#FB923C", "bg": "rgba(251,146,60,0.05)"},
    "gaming":         {"color": "#60A5FA", "bg": "rgba(96,165,250,0.05)"},
    "health & fitness":{"color": "#4ADE80", "bg": "rgba(74,222,128,0.05)"},
}

def _score_bar(value: float, color: str) -> str:
    w = max(min(value, 100), 0)
    return (
        f'<div style="height:8px;background:#FFFFFF;border:2px solid #111111;border-radius:10px;margin-top:6px;overflow:hidden;">'
        f'<div style="height:100%;width:{w}%;background:{color};border-right:2px solid #111111;'
        f'transition:width 0.8s ease-in-out;"></div></div>'
    )

def save_trend_to_db(topic: str, niche: str, score: float, velocity: int, search: int, novelty: int, engagement: int, relevance: int) -> int:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO trends (topic, niche, score, timestamp, velocity, search_interest, novelty, engagement_potential, audience_relevance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (topic, niche, score, timestamp, velocity, search, novelty, engagement, relevance)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def render_trend_tab():
    st.markdown("""
    <div style="padding:0.5rem 0 0.25rem;">
      <h2 style="font-family: var(--font-display); font-size: 2.2rem; font-weight: 800;
                 color: var(--text-1); margin: 0; text-transform: uppercase; line-height:1.1;">
        Discover what's surging
      </h2>
      <p style="font-size:0.85rem; color:var(--text-2); margin:6px 0 0;">
        Real-time intelligence from Reddit, YouTube, Google News, and Hacker News refined by Gemini.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        niche = st.selectbox(
            "Niche",
            ["AI", "Technology", "Business", "Startups", "Finance", "Creator Economy", "Sports", "Entertainment", "Politics", "Gaming", "Health & Fitness"],
            key="niche_selector",
            label_visibility="collapsed"
        )
    with col_btn:
        search_clicked = st.button(
            "Discover Trends", type="primary", use_container_width=True
        )

    if search_clicked:
        with st.spinner("Analyzing surging global trends..."):
            try:
                engine = TrendDiscoveryEngine()
                raw = engine.combine_and_rank_trends(niche)
                db_trends = []
                for t in raw:
                    t["id"] = save_trend_to_db(
                        t["topic"], t["niche"], t["score"],
                        t.get("velocity", 80), t.get("search_interest", 80), t.get("novelty", 80),
                        t.get("engagement_potential", 80), t.get("audience_relevance", 80)
                    )
                    db_trends.append(t)
                st.session_state.discovered_trends = db_trends
                st.toast(f"Identified {len(db_trends)} trending topics", icon="✅")
            except Exception as e:
                st.error(f"Intake error: {e}")

    if st.session_state.discovered_trends:
        st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            '<p class="cb-label">Ranked by Machine Learning Trend Score</p>',
            unsafe_allow_html=True
        )

        for idx, trend in enumerate(st.session_state.discovered_trends):
            score     = trend["score"]
            niche_key = trend["niche"].lower()
            style     = NICHE_STYLES.get(niche_key, NICHE_STYLES["ai"])
            color     = style["color"]
            is_sel    = (
                st.session_state.selected_trend is not None and
                st.session_state.selected_trend.get("id") == trend["id"]
            )

            with st.container(border=True):
                col_rank, col_body, col_action = st.columns([0.65, 4.5, 1.1])

                with col_rank:
                    st.markdown(
                        f'<div style="text-align:center; padding:8px 0;">'
                        f'<p style="font-family: var(--font-display); font-size:2.2rem; '
                        f'font-weight:800; color:{color}; margin:0; line-height:1;">{score:.0f}</p>'
                        f'<p style="font-size:0.56rem; color:var(--text-3); margin:2px 0 0; '
                        f'text-transform:uppercase; letter-spacing:0.08em; font-weight:700;">ML score</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                with col_body:
                    st.markdown(
                        f'<div style="padding:8px 0;">'
                        f'<span style="background:{style["bg"]}; color:{color}; '
                        f'border:2px solid #111111; padding:4px 12px; border-radius:50px; '
                        f'font-size:0.7rem; font-weight:800; letter-spacing:0.05em; '
                        f'text-transform:uppercase; box-shadow: 2px 2px 0px #111111;">'
                        f'{trend["niche"]}</span>'
                        f'<p style="font-family: var(--font-sans); font-size:1.1rem; '
                        f'font-weight:700; color:var(--text-1); '
                        f'margin:12px 0 10px; line-height:1.4;">{trend["topic"]}</p>'
                        f'<div style="display: flex; flex-wrap: wrap; gap: 16px; margin-top: 15px;">'
                        f'<div style="flex: 1; min-width: 110px;">'
                        f'<p style="font-size: 0.58rem; color: var(--text-2); margin: 0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Growth Velocity</p>'
                        f'<p style="font-size: 0.82rem; font-weight: 800; color: {color}; margin: 2px 0 0;">+{trend["velocity"]}%</p>'
                        f'{_score_bar(trend["velocity"], color)}'
                        f'</div>'
                        f'<div style="flex: 1; min-width: 110px;">'
                        f'<p style="font-size: 0.58rem; color: var(--text-2); margin: 0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Search Interest</p>'
                        f'<p style="font-size: 0.82rem; font-weight: 800; color: var(--text-1); margin: 2px 0 0;">{trend["search_interest"]}</p>'
                        f'{_score_bar(trend["search_interest"], "var(--text-2)")}'
                        f'</div>'
                        f'<div style="flex: 1; min-width: 110px;">'
                        f'<p style="font-size: 0.58rem; color: var(--text-2); margin: 0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Engagement</p>'
                        f'<p style="font-size: 0.82rem; font-weight: 800; color: var(--text-1); margin: 2px 0 0;">{trend.get("engagement_potential", 80)}</p>'
                        f'{_score_bar(trend.get("engagement_potential", 80), "var(--accent-2)")}'
                        f'</div>'
                        f'<div style="flex: 1; min-width: 110px;">'
                        f'<p style="font-size: 0.58rem; color: var(--text-2); margin: 0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Novelty</p>'
                        f'<p style="font-size: 0.82rem; font-weight: 800; color: var(--text-1); margin: 2px 0 0;">{trend["novelty"]}</p>'
                        f'{_score_bar(trend["novelty"], "var(--red)")}'
                        f'</div>'
                        f'<div style="flex: 1; min-width: 110px;">'
                        f'<p style="font-size: 0.58rem; color: var(--text-2); margin: 0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Relevance</p>'
                        f'<p style="font-size: 0.82rem; font-weight: 800; color: var(--text-1); margin: 2px 0 0;">{trend.get("audience_relevance", 80)}</p>'
                        f'{_score_bar(trend.get("audience_relevance", 80), "var(--lime)")}'
                        f'</div>'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    
                    from core.trend_ml_model import TrendMLRanker
                    explain_report = TrendMLRanker().get_explainability_report(
                        velocity=trend["velocity"],
                        search=trend["search_interest"],
                        engagement=trend.get("engagement_potential", 80),
                        novelty=trend["novelty"],
                        relevance=trend.get("audience_relevance", 80)
                    )
                    with st.expander("💡 Machine Learning Score Decision Breakdown", expanded=False):
                        st.markdown(
                            f'<div style="background:#F4F0EA; border:2px solid #111111; border-radius:10px; padding:15px; margin-top:10px; box-shadow: 2px 2px 0px #111111; color:#111111;">'
                            f'<p style="font-size:0.82rem; font-weight:800; text-transform:uppercase; letter-spacing:0.04em; margin:0 0 10px; color:#111111;">'
                            f'🤖 Random Forest Decision Analytics</p>'
                            f'<p style="font-size:0.78rem; color:#4A5568; margin:0 0 12px; line-height:1.4; font-weight:600;">'
                            f'Our ensemble ML model predicted this topic\'s composite score by evaluating non-linear features against a baseline historical average of <strong>{explain_report["baseline_score"]}</strong>. Here are the exact feature importances for this prediction:</p>'
                            f'<div style="display:flex; flex-direction:column; gap:8px;">'
                            + "".join([
                                f'<div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px dashed #D5D0C9; padding-bottom:4px;">'
                                f'<span style="font-size:0.75rem; font-weight:700; color:#111111;">🎯 {f_name}</span>'
                                f'<span style="font-size:0.75rem; font-weight:800; background:var(--accent); border:1px solid #111111; padding:1px 8px; border-radius:50px;">{contrib}</span>'
                                f'</div>'
                                for f_name, contrib in explain_report["contributions"].items()
                            ]) +
                            f'</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                with col_action:
                    st.write("")
                    st.write("")
                    if is_sel:
                        st.markdown(
                            f'<div style="text-align:center; padding: 6px 0;">'
                            f'<p style="font-size:0.82rem; color:var(--lime); font-weight:700; margin:0;">✓ Locked</p>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        if st.button(
                            "Lock Topic", key=f"sel_{trend['id']}",
                            type="primary", use_container_width=True
                        ):
                            st.session_state.selected_trend = trend
                            st.session_state["active_tab"] = "studio"
                            st.toast(f"Topic locked for Creator Studio", icon="🔒")
                            st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center; padding:80px 20px; margin-top:20px;
                    border:2px dashed #111111; border-radius:16px;
                    background: #FFFFFF; box-shadow: 4px 4px 0px #111111;">
          <p style="font-family: var(--font-display); font-size: 2.2rem;
                    font-weight: 800; color: #EAE3D8; margin: 0 0 12px;
                    text-transform: uppercase; letter-spacing: -0.01em;">
            Surging Intelligence
          </p>
          <p style="color: #4A5568; font-size:0.9rem; margin:0; font-family: var(--font-sans); font-weight: 600;">
            Select a target niche from the control panel and click <b>Discover Trends</b>.
          </p>
        </div>
        """, unsafe_allow_html=True)

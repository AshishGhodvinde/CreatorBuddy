import streamlit as st
import pandas as pd

def render_analytics_tab():
    if not st.session_state.generated_video_path:
        st.markdown("""
        <div style="padding:0.5rem 0 0.25rem;">
          <h2 style="font-family: var(--font-display); font-size: 2.2rem; font-weight: 800;
                     color: var(--text-1); margin: 0; text-transform: uppercase; line-height:1.1;">
            Performance Forecast
          </h2>
          <p style="font-size:0.85rem; color:var(--text-2); margin:6px 0 0;">
            Heuristic virality analysis based on hook density, structures, CTA strength, and pacing.
          </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; padding:80px 20px;
                    border:3px dashed #111111; border-radius:18px;
                    background: #FFFFFF; box-shadow: 4px 4px 0px #111111;">
          <p style="font-family: var(--font-display); font-size: 2.2rem;
                    font-weight: 800; color: #EAE3D8; margin:0 0 12px;
                    text-transform: uppercase; letter-spacing: -0.01em;">
            Forecast Ready
          </p>
          <p style="color: var(--text-2); font-size:0.88rem; margin:0; font-family: var(--font-sans); font-weight: 600;">
            Synthesize and compile a video reel in <b>Creator Studio</b> to view analysis.
          </p>
        </div>
        """, unsafe_allow_html=True)
        return

    col_title, col_plat = st.columns([1.8, 1])
    with col_title:
        st.markdown("""
        <div style="padding:0.5rem 0 0.25rem;">
          <h2 style="font-family: var(--font-display); font-size: 2.2rem; font-weight: 800;
                     color: var(--text-1); margin: 0; text-transform: uppercase; line-height:1.1;">
            Performance Forecast
          </h2>
          <p style="font-size:0.85rem; color:var(--text-2); margin:6px 0 0;">
            Heuristic virality analysis across major social media distribution channels.
          </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_plat:
        platform = st.selectbox(
            "Select Target Social Network",
            ["Instagram Reels", "TikTok", "YouTube Shorts", "LinkedIn Video"],
            key="analytics_platform_selector"
        )

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    report = st.session_state.virality_report
    if not report:
        st.error("Virality report metrics missing — re-compile your asset.")
        return

    plat_report = report.get("platforms", {}).get(platform, report)
    score = plat_report.get("virality_score", report["virality_score"])

    if score >= 80:
        tier_color, tier_label, tier_bg = "var(--red)", "Mega Viral",    "#FB7171"
    elif score >= 60:
        tier_color, tier_label, tier_bg = "var(--accent)", "Strong Reach",  "#FFD25A"
    else:
        tier_color, tier_label, tier_bg = "var(--lime)", "Steady Growth", "#4ADE80"

    col_player, col_metrics = st.columns([1, 1.1], gap="large")

    with col_player:
        st.markdown('<p class="cb-label">Reel Render Preview</p>', unsafe_allow_html=True)
        try:
            with open(st.session_state.generated_video_path, "rb") as vf:
                st.video(vf.read(), format="video/mp4")
            st.markdown(
                f'<p style="font-size:0.68rem; color:var(--text-2); margin:8px 0 0; font-family:\'Space Grotesk\', monospace; font-weight:700;">'
                f'File Path: data/outputs/rendered_reel.mp4</p>',
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Playback error: {e}")

    with col_metrics:
        st.markdown(
            f'<div style="background:#FFFFFF; border:1px solid #E5E2DC; '
            f'border-radius:16px; padding:25px; margin-bottom:20px; text-align: center; '
            f'box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);">'
            f'<p style="font-size:0.75rem; color:#4A5568; text-transform:uppercase; '
            f'letter-spacing:0.12em; font-weight:700; margin:0 0 15px;">Projected {platform.upper()} Rating</p>'
            f'<div style="position: relative; width: 130px; height: 130px; margin: 0 auto 15px; '
            f'border-radius: 50%; display: flex; align-items: center; justify-content: center; '
            f'background: #F4F0EA; '
            f'border: 1px solid #E5E2DC;">'
            f'<div style="text-align: center;">'
            f'<span style="font-family: var(--font-display); font-size:3rem; font-weight:800; color:#111111;">{score}</span>'
            f'<span style="font-size:0.75rem; color:#4A5568; display:block; margin-top:-8px;">/ 100</span>'
            f'</div>'
            f'</div>'
            f'<span style="display:inline-flex; align-items:center; '
            f'background:{tier_bg}; border:1px solid rgba(0,0,0,0.06); '
            f'border-radius:50px; padding:6px 16px; font-size:0.72rem; '
            f'font-weight:700; letter-spacing:0.05em; color:#111111 !important; text-transform: uppercase;">'
            f'{tier_label}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        def metric_html(label, value, sub, color):
            return (
                f'<div style="background:#FFFFFF; border:1px solid #E5E2DC; border-top: 5px solid {color}; '
                f'border-radius:12px; padding:18px 20px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04); transition: transform 0.2s ease;">'
                f'<p style="font-size:0.65rem; color:#4A5568; margin:0 0 6px; '
                f'text-transform:uppercase; letter-spacing:0.08em; font-weight:700;">{label}</p>'
                f'<p style="font-family: var(--font-sans); font-size: 1.7rem; font-weight: 800; '
                f'color:#111111; margin:0; line-height:1.1;">{value}</p>'
                f'<p style="font-size:0.68rem; color:#718096; margin:5px 0 0; font-weight:600;">{sub}</p>'
                f'</div>'
            )

        views_val = plat_report.get('expected_views', 0)
        likes_val = plat_report.get('expected_likes', 0)
        shares_val = plat_report.get('expected_shares', 0)
        saves_val = plat_report.get('expected_saves', 0)

        st.markdown(
            f'<div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:20px;">'
            f'{metric_html("Views Forecast",  f"{views_val:,}",  "projected impressions",  "var(--red)")}'
            f'{metric_html("Likes Forecast",  f"{likes_val:,}",  "projected engagement",   "var(--accent)")}'
            f'{metric_html("Shares Forecast", f"{shares_val:,}", "viral distribution",     "var(--accent-2)")}'
            f'{metric_html("Saves Forecast",  f"{saves_val:,}",  "content persistence",    "var(--lime)")}'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown('<p class="cb-label">Factor Weight Analysis</p>', unsafe_allow_html=True)
        factors = report.get("factors", {})
        rows_html = ""
        for label, key, color in [
            ("Hook Strength",       "hook_strength",       "var(--red)"),
            ("Structure Integrity", "structure_integrity",  "var(--accent-2)"),
            ("CTA Effectiveness",   "cta_power",           "var(--accent)"),
            ("Pacing Score",        "pacing_efficiency",   "var(--lime)"),
        ]:
            val = float(factors.get(key, 50))
            rows_html += (
                f'<div style="margin-bottom:14px;">'
                f'<div style="display:flex; justify-content:space-between; margin-bottom:6px;">'
                f'<span style="font-size:0.8rem; color:#111111; font-weight:700;">{label}</span>'
                f'<span style="font-family: var(--font-sans); font-size:0.88rem; '
                f'font-weight:800; color:#111111;">{val:.0f}</span>'
                f'</div>'
                f'<div style="background:#FFFFFF; border:2px solid #111111; border-radius:10px; height:8px; overflow:hidden;">'
                f'<div style="background:{color}; border-right:2px solid #111111; width:{val}%; height:100%; '
                f'transition:width 0.8s ease;"></div>'
                f'</div></div>'
            )
        st.markdown(rows_html, unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    col_curve, col_heatmap = st.columns([1, 1.1], gap="large")
    
    with col_curve:
        st.markdown('<p class="cb-label">Audience Retention Curve Simulation</p>', unsafe_allow_html=True)
        retention_curve = report.get("retention_curve", [])
        if retention_curve:
            try:
                df_ret = pd.DataFrame(retention_curve)
                df_ret.columns = ["Time (Seconds)", "Retention (%)"]
                df_ret = df_ret.set_index("Time (Seconds)")
                st.area_chart(df_ret, color="#FF5B84")
            except Exception as e:
                st.caption(f"Could not load retention visual: {e}")
        else:
            st.caption("Audience retention metrics unavailable for this simulation run.")

    with col_heatmap:
        st.markdown('<p class="cb-label">Explainable AI (XAI) Retention Heatmap</p>', unsafe_allow_html=True)
        
        segments = [
            {"name": "HOOK (0:00 - 0:03)", "score_key": "hook_strength", "risk_threshold": 75,
             "success_advice": "Hook is highly compelling, utilizing viral curiosity power words.",
             "fail_advice": "Hook phrasing is slightly dry. Replace passive statements with contrarian, shocking, or high-urgency phrases."},
            {"name": "STORY (0:03 - 0:08)", "score_key": "structure_integrity", "risk_threshold": 70,
             "success_advice": "Excellent structural build, smoothly pacing the user into core concepts.",
             "fail_advice": "Narrative pace slows down. Inject a faster rhetorical bridge (e.g. 'But here is the real kicker...') to double retention."},
            {"name": "INSIGHTS (0:08 - 0:25)", "score_key": "pacing_efficiency", "risk_threshold": 75,
             "success_advice": "High-value metrics and key insights maintain excellent interest.",
             "fail_advice": "Insight density is too complex. Break concepts into 3 clear, highly scannable bullet points."},
            {"name": "CTA (0:25 - 0:30)", "score_key": "cta_power", "risk_threshold": 75,
             "success_advice": "Provocative CTA drives solid conversion likelihood.",
             "fail_advice": "CTA is too passive. Use direct high-intent triggers (e.g. 'Comment below to unlock resources' or 'Follow for part 2')."}
        ]
        
        for seg in segments:
            val = float(factors.get(seg["score_key"], 70))
            is_risk = val < seg["risk_threshold"]
            color = "var(--red)" if is_risk else "var(--lime)"
            badge = "HIGH DROP-OFF RISK" if is_risk else "EXCELLENT RETAINED"
            advice = seg["fail_advice"] if is_risk else seg["success_advice"]
            
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E5E2DC; border-radius: 12px; padding: 18px; margin-bottom: 14px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-family: var(--font-sans); font-size: 0.88rem; font-weight: 700; color: #111111;">{seg["name"]}</span>
                    <span style="font-size: 0.65rem; background: {color}; color: #111111 !important; border: 1px solid rgba(0,0,0,0.06); padding: 3px 10px; border-radius: 50px; font-weight: 700;">{badge}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; margin-top: 10px;">
                    <div style="flex: 1; background: #F4F0EA; border: 1px solid #E5E2DC; height: 10px; border-radius: 10px; overflow: hidden;">
                        <div style="width: {val}%; background: {color}; height: 100%;"></div>
                    </div>
                    <span style="font-family: var(--font-sans); font-size: 0.9rem; font-weight: 700; color: #111111; min-width: 40px; text-align: right;">{val:.0f}%</span>
                </div>
                <div style="margin-top: 12px; padding-top: 10px; border-top: 1px dashed #E5E2DC;">
                    <p style="font-size: 0.78rem; color: #4A5568; margin: 0; line-height: 1.45; font-weight:600;">
                        💡 <strong>AI Advisory:</strong> {advice}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<p class="cb-label">Evolutionary Memory Feedback Loop</p>', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-size:0.85rem; color:var(--text-2); margin:0 0 16px; line-height:1.5;">'
            'Log real-world published performance metrics to train CreatorBuddy\'s evolutionary memory network. '
            'The AI Creative Director retrieves high-performing historical scripts from your SQLite transactional history to dynamically optimize future hook prompt variables.'
            '</p>',
            unsafe_allow_html=True
        )
        
        col_inp, col_btn = st.columns([3, 1])
        with col_inp:
            real_views = st.number_input(
                "Enter Published Reel / Video Views",
                min_value=0, step=1000,
                key="real_views_input_field",
                help="Input the real view count of the video published from this script."
            )
        with col_btn:
            st.write("")
            st.write("")
            log_btn = st.button("Log Views to Database", type="primary", use_container_width=True)
            
        if log_btn:
            latest_id = st.session_state.get("db_content_id")
            if latest_id:
                import sqlite3
                from config import DATABASE_PATH
                try:
                    conn = sqlite3.connect(DATABASE_PATH)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE content SET performance_views = ? WHERE id = ?", (real_views, latest_id))
                    conn.commit()
                    conn.close()
                    st.toast(f"Successfully logged {real_views:,} views for Content ID #{latest_id}!", icon="📈")
                except Exception as e:
                    st.error(f"Failed to log view performance: {e}")
            else:
                st.error("No active generation run recorded in this session yet. Compile a video first!")

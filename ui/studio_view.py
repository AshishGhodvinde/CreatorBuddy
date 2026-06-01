import os
import sqlite3
import asyncio
import re
import streamlit as st
import edge_tts
from core.brain import AIEngine
from core.video_studio import MediaProductionFactory
from core.predictor import ViralityPredictorModel
from config import DATABASE_PATH, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID
from typing import List

def save_content_to_db(trend_id, script, ig_caption, li_post, video_path, virality_score, visual_keywords):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO content (trend_id, script, ig_caption, li_post, video_path, virality_score, visual_keywords) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (trend_id, script, ig_caption, li_post, video_path, virality_score, " | ".join(visual_keywords))
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def generate_voice_sample(voice: str) -> str:
    sample_dir = "data/outputs"
    os.makedirs(sample_dir, exist_ok=True)
    sample_path = os.path.abspath(f"{sample_dir}/sample_{voice}.mp3")
    if not os.path.exists(sample_path):
        text = "Welcome to CreatorBuddy. I am your AI voice actor, ready to bring your script to life."
        asyncio.run(edge_tts.Communicate(text, voice).save(sample_path))
    return sample_path

def get_timeline_from_package(package: dict) -> List[dict]:
    timeline = package.get("timeline", [])
    if timeline:
        return timeline
    
    script_text = package.get("script", "")
    keywords = package.get("visual_keywords", ["Artificial Intelligence", "Autonomous Agents", "Future Technology"])
    subtitles = [
        "Analyzing industry trends & real-time analytics",
        "Synthesizing high-impact viral content models",
        "Ready for deployment across enterprise platforms"
    ]
    
    segment_names = ["HOOK", "STORY", "INSIGHTS"]
    timeline = []
    duration_per_scene = 10.0
    for i, kw in enumerate(keywords[:3]):
        timeline.append({
            "start": i * duration_per_scene,
            "end": (i + 1) * duration_per_scene,
            "segment": segment_names[i] if i < len(segment_names) else "INSIGHTS",
            "voiceover_text": subtitles[i] if i < len(subtitles) else "Executing modern social-media paradigms",
            "visual_cue": f"Scene with keyword: {kw}",
            "sfx_cue": "Dynamic transition",
            "b_roll_keyword": kw
        })
    return timeline

def render_capcut_timeline(timeline: List[dict]):
    st.markdown('<p class="cb-label">CapCut-Style Visual Production Timeline</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    .timeline-container {
        display: flex; 
        gap: 16px; 
        overflow-x: auto; 
        padding: 10px 4px 20px 4px; 
        margin-bottom: 25px; 
        scrollbar-width: thin; 
        -webkit-overflow-scrolling: touch;
    }
    .timeline-card {
        min-width: 270px; 
        max-width: 270px; 
        background: #FFFFFF !important; 
        border: 1px solid #E5E2DC !important; 
        border-radius: 12px !important; 
        padding: 18px !important; 
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04) !important; 
        display: flex; 
        flex-direction: column; 
        justify-content: space-between; 
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    .timeline-card:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    html_timeline = '<div class="timeline-container">'
    
    color_map = {
        "HOOK": "#FF5B84",
        "STORY": "#60A5FA",
        "INSIGHTS": "#FFB03A",
        "CTA": "#10B981"
    }
    
    for seg in timeline:
        segment = seg.get("segment", "HOOK").upper()
        color = color_map.get(segment, "#FF5B84")
        start = float(seg.get("start", 0.0))
        end = float(seg.get("end", 3.0))
        text = seg.get("voiceover_text", "")
        visual = seg.get("visual_cue", "")
        sfx = seg.get("sfx_cue", "")
        b_roll = seg.get("b_roll_keyword", "")
        
        html_timeline += f"""<div class="timeline-card" style="border-top: 8px solid {color} !important;">
<div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<span style="font-size: 0.65rem; background: {color}; color: #111111; border: 1px solid rgba(0,0,0,0.06); padding: 2px 8px; border-radius: 50px; font-weight: 700; letter-spacing: 0.05em;">{segment}</span>
<span style="font-size: 0.72rem; color: #4A5568; font-weight: 700;">{start:.1f}s - {end:.1f}s</span>
</div>
<p style="font-size: 0.85rem; color: #111111; line-height: 1.45; margin: 0 0 10px; font-weight: 600; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">"{text}"</p>
</div>
<div style="border-top: 1px solid #E5E2DC; padding-top: 8px; margin-top: 10px;">
<p style="font-size: 0.7rem; color: #4A5568; margin: 0 0 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">🎬 B-ROLL: <strong style="color: #111111;">{b_roll}</strong></p>
<p style="font-size: 0.7rem; color: #4A5568; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">🎵 SFX: <strong style="color: #111111;">{sfx}</strong></p>
</div>
</div>"""
        
    html_timeline += '</div>'
    st.markdown(html_timeline, unsafe_allow_html=True)

def render_highly_styled_script(script_text: str):
    parts = re.split(r'(\[[A-Z\s]+\])', script_text)
    html_output = '<div style="background:#FFFFFF; border:1px solid #E5E2DC; border-radius:12px; padding:20px; font-family:\'Space Grotesk\', sans-serif; line-height:1.6; max-height:360px; overflow-y:auto; margin-bottom:15px; box-shadow:0 8px 24px rgba(0, 0, 0, 0.04); color:#111111;">'

    color_map = {
        "HOOK": "#FF5B84",
        "STORY": "#60A5FA",
        "INSIGHTS": "#FFB03A",
        "CTA": "#10B981"
    }
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith('[') and part.endswith(']'):
            tag = part[1:-1]
            color = color_map.get(tag, "#FFD25A")
            html_output += f'<div style="margin-top:14px; margin-bottom:10px;"><span style="color:#111111; background:{color}; border:1px solid rgba(0,0,0,0.06); padding:3px 12px; border-radius:50px; font-size:0.7rem; font-weight:700; letter-spacing:0.05em; text-transform:uppercase;">{tag}</span></div>'
        else:
            html_output += f'<p style="font-size:0.92rem; color:#111111; margin:0 0 10px; line-height:1.6; font-weight:600;">{part}</p>'
    
    html_output += '</div>'
    return html_output

def render_highly_styled_social(content: str, title: str, accent_color: str):
    return (
        f'<div style="background:#FFFFFF; border:1px solid #E5E2DC; border-radius:12px; padding:20px; font-family:\'Space Grotesk\', sans-serif; margin-bottom:15px; box-shadow:0 8px 24px rgba(0, 0, 0, 0.04); color:#111111;">'
        f'<div style="display:inline-block; background:{accent_color}; color:#111111; border:1px solid rgba(0,0,0,0.06); border-radius:50px; padding:3px 12px; font-size:0.7rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:12px;">{title}</div>'
        f'<p style="font-size:0.9rem; color:#111111; line-height:1.6; white-space:pre-wrap; margin:0; font-weight:600;">{content}</p>'
        f'</div>'
    )

def render_studio_tab():
    st.markdown("""
    <div style="padding:0.5rem 0 0.25rem;">
      <h2 style="font-family: var(--font-display); font-size: 2.2rem; font-weight: 800;
                 color: var(--text-1); margin: 0; text-transform: uppercase; line-height:1.1;">
        Build your reel
      </h2>
      <p style="font-size:0.85rem; color:var(--text-2); margin:6px 0 0;">
        Gemini writes the script · edge-tts compiles the voiceover · MoviePy renders the vertical video.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    if not st.session_state.selected_trend:
        st.markdown("""
        <div style="text-align:center; padding:80px 20px;
                    border:3px dashed #111111; border-radius:18px;
                    background: #FFFFFF; box-shadow: 4px 4px 0px #111111;">
          <p style="font-family: var(--font-display); font-size: 2.2rem;
                    font-weight: 800; color: #EAE3D8; margin:0 0 12px;
                    text-transform: uppercase; letter-spacing: -0.01em;">
            No topic locked
          </p>
          <p style="color: var(--text-2); font-size:0.88rem; margin:0; font-family: var(--font-sans); font-weight: 600;">
            Head to <b>Trend Discovery</b>, find a surging topic and click <b>Lock Topic</b>.
          </p>
        </div>
        """, unsafe_allow_html=True)
        return

    selected = st.session_state.selected_trend

    st.markdown(
        f'<div style="background:#FFFFFF; border:2px solid var(--border-hard); '
        f'border-radius:12px; padding:16px 20px; margin-bottom:24px; box-shadow: 4px 4px 0px var(--border-hard);">'
        f'<div style="display:inline-block; background:var(--accent); color:#111111; border:2px solid var(--border-hard); '
        f'border-radius:50px; padding:2px 10px; font-size:0.65rem; text-transform:uppercase; '
        f'letter-spacing:0.08em; font-weight:800; margin:0 0 8px; box-shadow:2px 2px 0px var(--border-hard);">Locked Topic</div>'
        f'<p style="font-family: var(--font-sans); font-size:1.2rem; font-weight:800; '
        f'color:#111111; margin:0 0 8px; line-height:1.35;">{selected["topic"]}</p>'
        f'<p style="font-size:0.75rem; color:var(--text-2); margin:0; font-weight:700; text-transform:uppercase; letter-spacing:0.02em;">'
        f'📂 Niche: <strong>{selected["niche"]}</strong> &nbsp;·&nbsp; ⚡ Velocity Score: <strong>{selected["score"]:.0f}/100</strong></p>'
        f'</div>',
        unsafe_allow_html=True
    )

    col_v, col_g = st.columns([1.1, 1])

    with col_v:
        with st.container(border=True):
            st.markdown('<p class="cb-label">Voice Artist</p>', unsafe_allow_html=True)
            voice_opt = st.selectbox(
                "Voice",
                ["Guy — Male, Dynamic (en-US-GuyNeural)",
                 "Aria — Female, Professional (en-US-AriaNeural)",
                 "Ryan — Male, Energetic (en-GB-RyanNeural)",
                 "Jenny — Female, Friendly (en-US-JennyNeural)"],
                label_visibility="collapsed",
                key="default_voice_selector"
            )
            voice_map_edge = {
                "Guy": "en-US-GuyNeural",
                "Aria": "en-US-AriaNeural",
                "Ryan": "en-GB-RyanNeural",
                "Jenny": "en-US-JennyNeural"
            }
            voice_code = next((v for k, v in voice_map_edge.items() if k in voice_opt), "en-US-GuyNeural")
            
            el_api_key  = ELEVENLABS_API_KEY
            el_voice_id = ELEVENLABS_VOICE_ID
            
            if el_api_key:
                st.markdown(
                    f'<p style="font-size:0.72rem; color:var(--lime); margin:10px 0 0; font-weight:700;">'
                    f'⚡ ElevenLabs Premium Voice Active</p>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<p style="font-size:0.72rem; color:var(--text-2); margin:10px 0 0; font-weight:600;">'
                    f'Active Engine: <code style="color:var(--accent); font-weight:700;">edge-tts ({voice_code})</code></p>',
                    unsafe_allow_html=True
                )
                try:
                    sp = generate_voice_sample(voice_code)
                    with open(sp, "rb") as f:
                        st.audio(f.read(), format="audio/mp3")
                except Exception as e:
                    st.caption(f"Sample unavailable: {e}")

    with col_g:
        with st.container(border=True):
            st.markdown('<p class="cb-label">Generate Blueprint</p>', unsafe_allow_html=True)
            st.markdown(
                '<p style="font-size:0.82rem; color:var(--text-2); margin:0 0 14px; line-height:1.5;">'
                'Synthesize an structured video script, LinkedIn post, Instagram caption, and scene cues.</p>',
                unsafe_allow_html=True
            )
            bp_btn = st.button("Synthesize Blueprint", type="primary", use_container_width=True)

            if st.session_state.viral_package:
                st.markdown(
                    '<p style="font-size:0.75rem; color:var(--lime); font-weight:700; margin:10px 0 0;">'
                    '✓ Blueprint compiled — toggle Edit Mode below to adjust.</p>',
                    unsafe_allow_html=True
                )
                if st.session_state.get("agent_logs"):
                    st.markdown('<p class="cb-label" style="margin-top: 15px;">Agent Reasoning Logs</p>', unsafe_allow_html=True)
                    logs_html = "".join([f"<p style='margin:0 0 6px; line-height:1.4;'><span style='color:#059669; font-weight:800;'>➜</span> {log}</p>" for log in st.session_state["agent_logs"]])
                    st.markdown(f"""
                    <div style="background:#F4F0EA; border:2px solid var(--border-hard); border-radius:12px; padding:16px; font-family:'Courier New', monospace; max-height:180px; overflow-y:auto; font-size:0.78rem; color:#111111; margin-bottom:12px; box-shadow: 4px 4px 0px var(--border-hard);">
                        {logs_html}
                    </div>
                    """, unsafe_allow_html=True)
                st.write("")
                if st.button("Clear Blueprint", use_container_width=True):
                    st.session_state.viral_package     = None
                    st.session_state.generated_video_path = None
                    st.session_state.virality_report   = None
                    st.rerun()

    if bp_btn:
        with st.spinner("Synthesizing creative layout..."):
            try:
                pkg = AIEngine().generate_viral_package(selected["topic"], selected["niche"])
                st.session_state.viral_package = pkg
                st.toast("Blueprint synthesized successfully", icon="✨")
                st.rerun()
            except Exception as e:
                st.error(f"Generation failed: {e}")

    if not st.session_state.viral_package:
        return

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    
    col_header, col_toggle = st.columns([3, 1])
    with col_header:
        st.markdown(
            '<p style="font-family: var(--font-display); font-size:1.5rem; font-weight:800; '
            'color:var(--text-1); text-transform:uppercase; margin:0;">Creative Assets</p>',
            unsafe_allow_html=True
        )
    with col_toggle:
        edit_mode = st.toggle("Edit Content", value=False)

    package = st.session_state.viral_package
    timeline = get_timeline_from_package(package)
    
    render_capcut_timeline(timeline)

    col_l, col_r = st.columns([1.1, 1])

    if not edit_mode:
        with col_l:
            st.markdown('<p class="cb-label">Production Script</p>', unsafe_allow_html=True)
            script_content = package.get("script", " ".join([seg.get("voiceover_text", "") for seg in timeline]))
            st.markdown(render_highly_styled_script(script_content), unsafe_allow_html=True)
            
            st.markdown('<p class="cb-label">Scene B-Roll Directives</p>', unsafe_allow_html=True)
            color_map_broll = {
                "HOOK": "#FF5B84",
                "STORY": "#60A5FA",
                "INSIGHTS": "#FFB03A",
                "CTA": "#10B981"
            }
            for i, seg in enumerate(timeline):
                segment_name = seg.get("segment", "HOOK").upper()
                accent = color_map_broll.get(segment_name, "#FFD25A")
                st.markdown(
                    f'<div style="background:#FFFFFF; border:2px solid #111111; border-radius:8px; padding:10px 14px; margin-bottom:8px; box-shadow: 2px 2px 0px #111111;">'
                    f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">'
                    f'<span style="font-size:0.62rem; color:var(--text-2); font-weight:700; text-transform:uppercase;">Scene {i+1}</span>'
                    f'<span style="font-size:0.6rem; background:{accent}; color:#111111; border:1px solid #111111; padding:1px 6px; border-radius:50px; font-weight:800;">{segment_name}</span>'
                    f'</div>'
                    f'<span style="font-size:0.88rem; color:#111111; font-weight:600;">{seg.get("visual_cue", "")}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        
        with col_r:
            st.markdown(render_highly_styled_social(package["linkedin_post"], "LinkedIn Post Draft", "#F7C5CC"), unsafe_allow_html=True)
            st.markdown(render_highly_styled_social(package["instagram_caption"], "Instagram Caption Draft", "#10B981"), unsafe_allow_html=True)

        edited_timeline = timeline
        edited_linkedin = package["linkedin_post"]
        edited_instagram = package["instagram_caption"]
    else:
        with col_l:
            st.markdown('<p class="cb-label">Interactive Timeline Editor</p>', unsafe_allow_html=True)
            edited_timeline = []
            for i, seg in enumerate(timeline):
                with st.container(border=True):
                    segment_name = seg.get("segment", "HOOK").upper()
                    st.markdown(f"**Scene {i+1} — {segment_name}** ({seg.get('start', 0.0):.1f}s - {seg.get('end', 3.0):.1f}s)")
                    seg_text = st.text_area(
                        "Voiceover Script", value=seg.get("voiceover_text", ""), height=75,
                        key=f"seg_voiceover_{i}"
                    )
                    seg_broll = st.text_input(
                        "B-Roll Keyword", value=seg.get("b_roll_keyword", ""),
                        key=f"seg_broll_{i}"
                    )
                edited_seg = seg.copy()
                edited_seg["voiceover_text"] = seg_text
                edited_seg["b_roll_keyword"] = seg_broll
                edited_timeline.append(edited_seg)

        with col_r:
            st.markdown('<p class="cb-label">LinkedIn & Instagram Copy Editor</p>', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown('<p class="cb-label" style="margin: 0 0 8px;">LinkedIn Post Editor</p>', unsafe_allow_html=True)
                edited_linkedin = st.text_area(
                    "LinkedIn", value=package["linkedin_post"], height=210,
                    label_visibility="collapsed", key="edited_li_area"
                )
            st.write("")
            with st.container(border=True):
                st.markdown('<p class="cb-label" style="margin: 0 0 8px;">Instagram Caption Editor</p>', unsafe_allow_html=True)
                edited_instagram = st.text_area(
                    "Instagram", value=package["instagram_caption"], height=170,
                    label_visibility="collapsed", key="edited_ig_area"
                )

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    render_btn = st.button(
        "Compile Reel & Run Analytics",
        type="primary", use_container_width=True
    )

    if render_btn:
        steps = [st.empty() for _ in range(4)]

        def step(i, done, msg):
            icon  = "Completed" if done else "Pending"
            color = "#10B981" if done else "#78716c"
            badge_bg = "rgba(16,185,129,0.06)" if done else "rgba(0,0,0,0.01)"
            badge_border = "rgba(16,185,129,0.15)" if done else "rgba(0,0,0,0.04)"
            
            steps[i].markdown(
                f'<div style="display:flex; justify-content:space-between; align-items:center; background:{badge_bg}; border:1px solid {badge_border}; border-radius:8px; padding:10px 14px; margin-bottom:8px;">'
                f'<span style="font-size:0.85rem; color:var(--text-1); font-weight:600;">{msg}</span>'
                f'<span style="font-size:0.68rem; font-weight:700; color:{color}; text-transform:uppercase; letter-spacing:0.05em;">{icon}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        step(0, False, "Phase 1 / 4 — Preserving custom assets…")
        try:
            reconstructed_script = " ".join([seg.get("voiceover_text", "") for seg in edited_timeline])
            reconstructed_keywords = [seg.get("b_roll_keyword", "") for seg in edited_timeline]
            
            package["timeline"]          = edited_timeline
            package["script"]            = reconstructed_script
            package["linkedin_post"]     = edited_linkedin
            package["instagram_caption"] = edited_instagram
            package["visual_keywords"]   = reconstructed_keywords
            st.session_state.viral_package = package
            step(0, True, "Phase 1 / 4 — Assets cataloged.")

            step(1, False, "Phase 2 / 4 — Generating high-fidelity voiceover... (edge-tts / ElevenLabs)")
            os.makedirs("data/outputs", exist_ok=True)
            voice_path = os.path.abspath(f"data/outputs/voiceover_{selected['id']}.mp3")
            video_path = os.path.abspath("data/outputs/rendered_reel.mp4")
            factory = MediaProductionFactory()
            asyncio.run(factory.async_generate_voiceover(
                reconstructed_script, 
                voice_path, 
                voice=voice_code,
                elevenlabs_api_key=el_api_key,
                elevenlabs_voice_id=el_voice_id
            ))
            step(1, True, "Phase 2 / 4 — Voiceover track synthesized.")

            step(2, False, "Phase 3 / 4 — Rendering vertical MP4 video reel...")
            factory.assemble_reel_video(voice_path, edited_timeline, video_path, niche=selected["niche"])
            st.session_state.generated_video_path = video_path
            step(2, True, "Phase 3 / 4 — Video track rendered.")

            step(3, False, "Phase 4 / 4 — Running predictive analytics and storing results...")
            vr = ViralityPredictorModel().predict_content_virality(reconstructed_script)
            st.session_state.virality_report = vr
            new_id = save_content_to_db(
                selected["id"], reconstructed_script, edited_instagram,
                edited_linkedin, video_path, vr["virality_score"], reconstructed_keywords
            )
            st.session_state["db_content_id"] = new_id
            step(3, True, "Phase 4 / 4 — Database committed.")

            st.session_state["active_tab"] = "analytics"
            st.toast("Video production complete", icon="🎉")
            st.rerun()
        except Exception as e:
            st.error(f"Production failed: {e}")

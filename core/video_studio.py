import os
import re
import math
import hashlib
import logging
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Any
import edge_tts

try:
    from moviepy import AudioFileClip, VideoFileClip, ImageClip, concatenate_videoclips
except ImportError as err:
    raise ImportError("Failed to import MoviePy v2. Run: pip install moviepy>=2.0.0") from err

try:
    from config import PEXELS_API_KEY
except ImportError:
    PEXELS_API_KEY = "mock_pexels_api_key"

logger = logging.getLogger("MediaProductionFactory")

class MediaProductionFactory:
    def __init__(self):
        os.makedirs("data/cache", exist_ok=True)
        os.makedirs("data/outputs", exist_ok=True)

    @staticmethod
    def clean_script_for_tts(text: str) -> str:
        cleaned = re.sub(r'\[.*?\]', '', text)
        cleaned = re.sub(r'\(.*?\)', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    async def async_generate_voiceover(
        self, 
        text: str, 
        output_path: str, 
        voice: str = "en-US-GuyNeural",
        elevenlabs_api_key: str = None,
        elevenlabs_voice_id: str = None
    ) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        cleaned_text = self.clean_script_for_tts(text)
        
        if elevenlabs_api_key and elevenlabs_api_key.strip():
            try:
                def call_elevenlabs():
                    voice_id = elevenlabs_voice_id.strip() if elevenlabs_voice_id else "21m00Tcm4TlvDq8ikWAM"
                    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                    headers = {
                        "Accept": "audio/mpeg",
                        "Content-Type": "application/json",
                        "xi-api-key": elevenlabs_api_key.strip()
                    }
                    data = {
                        "text": cleaned_text,
                        "model_id": "eleven_monolingual_v1",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75
                        }
                    }
                    res = requests.post(url, json=data, headers=headers, timeout=30)
                    if res.status_code == 200:
                        with open(output_path, "wb") as f:
                            f.write(res.content)
                        return True
                    return False

                import asyncio
                loop = asyncio.get_event_loop()
                success = await loop.run_in_executor(None, call_elevenlabs)
                if success:
                    return output_path
            except Exception:
                pass

        communicate = edge_tts.Communicate(cleaned_text, voice)
        await communicate.save(output_path)
        return output_path

    def simplify_pexels_query(self, query: str) -> str:
        q = query.lower()
        q = re.sub(r'[^\w\s]', ' ', q)
        words = q.split()
        
        stop_words = {
            "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with", "about",
            "close", "up", "shot", "showing", "glowing", "futuristic", "dynamic", "aesthetic",
            "neon", "bright", "pulsing", "cool", "epic", "high", "quality", "hd", "4k", "beautiful",
            "awesome", "best", "of", "from", "by", "scene", "view", "background", "loop", "slow", "motion",
            "zoom", "zoom-in", "pan", "cinematic", "overlay", "illustration", "graphic", "animation",
            "effects", "sfx", "sfx-cue", "visual", "visuals"
        }
        
        filtered = [w for w in words if w not in stop_words]
        if not filtered:
            return "technology"
            
        return " ".join(filtered[:3])

    def fetch_pexels_broll(self, visual_keywords: List[str]) -> List[str]:
        downloaded_paths = []
        
        keywords = [kw.strip() for kw in visual_keywords if kw.strip()]
        if not keywords:
            keywords = ["technology", "digital", "creative"]
            
        headers = {
            "Authorization": PEXELS_API_KEY
        }
        
        for raw_kw in keywords[:3]:
            kw = self.simplify_pexels_query(raw_kw)
            cache_path = os.path.abspath(f"data/cache/pexels_{hashlib.md5(kw.encode()).hexdigest()}.mp4")
            
            if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
                downloaded_paths.append(cache_path)
                continue
                
            if PEXELS_API_KEY == "mock_pexels_api_key" or not PEXELS_API_KEY.strip():
                continue
                
            try:
                url = "https://api.pexels.com/videos/search"
                params = {
                    "query": kw,
                    "orientation": "portrait",
                    "per_page": 5
                }
                res = requests.get(url, headers=headers, params=params, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    videos = data.get("videos", [])
                    if videos:
                        best_file = None
                        best_is_portrait = False
                        best_resolution = 0
                        
                        for video in videos[:3]:
                            files = video.get("video_files", [])
                            for f in files:
                                if f.get("file_type") == "video/mp4" or "mp4" in f.get("link", ""):
                                    w = f.get("width", 0)
                                    h = f.get("height", 0)
                                    resolution = w * h
                                    is_portrait = w < h
                                    
                                    if best_file is None:
                                        best_file = f
                                        best_is_portrait = is_portrait
                                        best_resolution = resolution
                                    elif is_portrait and not best_is_portrait:
                                        best_file = f
                                        best_is_portrait = True
                                        best_resolution = resolution
                                    elif is_portrait == best_is_portrait:
                                        if resolution > best_resolution and best_resolution < 2000000:
                                            best_file = f
                                            best_resolution = resolution
                        
                        download_url = best_file.get("link") if best_file else None
                        
                        if download_url:
                            vid_res = requests.get(download_url, timeout=25)
                            if vid_res.status_code == 200:
                                with open(cache_path, "wb") as out_f:
                                    out_f.write(vid_res.content)
                                downloaded_paths.append(cache_path)
            except Exception:
                pass
                
        return downloaded_paths

    def _create_gradient_fallback_canvas(self, niche: str) -> np.ndarray:
        width, height = 720, 1280
        img = Image.new("RGB", (width, height), (244, 240, 234))
        draw = ImageDraw.Draw(img)
        
        grid_color = (234, 227, 216)
        grid_spacing = 60
        for x in range(0, width, grid_spacing):
            draw.line([(x, 0), (x, height)], fill=grid_color, width=2)
        for y in range(0, height, grid_spacing):
            draw.line([(0, y), (width, y)], fill=grid_color, width=2)
            
        circle_color = (255, 210, 90)
        n_low = niche.lower()
        if "ai" in n_low or "tech" in n_low:
            circle_color = (96, 165, 250)
        elif "sport" in n_low:
            circle_color = (255, 91, 132)
        elif "finance" in n_low or "business" in n_low:
            circle_color = (16, 185, 129)
            
        draw.ellipse([(100, 200), (620, 720)], outline=circle_color, width=6)
        draw.ellipse([(200, 600), (520, 920)], outline=(17, 17, 17), width=3)
        
        return np.array(img)

    def assemble_reel_video(self, voice_path: str, visual_keywords: List[Any], output_mp4_path: str, niche: str = "AI") -> str:
        audio_clip = None
        final_video = None
        clips = []
        
        try:
            audio_clip = AudioFileClip(voice_path)
            total_duration = audio_clip.duration
            
            kw_strings = []
            timeline_segments = []
            if isinstance(visual_keywords, list) and len(visual_keywords) > 0 and isinstance(visual_keywords[0], dict):
                timeline_segments = visual_keywords
                for seg in timeline_segments:
                    kw = seg.get("b_roll_keyword", "")
                    if kw:
                        kw_strings.append(kw)
            else:
                for item in visual_keywords:
                    kw_strings.append(str(item))
            
            downloaded_clips = self.fetch_pexels_broll(kw_strings)
            
            if downloaded_clips:
                duration_per_clip = total_duration / len(downloaded_clips)
                
                for path in downloaded_clips:
                    try:
                        v_clip = VideoFileClip(path)
                        v_clip = v_clip.without_audio()
                        
                        w, h = v_clip.size
                        if w > h:
                            target_w = int(h * 9 / 16)
                            x1 = (w - target_w) // 2
                            v_clip = v_clip.cropped(x1=x1, y1=0, width=target_w, height=h)
                            
                        v_clip = v_clip.resized(new_size=(720, 1280))
                        
                        if v_clip.duration >= duration_per_clip:
                            v_clip = v_clip.subclipped(0, duration_per_clip)
                        else:
                            loops_needed = int(math.ceil(duration_per_clip / v_clip.duration))
                            clones = []
                            for _ in range(loops_needed):
                                loop_clip = VideoFileClip(path).without_audio()
                                lw, lh = loop_clip.size
                                if lw > lh:
                                    ltarget_w = int(lh * 9 / 16)
                                    lx1 = (lw - ltarget_w) // 2
                                    loop_clip = loop_clip.cropped(x1=lx1, y1=0, width=ltarget_w, height=lh)
                                loop_clip = loop_clip.resized(new_size=(720, 1280))
                                clones.append(loop_clip)
                            v_clip = concatenate_videoclips(clones).subclipped(0, duration_per_clip)
                            
                        clips.append(v_clip)
                    except Exception as e:
                        logger.error(f"Failed to process clip: {e}")
                        
            if not clips:
                fallback_frame = self._create_gradient_fallback_canvas(niche)
                fallback_clip = ImageClip(fallback_frame)
                fallback_clip = fallback_clip.with_duration(total_duration)
                clips.append(fallback_clip)
                
            video_sequence = concatenate_videoclips(clips, method="compose")
            
            timed_words = []
            if timeline_segments:
                max_seg_end = max(float(seg.get("end", 0.0)) for seg in timeline_segments) if timeline_segments else 30.0
                scale = total_duration / max_seg_end if max_seg_end > 0 else 1.0
                for seg in timeline_segments:
                    seg_start = float(seg.get("start", 0.0)) * scale
                    seg_end = float(seg.get("end", 0.0)) * scale
                    txt = seg.get("voiceover_text", "")
                    
                    seg_words = [w.strip() for w in re.split(r'\s+', txt) if w.strip()]
                    clean_words = [w.upper().replace('"', '').replace('.', '').replace(',', '').replace('?', '').replace('!', '') for w in seg_words if w]
                    
                    if not clean_words:
                        continue
                        
                    seg_duration = seg_end - seg_start
                    word_dur = seg_duration / len(clean_words)
                    
                    for idx, w_text in enumerate(clean_words):
                        w_start = seg_start + (idx * word_dur)
                        w_end = w_start + word_dur
                        timed_words.append((w_start, w_end, w_text))
            else:
                raw_words = ["CREATE", "VIRAL", "CONTENT", "AUTONOMOUSLY", "WITH", "CREATORBUDDY"]
                clean_words = [w.upper() for w in raw_words]
                word_dur = total_duration / len(clean_words)
                for idx, w_text in enumerate(clean_words):
                    timed_words.append((idx * word_dur, (idx + 1) * word_dur, w_text))
            
            def draw_text_with_outline(draw_ctx, text, x, y, font, fill_color, outline_color=(17, 17, 17, 255), outline_width=3):
                for dx in range(-outline_width, outline_width+1):
                    for dy in range(-outline_width, outline_width+1):
                        if dx != 0 or dy != 0:
                            draw_ctx.text((x + dx, y + dy), text, fill=outline_color, font=font, anchor="mm")
                draw_ctx.text((x, y), text, fill=fill_color, font=font, anchor="mm")

            def process_frame(frame, t):
                img_pil = Image.fromarray(frame).convert("RGBA")
                draw = ImageDraw.Draw(img_pil)
                w, h = 720, 1280
                
                is_cta_phase = (t >= total_duration - 3.0)
                
                if not is_cta_phase and timed_words:
                    active_word = ""
                    for w_start, w_end, w_text in timed_words:
                        if w_start <= t < w_end:
                            active_word = w_text
                            break
                    if not active_word:
                        closest_w = timed_words[0][2]
                        min_dist = abs(t - timed_words[0][0])
                        for w_start, w_end, w_text in timed_words:
                            dist = abs(t - w_start)
                            if dist < min_dist:
                                min_dist = dist
                                closest_w = w_text
                        active_word = closest_w
                    
                    try:
                        sub_font = ImageFont.truetype("arial.ttf", size=65)
                    except OSError:
                        sub_font = ImageFont.load_default()
                        
                    draw_text_with_outline(draw, active_word, w // 2, h - 240, sub_font, (255, 210, 90, 255))
                    
                if is_cta_phase:
                    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                    overlay_draw = ImageDraw.Draw(overlay)
                    
                    cx1, cy1, cx2, cy2 = 100, 480, 620, 840
                    overlay_draw.rounded_rectangle(
                        [(cx1, cy1), (cx2, cy2)], 
                        radius=20, 
                        fill=(17, 17, 17, 225), 
                        outline=(255, 210, 90, 255), 
                        width=4
                    )
                    
                    try:
                        title_font = ImageFont.truetype("arial.ttf", size=32)
                        body_font = ImageFont.truetype("arial.ttf", size=24)
                    except OSError:
                        title_font = ImageFont.load_default()
                        body_font = ImageFont.load_default()
                        
                    draw_text_with_outline(overlay_draw, "CREATORBUDDY AI", w // 2, cy1 + 60, title_font, (255, 91, 132, 255))
                    draw_text_with_outline(overlay_draw, "⚡ LAUNCH SUCCESS ⚡", w // 2, cy1 + 130, body_font, (255, 255, 255, 255))
                    draw_text_with_outline(overlay_draw, "COMMENT 'RECHARGE'", w // 2, cy1 + 220, title_font, (255, 210, 90, 255))
                    draw_text_with_outline(overlay_draw, "TO ACCESS BLUEPRINT!", w // 2, cy1 + 290, body_font, (255, 255, 255, 255))
                    
                    img_pil = Image.alpha_composite(img_pil, overlay)
                    
                return np.array(img_pil.convert("RGB"))
                
            video_sequence = video_sequence.transform(lambda gf, t: process_frame(gf(t), t))
            final_video = video_sequence.with_audio(audio_clip)
            final_video.write_videofile(
                output_mp4_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                logger=None
            )
            
        finally:
            if audio_clip:
                audio_clip.close()
            for c in clips:
                try:
                    c.close()
                except Exception:
                    pass
            if final_video:
                try:
                    final_video.close()
                except Exception:
                    pass
                    
        return output_mp4_path

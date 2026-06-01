import logging
import sqlite3
import hashlib
import time
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, DATABASE_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIEngine")

def log_agent(msg: str):
    logger.info(msg)
    try:
        import streamlit as st
        if "agent_logs" not in st.session_state:
            st.session_state["agent_logs"] = []
        st.session_state["agent_logs"].append(msg)
    except Exception:
        pass

class TimelineSegmentSchema(BaseModel):
    start: float = Field(..., description="Start timestamp in seconds (e.g. 0.0).")
    end: float = Field(..., description="End timestamp in seconds (e.g. 3.5).")
    segment: str = Field(..., description="Segment type: must be either HOOK, STORY, INSIGHTS, or CTA.")
    voiceover_text: str = Field(..., description="The engaging script text to be spoken in this segment. Must fit pacing.")
    visual_cue: str = Field(..., description="Visual scene directive (e.g., zooms, text overlays, high-tech graphs).")
    sfx_cue: str = Field(..., description="Sound effect transition marker (e.g., 'Rapid typing click', 'Whoosh transition').")
    b_roll_keyword: str = Field(..., description="High-fidelity visual keyword description for dynamic mesh backgrounds.")

class ViralPackageSchema(BaseModel):
    total_duration_seconds: float = Field(..., description="Estimated total duration of the script in seconds.")
    timeline: List[TimelineSegmentSchema] = Field(..., description="A sequence of chronological visual and voiceover timeline segments.")
    linkedin_post: str = Field(
        ..., 
        description="A highly formatted professional B2B narrative LinkedIn post following strict PAS (Problem-Agitation-Solution) format."
    )
    instagram_caption: str = Field(
        ..., 
        description="A casual, high-converting caption with emojis, three value bullets, a direct CTA, and hashtag cloud."
    )

class AIEngine:
    def __init__(self):
        self.enabled = False
        try:
            if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                self.enabled = True
                logger.info("Successfully initialized official Gemini Client using google-genai SDK.")
            else:
                self.client = None
                logger.warning("Gemini API key is set to a placeholder. Fallback mode will be triggered.")
        except Exception as e:
            self.client = None
            logger.error(f"Failed to initialize official Google GenAI client: {e}. Activating fallbacks.")

    def fetch_top_performing_scripts(self, niche: str) -> List[str]:
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.script 
                FROM content c
                INNER JOIN trends t ON c.trend_id = t.id
                WHERE LOWER(t.niche) = ?
                ORDER BY c.performance_views DESC, c.virality_score DESC
                LIMIT 3
            """, (niche.lower().strip(),))
            scripts = [row[0] for row in cursor.fetchall()]
            conn.close()
            return scripts
        except Exception as e:
            logger.warning(f"Failed to query niche memory: {e}")
            return []

    def call_gemini_writer(self, prompt: str) -> Dict[str, Any]:
        if not self.enabled or not self.client:
            return None
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ViralPackageSchema,
                    temperature=0.85,
                ),
            )
            if response.text:
                package = ViralPackageSchema.model_validate_json(response.text)
                return package.model_dump()
        except Exception as e:
            logger.error(f"Gemini API writer error: {e}")
        return None

    def generate_agent_critique(self, script: str, report: Dict[str, Any]) -> str:
        factors = report.get("factors", {})
        flesch_score = report.get("flesch_reading_ease", 80.0)
        
        critique = f"Reviewing initial draft. Virality: {report['virality_score']}/100. Flesch Ease: {flesch_score}.\n"
        
        if factors.get("hook_strength", 50) < 80:
            critique += "  - Hook lacks conversational punch. Replace passive statements with a shock trigger or pattern interrupt.\n"
        if flesch_score < 70.0:
            critique += "  - Script language is too corporate/academic. Simplify sentences. Remove complex vocabulary.\n"
        if factors.get("structure_integrity", 50) < 80:
            critique += "  - Framework is not fully structured. Enforce HOOK -> STORY -> INSIGHTS -> CTA segments.\n"
        if factors.get("cta_power", 50) < 80:
            critique += "  - Call to Action is too passive. Use direct high-intent triggers (e.g. 'Comment below to get access').\n"
        return critique

    def generate_viral_package(self, trend_topic: str, niche: str) -> Dict[str, Any]:
        try:
            import streamlit as st
            st.session_state["agent_logs"] = []
        except Exception:
            pass

        niche_upper = niche.upper()
        log_agent(f"[System Log] Triggering AI Co-Director for niche: {niche_upper}")
        log_agent(f"[System Log] Target Topic: '{trend_topic}'")
        
        top_scripts = self.fetch_top_performing_scripts(niche)
        memory_context = ""
        if top_scripts:
            log_agent(f"[System Log] Evolutionary Memory: Loaded {len(top_scripts)} top-performing scripts from sqlite history.")
            memory_context = "\nBelow are examples of successful past runs in this niche. Study their flow and conversational pace:\n"
            for idx, old_script in enumerate(top_scripts):
                memory_context += f"\n--- PAST HIGH-PERFORMING WORK #{idx+1} ---\n{old_script}\n"
        else:
            log_agent("[System Log] Evolutionary Memory: No performance history found. Bootstrapping raw parameters.")

        framework_instructions = """
        Your generation MUST strictly align with the following copywriting framework constraints:
        
        - VIDEO TIMELINE STRUCTURE: Follow the exact 'Pattern-Interrupt' vertical reel structure:
          1. HOOK (0s - 4s): Must start with an attention-grabbing trigger word or pattern-interrupt root.
          2. STORY (4s - 15s): Agitate the problem and build narrative curiosity.
          3. INSIGHTS (15s - 25s): Deliver clear, metric-driven value or facts.
          4. CTA (25s - 30s): High-converting action trigger.
        
        - LINKEDIN POST: Follow the exact AIDA (Attention, Interest, Desire, Action) framework:
          - Hook paragraph grabs Attention.
          - Bullet points build Interest and Desire.
          - Direct CTA tells them what Action to take.
          - Break lines frequently; keep sentences simple and under 15 words.
          
        - INSTAGRAM CAPTION: Follow the PAS (Problem, Agitation, Solution) framework. Keep it casual, conversational, and rich in emojis.
        """

        prompt = f"""
        You are a world-class viral growth hacker, copywriting agent, and creative director.
        Your task is to generate a comprehensive, highly-viral social media package based on this trend:
        
        TREND TOPIC: "{trend_topic}"
        NICHE: {niche_upper}
        
        {framework_instructions}
        {memory_context}
        
        Deliver a highly engaging visual timeline package matching the structured ViralPackageSchema.
        Ensure the script sounds conversational, simple, and is written at a 5th-7th grade comprehension level.
        """

        draft = None
        if self.enabled and self.client:
            log_agent("[System Log] Spawning Creative Agent (gemini-2.5-flash). Compiling initial draft...")
            draft = self.call_gemini_writer(prompt)
            
            if draft:
                timeline = draft.get("timeline", [])
                full_script = " ".join([seg.get("voiceover_text", "") for seg in timeline])
                
                from core.predictor import ViralityPredictorModel
                report = ViralityPredictorModel().predict_content_virality(full_script)
                score = report["virality_score"]
                flesch_score = report["flesch_reading_ease"]
                
                log_agent(f"[Predictor Evaluator] Draft Score: Virality = {score}/100 | Flesch Ease = {flesch_score}")
                
                if score < 80:
                    critique = self.generate_agent_critique(full_script, report)
                    log_agent(f"[Critic Agent] Audit Complete:\n{critique}")
                    log_agent("[System Log] Dispatching critique to Creative Agent for final optimization pass...")
                    
                    rewrite_prompt = f"""
                    You are the Creative Writer Agent in a critique-and-rewrite multi-agent loop.
                    Your goal is to rewrite this viral content package to score >= 80 on virality.
                    
                    CRITIQUE AUDIT:
                    {critique}
                    
                    ORIGINAL DRAFT:
                    {draft}
                    
                    TOPIC: "{trend_topic}" | NICHE: {niche_upper}
                    
                    Rewrite ALL timeline segments and social copies with the critique in mind.
                    The script must be highly conversational, punchy, and follow HOOK->STORY->INSIGHTS->CTA.
                    Make it 100% specific to the topic above — no generic filler.
                    """
                    
                    rewritten = self.call_gemini_writer(rewrite_prompt)
                    if rewritten:
                        draft = rewritten
                        log_agent("[System Log] Adversarial rewrite complete. Final assets compiled.")
                    else:
                        log_agent("[System Log] Rewrite quota exceeded. Using initial draft.")
                else:
                    log_agent(f"[System Log] Score {score}/100 cleared threshold. No rewrite needed.")
                
                return draft

        log_agent("[System Log] Gemini Client disabled. Bootstrapping dynamic professional fallback assets.")
        return self._generate_high_fidelity_fallback(trend_topic, niche_upper)

    def _generate_high_fidelity_fallback(self, topic: str, niche: str) -> Dict[str, Any]:
        clean_topic = topic.split(":")[0].strip() if ":" in topic else topic.strip()
        niche_cap = niche.capitalize()
        
        topic_hash = int(hashlib.md5(topic.encode()).hexdigest(), 16)
        
        hook_templates = [
            f"Nobody is talking about this yet. {clean_topic} is quietly changing everything — and you need to know why.",
            f"This one caught me off guard. {clean_topic} just flipped everything we knew about {niche_cap}.",
            f"Wait — {clean_topic}? This is bigger than you think. Here's what's actually happening.",
            f"Everyone in {niche_cap} is suddenly talking about {clean_topic}. Here's the real reason why.",
            f"If you haven't heard about {clean_topic} yet, you're already behind. Let me break it down fast.",
        ]
        story_templates = [
            f"For years, the {niche_cap} space was stuck in the same loop — slow, expensive, and falling behind. Then {clean_topic} arrived and broke the pattern entirely.",
            f"Most people in {niche_cap} are still doing things the old way. They don't realize that {clean_topic} has already made that approach obsolete.",
            f"The shift started quietly. A few early movers picked up on {clean_topic} and suddenly their results were completely different from everyone else in {niche_cap}.",
            f"Here's what nobody tells you: the biggest players in {niche_cap} spotted {clean_topic} six months ago. While everyone else waited, they moved fast.",
        ]
        insight_templates = [
            f"Here's the data: teams and creators who adopted {clean_topic} are seeing 3x faster results, lower overhead, and audiences that actually stay engaged. This isn't hype — this is a measurable shift.",
            f"The numbers don't lie. Early adopters of {clean_topic} are reporting major gains in reach, efficiency, and ROI — while late movers are still catching up.",
            f"What makes {clean_topic} different is the compound effect. In {niche_cap}, that means more reach with less effort — and the gap between early and late adopters is widening fast.",
            f"In {niche_cap}, the winners right now are those who understand {clean_topic} deeply. The gap between those who do and those who don't is growing every single week.",
        ]
        cta_templates = [
            "Comment 'SEND IT' below and I'll drop the full breakdown in your DMs. And follow — part 2 drops this week.",
            "Save this video right now. Share it with one person who needs to hear this. And follow for the next breakdown.",
            "Drop a comment with your thoughts — I read every single one. Follow so you don't miss what's coming next.",
            "If this hit different, follow for more breakdowns like this. And comment below — what's your take on this shift?",
        ]
        
        hook_text    = hook_templates[topic_hash % len(hook_templates)]
        story_text   = story_templates[topic_hash % len(story_templates)]
        insight_text = insight_templates[topic_hash % len(insight_templates)]
        cta_text     = cta_templates[topic_hash % len(cta_templates)]
        
        niche_lower = niche.lower()
        if "sport" in niche_lower:
            broll_hook    = f"{clean_topic} stadium crowd energy"
            broll_story   = "athletes training intense close-up"
            broll_insight = "sports statistics data screen"
        elif "entertain" in niche_lower:
            broll_hook    = f"{clean_topic} cinematic reveal"
            broll_story   = "entertainment industry behind the scenes"
            broll_insight = "streaming charts box office numbers"
        elif "politic" in niche_lower:
            broll_hook    = f"{clean_topic} press conference crowd"
            broll_story   = "government building urban city skyline"
            broll_insight = "polling data political infographic"
        elif "finance" in niche_lower or "business" in niche_lower:
            broll_hook    = f"{clean_topic} stock market trading floor"
            broll_story   = "business meeting strategy planning"
            broll_insight = "financial charts upward trend graphs"
        elif "gaming" in niche_lower:
            broll_hook    = f"{clean_topic} gaming setup RGB lights"
            broll_story   = "esports tournament stadium crowd"
            broll_insight = "game analytics dashboard"
        elif "health" in niche_lower:
            broll_hook    = f"{clean_topic} fitness training dynamic"
            broll_story   = "gym workout close-up motion"
            broll_insight = "health data biometric tracking"
        else:
            broll_hook    = f"{clean_topic} technology innovation"
            broll_story   = f"{niche_cap} professionals working"
            broll_insight = f"{niche_cap} data analytics visualization"

        timeline = [
            {
                "start": 0.0, "end": 4.0, "segment": "HOOK",
                "voiceover_text": hook_text,
                "visual_cue": f"Fast zoom in, bold text overlay: '{clean_topic.upper()}'",
                "sfx_cue": "Whoosh speed transition with impact hit",
                "b_roll_keyword": broll_hook
            },
            {
                "start": 4.0, "end": 15.0, "segment": "STORY",
                "voiceover_text": story_text,
                "visual_cue": f"Cinematic B-roll of {niche_cap} context with slow pan",
                "sfx_cue": "Subtle ambient background drone",
                "b_roll_keyword": broll_story
            },
            {
                "start": 15.0, "end": 25.0, "segment": "INSIGHTS",
                "voiceover_text": insight_text,
                "visual_cue": "Data cards fly in, animated charts, split screen comparison",
                "sfx_cue": "Rapid UI ping sounds and data whooshes",
                "b_roll_keyword": broll_insight
            },
            {
                "start": 25.0, "end": 30.0, "segment": "CTA",
                "voiceover_text": cta_text,
                "visual_cue": "Creator face-to-camera, follow button animation, glow effect",
                "sfx_cue": "Uplifting sparkle confirmation chime",
                "b_roll_keyword": f"{niche_cap} creator content studio"
            }
        ]

        li_post = f"""🚀 {clean_topic} is shifting the {niche_cap} landscape — and most people haven't noticed yet.
 
Here's what the data actually shows:
 
The gap between those who understand this and those who don't is growing every week.
 
💡 3 things you need to know right now:
1️⃣ This is not a trend — it's a structural shift in how {niche_cap} operates.
2️⃣ Early adopters are already seeing measurable advantages in reach, efficiency, and output.
3️⃣ The window to get ahead of this is narrowing fast.
 
Whether you're building, investing, or creating in {niche_cap} — this affects you directly.
 
👇 What's your take? Drop a comment — I want to hear how you're approaching this.
 
#{niche_cap.replace(' ', '')} #Innovation #Growth #Strategy #CreatorEconomy"""

        ig_caption = f"""Nobody's talking about this. 🛑 {clean_topic} is changing {niche_cap} faster than people realize.
 
Here's what you need to know right now:
🔥 It's already impacting how top creators operate
📈 Early movers are seeing real, measurable results
💡 And the window to act is closing fast
 
Watch the full breakdown and share this with someone in {niche_cap} who needs to see it. 👇
 
#{''.join(w.capitalize() for w in niche_cap.split())} #{clean_topic.split()[0].capitalize() if clean_topic.split() else 'Trending'} #ViralContent #CreatorTips #Trending2026"""

        return {
            "total_duration_seconds": 30.0,
            "timeline": timeline,
            "linkedin_post": li_post,
            "instagram_caption": ig_caption
        }

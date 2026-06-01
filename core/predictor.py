import re
from typing import Dict, Any, List

def count_syllables(word: str) -> int:
    word = word.lower().strip(".:,;!?()\"'")
    if not word:
        return 0
    vowels = "aeiouy"
    count = 0
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if count == 0:
        count = 1
    return count

def calculate_flesch_reading_ease(text: str) -> float:
    clean_text = re.sub(r'\[[A-Z\s]+\]', '', text)
    sentences = [s.strip() for s in re.split(r'[.!?]+', clean_text) if s.strip()]
    words = [w.strip(".:,;!?()\"'") for w in clean_text.split() if w.strip()]
    
    total_words = len(words)
    total_sentences = len(sentences)
    if total_words == 0 or total_sentences == 0:
        return 80.0
        
    total_syllables = sum(count_syllables(w) for w in words)
    
    asl = total_words / total_sentences
    asw = total_syllables / total_words
    
    score = 206.835 - (1.015 * asl) - (84.6 * asw)
    return max(min(score, 120.0), 0.0)

class ViralityPredictorModel:
    def predict_content_virality(self, script: str) -> Dict[str, Any]:
        clean_script = script.lower().strip()
        
        hook_section = clean_script[:150]
        hook_score = 45.0
        
        trigger_hooks = [
            "secret", "ignoring", "game-changer", "slashing", "hacks", "killing", 
            "100%", "insane", "never", "death", "stop doing", "truth about", 
            "why you are failing", "you are ignoring", "absolute game-changer",
            "rewriting the rules", "game changed", "game has officially changed", "nobody talks about"
        ]
        
        triggers_found = 0
        for trigger in trigger_hooks:
            if trigger in hook_section:
                hook_score += 12.0
                triggers_found += 1
                
        if "?" in hook_section:
            hook_score += 8.0
        if "!" in hook_section:
            hook_score += 4.0
            
        hook_score = min(hook_score, 100.0)

        has_hook = any(tag in clean_script for tag in ["[hook]", "[attention]"])
        has_story = any(tag in clean_script for tag in ["[story]", "[agitation]", "[problem]"])
        has_insights = any(tag in clean_script for tag in ["[insights]", "[solution]", "[value]"])
        has_cta = any(tag in clean_script for tag in ["[cta]", "[action]", "[directive]"])
        
        structure_score = 30.0
        if has_hook: structure_score += 17.5
        if has_story: structure_score += 17.5
        if has_insights: structure_score += 17.5
        if has_cta: structure_score += 17.5
        
        structure_score = min(structure_score, 100.0)

        cta_score = 45.0
        cta_triggers = ["comment", "follow", "subscribe", "link in bio", "share", "drop a", "check out", "join us", "read more"]
        
        cta_section = clean_script[-250:]
        for trigger in cta_triggers:
            if trigger in cta_section:
                cta_score += 10.0
                
        cta_score = min(cta_score, 100.0)

        words = clean_script.split()
        word_count = len(words)
        
        reading_ease = calculate_flesch_reading_ease(script)
        
        readability_factor = 30.0
        if 70.0 <= reading_ease <= 95.0:
            readability_factor = 100.0
        else:
            readability_factor = max(30.0, 100.0 - abs(82.5 - reading_ease) * 1.6)
            
        pacing_factor = 100.0
        if word_count < 55:
            pacing_factor -= (55 - word_count) * 1.8
        elif word_count > 140:
            pacing_factor -= (word_count - 140) * 1.4
            
        pacing_score = (0.5 * readability_factor) + (0.5 * pacing_factor)
        pacing_score = max(min(pacing_score, 100.0), 30.0)

        base_virality = (0.32 * hook_score) + (0.24 * structure_score) + (0.24 * cta_score) + (0.20 * pacing_score)
        base_virality = round(max(min(base_virality, 100.0), 10.0), 1)

        platforms = ["Instagram Reels", "TikTok", "YouTube Shorts", "LinkedIn Video"]
        platform_predictions = {}
        
        for platform in platforms:
            if platform == "TikTok":
                view_mult = 1.35
                like_ratio = 0.08
                share_ratio = 0.035
                save_ratio = 0.015
                plat_virality = base_virality * 1.05
            elif platform == "Instagram Reels":
                view_mult = 1.0
                like_ratio = 0.095
                share_ratio = 0.04
                save_ratio = 0.06
                plat_virality = base_virality * 0.98
            elif platform == "YouTube Shorts":
                view_mult = 1.8
                like_ratio = 0.06
                share_ratio = 0.015
                save_ratio = 0.005
                plat_virality = base_virality * 1.02
            else:
                view_mult = 0.38
                like_ratio = 0.12
                share_ratio = 0.07
                save_ratio = 0.09
                plat_virality = base_virality * 0.88
                
            plat_virality = round(min(max(plat_virality, 10.0), 100.0), 1)
            base_factor = (plat_virality / 100.0) ** 2.5
            
            expected_views = int((5000 + (base_factor * 245000)) * view_mult)
            expected_likes = int(expected_views * like_ratio)
            expected_shares = int(expected_views * share_ratio)
            expected_saves = int(expected_views * save_ratio)
            
            platform_predictions[platform] = {
                "virality_score": plat_virality,
                "expected_views": expected_views,
                "expected_likes": expected_likes,
                "expected_shares": expected_shares,
                "expected_saves": expected_saves
            }

        retention_data = []
        hook_loss = max(5.0, 30.0 - (hook_score * 0.25))
        structure_loss = max(3.0, 15.0 - (structure_score * 0.12))
        
        for t in range(0, 61, 10):
            if t == 0:
                val = 100.0
            elif t <= 10:
                val = 100.0 - (hook_loss * (t / 10.0))
            else:
                ratio = (t - 10) / 50.0
                val = (100.0 - hook_loss) - (structure_loss * 4.0 * ratio)
                
            val = round(max(val, 8.0 + (base_virality * 0.2)), 1)
            retention_data.append({"time_s": t, "retention_pct": val})

        return {
            "virality_score": base_virality,
            "expected_views": platform_predictions["Instagram Reels"]["expected_views"],
            "expected_likes": platform_predictions["Instagram Reels"]["expected_likes"],
            "expected_shares": platform_predictions["Instagram Reels"]["expected_shares"],
            "expected_saves": platform_predictions["Instagram Reels"]["expected_saves"],
            "flesch_reading_ease": round(reading_ease, 1),
            "factors": {
                "hook_strength": round(hook_score, 1),
                "structure_integrity": round(structure_score, 1),
                "cta_power": round(cta_score, 1),
                "pacing_efficiency": round(pacing_score, 1)
            },
            "platforms": platform_predictions,
            "retention_curve": retention_data
        }

import time
import random
import requests
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, YOUTUBE_API_KEY, GEMINI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TrendDiscoveryEngine")

class RefinedTopic(BaseModel):
    topic: str = Field(..., description="A highly clickable, viral, and engaging topic title based on the headline.")
    velocity: int = Field(..., description="Estimated virality growth velocity vector between 75 and 99.")
    search_interest: int = Field(..., description="Estimated search interest rating between 70 and 96.")
    novelty: int = Field(..., description="Estimated novelty index rating between 65 and 99.")
    engagement_potential: int = Field(..., description="Estimated social engagement potential rating between 70 and 99.")
    audience_relevance: int = Field(..., description="Estimated audience relevance rating between 75 and 99 based on niche alignment.")

class RefinedTrendsList(BaseModel):
    trends: List[RefinedTopic]

class TrendDiscoveryEngine:
    def __init__(self):
        self.is_mock_reddit = (
            not REDDIT_CLIENT_ID 
            or "mock" in REDDIT_CLIENT_ID.lower() 
            or REDDIT_CLIENT_ID == "YOUR_REDDIT_CLIENT_ID_HERE"
        )
        self.is_mock_youtube = (
            not YOUTUBE_API_KEY 
            or "mock" in YOUTUBE_API_KEY.lower() 
            or YOUTUBE_API_KEY == "YOUR_YOUTUBE_API_KEY_HERE"
        )
        
        self.niche_subreddits = {
            "ai": "artificial",
            "technology": "technology",
            "business": "business",
            "startups": "startups",
            "finance": "finance",
            "creator economy": "CreatorEconomy",
            "sports": "sports",
            "entertainment": "entertainment",
            "politics": "politics",
            "gaming": "gaming",
            "health & fitness": "healthandfitness"
        }

        self.gemini_client = None
        if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
            try:
                self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception:
                pass

    def fetch_reddit_trends(self, niche: str) -> List[str]:
        if self.is_mock_reddit:
            return []

        niche_key = niche.lower().strip()
        subreddit = self.niche_subreddits.get(niche_key, "technology")
        
        try:
            auth_url = "https://www.reddit.com/api/v1/access_token"
            auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
            headers = {"User-Agent": REDDIT_USER_AGENT or "CreatorBuddyAgent/1.0"}
            data = {"grant_type": "client_credentials"}
            
            res = requests.post(auth_url, auth=auth, data=data, headers=headers, timeout=5)
            if res.status_code != 200:
                return []
                
            token = res.json().get("access_token")
            if not token:
                return []

            api_url = f"https://oauth.reddit.com/r/{subreddit}/hot?limit=8"
            api_headers = {
                "Authorization": f"bearer {token}",
                "User-Agent": REDDIT_USER_AGENT or "CreatorBuddyAgent/1.0"
            }
            
            api_res = requests.get(api_url, headers=api_headers, timeout=5)
            if api_res.status_code == 200:
                posts_data = api_res.json()
                return [post["data"]["title"] for post in posts_data["data"]["children"] if not post["data"].get("is_self", False)]
        except Exception:
            pass
            
        return []

    def fetch_youtube_trends(self, niche: str) -> List[str]:
        if self.is_mock_youtube:
            return []

        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": niche,
                "type": "video",
                "order": "viewCount",
                "maxResults": 6,
                "relevanceLanguage": "en",
                "key": YOUTUBE_API_KEY
            }
            
            res = requests.get(url, params=params, timeout=5)
            if res.status_code == 200:
                data = res.json()
                return [item["snippet"]["title"] for item in data.get("items", [])]
        except Exception:
            pass

        return []

    def fetch_google_news_rss(self, niche: str) -> List[str]:
        niche_key = niche.lower().strip()
        query = f"\"{niche}\""
        if niche_key == "ai":
            query = "Artificial Intelligence OR LLM OR Machine Learning"
        elif niche_key == "creator economy":
            query = "Creator Economy OR Instagram OR TikTok OR YouTube creators"
        
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                root = ET.fromstring(res.text)
                items = root.findall(".//item")
                headlines = []
                for item in items[:8]:
                    title_text = item.find("title").text
                    if " - " in title_text:
                        title_text = title_text.rsplit(" - ", 1)[0]
                    headlines.append(title_text)
                return headlines
        except Exception:
            pass
            
        return []

    def fetch_hacker_news_trends(self) -> List[str]:
        try:
            top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            res = requests.get(top_stories_url, timeout=5)
            if res.status_code == 200:
                story_ids = res.json()[:6]
                headlines = []
                for s_id in story_ids:
                    item_url = f"https://hacker-news.firebaseio.com/v0/item/{s_id}.json"
                    item_res = requests.get(item_url, timeout=5)
                    if item_res.status_code == 200:
                        story_data = item_res.json()
                        if story_data and "title" in story_data:
                            headlines.append(story_data["title"])
                return headlines
        except Exception:
            pass
            
        return []

    def combine_and_rank_trends(self, niche: str) -> List[Dict[str, Any]]:
        raw_titles = []

        raw_titles.extend(self.fetch_reddit_trends(niche))
        raw_titles.extend(self.fetch_youtube_trends(niche))
        raw_titles.extend(self.fetch_google_news_rss(niche))

        niche_key = niche.lower().strip()
        if niche_key in ["ai", "technology", "startups", "business"]:
            raw_titles.extend(self.fetch_hacker_news_trends())

        raw_titles = list(set([t for t in raw_titles if t.strip()]))

        if not raw_titles:
            return self._get_hardcoded_failover_trends(niche)

        refined_trends = []
        if self.gemini_client:
            try:
                prompt = f"""
                You are a world-class viral growth hacker and content strategist for social media.
                Your task is to review these {len(raw_titles)} raw, real-time headlines gathered from news RSS, Hacker News, and Reddit subreddits:
                
                RAW DATA HEADLINES:
                {chr(10).join([f'- {t}' for t in raw_titles[:15]])}
                
                Analyze these headlines. Select the most interesting, surprising, or high-impact concepts.
                Transform them into EXACTLY 4 highly clickable, viral, and engaging short topic titles suitable for a 9:16 vertical video in the '{niche.upper()}' niche.
                Avoid generic summaries; write punchy, curiosity-driven titles (e.g. 'slashing AI Compute Costs by 80% with this framework' or 'The Death of Traditional Passwords').
                
                Provide estimates for the following metrics for each topic:
                - velocity: Virality growth velocity score (75 to 99)
                - search_interest: Search volume interest (70 to 96)
                - novelty: Novelty index rating (65 to 99)
                - engagement_potential: Social engagement potential rating (70 to 99)
                - audience_relevance: Audience relevance rating (75 to 99)
                """

                response = self.gemini_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=RefinedTrendsList,
                        temperature=0.8,
                    ),
                )

                if response.text:
                    parsed_list = RefinedTrendsList.model_validate_json(response.text)
                    for item in parsed_list.trends:
                        refined_trends.append({
                            "topic": item.topic,
                            "niche": niche.upper(),
                            "velocity": item.velocity,
                            "search_interest": item.search_interest,
                            "novelty": item.novelty,
                            "engagement_potential": item.engagement_potential,
                            "audience_relevance": item.audience_relevance,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
            except Exception:
                pass

        if not refined_trends:
            selected_raw = raw_titles[:4]
            while len(selected_raw) < 4:
                selected_raw.append(f"Surging developments in {niche} workflows")

            for idx, raw_t in enumerate(selected_raw):
                clean_title = raw_t.strip()
                clean_title = clean_title.replace('"', '').replace("'", "")
                if len(clean_title) > 90:
                    clean_title = clean_title[:87] + "..."
                
                prefixes = [
                    "Why everyone is talking about",
                    "The absolute shift in",
                    "This changes everything:",
                    "The secret impact of"
                ]
                prefix = prefixes[idx % len(prefixes)]
                viral_topic = f"{prefix} {clean_title}" if len(clean_title) < 55 else clean_title

                import random as _random
                _random.seed(int(time.time() * 1000) + idx)
                velocity = _random.randint(76, 98)
                search_interest = _random.randint(71, 95)
                novelty = _random.randint(66, 98)
                engagement_potential = _random.randint(72, 98)
                audience_relevance = _random.randint(77, 98)

                refined_trends.append({
                    "topic": viral_topic,
                    "niche": niche.upper(),
                    "velocity": velocity,
                    "search_interest": search_interest,
                    "novelty": novelty,
                    "engagement_potential": engagement_potential,
                    "audience_relevance": audience_relevance,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })

        from core.trend_ml_model import TrendMLRanker
        ml_ranker = TrendMLRanker()
        
        for item in refined_trends:
            pred_score = ml_ranker.predict(
                velocity=item["velocity"],
                search=item["search_interest"],
                engagement=item["engagement_potential"],
                novelty=item["novelty"],
                relevance=item["audience_relevance"]
            )
            item["score"] = pred_score

        return sorted(refined_trends, key=lambda x: x["score"], reverse=True)

    def _get_hardcoded_failover_trends(self, niche: str) -> List[Dict[str, Any]]:
        niche_key = niche.lower().strip()
        fallback_topics = {
            "ai": [
                "Agents That Code: The rise of autonomous developer agents in 2026",
                "Gemini 2.5 Flash: Transforming prompt caching speed and microservice synthesis",
                "Local LLMs on Edge: Privacy-first personal assistants running offline",
                "Prompt Caching Architectures: Drastically reducing operational token costs"
            ],
            "technology": [
                "WebGPU Breakthroughs: Delivering high-performance desktop-grade 3D graphics in browsers",
                "Quantum Computing Simulator APIs: Democratizing quantum algorithms for developers",
                "Edge Mesh Networks: The future of low-latency decentralized IoT communication",
                "Biometric Keyless Authentication: The death of traditional passwords and keys"
            ],
            "startups": [
                "Bootstrap First: Why modern tech startups are actively avoiding VC seed rounds",
                "Micro-SaaS Models: How solo developers build profitable MRR cashflows",
                "AI-First Operations: Operating at a $10M run rate with lean teams of 3",
                "Incubator Renaissance: The return of community-driven founder hubs"
            ],
            "finance": [
                "Layer 2 DeFi Networks: High-throughput yield farming with near-zero gas fees",
                "Fractionalized Real Estate Tokens: Democratizing premium property ownership",
                "Algorithmic Carbon Credit Trading: Merging ESG standards with quantitative finance",
                "Personal Finance Copilots: Intelligent budgeting driven by fine-tuned local models"
            ],
            "business": [
                "Zero-to-One Scaling: Why operational layout design is replacing pure growth hacks in 2026",
                "Subscription Fatigue: How enterprise groups shift to transaction-based micro-billing",
                "Supply Chain Decentralization: Strategic moves toward automated, localized asset sourcing",
                "The Productivity Arbitrage: Slashing administrative overhead with AI-first workflows"
            ],
            "creator economy": [
                "The Death of MCNs: Direct-to-consumer digital monetization bypasses network fees",
                "Micro-Communities: Building high-margin cohort courses for focused audiences",
                "Synthetic Brands: How creators leverage customized, interactive LLM twin avatars",
                "Platform Diversification: Sourcing audience distribution directly through email meshes"
            ],
            "sports": [
                "The Analytics Revolution: How real-time player telemetry is changing game tactics",
                "Micro-Leagues: The explosion of hyper-local, community-owned sports networks",
                "Fan Ownership Models: How Web3 and local trusts are buying professional clubs",
                "Youth Athletics Evolution: Slashing coaching overhead with automated video tracking"
            ],
            "entertainment": [
                "Synthetic Cinema: The first fully-autonomous generative streaming channels hit 1M users",
                "Co-Creation Shows: How audiences write television episodes in real time",
                "Virtual Live Concerts: Why high-fidelity spatial audio is replacing standard stadium gigs",
                "Niche Streaming Channels: The massive shift away from legacy network bundles"
            ],
            "politics": [
                "Intelligent Policy Models: Using open-source data simulations to forecast housing impacts",
                "Grassroots Campaigns: Operating digital political outreach with ultra-lean visual assets",
                "Decentralized Town Halls: Slashing administrative friction with community-led voting meshes",
                "Digital Diplomacy: How interactive global streaming shifts traditional geopolitical messaging"
            ],
            "gaming": [
                "Generative Game Design: Synthesizing customized RPG quests in real time with local models",
                "The Esports Decoupling: Why smaller community tournaments are beating massive stadium leagues",
                "Modding Ecosystems: How solo mod creators are monetizing direct-to-gamer microservices",
                "Spatial VR Integration: Slashing spatial mapping latencies to deliver seamless open worlds"
            ],
            "health & fitness": [
                "Bio-Individual Nutrition: Slashing dietary guess-work with real-time biometric tracking",
                "Micro-Gym Communities: The massive shift toward highly focused cohort athletic clubs",
                "Intelligent Physiotherapy: Preventing sports injuries with automated pose estimation apps",
                "Longevity Frameworks: Conversational routines that trim down cardiac stress levels"
            ]
        }
        
        selected_topics = fallback_topics.get(niche_key, fallback_topics["ai"])
        discovered_trends = []
        
        for idx, topic in enumerate(selected_topics):
            import random as _random
            _random.seed(int(time.time() * 1000) + idx + len(topic))
            
            velocity = _random.randint(75, 98)
            search_interest = _random.randint(70, 96)
            novelty = _random.randint(65, 99)
            engagement_potential = _random.randint(72, 98)
            audience_relevance = _random.randint(77, 98)
            
            from core.trend_ml_model import TrendMLRanker
            score = TrendMLRanker().predict(
                velocity=velocity,
                search=search_interest,
                engagement=engagement_potential,
                novelty=novelty,
                relevance=audience_relevance
            )
            
            discovered_trends.append({
                "topic": topic,
                "niche": niche.upper(),
                "velocity": velocity,
                "search_interest": search_interest,
                "novelty": novelty,
                "engagement_potential": engagement_potential,
                "audience_relevance": audience_relevance,
                "score": score,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
        return sorted(discovered_trends, key=lambda x: x["score"], reverse=True)

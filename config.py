import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "mock_reddit_client_id")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "mock_reddit_client_secret")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "CreatorBuddyAgent/1.0")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "mock_youtube_api_key")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM").strip()

DATABASE_PATH_STR = os.getenv("DATABASE_PATH", "data/creator_buddy.db")
DATABASE_PATH = Path(DATABASE_PATH_STR)

if GEMINI_API_KEY is None or GEMINI_API_KEY.strip() == "":
    raise ValueError(
        "CRITICAL ERROR: 'GEMINI_API_KEY' is entirely missing from the environment. "
        "Please set GEMINI_API_KEY in your .env file (must start with 'AIza...')."
    )

if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    print("WARNING: 'GEMINI_API_KEY' is configured with a placeholder value. Falling back to structured simulations.")

def init_database() -> str:
    db_dir = DATABASE_PATH.parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    outputs_dir = db_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                niche TEXT NOT NULL,
                score REAL NOT NULL,
                timestamp TEXT NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trend_id INTEGER,
                script TEXT NOT NULL,
                ig_caption TEXT NOT NULL,
                li_post TEXT NOT NULL,
                video_path TEXT,
                virality_score REAL,
                visual_keywords TEXT,
                FOREIGN KEY (trend_id) REFERENCES trends (id) ON DELETE CASCADE
            );
        """)

        try:
            cursor.execute("ALTER TABLE content ADD COLUMN visual_keywords TEXT;")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE content ADD COLUMN performance_views INTEGER DEFAULT 0;")
        except sqlite3.OperationalError:
            pass

        for col in ["velocity", "search_interest", "novelty", "engagement_potential", "audience_relevance"]:
            try:
                cursor.execute(f"ALTER TABLE trends ADD COLUMN {col} INTEGER DEFAULT 80;")
            except sqlite3.OperationalError:
                pass

        conn.commit()
    finally:
        conn.close()

    return str(DATABASE_PATH.resolve())

# 🎬 CreatorBuddy AI — Autonomous Viral Reel Agent 🚀

**CreatorBuddy AI** is a state-of-the-art SaaS web application engineered for autonomous trend discovery, local machine learning ranking, high-fidelity AI copywriting, and pixel-perfect synchronized media synthesis.

Designed for developers, creators, and marketers, CreatorBuddy integrates a full suite of AI engines, local ML rankers, and an advanced event-driven video rendering factory, wrapped inside a gorgeous, high-end **Vibrant Cartoon Neo-Brutalist UI**.

---

## ✨ Core Features

### 🤖 1. Zero-API Machine Learning Trend Engine
* **Ensemble Model**: Trains an offline `scikit-learn` `RandomForestRegressor` (with 100 decision trees) on a preloaded dataset of 150 historical trends. Bypasses API costs entirely while capturing complex feature weights.
* **Bulletproof Fallback**: Automatically activates a custom NumPy-based Non-Linear Ridge Regression model if packages are missing.
* **Explainable AI (XAI)**: Computes a perturbation sensitivity analysis ($\pm10\%$) to show users the exact percentage contributions of Growth Velocity, Novelty, and Engagement to the final Trend Score.

### ✍️ 2. AI Creative Co-Director (Gemini 2.5)
* **Evolutionary Memory**: Automatically queries historical sqlite records for top-performing scripts in the selected niche and injects them as a benchmark for the next generation.
* **Structured Output Validation**: Utilizes Pydantic validation schemas (`ViralPackageSchema` & `TimelineSegmentSchema`) via `gemini-2.5-flash` to return structured timelines mapping audio, visual cues, sound effects, and B-roll terms.

### ⏱️ 3. Flawless Subtitle Timing & Voice Sync
* **Event-Driven Captions**: Connects to the Microsoft Edge TTS engine using `boundary="WordBoundary"`. Captures microsecond-accurate speech offsets rather than linear duration estimations.
* **Pause-Aware 3-Word Phrase Grouping**: Groups words into highly readable **2 to 3 word phrases** to prevent text flashing. Automatically splits captions when a pause greater than `0.35 seconds` is detected.
* **Cross-Version MoviePy Timing**: Uses a dynamic fallback wrapper that supports both `.with_start()`/`.with_end()` (MoviePy v2.x) and `.set_start()`/`.set_end()` (MoviePy v1.x).
* **Anti-Clipping Canvas**: Applies a `margin=(20, 20)` to `TextClip` properties, protecting outer outline strokes from being cut off at the canvas boundaries.
* **Memory Leak Prevention**: Employs rigorous `.close()` routines inside `finally` blocks to guarantee robust container deployments.

### 📹 4. HD B-Roll Portrait Crop Pipeline
* **Query Simplification**: Cleans semantic visual terms down to 2-3 high-impact keywords to maximize Pexels search relevance.
* **Center-Cropping (Zero Distortion)**: Center-crops downloaded landscape MP4s into a perfect vertical 9:16 aspect ratio ($720 \times 1280$) without any stretching or squishing.

---

## 🛠️ Setup & Installation Instructions

Follow these instructions to run CreatorBuddy AI locally or host it for free in the cloud.

### A. Local Setup Instructions

#### 1. Prerequisites
Ensure you have the following installed on your machine:
* Python **3.9 to 3.11**
* `git` (to manage versioning)
* **FFmpeg** installed on your system path (required for video/audio rendering)
  * *Windows (via winget)*: `winget install Gyan.FFmpeg`
  * *macOS (via Homebrew)*: `brew install ffmpeg`
  * *Linux (via apt)*: `sudo apt update && sudo apt install ffmpeg`

#### 2. Clone the Repository
```bash
git clone https://github.com/AshishGhodvinde/CreatorBuddy.git
cd CreatorBuddy
```

#### 3. Establish a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 5. Configure API Credentials
Create a `.env` file in the root of the project directory and fill in your API tokens:
```ini
# Core AI Client Config
GEMINI_API_KEY="your_actual_gemini_api_key"

# Media Assets API Config (Optional, Mocked fallback available)
PEXELS_API_KEY="your_pexels_api_key"

# Database Configuration
DATABASE_PATH="data/creatorbuddy.db"
```

#### 6. Run the Application
Start the local Streamlit dashboard server:
```bash
python -m streamlit run app.py
```
Open your browser and navigate to **`http://localhost:8501`**.

---

### B. Free Cloud Deploy Setup (Streamlit Community Cloud)

CreatorBuddy is fully optimized for **Streamlit Community Cloud** hosting:

1. **Push configuration files**: Ensure the `packages.txt` (listing `ffmpeg`) and updated `requirements.txt` are pushed to your GitHub main branch.
2. Go to **[share.streamlit.io](https://share.streamlit.io/)** and click **Sign in with GitHub**.
3. Click **"New App"** in the top-right corner.
4. Select your `CreatorBuddy` repository, set the branch to `main`, and the entry file path to `app.py`.
5. Open the **Settings** menu, click **"Secrets"**, and paste your API keys in TOML format:
   ```toml
   GEMINI_API_KEY = "your_actual_gemini_api_key"
   PEXELS_API_KEY = "your_actual_pexels_api_key"
   DATABASE_PATH = "data/creatorbuddy.db"
   ```
6. Click **Save** and click **Deploy**. Streamlit Cloud will spin up your container, compile FFmpeg, install the requirements, and make your app live!

---

## 📁 Repository Structure

```
├── app.py                  # Entry Point Streamlit Dashboard
├── config.py               # SQLite Migrations & API Configurations
├── packages.txt            # System dependencies (FFmpeg installer)
├── requirements.txt        # Python package dependencies
├── project_overview.md     # In-depth architectural report
├── core/
│   ├── brain.py            # AI Creative Co-Director (Gemini integration)
│   ├── intake.py           # Trend Scanner & Structured Output Manager
│   ├── predictor.py        # Copywriting Flesch & Hook Scorer
│   ├── trend_ml_model.py   # Zero-API RandomForest ML Ranker
│   └── video_studio.py     # Video Synthesis Pipeline (Edge-TTS & MoviePy)
└── ui/
    ├── trend_view.py       # Trend Scanner and decision card interface
    ├── studio_view.py      # CapCut-style script timeline workspace
    └── analytics_view.py   # Engagement breakdowns & SQLite histories
```

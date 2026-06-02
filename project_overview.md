# CreatorBuddy AI — Core Project Overview & Technical Report

Welcome to the **CreatorBuddy AI** system documentation. This comprehensive, "hair-to-toe" overview acts as a central blueprint explaining every service, class, module, database schema, algorithm, and media composition pipeline integrated within the CreatorBuddy ecosystem.

---

## 1. System Architecture

CreatorBuddy is structured following a high-fidelity **Decoupled Three-Tier SaaS Architecture**:

```mermaid
graph TD
    %% Styling
    classDef ui fill:#ffd25a,stroke:#111,stroke-width:2px;
    classDef core fill:#93c5fd,stroke:#111,stroke-width:2px;
    classDef model fill:#c084fc,stroke:#111,stroke-width:2px;
    classDef storage fill:#86efac,stroke:#111,stroke-width:2px;

    %% Components
    A[Streamlit Web UI: app.py]:::ui
    B[Trend scanning: ui/trend_view.py]:::ui
    C[Creator Studio: ui/studio_view.py]:::ui
    D[Analytics Dashboard: ui/analytics_view.py]:::ui
    
    E[Trend Intake Engine: core/intake.py]:::core
    F[AI Scripting Orchestrator: core/brain.py]:::core
    G[Predictive Scorer: core/predictor.py]:::core
    H[Media Synthesis: core/video_studio.py]:::core
    
    I[Zero-API ML Ranker: core/trend_ml_model.py]:::model
    J[SQLite Database: config.py]:::storage

    %% Interactions
    A --> B
    A --> C
    A --> D

    B --> E
    E --> I
    I --> J

    C --> F
    C --> G
    C --> H
    
    H --> J
    D --> J
```

---

## 2. Core Service Deep-Dive

### 2.1 UI Presentation Layer (Streamlit & Custom CSS)

The user interface adopts a high-end **Vibrant Cartoon Neo-Brutalist Drafting Aesthetic**:
* **`app.py`**: The main entry point. It configures the overall theme, registers session states, injects the full-screen dotted drafting grid background (`.cb-dot-grid`), and renders the side border glow columns (`.cb-pillars`). It manages the tab-based navigation spanning Trend Discovery, Creator Studio, and Performance Analytics.
* **`ui/trend_view.py`**: Manages search query submission, triggers the ML trend scoring engine, and renders metrics (Growth, Novelty, Interest) alongside the explainable AI sensitivity breakdowns.
* **`ui/studio_view.py`**: Controls script synthesis and timelines. Provides users with inline script editing and renders the video player displaying the rendered `.mp4`.
* **`ui/analytics_view.py`**: Pulls past runs from SQLite to chart audience retention metrics and view counts.

---

### 2.2 Local Machine Learning Layer (Zero-API cost)

* **`core/trend_ml_model.py`**:
  * **Static Historical Database**: Contains a statically preloaded training set of 150 successful viral trend profiles.
  * **RandomForestRegressor Ensemble**: Trains an ensemble of 100 decision trees to calculate the compound viral weight of incoming trends.
  * **Numpy Fallback Model**: Uses a pure Python multi-layered Non-Linear Ridge Regression model if `scikit-learn` is missing, preventing system crashes.
  * **Explainable AI (XAI)**: Calculates the percentage contribution of each metric using a perturbation analysis delta ($\pm10\%$) and normalizes the standard deviations:
    $$\text{Importance}(x_i) = \text{std\_dev}\left(f(X \pm \delta_i)\right)$$

---

### 2.3 AI Scriptwriting Orchestrator Layer

* **`core/brain.py`**:
  * **Official Google GenAI SDK**: Uses `google-genai` to interact with `gemini-2.5-flash`.
  * **Evolutionary Context Memory**: Automatically queries SQLite for the top 3 highest-rated scripts in the active niche and feeds them into the generation context to train the scriptwriter over time.
  * **Structured Schema Validation**: Enforces exact JSON schemas for B2B social copy, captions, timestamps, and video visual cues:

```mermaid
classDiagram
    class ViralPackageSchema {
        +float total_duration_seconds
        +List~TimelineSegmentSchema~ timeline
        +str linkedin_post
        +str instagram_caption
    }
    class TimelineSegmentSchema {
        +float start
        +float end
        +str segment
        +str voiceover_text
        +str visual_cue
        +str sfx_cue
        +str b_roll_keyword
    }
    ViralPackageSchema *-- TimelineSegmentSchema
```

---

### 2.4 Predictive Scoring Layer

* **`core/predictor.py`**:
  * Evaluates the generated script's virality before compilation.
  * **Flesch Reading Ease Formula**: Analyzes readability by examining sentence structures and syllable counts:
    $$\text{Flesch Score} = 206.835 - 1.015 \left(\frac{\text{words}}{\text{sentences}}\right) - 84.6 \left(\frac{\text{syllables}}{\text{words}}\right)$$
  * **Copywriting Structure Audits**: Checks hook power, the transition structure (Hook $\to$ Story $\to$ Insights $\to$ CTA), and direct CTA keywords to issue improvements.

---

### 2.5 Media Synthesis Layer (flawless Subtitle Sync)

* **`core/video_studio.py`**:
  * **Asynchronous Voice Streaming**: Streams chunks from the Microsoft Edge TTS engine using `boundary="WordBoundary"`.
  * **Event-Driven Subtitle Capture**: Feeds individual `"WordBoundary"` ticks (offset timings) directly into `edge_tts.SubMaker` to generate microsecond-accurate SRT captions.
  * **Pause-Aware Phrase Grouping**: Groups individual words into 2-3 word segments to improve readability. Phrases split when pauses exceed `0.35 seconds`:

```
   Word Timings Stream:
   [Hello (0.1s)] --> [World (0.5s)] --> (pause: 0.45s) --> [Welcome (1.05s)]
   
   Grouped Cues Output:
   1. "HELLO WORLD" (0.1s - 0.5s)
   2. "WELCOME" (1.05s - 1.35s)
```

  * **Pexels Portrait HD Pipeline**: Simplifies search parameters, checks aspect ratios, and crops landscape videos to a portrait 9:16 aspect ratio:
    $$\text{target\_width} = h \times \frac{9}{16}$$
  * **Cross-Version MoviePy Timing**: Uses fallback methods for `.with_start()`/`.with_end()` (MoviePy v2.x) and `.set_start()`/`.set_end()` (MoviePy v1.x) to support different environments.
  * **Zero-Clipping Margins**: Adds `margin=(20, 20)` to `TextClip` properties to prevent outline strokes from clipping at text box borders.
  * **Memory Leak Prevention**: Uses a robust `finally` block to execute `.close()` on all loaded video, audio, text, and composite clips.

---

## 3. Data Pipelines & Mappings

The database schema (defined in `config.py`) is structured as follows:

```mermaid
erDiagram
    trends {
        INTEGER id PK
        TEXT topic
        TEXT niche
        INTEGER score
        INTEGER status
        INTEGER velocity
        INTEGER search_interest
        INTEGER novelty
        INTEGER engagement_potential
        INTEGER audience_relevance
        TEXT timestamp
    }
    content {
        INTEGER id PK
        INTEGER trend_id FK
        TEXT script
        TEXT visual_keywords
        TEXT voiceover_audio_path
        TEXT output_video_path
        TEXT linkedin_post
        TEXT instagram_caption
        INTEGER virality_score
        INTEGER performance_views
        TEXT timestamp
    }
    trends ||--o| content : "generates"
```

---

## 4. Key Execution Flows

### 4.1 Voiceover & Subtitle Extraction Flow

```mermaid
sequenceDiagram
    participant Studio as studio_view.py
    participant Factory as video_studio.py
    participant EdgeTTS as Microsoft Edge TTS
    participant SubMaker as edge_tts.SubMaker
    
    Studio->>Factory: async_generate_voiceover(text)
    Factory->>EdgeTTS: Request Audio Stream (boundary="WordBoundary")
    EdgeTTS-->>Factory: Yield Stream Chunk
    alt chunk type == "audio"
        Factory->>Factory: Save Audio Bytes to Disk
    else chunk type == "WordBoundary"
        Factory->>SubMaker: feed(chunk)
    end
    Factory->>SubMaker: get_srt()
    Factory-->>Studio: Save data/cache/subtitles.srt
```

### 4.2 Timeline Composition Flow

```mermaid
flowchart TD
    A[Start assemble_reel_video] --> B[Load Voice Audio File]
    B --> C[Fetch and Clean B-Roll Search Terms]
    C --> D[Download Pexels Video Clips]
    D --> E{Portrait check?}
    E -- Yes --> F[Resize to 720x1280]
    E -- No --> G[Center Crop landscape to 9:16] --> F
    F --> H[Concatenate Clips to Match Voice Duration]
    H --> I[Parse subtitles.srt & Group into 3-Word Phrases]
    I --> J{TextClip composite functional?}
    J -- Yes --> K[Generate Styled TextClips with 20px margins]
    K --> L[Align times via set_start/with_start fallback]
    L --> M[Layer overlays using CompositeVideoClip] --> O[Merge Composed video & Audio Track]
    J -- No --> N[Apply PIL Frame Drawing transform] --> O
    O --> P[Render and Export final MP4]
    P --> Q[Clean Resource closing in finally block]
```

# EraForge

### Turn History Into Motion

![EraForge Interface](![alt text](image.png))

EraForge is an open-source, local-first AI-assisted application for turning historical scripts into editable animated educational videos.

Write a history script → generate an AI scene plan → edit the timeline → plan assets and geography → generate narration and subtitles → render → export an MP4 video.

---

## Features

- AI-assisted historical scene planning
- Structured scene schema
- Editable scene timeline
- Scene timing validation
- Scene asset planning
- Local asset resolution
- Geographic/map planning
- Scene animation rendering
- Local text-to-speech narration
- Narration timeline validation
- Automatic subtitle generation
- Subtitle synchronization
- SRT subtitle export
- Video frame rendering
- FFmpeg MP4 export
- Video preview and download
- Project creation and management
- Project persistence
- Script and duration persistence
- Last opened project restoration
- Local-first AI with Ollama
- Optional OpenAI provider
- Configurable CORS and trusted hosts
- Request-size protection
- Security headers
- Sanitized internal error responses

---

## How It Works

```text
Historical Script
       ↓
AI Scene Planner
       ↓
Editable Scene Timeline
       ↓
 ┌─────┼──────────┬────────────┐
 ↓     ↓          ↓            ↓
Assets Geography Narration   Subtitles
 └─────┼──────────┴────────────┘
       ↓
   Render Plan
       ↓
 Frame Renderer
       ↓
    FFmpeg
       ↓
      MP4
````

---

## Tech Stack

### Frontend

* React
* Vite
* JavaScript
* CSS

### Backend

* Python
* FastAPI
* Pydantic

### AI

* Ollama
* Local LLM support
* Optional OpenAI provider

### Media

* Pillow
* FFmpeg
* Local Text-to-Speech

---

## Project Structure

```text
EraForge/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   ├── assets.py
│   │   ├── asset_manifest.py
│   │   ├── asset_planner.py
│   │   ├── geography.py
│   │   ├── geography_manifest.py
│   │   ├── geography_planner.py
│   │   ├── narration.py
│   │   ├── project_store.py
│   │   ├── renderer.py
│   │   ├── renderer_planner.py
│   │   ├── render_pipeline.py
│   │   ├── scene_renderer.py
│   │   ├── security.py
│   │   ├── subtitles.py
│   │   ├── video_export.py
│   │   └── video_pipeline.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── ...
│
├── frontend/
│   └── src/
│       ├── main.jsx
│       └── styles.css
│
├── docs/
├── projects/
├── tests/
├── .gitignore
├── LICENSE
└── README.md
```

---

## Requirements

Before running EraForge, install:

* Python 3.11+
* Node.js
* FFmpeg
* Ollama

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/chotarahat/EraForge.git
cd EraForge
```

---

### 2. Backend

```powershell
cd backend

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Create your environment file:

```powershell
Copy-Item .env.example .env
```

---

### 3. Frontend

Open another terminal:

```powershell
cd frontend

npm install
```

---

## Run EraForge

### Backend

From the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/api/health
```

---

### Frontend

In another terminal:

```powershell
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

---

## AI Provider

EraForge uses Ollama locally by default.

Make sure Ollama is running and download the configured model:

```bash
ollama pull qwen2.5:7b
```

The default local Ollama API is:

```text
http://localhost:11434
```

Example configuration:

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT_SECONDS=900
```

### OpenAI

OpenAI can be used as an optional provider through the backend environment configuration.

Example:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=your_model
```

Never commit API keys or `.env` files.

---

## Video Export

EraForge uses FFmpeg to generate MP4 videos from rendered frames.

Verify FFmpeg:

```powershell
ffmpeg -version
```

The export pipeline is:

```text
Render Plan
    ↓
PNG Frames
    ↓
FFmpeg
    ↓
MP4
```

---

## Projects

EraForge supports local project persistence.

Projects can store:

* Project name
* Source script
* Video duration
* Scene plan
* Project metadata

Supported operations include:

* Create project
* Open project
* Save project
* Update project
* Delete project
* Restore the last opened project

Project data is stored locally.

---

## Configuration

EraForge supports environment-based configuration.

Example:

```env
ERAFORGE_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ERAFORGE_ALLOWED_HOSTS=localhost,127.0.0.1
ERAFORGE_ENABLE_DOCS=true
ERAFORGE_MAX_REQUEST_BYTES=10485760
```

For non-local deployments, configure these values for the actual environment.

---

## API

The backend exposes APIs for:

```text
/api/health

/api/plan
/api/validate-plan

/api/projects
/api/projects/{project_id}

/api/assets/plan
/api/assets/resolve

/api/geography/plan

/api/narration/plan
/api/narration/generate
/api/narration/manifest
/api/narration/voices
/api/narration/file/{filename}

/api/subtitles/plan
/api/subtitles/sync
/api/subtitles/srt
/api/subtitles/generate
/api/subtitles/file/{filename}

/api/render/plan
/api/render/scene
/api/render/preview
/api/render/file/{filename}
 /api/render/export
/api/render/video/{filename}
```

---

## Testing

### Backend

```powershell
cd backend
python -m unittest discover -s tests -v
```

### Root tests

```powershell
cd ..
python -m unittest discover -s tests -v
```

### Frontend

```powershell
cd frontend
npm run build
```

---

## Security

EraForge includes:

* Configurable CORS origins
* Trusted host protection
* Request-size limits
* Security response headers
* Sanitized internal server errors
* Environment-based configuration
* Path-safe local file serving

---

## Current Status

### v0.1.0

EraForge currently provides the core end-to-end workflow:

```text
Script
  ↓
AI Scene Planning
  ↓
Timeline Editing
  ↓
Assets + Geography
  ↓
Narration + Subtitles
  ↓
Frame Rendering
  ↓
FFmpeg
  ↓
MP4 Export
```

The project is currently focused on improving visual quality, animation capabilities, and the overall video-generation workflow.

---

## Roadmap

* Advanced character animation
* Richer asset generation
* More advanced map animations
* Improved cinematic camera controls
* Additional TTS providers
* Higher-quality rendering
* More advanced timeline editing
* Batch video generation
* Improved project portability
* Easier distribution and packaging

---

## Contributing

Contributions, bug reports, feature requests, documentation improvements, and pull requests are welcome.

Before submitting a pull request:

1. Run the backend test suite.
2. Run the frontend production build.
3. Verify that the working tree is clean.
4. Describe the changes clearly in the pull request.

---

## License

EraForge is released under the MIT License.

See [LICENSE](LICENSE).

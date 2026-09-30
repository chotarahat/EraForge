# EraForge

**Turn History Into Motion.**

EraForge is an open-source AI-assisted application for turning historical scripts into animated educational videos.

## v0.1 goal

Script → AI scene plan → editable scene timeline.

This first milestone does not render video yet. It establishes the structured scene language that the future renderer will consume.

## Stack

- Backend: FastAPI + Python
- AI: Ollama with local structured outputs by default; OpenAI is optional
- Frontend: React + Vite
- Future renderer: Remotion + FFmpeg

## Run locally

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Install Ollama, then download the default model once:
python run.py
```

Backend: http://127.0.0.1:8000
Health check: http://127.0.0.1:8000/api/health

### Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL shown by Vite, usually http://localhost:5173.

## AI provider

EraForge uses Ollama locally by default. Keep Ollama running and make sure the configured model is downloaded with `ollama pull qwen2.5:7b` if it is not already installed. Planning requests use the local Ollama API at `http://localhost:11434`; no API key or cloud request is needed.

The defaults can be changed in `backend/.env`:

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT_SECONDS=900
```

OpenAI remains available as an optional paid provider by setting `AI_PROVIDER=openai`, `OPENAI_API_KEY`, and optionally `OPENAI_MODEL` in `backend/.env`.

Never commit `.env` or API keys.

## Roadmap

- [x] Script → scene planner
- [x] Structured scene schema
- [x] Editable scene timeline UI
- [ ] Scene asset resolver
- [ ] Geographic map layer
- [ ] Remotion renderer
- [ ] Voice generation
- [ ] Subtitle generation
- [ ] MP4 export
- [x] Local AI provider support

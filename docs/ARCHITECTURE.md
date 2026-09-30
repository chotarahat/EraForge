# EraForge v0.1 Architecture

```text
User Script
    |
    v
React Frontend
    |
    | POST /api/plan
    v
FastAPI Backend
    |
    v
AI Provider (Ollama by default; OpenAI optional)
    |
    | Structured ScenePlan JSON
    v
Editable Timeline
    |
    v
Future: Asset Resolver -> Remotion -> FFmpeg -> MP4
```

## ScenePlan contract

The AI returns a stable JSON structure. The renderer will later consume the same contract without needing to understand the original script.

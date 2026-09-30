import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_URL = "http://127.0.0.1:8000";

const defaultScript = `Before Bangladesh...\nbefore Bengal...\nbefore humans ever walked this land...\n\nMillions of years ago, the region we now call Bangladesh was part of a constantly changing geological world.`;

function App() {
  const [script, setScript] = useState(defaultScript);
  const [duration, setDuration] = useState(60);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [plan, setPlan] = useState(null);
  const [aiConfig, setAIConfig] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/api/health`)
      .then((response) => response.json())
      .then((data) => setAIConfig(data))
      .catch(() => setAIConfig(null));
  }, []);

  async function generatePlan() {
    setLoading(true);
    setError("");
    setPlan(null);

    try {
      const response = await fetch(`${API_URL}/api/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          script,
          duration: Number(duration),
          aspect_ratio: "9:16",
          style: "animated historical documentary"
        })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Scene planning failed");
      setPlan(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <header>
        <div>
          <div className="brand">Era<span>Forge</span></div>
          <div className="tagline">TURN HISTORY INTO MOTION</div>
        </div>
        <div className="version">v0.1</div>
      </header>

      <main className="workspace">
        <section className="panel input-panel">
          <h2>Script</h2>
          <p className="muted">Give EraForge the narration. v0.1 turns it into an editable scene plan.</p>
          <textarea value={script} onChange={(e) => setScript(e.target.value)} />
          <div className="controls">
            <label>
              Duration
              <select value={duration} onChange={(e) => setDuration(e.target.value)}>
                <option value="30">30 sec</option>
                <option value="60">60 sec</option>
                <option value="90">90 sec</option>
                <option value="120">120 sec</option>
              </select>
            </label>
            <div className="generation-meta">
              <div className="meta">Format: 9:16 · Style: Animated documentary</div>
              <div className="provider-status">
                <span className="provider-indicator" aria-hidden="true" />
                <span>{aiConfig?.provider === "openai" ? "OpenAI API" : "Local · Ollama"}</span>
                <span className="provider-model">{aiConfig?.model || "qwen2.5:7b"}</span>
              </div>
            </div>
          </div>
          <button className="generate" disabled={loading || script.trim().length < 20} onClick={generatePlan}>
            {loading ? "Planning scenes…" : "Generate Scene Plan"}
          </button>
          {error && <div className="error">{error}</div>}
        </section>

        <section className="panel output-panel">
          <div className="panel-heading">
            <div>
              <h2>Scene Timeline</h2>
              <p className="muted">AI-generated storyboard for the renderer.</p>
            </div>
            {plan && <span className="pill">{plan.scenes.length} scenes</span>}
          </div>

          {!plan ? (
            <div className="empty">Your generated scene plan will appear here.</div>
          ) : (
            <div className="timeline">
              {plan.scenes.map((scene) => (
                <article className="scene" key={scene.id}>
                  <div className="scene-time">{scene.start.toFixed(1)}s → {scene.end.toFixed(1)}s</div>
                  <h3>{scene.title}</h3>
                  <p><strong>Visual:</strong> {scene.visual}</p>
                  <p><strong>Animation:</strong> {scene.animation}</p>
                  <p><strong>Camera:</strong> {scene.camera}</p>
                  <div className="caption">{scene.caption}</div>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);

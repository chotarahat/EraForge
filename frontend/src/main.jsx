import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_URL = "http://127.0.0.1:8000";

const defaultScript = `Before Bangladesh...\nbefore Bengal...\nbefore humans ever walked this land...\n\nMillions of years ago, the region we now call Bangladesh was part of a constantly changing geological world.`;

const MIN_SCENE_DURATION = 0.1;

function normalizeTimeline(scenes, targetDuration) {
  if (!scenes.length) return [];

  const durations = scenes.map((scene) => {
    const start = Number(scene.start);
    const end = Number(scene.end);

    return Math.max(end - start, MIN_SCENE_DURATION);
  });

  let total = durations.reduce((sum, value) => sum + value, 0);

  if (total < targetDuration) {
    durations[durations.length - 1] += targetDuration - total;
    total = targetDuration;
  }

  if (total > targetDuration) {
    let excess = total - targetDuration;

    for (let i = durations.length - 1; i >= 0 && excess > 0; i -= 1) {
      const reducible = Math.max(
        durations[i] - MIN_SCENE_DURATION,
        0
      );

      const reduction = Math.min(reducible, excess);

      durations[i] -= reduction;
      excess -= reduction;
    }

    if (excess > 0) {
      const minimumTotal =
        scenes.length * MIN_SCENE_DURATION;

      if (targetDuration < minimumTotal) {
        throw new Error(
          `Video duration is too short for ${scenes.length} scenes.`
        );
      }

      const scale =
        (targetDuration - minimumTotal) /
        (total - minimumTotal);

      for (let i = 0; i < durations.length; i += 1) {
        durations[i] =
          MIN_SCENE_DURATION +
          (durations[i] - MIN_SCENE_DURATION) * scale;
      }
    }
  }

  let currentTime = 0;

  return scenes.map((scene, index) => {
    const start = currentTime;
    const end =
      index === scenes.length - 1
        ? targetDuration
        : currentTime + durations[index];

    currentTime = end;

    return {
      ...scene,
      start: Number(start.toFixed(3)),
      end: Number(end.toFixed(3)),
    };
  });
}

function validateTimeline(plan) {
  if (!plan || !plan.scenes?.length) {
    return ["No scenes available."];
  }

  const errors = [];
  const targetDuration = Number(plan.total_duration);

  let previousEnd = 0;

  plan.scenes.forEach((scene, index) => {
    const start = Number(scene.start);
    const end = Number(scene.end);

    if (start < 0) {
      errors.push(`Scene ${index + 1} starts before 0 seconds.`);
    }

    if (end <= start) {
      errors.push(
        `Scene ${index + 1} has an invalid duration.`
      );
    }

    if (Math.abs(start - previousEnd) > 0.01) {
      errors.push(
        `Scene ${index + 1} creates a gap or overlap.`
      );
    }

    previousEnd = end;
  });

  if (Math.abs(previousEnd - targetDuration) > 0.01) {
    errors.push(
      `Timeline ends at ${previousEnd.toFixed(
        2
      )}s instead of ${targetDuration.toFixed(2)}s.`
    );
  }

  return errors;
}

function App() {
  const [script, setScript] = useState(defaultScript);
  const [duration, setDuration] = useState(60);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [plan, setPlan] = useState(null);
  const [draftPlan, setDraftPlan] = useState(null);
  const [savedPlan, setSavedPlan] = useState(null);
  const [aiConfig, setAIConfig] = useState(null);
  const [assetPlan, setAssetPlan] = useState([]);
  const [narrationPlan, setNarrationPlan] = useState({
    segments: [],
  });
  const [subtitleTrack, setSubtitleTrack] = useState({
    cues: [],
  });
  const [subtitleSrt, setSubtitleSrt] = useState("");
  const [subtitleOutputFile, setSubtitleOutputFile] = useState("");
  const [subtitleLoading, setSubtitleLoading] = useState(false);
  const [subtitleError, setSubtitleError] = useState("");
  const [narrationManifest, setNarrationManifest] = useState({
    segments: [],
  });
  const [narrationManifestLoading, setNarrationManifestLoading] =
    useState(false);
  const [narrationVoices, setNarrationVoices] = useState([]);
  const [selectedNarrationVoice, setSelectedNarrationVoice] = useState("");
  const [narrationRate, setNarrationRate] = useState(170);
  const [narrationVolume, setNarrationVolume] = useState(1);
  const [narrationLoading, setNarrationLoading] = useState(false);
  const [narrationError, setNarrationError] = useState("");
  const [selectedNarrationScene, setSelectedNarrationScene] = useState(null);
  const [renderPreview, setRenderPreview] = useState(null);
  const [renderLoading, setRenderLoading] = useState(false);
  const [renderError, setRenderError] = useState("");
  const [selectedRenderScene, setSelectedRenderScene] = useState(null);
  const [assetLoading, setAssetLoading] = useState(false);
  const [assetError, setAssetError] = useState("");
  const [assetResolution, setAssetResolution] = useState({
    resolved: [],
    missing: [],
    placeholders: [],
  });

  const [assetResolving, setAssetResolving] = useState(false);
  const [geographyPlan, setGeographyPlan] = useState({});
  const [geographyLoading, setGeographyLoading] = useState(false);
  const [geographyError, setGeographyError] = useState("");
  const timelineErrors = draftPlan
    ? validateTimeline(draftPlan)
    : [];

  useEffect(() => {
    fetch(`${API_URL}/api/health`)
      .then((response) => response.json())
      .then((data) => setAIConfig(data))
      .catch(() => setAIConfig(null));
  }, []);

  useEffect(() => {
    loadNarrationVoices();
  }, []);

  async function refreshAssetPlan(planToAnalyze = draftPlan) {
    if (!planToAnalyze) {
      setAssetPlan([]);
      return;
    }

    try {
      setAssetLoading(true);
      setAssetError("");

      const response = await fetch(`${API_URL}/api/assets/plan`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(planToAnalyze),
      });

      const data = await response.json();

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join("; ")
          : data.detail || "Failed to build asset plan.";

        throw new Error(detail);
      }

      setAssetPlan(data);
    } catch (err) {
      setAssetError(err.message || "Failed to build asset plan.");
      setAssetPlan([]);
    } finally {
      setAssetLoading(false);
    }
  }

  async function resolveAssets(planToResolve = draftPlan) {
    if (!planToResolve) {
      return;
    }

    try {
      setAssetResolving(true);
      setAssetError("");

      const response = await fetch(
        `${API_URL}/api/assets/resolve`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(planToResolve),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join("; ")
          : data.detail || "Failed to resolve assets.";

        throw new Error(detail);
      }

      setAssetResolution(data);
    } catch (err) {
      setAssetError(
        err.message || "Failed to resolve assets."
      );

      setAssetResolution({
        resolved: [],
        missing: [],
        placeholders: [],
      });
    } finally {
      setAssetResolving(false);
    }
  }

  async function loadNarrationVoices() {
    try {
      const response = await fetch(
        `${API_URL}/api/narration/voices`
      );

      if (!response.ok) {
        throw new Error("Failed to load narration voices");
      }

      const data = await response.json();

      setNarrationVoices(data.voices || []);

      if (data.voices?.length && !selectedNarrationVoice) {
        setSelectedNarrationVoice(data.voices[0].id);
      }
    } catch (error) {
      setNarrationError(
        error.message || "Failed to load narration voices"
      );
    }
  }

  async function generateNarration() {
    setNarrationLoading(true);
    setNarrationError("");

    try {
      const payload = {
        ...plan,
        _narration_settings: {
          voice: selectedNarrationVoice || null,
          rate: Number(narrationRate),
          volume: Number(narrationVolume),
        },
      };

      const response = await fetch(
        `${API_URL}/api/narration/generate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        throw new Error(
          errorData.detail ||
            `Narration generation failed (${response.status})`
        );
      }

      const data = await response.json();

      setNarrationPlan(data);

      if (data.segments?.length) {
        setSelectedNarrationScene(data.segments[0].scene_id);
      }

      await syncNarrationManifest(data);
    } catch (error) {
      setNarrationError(
        error.message || "Failed to generate narration"
      );
    } finally {
      setNarrationLoading(false);
    }
  }

  async function generateSubtitles() {
    setSubtitleLoading(true);
    setSubtitleError("");

    try {
      let narrationManifestData = null;

      if (narrationPlan?.segments?.length) {
        const manifestResponse = await fetch(
          `${API_URL}/api/narration/manifest`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              plan,
              narration: narrationPlan,
            }),
          }
        );

        if (manifestResponse.ok) {
          narrationManifestData =
            await manifestResponse.json();
        }
      }

      const response = await fetch(
        `${API_URL}/api/subtitles/plan`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(plan),
        }
      );

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({}));

        throw new Error(
          errorData.detail ||
            `Subtitle generation failed (${response.status})`
        );
      }

      const track = await response.json();

      setSubtitleTrack(track);

      const srtResponse = await fetch(
        `${API_URL}/api/subtitles/srt`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(plan),
        }
      );

      if (!srtResponse.ok) {
        const errorData = await srtResponse
          .json()
          .catch(() => ({}));

        throw new Error(
          errorData.detail ||
            `Subtitle SRT generation failed (${srtResponse.status})`
        );
      }

      const srtData = await srtResponse.json();

      setSubtitleSrt(
        srtData.srt || ""
      );

      if (narrationManifestData) {
        const syncResponse = await fetch(
          `${API_URL}/api/subtitles/sync`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              plan,
              narration_manifest:
                narrationManifestData,
            }),
          }
        );

        if (syncResponse.ok) {
          const syncData =
            await syncResponse.json();

          if (!syncData.valid) {
            setSubtitleError(
              syncData.issues
                .map((issue) => issue.message)
                .join(" ")
            );
          }
        }
      }
    } catch (error) {
      setSubtitleError(
        error.message ||
          "Failed to generate subtitles"
      );
    } finally {
      setSubtitleLoading(false);
    }
  }

  async function generateSubtitleFile() {
    setSubtitleLoading(true);
    setSubtitleError("");

    try {
      const response = await fetch(
        `${API_URL}/api/subtitles/generate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(plan),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        throw new Error(
          errorData.detail ||
            `Subtitle file generation failed (${response.status})`
        );
      }

      const data = await response.json();

      setSubtitleSrt(data.srt || "");
      setSubtitleOutputFile(data.output_file || "");

      const trackResponse = await fetch(
        `${API_URL}/api/subtitles/plan`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(plan),
        }
      );

      if (trackResponse.ok) {
        const track = await trackResponse.json();
        setSubtitleTrack(track);
      }
    } catch (error) {
      setSubtitleError(
        error.message || "Failed to generate subtitle file"
      );
    } finally {
      setSubtitleLoading(false);
    }
  }

  async function syncNarrationManifest(narrationData = narrationPlan) {
    if (!plan?.scenes?.length || !narrationData?.segments?.length) {
      setNarrationManifest({
        segments: [],
      });
      return;
    }

    setNarrationManifestLoading(true);
    setNarrationError("");

    try {
      const response = await fetch(
        `${API_URL}/api/narration/manifest`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            plan,
            narration: narrationData,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        throw new Error(
          errorData.detail ||
            `Narration sync failed (${response.status})`
        );
      }

      const data = await response.json();

      setNarrationManifest(data);
    } catch (error) {
      setNarrationError(
        error.message || "Failed to sync narration timeline"
      );
    } finally {
      setNarrationManifestLoading(false);
    }
  }

  async function renderPreviewScenes() {
    setRenderLoading(true);
    setRenderError("");

    try {
      const response = await fetch(`${API_URL}/api/render/preview`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(plan),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Render failed (${response.status})`
        );
      }

      const data = await response.json();

      setRenderPreview(data);

      if (data.scene_files?.length) {
        setSelectedRenderScene(data.scene_files[0]);
      }
    } catch (error) {
      setRenderError(error.message || "Failed to render preview");
    } finally {
      setRenderLoading(false);
    }
  }

  async function planGeography(planToAnalyze = draftPlan) {
    if (!planToAnalyze) {
      setGeographyPlan({});
      return;
    }

    try {
      setGeographyLoading(true);
      setGeographyError("");

      const response = await fetch(
        `${API_URL}/api/geography/plan`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(planToAnalyze),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join("; ")
          : data.detail || "Failed to build geography plan.";

        throw new Error(detail);
      }

      setGeographyPlan(data);
    } catch (err) {
      setGeographyError(
        err.message || "Failed to build geography plan."
      );

      setGeographyPlan({});
    } finally {
      setGeographyLoading(false);
    }
  }
  
  function updateScene(sceneId, field, value) {
    setDraftPlan((current) => {
      if (!current) return current;

      const targetDuration = Number(current.total_duration);

      if (field !== "start" && field !== "end") {
        return {
          ...current,
          scenes: current.scenes.map((scene) =>
            scene.id === sceneId
              ? {
                  ...scene,
                  [field]:
                    field === "asset_hints"
                      ? value
                      : value,
                }
              : scene
          ),
        };
      }

      const index = current.scenes.findIndex(
        (scene) => scene.id === sceneId
      );

      if (index === -1) return current;

      const scenes = current.scenes.map((scene) => ({
        ...scene,
      }));

      const scene = scenes[index];

      const numericValue = Number(value);

      if (!Number.isFinite(numericValue)) {
        return current;
      }

      if (field === "start") {
        const minimumStart =
          index === 0
            ? 0
            : Number(scenes[index - 1].start) + MIN_SCENE_DURATION;

        const maximumStart =
          Number(scene.end) - MIN_SCENE_DURATION;

        const newStart = Math.min(
          Math.max(numericValue, minimumStart),
          maximumStart
        );

        scene.start = newStart;

        if (index > 0) {
          scenes[index - 1].end = newStart;
        }
      }

      if (field === "end") {
        const minimumEnd =
          Number(scene.start) + MIN_SCENE_DURATION;

        const newEnd = Math.min(
          Math.max(numericValue, minimumEnd),
          targetDuration
        );

        scene.end = newEnd;
      }

      return {
        ...current,
        scenes: normalizeTimeline(
          scenes,
          targetDuration
        ),
      };
    });
  }

  function resequenceScenes(scenes) {
    let currentTime = 0;

    return scenes.map((scene) => {
      const rawDuration = Number(scene.end) - Number(scene.start);
      const sceneDuration = Math.max(rawDuration, 0.1);

      const updatedScene = {
        ...scene,
        start: Number(currentTime.toFixed(3)),
        end: Number((currentTime + sceneDuration).toFixed(3)),
      };

      currentTime += sceneDuration;

      return updatedScene;
    });
  }

  function deleteScene(sceneId) {
    setDraftPlan((current) => {
      if (!current || current.scenes.length <= 1) {
        return current;
      }

      const index = current.scenes.findIndex(
        (scene) => scene.id === sceneId
      );

      if (index === -1) return current;

      const removedScene = current.scenes[index];
      const remaining = current.scenes.filter(
        (scene) => scene.id !== sceneId
      );

      if (remaining.length === 0) {
        return current;
      }

      // Give the removed scene's duration to the next scene.
      const removedDuration =
        Number(removedScene.end) - Number(removedScene.start);

      const targetIndex =
        index < remaining.length ? index : remaining.length - 1;

      const updated = remaining.map((scene, i) => {
        if (i !== targetIndex) return scene;

        return {
          ...scene,
          end: Number(
            (Number(scene.end) + Math.max(removedDuration, 0)).toFixed(3)
          ),
        };
      });

      return {
        ...current,
        scenes: resequenceScenes(updated),
      };
    });
  }

  function duplicateScene(sceneId) {
    setDraftPlan((current) => {
      if (!current) return current;

      const index = current.scenes.findIndex(
        (scene) => scene.id === sceneId
      );

      if (index === -1) return current;

      const original = current.scenes[index];

      const originalDuration =
        Number(original.end) - Number(original.start);

      const duration = Math.max(originalDuration, 0.2);
      const halfDuration = duration / 2;

      const first = {
        ...original,
        end: original.start + halfDuration,
      };

      const duplicate = {
        ...structuredClone(original),
        id: `${original.id}-copy-${Date.now()}`,
        start: original.start + halfDuration,
        end: original.end,
        title: `${original.title} (Copy)`,
      };

      const scenes = [...current.scenes];

      scenes.splice(index, 1, first, duplicate);

      return {
        ...current,
        scenes: resequenceScenes(scenes),
      };
    });
  }

  function moveScene(sceneId, direction) {
    setDraftPlan((current) => {
      if (!current) return current;

      const index = current.scenes.findIndex(
        (scene) => scene.id === sceneId
      );

      if (index === -1) return current;

      const newIndex = index + direction;

      if (newIndex < 0 || newIndex >= current.scenes.length) {
        return current;
      }

      const scenes = [...current.scenes];

      [scenes[index], scenes[newIndex]] = [
        scenes[newIndex],
        scenes[index],
      ];

      return {
        ...current,
        scenes: resequenceScenes(scenes),
      };
    });
  }

  function addScene() {
    setDraftPlan((current) => {
      if (!current) return current;

      const scenes = current.scenes;

      if (scenes.length === 0) {
        return current;
      }

      // Split the longest scene so the total video duration stays unchanged.
      let longestIndex = 0;
      let longestDuration = -1;

      scenes.forEach((scene, index) => {
        const duration =
          Number(scene.end) - Number(scene.start);

        if (duration > longestDuration) {
          longestDuration = duration;
          longestIndex = index;
        }
      });

      const original = scenes[longestIndex];
      const duration = Math.max(
        Number(original.end) - Number(original.start),
        0.2
      );

      const halfDuration = duration / 2;

      const first = {
        ...original,
        end: original.start + halfDuration,
      };

      const second = {
        ...structuredClone(original),
        id: `scene-${Date.now()}`,
        start: original.start + halfDuration,
        end: original.end,
        title: "New Scene",
        narration: "",
        visual: "",
        animation: "",
        camera: "",
        caption: "",
        location: "",
        asset_hints: [],
      };

      const updated = [...scenes];

      updated.splice(longestIndex, 1, first, second);

      return {
        ...current,
        scenes: resequenceScenes(updated),
      };
    });
  }

  async function applyChanges() {
    if (!draftPlan) return;

    if (timelineErrors.length > 0) {
      setError(timelineErrors.join(" "));
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        "http://127.0.0.1:8000/api/validate-plan",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(draftPlan),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        const detail =
          Array.isArray(data.detail)
            ? data.detail
                .map((item) => item.msg)
                .join("; ")
            : data.detail || "Scene plan validation failed.";

        throw new Error(detail);
      }

      const applied = structuredClone(data.plan);

      setSavedPlan(applied);
      setPlan(applied);
      setDraftPlan(applied);

      await refreshAssetPlan(applied);
      await resolveAssets(applied);
      await planGeography(applied);

      setError("");
    } catch (err) {
      setError(err.message || "Failed to validate scene plan.");
    } finally {
      setLoading(false);
    }
  }

  function resetChanges() {
    if (!savedPlan) return;

    const restored = structuredClone(savedPlan);

    setDraftPlan(restored);
    setError("");
  }

  function hasUnsavedChanges() {
    if (!draftPlan || !savedPlan) return false;

    return (
      JSON.stringify(draftPlan) !==
      JSON.stringify(savedPlan)
    );
  }

  async function generatePlan() {
    setLoading(true);
    setError("");

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
      const initialPlan = structuredClone(data);

      setPlan(initialPlan);
      setDraftPlan(initialPlan);
      setSavedPlan(initialPlan);

      await refreshAssetPlan(initialPlan);
      await resolveAssets(initialPlan);
      await planGeography(initialPlan);
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
            {draftPlan && <span className="pill">{draftPlan.scenes.length} scenes</span>}
          </div>

          {!draftPlan ? (
            <div className="empty">Your generated scene plan will appear here.</div>
          ) : (
            <>
              <div className="timeline-toolbar">
                <div className="toolbar-left">
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={addScene}
                  >
                    + Add Scene
                  </button>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => refreshAssetPlan(draftPlan)}
                    disabled={
                      !draftPlan ||
                      timelineErrors.length > 0 ||
                      assetLoading
                    }
                  >
                    {assetLoading ? "Planning Assets..." : "Plan Assets"}
                  </button>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => resolveAssets(draftPlan)}
                    disabled={
                      !draftPlan ||
                      timelineErrors.length > 0 ||
                      assetResolving
                    }
                  >
                    {assetResolving
                      ? "Resolving Assets..."
                      : "Resolve Assets"}
                  </button>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => planGeography(draftPlan)}
                    disabled={
                      !draftPlan ||
                      timelineErrors.length > 0 ||
                      geographyLoading
                    }
                  >
                    {geographyLoading
                      ? "Planning Geography..."
                      : "Plan Geography"}
                  </button>

                  <span className="timeline-info">
                    {draftPlan.scenes.length} scenes ·{" "}
                    {draftPlan.total_duration.toFixed(1)}s
                  </span>
                </div>

                <div className="toolbar-right">
                  {hasUnsavedChanges() && (
                    <span className="unsaved-label">
                      Unsaved changes
                    </span>
                  )}

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={resetChanges}
                    disabled={!hasUnsavedChanges()}
                  >
                    Reset
                  </button>

                  <button
                    type="button"
                    className="primary-small-button"
                    onClick={applyChanges}
                    disabled={
                      !hasUnsavedChanges() ||
                      timelineErrors.length > 0
                    }
                  >
                    Apply Changes
                  </button>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={renderPreviewScenes}
                    disabled={renderLoading || !plan?.scenes?.length}
                  >
                    {renderLoading ? "Rendering..." : "Render Preview"}
                  </button>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={generateNarration}
                    disabled={
                      narrationLoading ||
                      !plan?.scenes?.length
                    }
                  >
                    {narrationLoading
                      ? "Generating Narration..."
                      : "Generate Narration"}
                  </button>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={generateSubtitles}
                    disabled={
                      subtitleLoading ||
                      !plan?.scenes?.length
                    }
                  >
                    {subtitleLoading
                      ? "Generating Subtitles..."
                      : "Generate Subtitles"}
                  </button>
                </div>
              </div>

              <div
                className={
                  timelineErrors.length === 0
                    ? "timeline-status valid"
                    : "timeline-status invalid"
                }
              >
                {timelineErrors.length === 0 ? (
                  <>
                    <span className="status-dot" />
                    Timeline valid ·{" "}
                    {draftPlan.total_duration.toFixed(1)}s
                    {hasUnsavedChanges() && " · unsaved"}
                  </>
                ) : (
                  <>
                    Timeline has {timelineErrors.length} issue
                    {timelineErrors.length !== 1 ? "s" : ""}
                  </>
                )}
              </div>

              <div className="timeline">
                {draftPlan.scenes.map((scene, index) => (
                <article className="scene" key={scene.id}>
                  <div className="scene-header">
                    <div>
                      <div className="scene-number">SCENE {index + 1}</div>
                      <div className="scene-time">
                        {scene.start.toFixed(1)}s → {scene.end.toFixed(1)}s
                      </div>
                    </div>

                    <div className="scene-actions">
                      <button
                        type="button"
                        className="scene-action"
                        onClick={() => moveScene(scene.id, -1)}
                        disabled={index === 0}
                        title="Move scene up"
                      >
                        ↑
                      </button>

                      <button
                        type="button"
                        className="scene-action"
                        onClick={() => moveScene(scene.id, 1)}
                        disabled={index === draftPlan.scenes.length - 1}
                        title="Move scene down"
                      >
                        ↓
                      </button>

                      <button
                        type="button"
                        className="scene-action"
                        onClick={() => duplicateScene(scene.id)}
                        title="Duplicate scene"
                      >
                        ⧉
                      </button>

                      <button
                        type="button"
                        className="scene-action danger"
                        onClick={() => deleteScene(scene.id)}
                        disabled={draftPlan.scenes.length <= 1}
                        title="Delete scene"
                      >
                        ×
                      </button>
                    </div>
                  </div>

                  <label>
                    Title
                    <input
                      value={scene.title}
                      onChange={(e) =>
                        updateScene(scene.id, "title", e.target.value)
                      }
                    />
                  </label>

                  <div className="time-fields">
                    <label>
                      Start
                      <input
                        type="number"
                        min="0"
                        step="0.1"
                        value={scene.start}
                        onChange={(e) =>
                          updateScene(scene.id, "start", e.target.value)
                        }
                      />
                    </label>

                    <label>
                      End
                      <input
                        type="number"
                        min="0"
                        step="0.1"
                        value={scene.end}
                        onChange={(e) =>
                          updateScene(scene.id, "end", e.target.value)
                        }
                      />
                    </label>
                  </div>

                  <label>
                    Narration
                    <textarea
                      className="scene-textarea"
                      value={scene.narration}
                      onChange={(e) =>
                        updateScene(scene.id, "narration", e.target.value)
                      }
                    />
                  </label>

                  <label>
                    Visual
                    <textarea
                      className="scene-textarea"
                      value={scene.visual}
                      onChange={(e) =>
                        updateScene(scene.id, "visual", e.target.value)
                      }
                    />
                  </label>

                  <label>
                    Animation
                    <textarea
                      className="scene-textarea"
                      value={scene.animation}
                      onChange={(e) =>
                        updateScene(scene.id, "animation", e.target.value)
                      }
                    />
                  </label>

                  <label>
                    Camera
                    <textarea
                      className="scene-textarea"
                      value={scene.camera}
                      onChange={(e) =>
                        updateScene(scene.id, "camera", e.target.value)
                      }
                    />
                  </label>

                  <label>
                    Caption
                    <input
                      value={scene.caption}
                      onChange={(e) =>
                        updateScene(scene.id, "caption", e.target.value)
                      }
                    />
                  </label>

                  <label>
                    Location
                    <input
                      value={scene.location || ""}
                      onChange={(e) =>
                        updateScene(scene.id, "location", e.target.value)
                      }
                    />
                  </label>

                  <label>
                    Asset Hints
                    <input
                      value={scene.asset_hints.join(", ")}
                      onChange={(e) =>
                        updateScene(
                          scene.id,
                          "asset_hints",
                          e.target.value
                            .split(",")
                            .map((item) => item.trim())
                            .filter(Boolean)
                        )
                      }
                    />
                  </label>
                </article>
                ))}
              </div>

              <div className="asset-panel">
                <div className="asset-panel-header">
                  <div>
                    <h3>Asset Manifest</h3>
                    <p className="muted">
                      Structured visual assets required by the current scene plan.
                    </p>
                  </div>

                  {draftPlan && (
                    <span className="pill">
                      {assetPlan.length} assets
                    </span>
                  )}

                  <div className="asset-resolution-summary">
                    <span>
                      Available:{" "}
                      <strong>
                        {assetResolution.resolved.length}
                      </strong>
                    </span>

                    <span>
                      Placeholders:{" "}
                      <strong>
                        {assetResolution.placeholders.length}
                      </strong>
                    </span>

                    <span>
                      Missing:{" "}
                      <strong>
                        {assetResolution.missing.length}
                      </strong>
                    </span>
                  </div>
                </div>

                {assetError && (
                  <div className="asset-error">
                    {assetError}
                  </div>
                )}

                {!assetError && assetPlan.length === 0 ? (
                  <div className="asset-empty">
                    {assetLoading
                      ? "Building asset manifest..."
                      : "No asset manifest generated yet."}
                  </div>
                ) : (
                  <div className="asset-list">
                    {assetPlan.map((asset) => {
                      const sceneIds = asset.metadata?.scene_ids || [];

                      return (
                        <article
                          className="asset-card"
                          key={asset.id}
                        >
                          <div className="asset-card-header">
                            <div>
                              <div className="asset-name">
                                {asset.name}
                              </div>

                              <div className="asset-id">
                                {asset.id}
                              </div>
                            </div>

                            <span className="asset-status">
                              {asset.status}
                            </span>

                            {assetResolution.resolved.some(
                              (item) => item.id === asset.id
                            ) && (
                              <span className="asset-resolution-badge available">
                                available
                              </span>
                            )}

                            {assetResolution.placeholders.some(
                              (item) => item.name === asset.name
                            ) && (
                              <span className="asset-resolution-badge placeholder">
                                placeholder
                              </span>
                            )}
                          </div>

                          <div className="asset-meta">
                            <span>
                              Type: <strong>{asset.type}</strong>
                            </span>

                            <span>
                              Source: <strong>{asset.source}</strong>
                            </span>
                          </div>

                          <div className="asset-scenes">
                            <span>Used in:</span>

                            {sceneIds.length > 0 ? (
                              sceneIds.map((sceneId) => {
                                const sceneIndex =
                                  draftPlan?.scenes.findIndex(
                                    (scene) => scene.id === sceneId
                                  );

                                return (
                                  <span
                                    className="asset-scene-tag"
                                    key={sceneId}
                                  >
                                    Scene{" "}
                                    {sceneIndex >= 0
                                      ? sceneIndex + 1
                                      : sceneId}
                                  </span>
                                );
                              })
                            ) : (
                              <span className="muted">
                                No scene references
                              </span>
                            )}
                          </div>
                        </article>
                      );
                    })}
                  </div>
                )}
              </div>

              <div className="geography-panel">
                <div className="geography-panel-header">
                  <div>
                    <h3>Geographic Plan</h3>
                    <p className="muted">
                      Geographic regions, markers, routes, and map operations
                      detected for the current scene plan.
                    </p>
                  </div>

                  <span className="pill">
                    {Object.values(geographyPlan).filter(
                      (item) => item.enabled
                    ).length} geographic scenes
                  </span>
                </div>

                {geographyError && (
                  <div className="asset-error">
                    {geographyError}
                  </div>
                )}

                {!geographyLoading &&
                Object.keys(geographyPlan).length === 0 ? (
                  <div className="asset-empty">
                    No geography plan generated yet.
                  </div>
                ) : (
                  <div className="geography-scene-list">
                    {draftPlan?.scenes.map((scene, index) => {
                      const geo = geographyPlan[scene.id];

                      if (!geo?.enabled) {
                        return null;
                      }

                      return (
                        <article
                          className="geography-card"
                          key={scene.id}
                        >
                          <div className="geography-card-header">
                            <div>
                              <div className="scene-number">
                                SCENE {index + 1}
                              </div>

                              <h4>{scene.title}</h4>
                            </div>

                            <span className="asset-resolution-badge available">
                              geographic
                            </span>
                          </div>

                          <div className="geography-meta">
                            <span>
                              Source: <strong>{geo.map_source}</strong>
                            </span>

                            <span>
                              Zoom: <strong>{geo.zoom_level}</strong>
                            </span>
                          </div>

                          {geo.center && (
                            <div className="geography-center">
                              Center:
                              <strong>
                                {" "}
                                {geo.center.latitude.toFixed(4)},
                                {" "}
                                {geo.center.longitude.toFixed(4)}
                              </strong>
                            </div>
                          )}

                          {geo.regions.length > 0 && (
                            <div className="geography-section">
                              <span className="geography-label">
                                Regions
                              </span>

                              <div className="geography-tags">
                                {geo.regions.map((region) => (
                                  <span
                                    className="asset-scene-tag"
                                    key={region.id}
                                  >
                                    {region.name}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {geo.operations.length > 0 && (
                            <div className="geography-section">
                              <span className="geography-label">
                                Operations
                              </span>

                              <div className="geography-operations">
                                {geo.operations.map((operation, opIndex) => (
                                  <div
                                    className="geography-operation"
                                    key={`${scene.id}-${opIndex}`}
                                  >
                                    <strong>
                                      {operation.type}
                                    </strong>

                                    {operation.target_id && (
                                      <span>
                                        → {operation.target_id}
                                      </span>
                                    )}

                                    <span>
                                      {operation.duration}s
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </article>
                      );
                    })}
                  </div>
                )}
              </div>

              <section className="panel render-preview-panel">
                <div className="panel-header">
                  <div>
                    <h2>Render Preview</h2>
                    <p>Generate and preview the current scene animation render.</p>
                  </div>
                </div>

                {renderError && (
                  <div className="render-error">
                    {renderError}
                  </div>
                )}

                {renderPreview ? (
                  <div className="render-preview-content">
                    <div className="render-preview-meta">
                      <span>
                        {renderPreview.scene_count} scenes
                      </span>

                      <span>
                        {renderPreview.width} × {renderPreview.height}
                      </span>

                      <span>
                        {renderPreview.total_duration.toFixed(2)}s
                      </span>
                    </div>

                    <div className="render-preview-layout">
                      <div className="render-scene-list">
                        {renderPreview.scene_files.map((sceneFile, index) => {
                          const filename = sceneFile.split(/[\\/]/).pop();

                          return (
                            <button
                              type="button"
                              key={sceneFile}
                              className={
                                selectedRenderScene === sceneFile
                                  ? "render-scene-item active"
                                  : "render-scene-item"
                              }
                              onClick={() => setSelectedRenderScene(sceneFile)}
                            >
                              <span>Scene {index + 1}</span>
                              <small>{filename}</small>
                            </button>
                          );
                        })}
                      </div>

                      <div className="render-frame">
                        {selectedRenderScene ? (
                          <img
                            src={`${API_URL}/api/render/file/${encodeURIComponent(
                              selectedRenderScene.split(/[\\/]/).pop()
                            )}`}
                            alt="Rendered scene preview"
                          />
                        ) : (
                          <div className="render-empty">
                            Select a rendered scene.
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="render-empty">
                    Click <strong>Render Preview</strong> to generate scene previews.
                  </div>
                )}
              </section>

              <section className="panel narration-panel">
                <div className="panel-header">
                  <div>
                    <h2>Narration</h2>
                    <p>
                      Generate local voice narration from scene scripts.
                    </p>
                  </div>
                </div>

                {narrationError && (
                  <div className="narration-error">
                    {narrationError}
                  </div>
                )}

                <div className="narration-controls">
                  <label>
                    Voice

                    <select
                      value={selectedNarrationVoice}
                      onChange={(event) =>
                        setSelectedNarrationVoice(event.target.value)
                      }
                    >
                      <option value="">
                        Default voice
                      </option>

                      {narrationVoices.map((voice) => (
                        <option
                          key={voice.id}
                          value={voice.id}
                        >
                          {voice.name || voice.id}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Rate

                    <input
                      type="number"
                      min="80"
                      max="300"
                      value={narrationRate}
                      onChange={(event) =>
                        setNarrationRate(event.target.value)
                      }
                    />
                  </label>

                  <label>
                    Volume

                    <input
                      type="number"
                      min="0"
                      max="1"
                      step="0.1"
                      value={narrationVolume}
                      onChange={(event) =>
                        setNarrationVolume(event.target.value)
                      }
                    />
                  </label>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={generateNarration}
                    disabled={
                      narrationLoading ||
                      !plan?.scenes?.length
                    }
                  >
                    {narrationLoading
                      ? "Generating..."
                      : "Generate Audio"}
                  </button>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => syncNarrationManifest()}
                    disabled={
                      narrationManifestLoading ||
                      !narrationPlan.segments.length
                    }
                  >
                    {narrationManifestLoading
                      ? "Syncing..."
                      : "Sync Timeline"}
                  </button>
                </div>

                {narrationPlan.segments.length > 0 ? (
                  <div className="narration-content">
                    <div className="narration-scene-list">
                      {narrationPlan.segments.map((segment) => (
                        <button
                          type="button"
                          key={segment.scene_id}
                          className={
                            selectedNarrationScene === segment.scene_id
                              ? "narration-scene-item active"
                              : "narration-scene-item"
                          }
                          onClick={() =>
                            setSelectedNarrationScene(segment.scene_id)
                          }
                        >
                          <span>{segment.scene_id}</span>

                          <small>
                            {segment.duration_seconds.toFixed(2)}s
                          </small>
                        </button>
                      ))}
                    </div>

                    <div className="narration-preview">
                      {(() => {
                        const segment =
                          narrationPlan.segments.find(
                            (item) =>
                              item.scene_id === selectedNarrationScene
                          );

                        if (!segment?.audio_file) {
                          return (
                            <div className="narration-empty">
                              Select a narration segment.
                            </div>
                          );
                        }

                        const filename =
                          segment.audio_file.split(/[\\/]/).pop();

                        return (
                          <div className="narration-player">
                            <div className="narration-text">
                              {segment.text}
                            </div>

                            <audio
                              controls
                              src={`${API_URL}/api/narration/file/${encodeURIComponent(
                                filename
                              )}`}
                            />

                            <div className="narration-duration">
                              Duration:{" "}
                              {segment.duration_seconds.toFixed(2)}s
                            </div>
                          </div>
                        );
                      })()}
                    </div>

                    <div className="narration-sync-status">
                      <div className="narration-sync-header">
                        <strong>Timeline Sync</strong>

                        <span>
                          {narrationManifest.segments.length} synced scene
                          {narrationManifest.segments.length === 1 ? "" : "s"}
                        </span>
                      </div>

                      {narrationManifest.segments.length > 0 ? (
                        <div className="narration-sync-list">
                          {narrationManifest.segments.map((segment) => (
                            <div
                              key={segment.scene_id}
                              className={
                                segment.fits_scene
                                  ? "narration-sync-item valid"
                                  : "narration-sync-item warning"
                              }
                            >
                              <div>
                                <strong>{segment.scene_id}</strong>

                                <small>
                                  Scene {segment.start.toFixed(2)}s →{" "}
                                  {segment.end.toFixed(2)}s
                                </small>
                              </div>

                              <div className="narration-sync-duration">
                                <span>
                                  Audio {segment.audio_duration.toFixed(2)}s
                                </span>

                                <span>
                                  {segment.fits_scene
                                    ? "Fits scene"
                                    : "Longer than scene"}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="narration-empty">
                          Generate narration and sync the timeline.
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="narration-empty">
                    No narration generated yet.
                  </div>
                )}
              </section>

              <section className="panel subtitle-panel">
                <div className="panel-header">
                  <div>
                    <h2>Subtitles</h2>
                    <p>
                      Generate synchronized subtitles from scene narration.
                    </p>
                  </div>
                </div>

                {subtitleError && (
                  <div className="subtitle-error">
                    {subtitleError}
                  </div>
                )}

                <div className="subtitle-controls">
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={generateSubtitles}
                    disabled={
                      subtitleLoading ||
                      !plan?.scenes?.length
                    }
                  >
                    {subtitleLoading
                      ? "Generating..."
                      : "Generate Subtitles"}
                  </button>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={generateSubtitleFile}
                    disabled={
                      subtitleLoading ||
                      !plan?.scenes?.length
                    }
                  >
                    {subtitleLoading
                      ? "Generating..."
                      : "Generate SRT File"}
                  </button>
                </div>

                {subtitleTrack.cues.length > 0 ? (
                  <div className="subtitle-content">
                    <div className="subtitle-summary">
                      <span>
                        {subtitleTrack.cues.length} cues
                      </span>

                      <span>
                        Duration{" "}
                        {subtitleTrack.cues.at(-1)?.end.toFixed(2)}s
                      </span>
                    </div>

                    <div className="subtitle-sync-badge">
                      Narration-aware synchronization enabled
                    </div>

                    <div className="subtitle-cue-list">
                      {subtitleTrack.cues.map((cue) => (
                        <div
                          key={cue.index}
                          className="subtitle-cue"
                        >
                          <div className="subtitle-cue-number">
                            {cue.index}
                          </div>

                          <div className="subtitle-cue-main">
                            <div className="subtitle-cue-time">
                              {cue.start.toFixed(2)}s
                              {" → "}
                              {cue.end.toFixed(2)}s
                            </div>

                            <div className="subtitle-cue-text">
                              {cue.text}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {subtitleSrt && (
                      <>
                        {subtitleOutputFile && (
                          <div className="subtitle-export">
                            <div>
                              <strong>Subtitle File</strong>

                              <small>
                                {subtitleOutputFile.split(/[\\/]/).pop()}
                              </small>
                            </div>

                            <a
                              className="secondary-button subtitle-download"
                              href={`${API_URL}/api/subtitles/file/subtitles.srt`}
                              download="subtitles.srt"
                            >
                              Download SRT
                            </a>
                          </div>
                        )}

                        <div className="subtitle-srt-preview">
                          <div className="subtitle-srt-header">
                            <strong>SRT Preview</strong>
                          </div>

                          <pre>{subtitleSrt}</pre>
                        </div>
                      </>
                    )}
                  </div>
                ) : (
                  <div className="subtitle-empty">
                    No subtitles generated yet.
                  </div>
                )}
              </section>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);

import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

import { TopBar } from "./components/TopBar";
import { Sidebar } from "./components/Sidebar";
import { BottomTimeline } from "./components/BottomTimeline";
import { SceneInspector } from "./components/SceneInspector";
import { StoryView } from "./components/StoryView";
import { ScenesView } from "./components/ScenesView";
import { PreviewView } from "./components/PreviewView";
import { AssetsView } from "./components/AssetsView";
import { GeographyView } from "./components/GeographyView";
import { NarrationView } from "./components/NarrationView";
import { SubtitleView } from "./components/SubtitleView";
import { ExportView } from "./components/ExportView";
import { ProjectModal } from "./components/ProjectModal";
import { SettingsModal } from "./components/SettingsModal";

const API_URL = "http://127.0.0.1:8000";

const defaultScript = `Before Bangladesh...\nbefore Bengal...\nbefore humans ever walked this land...\n\nMillions of years ago, the region we now call Bangladesh was part of a constantly changing geological world. The collision of the Indian tectonic plate with the Eurasian plate pushed up the Himalayas, birthing massive river systems that carved the fertile delta into motion.`;

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
      const reducible = Math.max(durations[i] - MIN_SCENE_DURATION, 0);
      const reduction = Math.min(reducible, excess);
      durations[i] -= reduction;
      excess -= reduction;
    }

    if (excess > 0) {
      const minimumTotal = scenes.length * MIN_SCENE_DURATION;
      if (targetDuration < minimumTotal) {
        throw new Error(`Video duration is too short for ${scenes.length} scenes.`);
      }

      const scale = (targetDuration - minimumTotal) / (total - minimumTotal);
      for (let i = 0; i < durations.length; i += 1) {
        durations[i] = MIN_SCENE_DURATION + (durations[i] - MIN_SCENE_DURATION) * scale;
      }
    }
  }

  let currentTime = 0;
  return scenes.map((scene, index) => {
    const start = currentTime;
    const end = index === scenes.length - 1 ? targetDuration : currentTime + durations[index];
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
      errors.push(`Scene ${index + 1} has an invalid duration.`);
    }

    if (Math.abs(start - previousEnd) > 0.01) {
      errors.push(`Scene ${index + 1} creates a gap or overlap.`);
    }

    previousEnd = end;
  });

  if (Math.abs(previousEnd - targetDuration) > 0.01) {
    errors.push(
      `Timeline ends at ${previousEnd.toFixed(2)}s instead of ${targetDuration.toFixed(2)}s.`
    );
  }

  return errors;
}

function App() {
  // Navigation & Workspace State
  const [activeTab, setActiveTab] = useState("story");
  const [selectedSceneIndex, setSelectedSceneIndex] = useState(0);
  const [isInspectorCollapsed, setIsInspectorCollapsed] = useState(false);
  const [isProjectsModalOpen, setIsProjectsModalOpen] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);

  // Script & Generation State
  const [script, setScript] = useState(defaultScript);
  const [duration, setDuration] = useState(60);
  const [aspectRatio, setAspectRatio] = useState("9:16");
  const [style, setStyle] = useState("animated historical documentary");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Plans & Timeline
  const [plan, setPlan] = useState(null);
  const [draftPlan, setDraftPlan] = useState(null);
  const [savedPlan, setSavedPlan] = useState(null);

  // Project Management & Persistence
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [projectName, setProjectName] = useState("");
  const [projectLoading, setProjectLoading] = useState(false);
  const [projectError, setProjectError] = useState("");

  // AI & Backend Health
  const [aiConfig, setAIConfig] = useState(null);

  // Visual Assets
  const [assetPlan, setAssetPlan] = useState([]);
  const [assetLoading, setAssetLoading] = useState(false);
  const [assetResolving, setAssetResolving] = useState(false);
  const [assetError, setAssetError] = useState("");
  const [assetResolution, setAssetResolution] = useState({
    resolved: [],
    missing: [],
    placeholders: [],
  });

  // Historical Geography
  const [geographyPlan, setGeographyPlan] = useState({});
  const [geographyLoading, setGeographyLoading] = useState(false);
  const [geographyError, setGeographyError] = useState("");

  // Narration TTS
  const [narrationPlan, setNarrationPlan] = useState({ segments: [] });
  const [narrationManifest, setNarrationManifest] = useState({ segments: [] });
  const [narrationVoices, setNarrationVoices] = useState([]);
  const [selectedNarrationVoice, setSelectedNarrationVoice] = useState("");
  const [narrationRate, setNarrationRate] = useState(170);
  const [narrationVolume, setNarrationVolume] = useState(1);
  const [narrationLoading, setNarrationLoading] = useState(false);
  const [narrationError, setNarrationError] = useState("");
  const [selectedNarrationScene, setSelectedNarrationScene] = useState(null);

  // Subtitles & SRT
  const [subtitleTrack, setSubtitleTrack] = useState({ cues: [] });
  const [subtitleSrt, setSubtitleSrt] = useState("");
  const [subtitleOutputFile, setSubtitleOutputFile] = useState("");
  const [subtitleLoading, setSubtitleLoading] = useState(false);
  const [subtitleError, setSubtitleError] = useState("");

  // Render Preview
  const [renderPreview, setRenderPreview] = useState(null);
  const [renderLoading, setRenderLoading] = useState(false);
  const [renderError, setRenderError] = useState("");
  const [selectedRenderScene, setSelectedRenderScene] = useState(null);

  // Master Video Export
  const [videoExport, setVideoExport] = useState(null);
  const [videoExporting, setVideoExporting] = useState(false);
  const [videoExportError, setVideoExportError] = useState("");

  // Validation
  const timelineErrors = draftPlan ? validateTimeline(draftPlan) : [];

  // 1. Initial Health Check & Voices
  useEffect(() => {
    fetch(`${API_URL}/api/health`)
      .then((res) => res.json())
      .then((data) => setAIConfig(data))
      .catch(() => setAIConfig(null));

    loadNarrationVoices();
  }, []);

  // 2. Initialize Projects & Restore Last Opened
  useEffect(() => {
    async function initializeProjects() {
      try {
        const response = await fetch(`${API_URL}/api/projects`);
        if (!response.ok) throw new Error("Failed to load projects.");
        const data = await response.json();
        setProjects(data);

        const savedProjectId = localStorage.getItem("eraforge_current_project");
        if (savedProjectId && data.some((p) => p.id === savedProjectId)) {
          await openProject(savedProjectId);
        } else {
          localStorage.removeItem("eraforge_current_project");
        }
      } catch (err) {
        setProjectError(err.message || "Failed to initialize projects.");
      }
    }

    initializeProjects();
  }, []);

  // --------------------------------------------------------------------------
  // Asset Management
  // --------------------------------------------------------------------------
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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(planToAnalyze),
      });

      const data = await response.json();
      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((i) => i.msg).join("; ")
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
    if (!planToResolve) return;

    try {
      setAssetResolving(true);
      setAssetError("");

      const response = await fetch(`${API_URL}/api/assets/resolve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(planToResolve),
      });

      const data = await response.json();
      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((i) => i.msg).join("; ")
          : data.detail || "Failed to resolve assets.";
        throw new Error(detail);
      }

      setAssetResolution(data);
    } catch (err) {
      setAssetError(err.message || "Failed to resolve assets.");
      setAssetResolution({ resolved: [], missing: [], placeholders: [] });
    } finally {
      setAssetResolving(false);
    }
  }

  // --------------------------------------------------------------------------
  // Geography Planning
  // --------------------------------------------------------------------------
  async function planGeography(planToAnalyze = draftPlan) {
    if (!planToAnalyze) return;

    try {
      setGeographyLoading(true);
      setGeographyError("");

      const response = await fetch(`${API_URL}/api/geography/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(planToAnalyze),
      });

      const data = await response.json();
      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((i) => i.msg).join("; ")
          : data.detail || "Failed to plan geography.";
        throw new Error(detail);
      }

      setGeographyPlan(data);
    } catch (err) {
      setGeographyError(err.message || "Failed to plan geography.");
      setGeographyPlan({});
    } finally {
      setGeographyLoading(false);
    }
  }

  // --------------------------------------------------------------------------
  // Narration TTS
  // --------------------------------------------------------------------------
  async function loadNarrationVoices() {
    try {
      const response = await fetch(`${API_URL}/api/narration/voices`);
      if (!response.ok) throw new Error("Failed to load voices");
      const data = await response.json();
      setNarrationVoices(data.voices || []);
      if (data.voices?.length && !selectedNarrationVoice) {
        setSelectedNarrationVoice(data.voices[0].id);
      }
    } catch (err) {
      setNarrationError(err.message || "Failed to load narration voices");
    }
  }

  async function generateNarration() {
    if (!plan) return;
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

      const response = await fetch(`${API_URL}/api/narration/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Narration generation failed (${response.status})`);
      }

      const data = await response.json();
      setNarrationPlan(data);

      if (data.segments?.length) {
        setSelectedNarrationScene(data.segments[0].scene_id);
      }

      await syncNarrationManifest(data);
    } catch (err) {
      setNarrationError(err.message || "Failed to generate narration");
    } finally {
      setNarrationLoading(false);
    }
  }

  async function syncNarrationManifest(narrationData = narrationPlan) {
    if (!plan || !narrationData?.segments?.length) return;

    try {
      const response = await fetch(`${API_URL}/api/narration/manifest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          plan,
          narration: narrationData,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setNarrationManifest(data);
      }
    } catch {
      // Manifest sync is non-blocking
    }
  }

  // --------------------------------------------------------------------------
  // Subtitles & SRT
  // --------------------------------------------------------------------------
  async function generateSubtitles() {
    if (!plan) return;
    setSubtitleLoading(true);
    setSubtitleError("");

    try {
      let narrationManifestData = null;
      if (narrationPlan?.segments?.length) {
        const manifestResponse = await fetch(`${API_URL}/api/narration/manifest`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ plan, narration: narrationPlan }),
        });
        if (manifestResponse.ok) {
          narrationManifestData = await manifestResponse.json();
        }
      }

      const response = await fetch(`${API_URL}/api/subtitles/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(plan),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Subtitle generation failed (${response.status})`);
      }

      const track = await response.json();
      setSubtitleTrack(track);

      const srtResponse = await fetch(`${API_URL}/api/subtitles/srt`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(plan),
      });

      if (srtResponse.ok) {
        const srtData = await srtResponse.json();
        setSubtitleSrt(srtData.srt || "");
      }

      if (narrationManifestData) {
        const syncResponse = await fetch(`${API_URL}/api/subtitles/sync`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ plan, narration_manifest: narrationManifestData }),
        });

        if (syncResponse.ok) {
          const syncData = await syncResponse.json();
          if (!syncData.valid) {
            setSubtitleError(syncData.issues.map((i) => i.message).join(" "));
          }
        }
      }
    } catch (err) {
      setSubtitleError(err.message || "Failed to generate subtitles");
    } finally {
      setSubtitleLoading(false);
    }
  }

  async function generateSubtitleFile() {
    if (!plan) return;
    setSubtitleLoading(true);
    setSubtitleError("");

    try {
      const response = await fetch(`${API_URL}/api/subtitles/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(plan),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Subtitle file generation failed");
      }

      const data = await response.json();
      setSubtitleSrt(data.srt || "");
      setSubtitleOutputFile(data.output_file || "");

      const trackResponse = await fetch(`${API_URL}/api/subtitles/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(plan),
      });

      if (trackResponse.ok) {
        setSubtitleTrack(await trackResponse.json());
      }
    } catch (err) {
      setSubtitleError(err.message || "Failed to generate subtitle file");
    } finally {
      setSubtitleLoading(false);
    }
  }

  // --------------------------------------------------------------------------
  // Render Preview
  // --------------------------------------------------------------------------
  async function renderPreviewScenes() {
    if (!plan) return;
    setRenderLoading(true);
    setRenderError("");

    try {
      const response = await fetch(`${API_URL}/api/render/preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(plan),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to render preview");
      }

      const data = await response.json();
      setRenderPreview(data);
      if (data.scene_files?.length) {
        const firstFilename = data.scene_files[0].split(/[\\/]/).pop();
        const firstSceneId = firstFilename.replace(/^scene_\d+_/, "").replace(/\.svg$/, "");
        setSelectedRenderScene(firstSceneId);
      }
    } catch (err) {
      setRenderError(err.message || "Failed to render preview");
    } finally {
      setRenderLoading(false);
    }
  }

  // --------------------------------------------------------------------------
  // Video Export (FFmpeg MP4)
  // --------------------------------------------------------------------------
  async function exportVideo() {
    if (!plan) return;
    setVideoExporting(true);
    setVideoExportError("");

    try {
      const response = await fetch(`${API_URL}/api/render/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(plan),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Video export failed (${response.status})`);
      }

      const data = await response.json();
      setVideoExport(data);
    } catch (err) {
      setVideoExportError(err.message || "Failed to export video");
    } finally {
      setVideoExporting(false);
    }
  }

  // --------------------------------------------------------------------------
  // Scene Editing & Timeline Manipulation
  // --------------------------------------------------------------------------
  function updateScene(sceneId, field, value) {
    if (!draftPlan) return;

    const nextScenes = draftPlan.scenes.map((scene) => {
      if (scene.id !== sceneId) return scene;

      if (field === "start" || field === "end") {
        const numeric = Number(value);
        return { ...scene, [field]: Number.isNaN(numeric) ? 0 : numeric };
      }

      return { ...scene, [field]: value };
    });

    setDraftPlan({ ...draftPlan, scenes: nextScenes });
  }

  function resequenceScenes(scenes) {
    let currentTime = 0;
    return scenes.map((scene) => {
      const duration = Math.max(scene.end - scene.start, MIN_SCENE_DURATION);
      const start = currentTime;
      const end = currentTime + duration;
      currentTime = end;

      return {
        ...scene,
        start: Number(start.toFixed(3)),
        end: Number(end.toFixed(3)),
      };
    });
  }

  function deleteScene(sceneId) {
    if (!draftPlan || draftPlan.scenes.length <= 1) return;

    const remaining = draftPlan.scenes.filter((scene) => scene.id !== sceneId);
    try {
      const resequenced = normalizeTimeline(remaining, draftPlan.total_duration);
      setDraftPlan({ ...draftPlan, scenes: resequenced });
      if (selectedSceneIndex >= resequenced.length) {
        setSelectedSceneIndex(Math.max(0, resequenced.length - 1));
      }
    } catch {
      setDraftPlan({ ...draftPlan, scenes: resequenceScenes(remaining) });
    }
  }

  function duplicateScene(sceneId) {
    if (!draftPlan) return;

    const sceneIndex = draftPlan.scenes.findIndex((scene) => scene.id === sceneId);
    if (sceneIndex === -1) return;

    const targetScene = draftPlan.scenes[sceneIndex];
    const newScene = {
      ...structuredClone(targetScene),
      id: `scene-${Date.now().toString().slice(-4)}`,
      title: `${targetScene.title} (Copy)`,
    };

    const nextScenes = [
      ...draftPlan.scenes.slice(0, sceneIndex + 1),
      newScene,
      ...draftPlan.scenes.slice(sceneIndex + 1),
    ];

    try {
      const resequenced = normalizeTimeline(nextScenes, draftPlan.total_duration);
      setDraftPlan({ ...draftPlan, scenes: resequenced });
      setSelectedSceneIndex(sceneIndex + 1);
    } catch {
      setDraftPlan({ ...draftPlan, scenes: resequenceScenes(nextScenes) });
    }
  }

  function moveScene(sceneId, direction) {
    if (!draftPlan) return;

    const sceneIndex = draftPlan.scenes.findIndex((scene) => scene.id === sceneId);
    if (sceneIndex === -1) return;

    const targetIndex = sceneIndex + direction;
    if (targetIndex < 0 || targetIndex >= draftPlan.scenes.length) return;

    const nextScenes = [...draftPlan.scenes];
    const [moved] = nextScenes.splice(sceneIndex, 1);
    nextScenes.splice(targetIndex, 0, moved);

    try {
      const resequenced = normalizeTimeline(nextScenes, draftPlan.total_duration);
      setDraftPlan({ ...draftPlan, scenes: resequenced });
      setSelectedSceneIndex(targetIndex);
    } catch {
      setDraftPlan({ ...draftPlan, scenes: resequenceScenes(nextScenes) });
    }
  }

  function addScene() {
    if (!draftPlan) return;

    const lastScene = draftPlan.scenes[draftPlan.scenes.length - 1];
    const newStart = lastScene ? lastScene.end : 0;
    const newEnd = newStart + 5.0;

    const newScene = {
      id: `scene-${(draftPlan.scenes.length + 1).toString().padStart(2, "0")}`,
      start: Number(newStart.toFixed(3)),
      end: Number(newEnd.toFixed(3)),
      title: `Scene ${draftPlan.scenes.length + 1}`,
      narration: "",
      visual: "Historical illustration or map background",
      animation: "fade in",
      camera: "static",
      caption: "",
      location: null,
      asset_hints: ["illustration"],
    };

    const nextScenes = [...draftPlan.scenes, newScene];
    try {
      const resequenced = normalizeTimeline(nextScenes, draftPlan.total_duration);
      setDraftPlan({ ...draftPlan, scenes: resequenced });
      setSelectedSceneIndex(resequenced.length - 1);
    } catch {
      setDraftPlan({
        ...draftPlan,
        total_duration: newEnd,
        scenes: nextScenes,
      });
      setSelectedSceneIndex(nextScenes.length - 1);
    }
  }

  function hasUnsavedChanges() {
    if (!savedPlan || !draftPlan) return false;
    return JSON.stringify(savedPlan) !== JSON.stringify(draftPlan);
  }

  function resetChanges() {
    if (!savedPlan) return;
    setDraftPlan(structuredClone(savedPlan));
  }

  async function applyChanges() {
    if (!draftPlan || timelineErrors.length > 0) return;

    try {
      const response = await fetch(`${API_URL}/api/validate-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(draftPlan),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Validation failed");

      const validatedPlan = structuredClone(draftPlan);
      setPlan(validatedPlan);
      setSavedPlan(validatedPlan);

      await refreshAssetPlan(validatedPlan);
      await resolveAssets(validatedPlan);
      await planGeography(validatedPlan);
    } catch (err) {
      setError(err.message || "Failed to apply changes");
    }
  }

  // --------------------------------------------------------------------------
  // Project Store Operations
  // --------------------------------------------------------------------------
  function rememberProject(projectId) {
    if (!projectId) {
      localStorage.removeItem("eraforge_current_project");
      return;
    }
    localStorage.setItem("eraforge_current_project", projectId);
  }

  async function loadProjects() {
    try {
      const response = await fetch(`${API_URL}/api/projects`);
      if (response.ok) {
        const data = await response.json();
        setProjects(data);
      }
    } catch {
      // Quiet fail
    }
  }

  async function createNewProject(name = "Untitled Project") {
    setProjectLoading(true);
    setProjectError("");

    try {
      const response = await fetch(`${API_URL}/api/projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name.trim(),
          script,
          duration: Number(duration),
          scene_plan: draftPlan,
        }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Failed to create project");

      setCurrentProject(data);
      rememberProject(data.id);
      await loadProjects();
    } catch (err) {
      setProjectError(err.message || "Failed to create project");
    } finally {
      setProjectLoading(false);
    }
  }

  async function saveProject() {
    if (!currentProject) {
      await createNewProject(projectName || "Untitled History Project");
      return;
    }

    setProjectLoading(true);
    setProjectError("");

    try {
      const response = await fetch(`${API_URL}/api/projects/${currentProject.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: currentProject.name,
          script,
          duration: Number(duration),
          scene_plan: draftPlan,
        }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Failed to save project");

      setCurrentProject(data);
      setPlan(structuredClone(draftPlan));
      setSavedPlan(structuredClone(draftPlan));
      await loadProjects();
    } catch (err) {
      setProjectError(err.message || "Failed to save project");
    } finally {
      setProjectLoading(false);
    }
  }

  async function openProject(projectId) {
    setProjectLoading(true);
    setProjectError("");

    try {
      const response = await fetch(`${API_URL}/api/projects/${projectId}`);
      if (!response.ok) throw new Error("Project not found");

      const data = await response.json();
      setCurrentProject(data);
      rememberProject(data.id);

      if (data.script) setScript(data.script);
      if (data.duration) setDuration(data.duration);

      if (data.scene_plan) {
        setPlan(structuredClone(data.scene_plan));
        setDraftPlan(structuredClone(data.scene_plan));
        setSavedPlan(structuredClone(data.scene_plan));
        setSelectedSceneIndex(0);

        await refreshAssetPlan(data.scene_plan);
        await resolveAssets(data.scene_plan);
        await planGeography(data.scene_plan);
      } else {
        setPlan(null);
        setDraftPlan(null);
        setSavedPlan(null);
      }
    } catch (err) {
      setProjectError(err.message || "Failed to open project");
    } finally {
      setProjectLoading(false);
    }
  }

  async function removeProject(projectId) {
    setProjectLoading(true);
    setProjectError("");

    try {
      const response = await fetch(`${API_URL}/api/projects/${projectId}`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error("Failed to delete project");

      if (currentProject?.id === projectId) {
        setCurrentProject(null);
        rememberProject(null);
      }

      await loadProjects();
    } catch (err) {
      setProjectError(err.message || "Failed to delete project");
    } finally {
      setProjectLoading(false);
    }
  }

  // --------------------------------------------------------------------------
  // AI Scene Planning
  // --------------------------------------------------------------------------
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
          aspect_ratio: aspectRatio || "9:16",
          style: style || "animated historical documentary",
        }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Scene planning failed");

      const initialPlan = structuredClone(data);
      setPlan(initialPlan);
      setDraftPlan(initialPlan);
      setSavedPlan(initialPlan);
      setSelectedSceneIndex(0);

      // Trigger asset and geography analysis automatically
      await refreshAssetPlan(initialPlan);
      await resolveAssets(initialPlan);
      await planGeography(initialPlan);

      // Auto-switch to scenes view to explore the generated timeline
      setActiveTab("scenes");
    } catch (err) {
      setError(err.message || "Scene planning failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      {/* Subtle Offline Grain Overlay */}
      <div className="noise-overlay" />

      {/* TOP BAR */}
      <TopBar
        currentProject={currentProject}
        draftPlan={draftPlan}
        timelineErrors={timelineErrors}
        hasUnsavedChanges={hasUnsavedChanges()}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onSaveProject={saveProject}
        projectLoading={projectLoading}
        onOpenProjectsModal={() => setIsProjectsModalOpen(true)}
        onOpenSettingsModal={() => setIsSettingsModalOpen(true)}
        aiConfig={aiConfig}
      />

      {/* STUDIO MIDDLE WORKSPACE (Sidebar + Main Workspace + Inspector) */}
      <div className="studio-body">
        {/* Project & Workflow Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          currentProject={currentProject}
          projects={projects}
          onNewProject={() => {
            setCurrentProject(null);
            rememberProject(null);
            setPlan(null);
            setDraftPlan(null);
            setSavedPlan(null);
            setActiveTab("story");
          }}
          onOpenProjectsModal={() => setIsProjectsModalOpen(true)}
          onOpenSettingsModal={() => setIsSettingsModalOpen(true)}
          aiConfig={aiConfig}
          draftPlan={draftPlan}
        />

        {/* Central Workspace Tab Views */}
        <main className="main-workspace">
          {activeTab === "story" && (
            <StoryView
              script={script}
              setScript={setScript}
              duration={duration}
              setDuration={setDuration}
              aspectRatio={aspectRatio}
              setAspectRatio={setAspectRatio}
              style={style}
              setStyle={setStyle}
              loading={loading}
              error={error}
              onGeneratePlan={generatePlan}
              aiConfig={aiConfig}
              draftPlan={draftPlan}
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === "scenes" && (
            <ScenesView
              draftPlan={draftPlan}
              selectedSceneIndex={selectedSceneIndex}
              onSelectScene={(idx) => {
                setSelectedSceneIndex(idx);
                if (isInspectorCollapsed) setIsInspectorCollapsed(false);
              }}
              onAddScene={addScene}
              onMoveScene={moveScene}
              onDuplicateScene={duplicateScene}
              onDeleteScene={deleteScene}
              timelineErrors={timelineErrors}
              hasUnsavedChanges={hasUnsavedChanges()}
              onApplyChanges={applyChanges}
              onResetChanges={resetChanges}
              onRefreshAssetPlan={refreshAssetPlan}
              assetLoading={assetLoading}
              onResolveAssets={resolveAssets}
              assetResolving={assetResolving}
              onPlanGeography={planGeography}
              geographyLoading={geographyLoading}
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === "preview" && (
            <PreviewView
              draftPlan={draftPlan}
              renderPreview={renderPreview}
              renderLoading={renderLoading}
              renderError={renderError}
              selectedRenderScene={selectedRenderScene}
              setSelectedRenderScene={setSelectedRenderScene}
              onRenderPreviewScenes={renderPreviewScenes}
              videoExport={videoExport}
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === "assets" && (
            <AssetsView
              assetPlan={assetPlan}
              assetResolution={assetResolution}
              assetLoading={assetLoading}
              assetResolving={assetResolving}
              assetError={assetError}
              onRefreshAssetPlan={refreshAssetPlan}
              onResolveAssets={resolveAssets}
              draftPlan={draftPlan}
            />
          )}

          {activeTab === "geography" && (
            <GeographyView
              geographyPlan={geographyPlan}
              geographyLoading={geographyLoading}
              geographyError={geographyError}
              onPlanGeography={planGeography}
              draftPlan={draftPlan}
            />
          )}

          {activeTab === "narration" && (
            <NarrationView
              narrationPlan={narrationPlan}
              narrationManifest={narrationManifest}
              narrationVoices={narrationVoices}
              selectedVoice={selectedNarrationVoice}
              setSelectedVoice={setSelectedNarrationVoice}
              rate={narrationRate}
              setRate={setNarrationRate}
              volume={narrationVolume}
              setVolume={setNarrationVolume}
              loading={narrationLoading}
              error={narrationError}
              onGenerateNarration={generateNarration}
              draftPlan={draftPlan}
            />
          )}

          {activeTab === "subtitles" && (
            <SubtitleView
              subtitleTrack={subtitleTrack}
              subtitleSrt={subtitleSrt}
              subtitleOutputFile={subtitleOutputFile}
              subtitleLoading={subtitleLoading}
              subtitleError={subtitleError}
              onGenerateSubtitles={generateSubtitles}
              onGenerateSubtitleFile={generateSubtitleFile}
              draftPlan={draftPlan}
            />
          )}

          {activeTab === "export" && (
            <ExportView
              draftPlan={draftPlan}
              videoExport={videoExport}
              videoExporting={videoExporting}
              videoExportError={videoExportError}
              onExportVideo={exportVideo}
            />
          )}
        </main>

        {/* Scene Inspector (Collapsible Right Sidebar) */}
        <SceneInspector
          draftPlan={draftPlan}
          selectedSceneIndex={selectedSceneIndex}
          onUpdateScene={updateScene}
          onDuplicateScene={duplicateScene}
          onDeleteScene={deleteScene}
          onMoveScene={moveScene}
          isCollapsed={isInspectorCollapsed}
          onToggleCollapse={() => setIsInspectorCollapsed(!isInspectorCollapsed)}
        />
      </div>

      {/* BOTTOM TIMELINE FILMSTRIP BAR */}
      <BottomTimeline
        draftPlan={draftPlan}
        selectedSceneIndex={selectedSceneIndex}
        onSelectScene={(idx) => {
          setSelectedSceneIndex(idx);
          if (isInspectorCollapsed) setIsInspectorCollapsed(false);
        }}
        onAddScene={addScene}
        onMoveScene={moveScene}
        onDuplicateScene={duplicateScene}
        onDeleteScene={deleteScene}
        timelineErrors={timelineErrors}
        hasUnsavedChanges={hasUnsavedChanges()}
        onApplyChanges={applyChanges}
        onResetChanges={resetChanges}
        setActiveTab={setActiveTab}
      />

      {/* ARCHIVE / PROJECTS MODAL */}
      <ProjectModal
        isOpen={isProjectsModalOpen}
        onClose={() => setIsProjectsModalOpen(false)}
        projects={projects}
        currentProject={currentProject}
        onOpenProject={openProject}
        onCreateProject={createNewProject}
        onRemoveProject={removeProject}
        projectLoading={projectLoading}
        projectError={projectError}
      />

      {/* SETTINGS MODAL */}
      <SettingsModal
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
        aiConfig={aiConfig}
      />
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);

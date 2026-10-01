import React, { useState } from "react";
import {
  ChevronUpIcon,
  ChevronDownIcon,
  CopyIcon,
  TrashIcon,
  CloseIcon,
  SlidersIcon,
} from "./Icons";

export function SceneInspector({
  draftPlan,
  selectedSceneIndex,
  onUpdateScene,
  onDuplicateScene,
  onDeleteScene,
  onMoveScene,
  isCollapsed,
  onToggleCollapse,
}) {
  const [collapsedSections, setCollapsedSections] = useState({
    story: false,
    visual: false,
    motion: false,
    geography: false,
    timing: false,
  });

  const toggleSection = (section) => {
    setCollapsedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  if (isCollapsed) {
    return (
      <div className="w-10 bg-[#0B0B0B] border-l border-white/5 flex flex-col items-center py-3">
        <button
          onClick={onToggleCollapse}
          className="btn-icon text-[#9A9A9A] hover:text-[#F5F2EA]"
          title="Open Scene Inspector"
        >
          <SlidersIcon className="w-4 h-4" />
        </button>
      </div>
    );
  }

  const scenes = draftPlan?.scenes || [];
  const scene = scenes[selectedSceneIndex];

  if (!scene) {
    return (
      <aside className="scene-inspector p-4 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between pb-3 border-b border-white/5">
            <span className="text-xs uppercase font-mono tracking-widest text-[#9A9A9A]">Inspector</span>
            <button onClick={onToggleCollapse} className="btn-icon text-[#9A9A9A]">
              <CloseIcon className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="text-center py-16 px-4 text-[#666666] text-xs">
            No scene selected. Click a scene on the timeline to inspect its parameters.
          </div>
        </div>
      </aside>
    );
  }

  const duration = (scene.end - scene.start).toFixed(2);

  return (
    <aside className="scene-inspector flex flex-col justify-between">
      {/* Inspector Header */}
      <div className="p-4 border-b border-white/5 flex items-center justify-between bg-[#0B0B0B] sticky top-0 z-10">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold text-[#FF5A1F]">
              SCENE {(selectedSceneIndex + 1).toString().padStart(2, "0")}
            </span>
            <span className="text-[11px] font-mono text-[#9A9A9A] px-2 py-0.5 rounded-full bg-white/5 border border-white/5">
              {duration}s
            </span>
          </div>
          <div className="text-xs font-medium text-[#F5F2EA] truncate max-w-[180px] mt-0.5">
            {scene.title || `Scene ${selectedSceneIndex + 1}`}
          </div>
        </div>

        {/* Scene Action Bar */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => onMoveScene(scene.id, -1)}
            disabled={selectedSceneIndex === 0}
            className="w-7 h-7 flex items-center justify-center rounded hover:bg-white/10 disabled:opacity-20 text-[#9A9A9A] hover:text-white"
            title="Move earlier"
          >
            <ChevronUpIcon className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => onMoveScene(scene.id, 1)}
            disabled={selectedSceneIndex === scenes.length - 1}
            className="w-7 h-7 flex items-center justify-center rounded hover:bg-white/10 disabled:opacity-20 text-[#9A9A9A] hover:text-white"
            title="Move later"
          >
            <ChevronDownIcon className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => onDuplicateScene(scene.id)}
            className="w-7 h-7 flex items-center justify-center rounded hover:bg-white/10 text-[#9A9A9A] hover:text-white"
            title="Duplicate scene"
          >
            <CopyIcon className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => onDeleteScene(scene.id)}
            disabled={scenes.length <= 1}
            className="w-7 h-7 flex items-center justify-center rounded hover:bg-red-500/20 disabled:opacity-20 text-[#9A9A9A] hover:text-red-400"
            title="Delete scene"
          >
            <TrashIcon className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onToggleCollapse}
            className="w-7 h-7 flex items-center justify-center rounded hover:bg-white/10 text-[#9A9A9A] ml-1"
            title="Collapse Inspector"
          >
            <CloseIcon className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Collapsible Property Sections */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* TIMING SECTION */}
        <div className="border border-white/5 rounded-xl bg-[#0E0E0E] overflow-hidden">
          <div
            onClick={() => toggleSection("timing")}
            className="px-3 py-2 flex items-center justify-between cursor-pointer hover:bg-white/[0.02] border-b border-white/5 text-[11px] font-mono tracking-wider text-[#9A9A9A] uppercase"
          >
            <span>Timing ({scene.start.toFixed(1)}s → {scene.end.toFixed(1)}s)</span>
            <ChevronDownIcon className={`w-3.5 h-3.5 transition-transform ${collapsedSections.timing ? "-rotate-90" : ""}`} />
          </div>

          {!collapsedSections.timing && (
            <div className="p-3 grid grid-cols-2 gap-2.5">
              <div>
                <label className="text-[10px] font-mono uppercase text-[#666666] block mb-1">Start (s)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  value={scene.start}
                  onChange={(e) => onUpdateScene(scene.id, "start", e.target.value)}
                  className="cinematic-input py-1.5 px-2.5 text-xs"
                />
              </div>
              <div>
                <label className="text-[10px] font-mono uppercase text-[#666666] block mb-1">End (s)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  value={scene.end}
                  onChange={(e) => onUpdateScene(scene.id, "end", e.target.value)}
                  className="cinematic-input py-1.5 px-2.5 text-xs"
                />
              </div>
            </div>
          )}
        </div>

        {/* STORY SECTION */}
        <div className="border border-white/5 rounded-xl bg-[#0E0E0E] overflow-hidden">
          <div
            onClick={() => toggleSection("story")}
            className="px-3 py-2 flex items-center justify-between cursor-pointer hover:bg-white/[0.02] border-b border-white/5 text-[11px] font-mono tracking-wider text-[#9A9A9A] uppercase"
          >
            <span>Story & Narration</span>
            <ChevronDownIcon className={`w-3.5 h-3.5 transition-transform ${collapsedSections.story ? "-rotate-90" : ""}`} />
          </div>

          {!collapsedSections.story && (
            <div className="p-3 space-y-3">
              <div>
                <label className="text-[10px] font-mono uppercase text-[#666666] block mb-1">Scene Title</label>
                <input
                  type="text"
                  value={scene.title}
                  onChange={(e) => onUpdateScene(scene.id, "title", e.target.value)}
                  className="cinematic-input py-1.5 px-2.5 text-xs"
                  placeholder="Scene title"
                />
              </div>

              <div>
                <label className="text-[10px] font-mono uppercase text-[#666666] block mb-1">Voice Narration</label>
                <textarea
                  rows={3}
                  value={scene.narration}
                  onChange={(e) => onUpdateScene(scene.id, "narration", e.target.value)}
                  className="cinematic-textarea py-2 px-2.5 text-xs"
                  placeholder="Narration spoken during this scene"
                />
              </div>

              <div>
                <label className="text-[10px] font-mono uppercase text-[#666666] block mb-1">On-Screen Caption</label>
                <input
                  type="text"
                  value={scene.caption}
                  onChange={(e) => onUpdateScene(scene.id, "caption", e.target.value)}
                  className="cinematic-input py-1.5 px-2.5 text-xs"
                  placeholder="Bottom caption text"
                />
              </div>
            </div>
          )}
        </div>

        {/* VISUAL & ASSETS SECTION */}
        <div className="border border-white/5 rounded-xl bg-[#0E0E0E] overflow-hidden">
          <div
            onClick={() => toggleSection("visual")}
            className="px-3 py-2 flex items-center justify-between cursor-pointer hover:bg-white/[0.02] border-b border-white/5 text-[11px] font-mono tracking-wider text-[#9A9A9A] uppercase"
          >
            <span>Visual & Assets</span>
            <ChevronDownIcon className={`w-3.5 h-3.5 transition-transform ${collapsedSections.visual ? "-rotate-90" : ""}`} />
          </div>

          {!collapsedSections.visual && (
            <div className="p-3 space-y-3">
              <div>
                <label className="text-[10px] font-mono uppercase text-[#666666] block mb-1">Visual Composition</label>
                <textarea
                  rows={3}
                  value={scene.visual}
                  onChange={(e) => onUpdateScene(scene.id, "visual", e.target.value)}
                  className="cinematic-textarea py-2 px-2.5 text-xs"
                  placeholder="What is visually displayed in the frame"
                />
              </div>

              <div>
                <label className="text-[10px] font-mono uppercase text-[#666666] block mb-1">Asset Hints (comma separated)</label>
                <input
                  type="text"
                  value={scene.asset_hints.join(", ")}
                  onChange={(e) =>
                    onUpdateScene(
                      scene.id,
                      "asset_hints",
                      e.target.value
                        .split(",")
                        .map((s) => s.trim())
                        .filter(Boolean)
                    )
                  }
                  className="cinematic-input py-1.5 px-2.5 text-xs"
                  placeholder="map, character, artifact, landmark..."
                />
              </div>
            </div>
          )}
        </div>

        {/* MOTION & CAMERA SECTION */}
        <div className="border border-white/5 rounded-xl bg-[#0E0E0E] overflow-hidden">
          <div
            onClick={() => toggleSection("motion")}
            className="px-3 py-2 flex items-center justify-between cursor-pointer hover:bg-white/[0.02] border-b border-white/5 text-[11px] font-mono tracking-wider text-[#9A9A9A] uppercase"
          >
            <span>Motion & Camera</span>
            <ChevronDownIcon className={`w-3.5 h-3.5 transition-transform ${collapsedSections.motion ? "-rotate-90" : ""}`} />
          </div>

          {!collapsedSections.motion && (
            <div className="p-3 space-y-3">
              <div>
                <label className="text-[10px] font-mono uppercase text-[#666666] block mb-1">Animation Dynamic</label>
                <input
                  type="text"
                  value={scene.animation}
                  onChange={(e) => onUpdateScene(scene.id, "animation", e.target.value)}
                  className="cinematic-input py-1.5 px-2.5 text-xs"
                  placeholder="fade, slide, scale, reveal..."
                />
              </div>

              <div>
                <label className="text-[10px] font-mono uppercase text-[#666666] block mb-1">Camera Movement</label>
                <input
                  type="text"
                  value={scene.camera}
                  onChange={(e) => onUpdateScene(scene.id, "camera", e.target.value)}
                  className="cinematic-input py-1.5 px-2.5 text-xs"
                  placeholder="static, zoom in, pan left..."
                />
              </div>
            </div>
          )}
        </div>

        {/* GEOGRAPHY SECTION */}
        <div className="border border-white/5 rounded-xl bg-[#0E0E0E] overflow-hidden">
          <div
            onClick={() => toggleSection("geography")}
            className="px-3 py-2 flex items-center justify-between cursor-pointer hover:bg-white/[0.02] border-b border-white/5 text-[11px] font-mono tracking-wider text-[#9A9A9A] uppercase"
          >
            <span>Geography</span>
            <ChevronDownIcon className={`w-3.5 h-3.5 transition-transform ${collapsedSections.geography ? "-rotate-90" : ""}`} />
          </div>

          {!collapsedSections.geography && (
            <div className="p-3">
              <label className="text-[10px] font-mono uppercase text-[#666666] block mb-1">Location Tag</label>
              <input
                type="text"
                value={scene.location || ""}
                onChange={(e) => onUpdateScene(scene.id, "location", e.target.value)}
                className="cinematic-input py-1.5 px-2.5 text-xs"
                placeholder="Historical region or landmark"
              />
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}

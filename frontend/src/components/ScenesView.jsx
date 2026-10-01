import React from "react";
import {
  ScenesIcon,
  PlusIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CopyIcon,
  TrashIcon,
  CheckCircleIcon,
  AlertCircleIcon,
  SplitIcon,
} from "./Icons";

export function ScenesView({
  draftPlan,
  selectedSceneIndex,
  onSelectScene,
  onAddScene,
  onMoveScene,
  onDuplicateScene,
  onDeleteScene,
  timelineErrors,
  hasUnsavedChanges,
  onApplyChanges,
  onResetChanges,
  onRefreshAssetPlan,
  assetLoading,
  onResolveAssets,
  assetResolving,
  onPlanGeography,
  geographyLoading,
  setActiveTab,
}) {
  if (!draftPlan || !draftPlan.scenes?.length) {
    return (
      <div className="flex-1 p-10 flex flex-col items-center justify-center text-center max-w-xl mx-auto">
        <div className="w-12 h-12 rounded-2xl bg-[#FF5A1F]/10 border border-[#FF5A1F]/30 flex items-center justify-center text-[#FF5A1F] mb-4">
          <ScenesIcon className="w-6 h-6" />
        </div>
        <h2 className="font-serif text-2xl text-[#F5F2EA] mb-2">No Scene Plan Yet</h2>
        <p className="text-xs text-[#9A9A9A] leading-relaxed mb-6">
          Write your story script in the Story editor to generate structured, timed scenes.
        </p>
        <button onClick={() => setActiveTab("story")} className="btn-primary">
          Open Story Editor
        </button>
      </div>
    );
  }

  // Helper to split a scene evenly into two
  const handleSplitScene = (sceneId) => {
    // handled via duplicate and halving or custom
    onDuplicateScene(sceneId);
  };

  return (
    <div className="flex-1 p-6 sm:p-10 max-w-6xl mx-auto w-full flex flex-col">
      {/* Header & Main Toolbar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 pb-6 border-b border-white/5">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-[#FF5A1F] mb-1.5">
            <ScenesIcon className="w-3.5 h-3.5" />
            <span>Timeline Director</span>
          </div>
          <h1 className="font-serif text-3xl font-medium tracking-tight text-[#F5F2EA]">
            Scene Sequence
          </h1>
          <div className="flex items-center gap-3 text-xs text-[#9A9A9A] mt-1">
            <span>{draftPlan.scenes.length} Scenes</span>
            <span>·</span>
            <span>{draftPlan.total_duration.toFixed(1)}s Total Duration</span>
            <span>·</span>
            <span>{draftPlan.aspect_ratio || "9:16"}</span>
          </div>
        </div>

        {/* Toolbar Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => onRefreshAssetPlan(draftPlan)}
            disabled={assetLoading || timelineErrors.length > 0}
            className="btn-secondary text-xs"
            title="Scan scenes and extract visual asset hints"
          >
            {assetLoading ? "Planning Assets…" : "Plan Assets"}
          </button>

          <button
            onClick={() => onResolveAssets(draftPlan)}
            disabled={assetResolving || timelineErrors.length > 0}
            className="btn-secondary text-xs"
            title="Resolve assets against local disk library"
          >
            {assetResolving ? "Resolving…" : "Resolve Assets"}
          </button>

          <button
            onClick={() => onPlanGeography(draftPlan)}
            disabled={geographyLoading || timelineErrors.length > 0}
            className="btn-secondary text-xs"
            title="Detect historical geography & map operations"
          >
            {geographyLoading ? "Planning Map…" : "Plan Geography"}
          </button>

          <button onClick={onAddScene} className="btn-primary text-xs">
            <PlusIcon className="w-3.5 h-3.5" />
            <span>Add Scene</span>
          </button>
        </div>
      </div>

      {/* Validation Health Banner */}
      <div className="mb-6 flex items-center justify-between p-3.5 rounded-xl bg-[#0B0B0B] border border-white/5 text-xs">
        <div className="flex items-center gap-2.5">
          {timelineErrors.length === 0 ? (
            <>
              <CheckCircleIcon className="w-4 h-4 text-emerald-400" />
              <span className="text-[#F5F2EA] font-medium">Timeline Valid</span>
              <span className="text-[#666666]">· Continuous timeline with no gaps or overlaps</span>
            </>
          ) : (
            <>
              <AlertCircleIcon className="w-4 h-4 text-amber-400" />
              <span className="text-amber-300 font-medium">Timeline Discrepancies</span>
              <span className="text-amber-400/80">({timelineErrors.join(" · ")})</span>
            </>
          )}
        </div>

        {hasUnsavedChanges && (
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono text-[#FF5A1F]">Unsaved edits</span>
            <button onClick={onResetChanges} className="btn-secondary text-[11px] py-1 px-2.5">
              Reset
            </button>
            <button
              onClick={onApplyChanges}
              disabled={timelineErrors.length > 0}
              className="btn-primary text-[11px] py-1 px-3"
            >
              Apply
            </button>
          </div>
        )}
      </div>

      {/* Filmstrip Scene Cards Grid */}
      <div className="space-y-3.5 flex-1 overflow-y-auto pr-1">
        {draftPlan.scenes.map((scene, index) => {
          const isSelected = selectedSceneIndex === index;
          const duration = (scene.end - scene.start).toFixed(1);

          return (
            <div
              key={scene.id || index}
              onClick={() => onSelectScene(index)}
              className={`p-4 rounded-xl border transition-all cursor-pointer ${
                isSelected
                  ? "bg-[#111111] border-[#FF5A1F] shadow-[0_4px_24px_rgba(255,90,31,0.15)]"
                  : "bg-[#090909] border-white/5 hover:border-white/15 hover:bg-[#0D0D0D]"
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 mb-3 border-b border-white/5">
                <div className="flex items-center gap-3">
                  <span
                    className={`font-mono text-xs font-bold px-2 py-0.5 rounded ${
                      isSelected
                        ? "bg-[#FF5A1F] text-white"
                        : "bg-white/5 text-[#9A9A9A]"
                    }`}
                  >
                    SCENE {(index + 1).toString().padStart(2, "0")}
                  </span>
                  <h3 className="text-sm font-medium text-[#F5F2EA]">{scene.title || `Scene ${index + 1}`}</h3>
                </div>

                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-[#9A9A9A]">
                    {scene.start.toFixed(1)}s → {scene.end.toFixed(1)}s ({duration}s)
                  </span>

                  {/* Actions */}
                  <div
                    className="flex items-center gap-1"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <button
                      onClick={() => onMoveScene(scene.id, -1)}
                      disabled={index === 0}
                      className="btn-icon w-7 h-7 text-xs disabled:opacity-20"
                      title="Move earlier"
                    >
                      <ChevronLeftIcon className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => onMoveScene(scene.id, 1)}
                      disabled={index === draftPlan.scenes.length - 1}
                      className="btn-icon w-7 h-7 text-xs disabled:opacity-20"
                      title="Move later"
                    >
                      <ChevronRightIcon className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => onDuplicateScene(scene.id)}
                      className="btn-icon w-7 h-7 text-xs"
                      title="Duplicate scene"
                    >
                      <CopyIcon className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => onDeleteScene(scene.id)}
                      disabled={draftPlan.scenes.length <= 1}
                      className="btn-icon w-7 h-7 text-xs hover:text-red-400 disabled:opacity-20"
                      title="Delete scene"
                    >
                      <TrashIcon className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Scene Content Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                {/* Story & Voice Narration */}
                <div className="space-y-1">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-[#666666]">Narration</span>
                  <p className="text-[#F5F2EA]/90 leading-relaxed italic bg-white/[0.02] p-2.5 rounded-lg border border-white/5">
                    "{scene.narration || "No voice narration specified."}"
                  </p>
                </div>

                {/* Visual, Motion & Hints */}
                <div className="space-y-2">
                  <div>
                    <span className="text-[10px] font-mono uppercase tracking-wider text-[#666666]">Visual Composition</span>
                    <p className="text-[#9A9A9A] leading-relaxed mt-0.5">
                      {scene.visual || "No visual direction specified."}
                    </p>
                  </div>

                  <div className="flex flex-wrap items-center gap-2 pt-1">
                    {scene.camera && (
                      <span className="badge badge-muted">Cam: {scene.camera}</span>
                    )}
                    {scene.animation && (
                      <span className="badge badge-muted">Anim: {scene.animation}</span>
                    )}
                    {scene.location && (
                      <span className="badge badge-accent">Geo: {scene.location}</span>
                    )}
                    {scene.asset_hints?.map((hint, i) => (
                      <span key={i} className="badge bg-white/5 text-[#9A9A9A] border border-white/5">
                        {hint}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

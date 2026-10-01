import React, { useRef } from "react";
import {
  PlusIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CopyIcon,
  TrashIcon,
  CheckCircleIcon,
  AlertCircleIcon,
} from "./Icons";

export function BottomTimeline({
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
  setActiveTab,
}) {
  const scrollRef = useRef(null);

  if (!draftPlan || !draftPlan.scenes?.length) {
    return (
      <div className="bottom-timeline px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs uppercase font-mono tracking-wider text-[#9A9A9A]">Timeline</span>
          <span className="text-xs text-[#666666]">No scene plan loaded yet. Enter a script in Story view to generate scenes.</span>
        </div>
        <button
          onClick={() => setActiveTab("story")}
          className="btn-secondary text-xs py-1.5 px-3"
        >
          Go to Story Editor
        </button>
      </div>
    );
  }

  const scrollLeft = () => {
    if (scrollRef.current) scrollRef.current.scrollBy({ left: -260, behavior: "smooth" });
  };

  const scrollRight = () => {
    if (scrollRef.current) scrollRef.current.scrollBy({ left: 260, behavior: "smooth" });
  };

  return (
    <footer className="bottom-timeline flex flex-col justify-between">
      {/* Top Controls / Status Strip */}
      <div className="h-9 px-4 border-b border-white/5 flex items-center justify-between text-xs bg-[#090909]">
        {/* Left: Summary & Format */}
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-mono uppercase tracking-widest text-[#FF5A1F]">
            Timeline
          </span>
          <span className="text-[#9A9A9A] text-xs">
            {draftPlan.scenes.length} Scenes · {draftPlan.total_duration.toFixed(1)}s · {draftPlan.aspect_ratio || "9:16"}
          </span>

          <span className="w-px h-3 bg-white/10 hidden sm:block" />

          {/* Validation Status Pill */}
          <div className="hidden sm:flex items-center gap-1.5">
            {timelineErrors.length === 0 ? (
              <span className="flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
                <CheckCircleIcon className="w-3.5 h-3.5" /> Valid
              </span>
            ) : (
              <span className="flex items-center gap-1 text-[11px] text-amber-400 font-medium" title={timelineErrors.join("; ")}>
                <AlertCircleIcon className="w-3.5 h-3.5" /> {timelineErrors.length} Issue{timelineErrors.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>
        </div>

        {/* Right: Unsaved status, Apply/Reset, Add Scene */}
        <div className="flex items-center gap-2">
          {hasUnsavedChanges && (
            <div className="flex items-center gap-1.5">
              <span className="text-[11px] font-mono text-[#FF5A1F] hidden md:inline">Unsaved changes</span>
              <button
                onClick={onResetChanges}
                className="px-2.5 py-1 text-[11px] rounded text-[#9A9A9A] hover:text-white bg-white/5 hover:bg-white/10 transition-colors"
                title="Discard draft changes"
              >
                Reset
              </button>
              <button
                onClick={onApplyChanges}
                disabled={timelineErrors.length > 0}
                className="px-2.5 py-1 text-[11px] font-medium rounded bg-[#FF5A1F] text-white hover:bg-[#FF6A32] disabled:opacity-40 transition-colors"
                title="Apply changes to working scene plan"
              >
                Apply
              </button>
            </div>
          )}

          <div className="h-3 w-px bg-white/10 mx-1 hidden sm:block" />

          <button
            onClick={onAddScene}
            className="flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-white/[0.04] border border-white/10 hover:border-white/20 text-[#F5F2EA] transition-all"
            title="Append a new scene to the timeline"
          >
            <PlusIcon className="w-3 h-3 text-[#FF5A1F]" />
            <span>Add Scene</span>
          </button>

          {/* Filmstrip scroll buttons */}
          <div className="flex items-center gap-0.5 ml-1">
            <button onClick={scrollLeft} className="w-6 h-6 flex items-center justify-center rounded hover:bg-white/10 text-[#9A9A9A] hover:text-white transition-colors">
              <ChevronLeftIcon className="w-3.5 h-3.5" />
            </button>
            <button onClick={scrollRight} className="w-6 h-6 flex items-center justify-center rounded hover:bg-white/10 text-[#9A9A9A] hover:text-white transition-colors">
              <ChevronRightIcon className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Horizontal Filmstrip Cards */}
      <div
        ref={scrollRef}
        className="flex-1 px-4 py-2.5 flex items-center gap-2.5 overflow-x-auto overflow-y-hidden"
      >
        {draftPlan.scenes.map((scene, index) => {
          const isSelected = selectedSceneIndex === index;
          const duration = (scene.end - scene.start).toFixed(1);

          return (
            <div
              key={scene.id || index}
              onClick={() => onSelectScene(index)}
              className={`timeline-card group ${isSelected ? "selected" : ""}`}
            >
              {/* Card Header: Scene # and Timing */}
              <div className="flex items-center justify-between text-[11px]">
                <span className={`font-mono font-bold ${isSelected ? "text-[#FF5A1F]" : "text-[#9A9A9A]"}`}>
                  {(index + 1).toString().padStart(2, "0")}
                </span>
                <span className="font-mono text-[10px] text-[#666666]">
                  {scene.start.toFixed(1)}s - {scene.end.toFixed(1)}s ({duration}s)
                </span>
              </div>

              {/* Title / Description */}
              <div className="truncate text-xs font-medium text-[#F5F2EA] my-0.5" title={scene.title}>
                {scene.title || `Scene ${index + 1}`}
              </div>

              {/* Card Footer: Metadata flags & Quick Actions on hover */}
              <div className="flex items-center justify-between pt-1 border-t border-white/5 text-[10px]">
                {/* Indicators */}
                <div className="flex items-center gap-1.5 text-[#9A9A9A]">
                  {scene.narration && (
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400" title="Narration text present" />
                  )}
                  {scene.asset_hints?.length > 0 && (
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" title={`${scene.asset_hints.length} asset hints`} />
                  )}
                  {scene.location && (
                    <span className="w-1.5 h-1.5 rounded-full bg-purple-400" title={`Location: ${scene.location}`} />
                  )}
                  {scene.camera && (
                    <span className="text-[9px] font-mono text-[#666666] uppercase truncate max-w-[45px]">
                      {scene.camera.split(" ")[0]}
                    </span>
                  )}
                </div>

                {/* Quick actions hover toolbar */}
                <div
                  className="opacity-0 group-hover:opacity-100 flex items-center gap-1 transition-opacity"
                  onClick={(e) => e.stopPropagation()}
                >
                  <button
                    onClick={() => onMoveScene(scene.id, -1)}
                    disabled={index === 0}
                    className="p-0.5 rounded hover:bg-white/10 disabled:opacity-20 text-[#9A9A9A] hover:text-white"
                    title="Move earlier"
                  >
                    <ChevronLeftIcon className="w-3 h-3" />
                  </button>
                  <button
                    onClick={() => onMoveScene(scene.id, 1)}
                    disabled={index === draftPlan.scenes.length - 1}
                    className="p-0.5 rounded hover:bg-white/10 disabled:opacity-20 text-[#9A9A9A] hover:text-white"
                    title="Move later"
                  >
                    <ChevronRightIcon className="w-3 h-3" />
                  </button>
                  <button
                    onClick={() => onDuplicateScene(scene.id)}
                    className="p-0.5 rounded hover:bg-white/10 text-[#9A9A9A] hover:text-white"
                    title="Duplicate scene"
                  >
                    <CopyIcon className="w-3 h-3" />
                  </button>
                  <button
                    onClick={() => onDeleteScene(scene.id)}
                    disabled={draftPlan.scenes.length <= 1}
                    className="p-0.5 rounded hover:bg-red-500/20 disabled:opacity-20 text-[#9A9A9A] hover:text-red-400"
                    title="Delete scene"
                  >
                    <TrashIcon className="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </footer>
  );
}

import React from "react";
import { PreviewIcon, AlertCircleIcon, ExportIcon } from "./Icons";

const API_URL = "http://127.0.0.1:8000";

export function PreviewView({
  draftPlan,
  renderPreview,
  renderLoading,
  renderError,
  selectedRenderScene,
  setSelectedRenderScene,
  onRenderPreviewScenes,
  videoExport,
  setActiveTab,
}) {
  const currentSceneFile = renderPreview?.scene_files?.find((file) => {
    if (!selectedRenderScene) return true;
    return file.includes(selectedRenderScene);
  }) || renderPreview?.scene_files?.[0];

  const currentFilename = currentSceneFile ? currentSceneFile.split(/[\\/]/).pop() : null;

  return (
    <div className="flex-1 p-6 sm:p-10 max-w-6xl mx-auto w-full flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-6 border-b border-white/5">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-[#FF5A1F] mb-1.5">
              <PreviewIcon className="w-3.5 h-3.5" />
              <span>Director's Monitor</span>
            </div>
            <h1 className="font-serif text-3xl font-medium tracking-tight text-[#F5F2EA]">
              Render Preview
            </h1>
            <p className="text-xs text-[#9A9A9A] mt-1">
              Real-time vector animation preview with SMIL camera motions, overlays, and typography.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onRenderPreviewScenes}
              disabled={renderLoading || !draftPlan?.scenes?.length}
              className="btn-primary text-xs"
            >
              {renderLoading ? "Synthesizing Preview…" : "Render SVG Preview"}
            </button>

            {videoExport && (
              <button
                onClick={() => setActiveTab("export")}
                className="btn-secondary text-xs"
              >
                <ExportIcon className="w-3.5 h-3.5" />
                <span>View MP4</span>
              </button>
            )}
          </div>
        </div>

        {/* Error message */}
        {renderError && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-3 mb-6">
            <AlertCircleIcon className="w-4 h-4 flex-shrink-0 text-red-400" />
            <span>{renderError}</span>
          </div>
        )}

        {/* Monitor Frame */}
        {renderPreview ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left: Video Preview Stage */}
            <div className="lg:col-span-8 flex flex-col items-center">
              <div className="w-full max-w-[420px] aspect-[9/16] bg-[#070707] border border-white/10 rounded-2xl overflow-hidden relative shadow-[0_20px_80px_rgba(0,0,0,0.8)] flex items-center justify-center">
                {currentFilename ? (
                  <img
                    src={`${API_URL}/api/render/file/${encodeURIComponent(currentFilename)}`}
                    alt="Scene Preview"
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="text-xs text-[#666666]">Preview frame loading…</div>
                )}

                {/* Subtle Overlaid Canvas Grid & Watermark */}
                <div className="absolute top-3 left-3 text-[10px] font-mono uppercase tracking-widest text-white/40 bg-black/60 px-2 py-0.5 rounded backdrop-blur-sm">
                  {selectedRenderScene || "LIVE PREVIEW"}
                </div>

                <div className="absolute bottom-3 right-3 text-[10px] font-mono text-white/40 bg-black/60 px-2 py-0.5 rounded backdrop-blur-sm">
                  {renderPreview.width} × {renderPreview.height}
                </div>
              </div>

              {/* Time Scrubber / Scene Selector */}
              <div className="w-full max-w-[420px] mt-4 flex items-center justify-between gap-2 px-1">
                <span className="text-[11px] font-mono text-[#9A9A9A]">
                  Scene {renderPreview.scene_files.findIndex(f => f.includes(selectedRenderScene || "")) + 1 || 1} of {renderPreview.scene_files.length}
                </span>

                <div className="flex items-center gap-1.5">
                  <a
                    href={currentFilename ? `${API_URL}/api/render/file/${encodeURIComponent(currentFilename)}` : "#"}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[11px] text-[#FF5A1F] hover:underline"
                  >
                    Open SVG Raw
                  </a>
                </div>
              </div>
            </div>

            {/* Right: Scene Frame Selector List */}
            <div className="lg:col-span-4 space-y-3">
              <div className="text-[11px] font-mono uppercase tracking-wider text-[#9A9A9A] pb-2 border-b border-white/5">
                Rendered Frames ({renderPreview.scene_files.length})
              </div>

              <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
                {renderPreview.scene_files.map((file, index) => {
                  const filename = file.split(/[\\/]/).pop();
                  const sceneId = filename.replace(/^scene_\d+_/, "").replace(/\.svg$/, "");
                  const isSelected = selectedRenderScene === sceneId || (!selectedRenderScene && index === 0);

                  return (
                    <button
                      key={file}
                      onClick={() => setSelectedRenderScene(sceneId)}
                      className={`w-full flex items-center justify-between p-3 rounded-xl text-left transition-all border ${
                        isSelected
                          ? "bg-[#141414] border-[#FF5A1F] text-[#F5F2EA] shadow-[0_2px_12px_rgba(255,90,31,0.15)]"
                          : "bg-[#090909] border-white/5 text-[#9A9A9A] hover:border-white/15 hover:text-white"
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <span className={`w-1.5 h-1.5 rounded-full ${isSelected ? "bg-[#FF5A1F]" : "bg-white/20"}`} />
                        <div>
                          <div className="text-xs font-medium">Scene {index + 1}</div>
                          <div className="text-[10px] font-mono text-[#666666] truncate max-w-[160px]">{sceneId}</div>
                        </div>
                      </div>
                      <span className="text-[10px] font-mono text-[#666666]">SVG</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          /* Empty State */
          <div className="cinematic-card p-12 text-center max-w-xl mx-auto my-8 bg-[#090909] border-white/5">
            <div className="w-12 h-12 rounded-2xl bg-[#FF5A1F]/10 border border-[#FF5A1F]/30 flex items-center justify-center text-[#FF5A1F] mx-auto mb-4">
              <PreviewIcon className="w-6 h-6" />
            </div>
            <h2 className="font-serif text-2xl text-[#F5F2EA] mb-2">
              Your story hasn't been rendered yet.
            </h2>
            <p className="text-xs text-[#9A9A9A] max-w-md mx-auto leading-relaxed mb-6">
              Generate a vector preview to review animations, typography, and camera movements, or export a broadcast MP4 when your timeline is ready.
            </p>
            <button
              onClick={onRenderPreviewScenes}
              disabled={renderLoading || !draftPlan?.scenes?.length}
              className="btn-primary text-xs"
            >
              {renderLoading ? "Synthesizing Preview…" : "Generate Preview Bundle"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

import React from "react";
import { ExportIcon, AlertCircleIcon, DownloadIcon, CheckCircleIcon } from "./Icons";

const API_URL = "http://127.0.0.1:8000";

export function ExportView({
  draftPlan,
  videoExport,
  videoExporting,
  videoExportError,
  onExportVideo,
}) {
  const videoFilename = videoExport?.output_file
    ? videoExport.output_file.split(/[\\/]/).pop()
    : null;

  return (
    <div className="flex-1 p-6 sm:p-10 max-w-5xl mx-auto w-full flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-[#FF5A1F] mb-2">
            <ExportIcon className="w-3.5 h-3.5" />
            <span>Master Video Production</span>
          </div>
          <h1 className="font-serif text-3xl sm:text-5xl font-medium tracking-tight text-[#F5F2EA] mb-3">
            Ready to bring history to motion?
          </h1>
          <p className="text-sm sm:text-base text-[#9A9A9A] font-light max-w-2xl leading-relaxed">
            Synthesize frame sequences with the local PIL renderer and encode high-fidelity MP4 video using hardware-accelerated FFmpeg.
          </p>
        </div>

        {/* Error Alert */}
        {videoExportError && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-3 mb-6">
            <AlertCircleIcon className="w-4 h-4 flex-shrink-0 text-red-400" />
            <span>{videoExportError}</span>
          </div>
        )}

        {/* Production Specs Card */}
        <div className="cinematic-card p-6 bg-[#0B0B0B] border-white/10 rounded-2xl mb-8 shadow-[0_10px_40px_rgba(0,0,0,0.6)]">
          <div className="text-[11px] font-mono uppercase tracking-wider text-[#9A9A9A] pb-3 mb-4 border-b border-white/5">
            Render Specifications
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <span className="text-[10px] font-mono uppercase text-[#666666] block mb-1">Resolution</span>
              <div className="text-sm font-mono font-medium text-[#F5F2EA]">
                {draftPlan?.aspect_ratio === "16:9" ? "1920 × 1080" : draftPlan?.aspect_ratio === "1:1" ? "1080 × 1080" : "1080 × 1920"}
              </div>
              <span className="text-[10px] text-[#9A9A9A]">{draftPlan?.aspect_ratio || "9:16"}</span>
            </div>

            <div>
              <span className="text-[10px] font-mono uppercase text-[#666666] block mb-1">Framerate</span>
              <div className="text-sm font-mono font-medium text-[#F5F2EA]">30.00 FPS</div>
              <span className="text-[10px] text-[#9A9A9A]">Progressive Scan</span>
            </div>

            <div>
              <span className="text-[10px] font-mono uppercase text-[#666666] block mb-1">Target Duration</span>
              <div className="text-sm font-mono font-medium text-[#F5F2EA]">
                {draftPlan?.total_duration ? `${draftPlan.total_duration.toFixed(1)}s` : "60.0s"}
              </div>
              <span className="text-[10px] text-[#9A9A9A]">{draftPlan?.scenes?.length || 0} Scenes</span>
            </div>

            <div>
              <span className="text-[10px] font-mono uppercase text-[#666666] block mb-1">Video Codec</span>
              <div className="text-sm font-mono font-medium text-[#F5F2EA]">libx264</div>
              <span className="text-[10px] text-[#9A9A9A]">yuv420p · FastStart</span>
            </div>
          </div>
        </div>

        {/* Export In-Progress Stepper */}
        {videoExporting && (
          <div className="cinematic-card p-6 bg-[#090909] border-[#FF5A1F]/30 rounded-2xl mb-8 shadow-[0_0_30px_var(--accent-glow)]">
            <div className="flex items-center gap-3 mb-4">
              <span className="w-4 h-4 border-2 border-[#FF5A1F] border-t-transparent rounded-full animate-spin" />
              <span className="text-sm font-medium text-[#F5F2EA]">
                Encoding Master MP4 Video…
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 text-xs font-mono">
              <div className="p-2.5 rounded bg-white/5 border border-white/5 text-emerald-400">
                1. Render Frames (PNG)
              </div>
              <div className="p-2.5 rounded bg-[#FF5A1F]/10 border border-[#FF5A1F]/30 text-[#FF5A1F] animate-pulse">
                2. FFmpeg Encoding
              </div>
              <div className="p-2.5 rounded bg-white/5 border border-white/5 text-[#666666]">
                3. Finalizing MP4
              </div>
            </div>
          </div>
        )}

        {/* Completed Master Video Player */}
        {videoExport && (
          <div className="cinematic-card p-6 bg-[#090909] border-emerald-500/20 rounded-2xl mb-8 space-y-6">
            <div className="flex items-center justify-between pb-3 border-b border-white/5">
              <div className="flex items-center gap-2">
                <CheckCircleIcon className="w-5 h-5 text-emerald-400" />
                <span className="text-sm font-medium text-[#F5F2EA]">Master Video Ready</span>
              </div>

              {videoFilename && (
                <a
                  href={`${API_URL}/api/render/video/${encodeURIComponent(videoFilename)}`}
                  download={videoFilename}
                  className="btn-primary text-xs py-1.5 px-4"
                >
                  <DownloadIcon className="w-3.5 h-3.5" />
                  <span>Download MP4</span>
                </a>
              )}
            </div>

            {/* Embedded HTML5 Video Player */}
            {videoFilename && (
              <div className="flex justify-center bg-[#050505] p-4 rounded-xl border border-white/5">
                <video
                  controls
                  preload="metadata"
                  src={`${API_URL}/api/render/video/${encodeURIComponent(videoFilename)}`}
                  className="max-h-[460px] rounded-lg shadow-2xl"
                />
              </div>
            )}

            {/* Render Output Details */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono bg-white/[0.02] p-3 rounded-lg border border-white/5 text-[#9A9A9A]">
              <div>Frames: <strong className="text-[#F5F2EA]">{videoExport.frame_count}</strong></div>
              <div>Duration: <strong className="text-[#F5F2EA]">{videoExport.duration?.toFixed(2) || "0.00"}s</strong></div>
              <div>Width: <strong className="text-[#F5F2EA]">{videoExport.width}px</strong></div>
              <div>Height: <strong className="text-[#F5F2EA]">{videoExport.height}px</strong></div>
            </div>
          </div>
        )}
      </div>

      {/* Primary Action Button */}
      <div className="pt-6 border-t border-white/5 flex items-center justify-between">
        <span className="text-xs text-[#666666]">
          Outputs are stored locally in <code className="text-[#9A9A9A]">outputs/video_export/videos/</code>
        </span>

        <button
          onClick={onExportVideo}
          disabled={videoExporting || !draftPlan?.scenes?.length}
          className="btn-primary py-3 px-8 text-sm"
        >
          {videoExporting ? "Encoding Video…" : "Export MP4"}
        </button>
      </div>
    </div>
  );
}

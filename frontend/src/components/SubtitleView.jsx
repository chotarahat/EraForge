import React from "react";
import { SubtitleIcon, AlertCircleIcon, DownloadIcon } from "./Icons";

const API_URL = "http://127.0.0.1:8000";

export function SubtitleView({
  subtitleTrack,
  subtitleSrt,
  subtitleOutputFile,
  subtitleLoading,
  subtitleError,
  onGenerateSubtitles,
  onGenerateSubtitleFile,
  draftPlan,
}) {
  const cues = subtitleTrack?.cues || [];
  const srtFilename = subtitleOutputFile ? subtitleOutputFile.split(/[\\/]/).pop() : "subtitles.srt";

  return (
    <div className="flex-1 p-6 sm:p-10 max-w-6xl mx-auto w-full flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-6 border-b border-white/5">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-[#FF5A1F] mb-1.5">
              <SubtitleIcon className="w-3.5 h-3.5" />
              <span>Closed Captions & Subtitles</span>
            </div>
            <h1 className="font-serif text-3xl font-medium tracking-tight text-[#F5F2EA]">
              Subtitle Track
            </h1>
            <p className="text-xs text-[#9A9A9A] mt-1">
              Sentence-weighted duration allocation synchronized with actual speech tracks and standard SRT export.
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={onGenerateSubtitles}
              disabled={subtitleLoading || !draftPlan?.scenes?.length}
              className="btn-secondary text-xs"
            >
              {subtitleLoading ? "Analyzing Cues…" : "Generate Subtitles"}
            </button>
            <button
              onClick={onGenerateSubtitleFile}
              disabled={subtitleLoading || !draftPlan?.scenes?.length}
              className="btn-primary text-xs"
            >
              {subtitleLoading ? "Writing SRT…" : "Generate SRT File"}
            </button>
          </div>
        </div>

        {/* Error Alert */}
        {subtitleError && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-3 mb-6">
            <AlertCircleIcon className="w-4 h-4 flex-shrink-0 text-red-400" />
            <span>{subtitleError}</span>
          </div>
        )}

        {cues.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left: Cue List */}
            <div className="lg:col-span-7 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-white/5 text-xs">
                <span className="text-[11px] font-mono uppercase tracking-wider text-[#9A9A9A]">
                  Subtitle Cues ({cues.length})
                </span>
                <span className="badge badge-accent text-[10px]">
                  Narration Sync Active
                </span>
              </div>

              <div className="space-y-2 max-h-[560px] overflow-y-auto pr-1">
                {cues.map((cue) => (
                  <div
                    key={cue.index}
                    className="p-3.5 rounded-xl bg-[#090909] border border-white/5 flex items-start gap-3 hover:border-white/15 transition-all"
                  >
                    <span className="font-mono text-xs font-bold text-[#FF5A1F] pt-0.5">
                      {cue.index.toString().padStart(2, "0")}
                    </span>

                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between text-[11px] font-mono text-[#666666]">
                        <span>
                          {cue.start.toFixed(2)}s → {cue.end.toFixed(2)}s
                        </span>
                        <span>{(cue.end - cue.start).toFixed(2)}s</span>
                      </div>
                      <p className="text-xs text-[#F5F2EA] leading-relaxed">
                        {cue.text}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Live SRT Preview & Download */}
            <div className="lg:col-span-5 space-y-4">
              <div className="cinematic-card p-4 bg-[#090909] border-white/10 space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-white/5">
                  <div className="flex items-center gap-2 text-xs">
                    <span className="font-mono font-medium text-[#F5F2EA]">SRT File Export</span>
                  </div>

                  {subtitleOutputFile && (
                    <a
                      href={`${API_URL}/api/subtitles/file/${encodeURIComponent(srtFilename)}`}
                      download="subtitles.srt"
                      className="btn-primary text-xs py-1 px-3"
                    >
                      <DownloadIcon className="w-3.5 h-3.5" />
                      <span>Download SRT</span>
                    </a>
                  )}
                </div>

                <div className="text-[11px] font-mono text-[#9A9A9A] truncate">
                  Output: {subtitleOutputFile || "outputs/subtitles/subtitles.srt"}
                </div>

                {/* SRT Code Syntax Preview */}
                <div className="rounded-xl bg-[#050505] border border-white/5 p-3.5 max-h-[420px] overflow-y-auto">
                  <pre className="text-[11px] font-mono text-[#9A9A9A] leading-relaxed whitespace-pre-wrap selection:bg-[#FF5A1F]">
                    {subtitleSrt || "No SRT text generated yet."}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="cinematic-card p-12 text-center max-w-md mx-auto my-8 bg-[#090909] border-white/5">
            <div className="w-10 h-10 rounded-full bg-[#FF5A1F]/10 border border-[#FF5A1F]/30 flex items-center justify-center text-[#FF5A1F] mx-auto mb-3">
              <SubtitleIcon className="w-5 h-5" />
            </div>
            <p className="text-xs text-[#9A9A9A] mb-4">
              No subtitles generated yet. Click "Generate Subtitles" to align narration sentences with scene timestamps.
            </p>
            {draftPlan && (
              <button
                onClick={onGenerateSubtitles}
                disabled={subtitleLoading}
                className="btn-primary text-xs"
              >
                Generate Subtitles Now
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

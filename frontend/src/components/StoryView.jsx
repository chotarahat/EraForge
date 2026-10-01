import React from "react";
import { ScriptIcon, AlertCircleIcon, CheckCircleIcon } from "./Icons";

export function StoryView({
  script,
  setScript,
  duration,
  setDuration,
  aspectRatio = "9:16",
  setAspectRatio,
  style = "animated historical documentary",
  setStyle,
  loading,
  error,
  onGeneratePlan,
  aiConfig,
  draftPlan,
  setActiveTab,
}) {
  const charCount = script.length;
  const wordCount = script.trim() ? script.trim().split(/\s+/).length : 0;

  return (
    <div className="flex-1 p-6 sm:p-10 max-w-5xl mx-auto w-full flex flex-col justify-between">
      <div>
        {/* Editorial Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-[#FF5A1F] mb-2">
            <ScriptIcon className="w-3.5 h-3.5" />
            <span>Story Planning & Script</span>
          </div>
          <h1 className="font-serif text-3xl sm:text-5xl font-medium tracking-tight text-[#F5F2EA] mb-3">
            Tell the story.
          </h1>
          <p className="text-sm sm:text-base text-[#9A9A9A] font-light max-w-2xl leading-relaxed">
            Turn historical research into a structured visual story. Write your historical script, set the target pacing, and let the AI architect an animated scene timeline.
          </p>
        </div>

        {/* Script Editor Canvas */}
        <div className="cinematic-card p-4 sm:p-6 mb-6 bg-[#0B0B0B] border border-white/10 rounded-2xl relative shadow-[0_10px_40px_rgba(0,0,0,0.6)]">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/5 text-xs text-[#9A9A9A]">
            <span className="font-mono text-[11px] uppercase tracking-wider text-[#666666]">
              Historical Narrative
            </span>
            <div className="flex items-center gap-4 font-mono text-[11px]">
              <span>{wordCount} words</span>
              <span className="text-white/20">|</span>
              <span>{charCount} characters</span>
            </div>
          </div>

          <textarea
            value={script}
            onChange={(e) => setScript(e.target.value)}
            placeholder="Write or paste your historical narrative here... (minimum 20 characters)"
            className="w-full min-h-[300px] sm:min-h-[360px] bg-transparent text-[#F5F2EA] text-sm sm:text-base leading-relaxed placeholder:text-[#555555] border-none outline-none resize-y font-sans"
          />

          {/* Quick Preload Samples */}
          <div className="pt-3 border-t border-white/5 flex flex-wrap items-center justify-between gap-3 text-xs">
            <span className="text-[11px] text-[#666666]">Sample Topics:</span>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() =>
                  setScript(
                    "Before Bangladesh... before Bengal... before humans ever walked this land...\n\nMillions of years ago, the region we now call Bangladesh was part of a constantly changing geological world. The collision of the Indian tectonic plate with the Eurasian plate pushed up the Himalayas, birthing massive river systems that carved the delta."
                  )
                }
                className="text-[11px] text-[#9A9A9A] hover:text-[#F5F2EA] px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 transition-colors"
              >
                Bengal Delta Origins
              </button>
              <button
                type="button"
                onClick={() =>
                  setScript(
                    "In 331 BC, Alexander the Great marched his army across the deserts of Mesopotamia toward the heart of the Persian Empire.\n\nAt Gaugamela, king Darius III assembled a colossal force, complete with scythed chariots and war elephants. What followed was a tactical masterstroke that redrew the map of the ancient world forever."
                  )
                }
                className="text-[11px] text-[#9A9A9A] hover:text-[#F5F2EA] px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 transition-colors"
              >
                Battle of Gaugamela
              </button>
            </div>
          </div>
        </div>

        {/* Pacing & Visual Parameters */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          {/* Duration Control */}
          <div className="cinematic-card p-4 bg-[#0B0B0B]">
            <label className="text-[11px] font-mono uppercase tracking-wider text-[#9A9A9A] block mb-2">
              Target Duration
            </label>
            <select
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              className="cinematic-select"
            >
              <option value="30">30 Seconds (Shorts / Reels)</option>
              <option value="60">60 Seconds (Standard Story)</option>
              <option value="90">90 Seconds (Deep Dive)</option>
              <option value="120">120 Seconds (Extended)</option>
            </select>
          </div>

          {/* Aspect Ratio */}
          <div className="cinematic-card p-4 bg-[#0B0B0B]">
            <label className="text-[11px] font-mono uppercase tracking-wider text-[#9A9A9A] block mb-2">
              Canvas Aspect Ratio
            </label>
            <select
              value={aspectRatio || "9:16"}
              onChange={(e) => setAspectRatio && setAspectRatio(e.target.value)}
              className="cinematic-select"
            >
              <option value="9:16">9:16 (Vertical Mobile Documentary)</option>
              <option value="16:9">16:9 (Cinematic Widescreen)</option>
              <option value="1:1">1:1 (Square Feed Format)</option>
            </select>
          </div>

          {/* Style */}
          <div className="cinematic-card p-4 bg-[#0B0B0B]">
            <label className="text-[11px] font-mono uppercase tracking-wider text-[#9A9A9A] block mb-2">
              Visual Direction
            </label>
            <input
              type="text"
              value={style || "animated historical documentary"}
              onChange={(e) => setStyle && setStyle(e.target.value)}
              className="cinematic-input"
              placeholder="e.g. animated historical documentary"
            />
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-3 mb-6">
            <AlertCircleIcon className="w-4 h-4 flex-shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Primary Action Dock */}
      <div className="pt-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* AI Provider Info */}
        <div className="flex items-center gap-3 text-xs text-[#9A9A9A]">
          <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
          <span>Engine: <strong className="text-[#F5F2EA]">{aiConfig?.provider === "openai" ? "OpenAI API" : "Local Ollama"}</strong></span>
          <span className="text-white/20">·</span>
          <span className="font-mono text-[11px]">{aiConfig?.model || "qwen2.5:7b"}</span>
        </div>

        {/* Generate Plan Button */}
        <div className="flex items-center gap-3 w-full sm:w-auto">
          {draftPlan && (
            <button
              type="button"
              onClick={() => setActiveTab("scenes")}
              className="btn-secondary flex-1 sm:flex-initial"
            >
              View Scene Timeline ({draftPlan.scenes.length})
            </button>
          )}

          <button
            type="button"
            onClick={onGeneratePlan}
            disabled={loading || script.trim().length < 20}
            className="btn-primary py-3 px-6 text-sm flex-1 sm:flex-initial justify-center"
          >
            {loading ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Architecting Scenes…</span>
              </>
            ) : (
              <span>Generate Scene Plan</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

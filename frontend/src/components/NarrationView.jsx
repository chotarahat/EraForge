import React from "react";
import { AudioIcon, AlertCircleIcon, WaveformIcon, CheckCircleIcon } from "./Icons";

const API_URL = "http://127.0.0.1:8000";

export function NarrationView({
  narrationPlan,
  narrationManifest,
  narrationVoices,
  selectedVoice,
  setSelectedVoice,
  rate,
  setRate,
  volume,
  setVolume,
  loading,
  error,
  onGenerateNarration,
  draftPlan,
}) {
  const segments = narrationPlan?.segments || [];
  const manifestMap = new Map(
    (narrationManifest?.segments || []).map((seg) => [seg.scene_id, seg])
  );

  return (
    <div className="flex-1 p-6 sm:p-10 max-w-6xl mx-auto w-full flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-6 border-b border-white/5">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-[#FF5A1F] mb-1.5">
              <AudioIcon className="w-3.5 h-3.5" />
              <span>Voice Narration & Synthesis</span>
            </div>
            <h1 className="font-serif text-3xl font-medium tracking-tight text-[#F5F2EA]">
              Voice Narration
            </h1>
            <p className="text-xs text-[#9A9A9A] mt-1">
              Synthesize offline text-to-speech WAV tracks using local neural/system voices with timing alignment.
            </p>
          </div>

          <button
            onClick={onGenerateNarration}
            disabled={loading || !draftPlan?.scenes?.length}
            className="btn-primary text-xs"
          >
            {loading ? "Synthesizing Speech…" : "Generate Narration"}
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-3 mb-6">
            <AlertCircleIcon className="w-4 h-4 flex-shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        {/* Voice Parameters Console */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {/* Voice Dropdown */}
          <div className="cinematic-card p-4 bg-[#090909]">
            <label className="text-[11px] font-mono uppercase tracking-wider text-[#9A9A9A] block mb-2">
              System Voice
            </label>
            <select
              value={selectedVoice}
              onChange={(e) => setSelectedVoice(e.target.value)}
              className="cinematic-select"
            >
              {narrationVoices?.length > 0 ? (
                narrationVoices.map((voice) => (
                  <option key={voice.id} value={voice.id}>
                    {voice.name || voice.id}
                  </option>
                ))
              ) : (
                <option value="">Default System Voice</option>
              )}
            </select>
          </div>

          {/* Rate Slider */}
          <div className="cinematic-card p-4 bg-[#090909]">
            <div className="flex items-center justify-between mb-2">
              <label className="text-[11px] font-mono uppercase tracking-wider text-[#9A9A9A]">
                Speech Rate
              </label>
              <span className="text-xs font-mono text-[#F5F2EA]">{rate} WPM</span>
            </div>
            <input
              type="range"
              min="80"
              max="260"
              step="5"
              value={rate}
              onChange={(e) => setRate(Number(e.target.value))}
              className="w-full accent-[#FF5A1F] cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-[#666666] font-mono mt-1">
              <span>Slow</span>
              <span>170 (Normal)</span>
              <span>Fast</span>
            </div>
          </div>

          {/* Volume Slider */}
          <div className="cinematic-card p-4 bg-[#090909]">
            <div className="flex items-center justify-between mb-2">
              <label className="text-[11px] font-mono uppercase tracking-wider text-[#9A9A9A]">
                Audio Volume
              </label>
              <span className="text-xs font-mono text-[#F5F2EA]">{Math.round(volume * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.1"
              max="1"
              step="0.05"
              value={volume}
              onChange={(e) => setVolume(Number(e.target.value))}
              className="w-full accent-[#FF5A1F] cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-[#666666] font-mono mt-1">
              <span>Quiet</span>
              <span>Full</span>
            </div>
          </div>
        </div>

        {/* Audio Waveform Placeholder Bar */}
        <div className="h-12 px-6 rounded-xl bg-[#090909] border border-white/5 flex items-center justify-between gap-1 mb-8 overflow-hidden">
          <div className="flex items-center gap-1.5 text-xs text-[#9A9A9A] font-mono">
            <WaveformIcon className="w-4 h-4 text-[#FF5A1F]" />
            <span>Master Audio Channel</span>
          </div>
          <div className="flex items-center gap-1 h-6">
            {[40, 70, 30, 85, 60, 45, 95, 30, 60, 80, 50, 65, 40, 75, 90, 35, 60, 85, 45, 70].map((h, i) => (
              <span
                key={i}
                className="w-1 bg-[#FF5A1F]/40 rounded-full"
                style={{ height: `${h}%` }}
              />
            ))}
          </div>
        </div>

        {/* Segments Audio List */}
        {segments.length > 0 ? (
          <div className="space-y-3">
            <div className="text-[11px] font-mono uppercase tracking-wider text-[#9A9A9A] pb-2 border-b border-white/5">
              Audio Tracks by Scene ({segments.length})
            </div>

            {segments.map((seg, index) => {
              const manifestSeg = manifestMap.get(seg.scene_id);
              const filename = seg.audio_file ? seg.audio_file.split(/[\\/]/).pop() : null;
              const fits = manifestSeg ? manifestSeg.fits_scene : true;

              return (
                <div
                  key={seg.scene_id || index}
                  className="p-4 rounded-xl bg-[#090909] border border-white/5 hover:border-white/15 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1 max-w-lg">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-[#FF5A1F]">
                        SCENE {(index + 1).toString().padStart(2, "0")}
                      </span>
                      {fits ? (
                        <span className="badge badge-success text-[10px]">Timing Aligned</span>
                      ) : (
                        <span className="badge badge-warning text-[10px]">Audio Exceeds Scene</span>
                      )}
                    </div>
                    <p className="text-xs text-[#F5F2EA] italic">"{seg.text}"</p>
                    <div className="text-[11px] font-mono text-[#666666]">
                      Duration: {seg.duration_seconds.toFixed(2)}s
                    </div>
                  </div>

                  {filename && (
                    <div className="flex items-center gap-3">
                      <audio
                        controls
                        src={`${API_URL}/api/narration/file/${encodeURIComponent(filename)}`}
                        className="h-8 max-w-[240px] accent-[#FF5A1F]"
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="cinematic-card p-12 text-center max-w-md mx-auto my-8 bg-[#090909] border-white/5">
            <div className="w-10 h-10 rounded-full bg-[#FF5A1F]/10 border border-[#FF5A1F]/30 flex items-center justify-center text-[#FF5A1F] mx-auto mb-3">
              <AudioIcon className="w-5 h-5" />
            </div>
            <p className="text-xs text-[#9A9A9A] mb-4">
              No voice tracks synthesized yet. Click "Generate Narration" to synthesize speech for all timeline scenes.
            </p>
            {draftPlan && (
              <button
                onClick={onGenerateNarration}
                disabled={loading}
                className="btn-primary text-xs"
              >
                Synthesize Narration Now
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

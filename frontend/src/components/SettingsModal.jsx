import React from "react";
import { SettingsIcon, CloseIcon, CheckCircleIcon } from "./Icons";

export function SettingsModal({ isOpen, onClose, aiConfig }) {
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content max-w-md" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="p-6 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#FF5A1F]/10 border border-[#FF5A1F]/30 flex items-center justify-center text-[#FF5A1F]">
              <SettingsIcon className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-serif text-xl font-medium text-[#F5F2EA]">Studio Settings</h2>
              <p className="text-xs text-[#9A9A9A]">AI provider and system configuration</p>
            </div>
          </div>

          <button onClick={onClose} className="btn-icon">
            <CloseIcon className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 text-xs">
          <div className="p-4 rounded-xl bg-[#070707] border border-white/5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[#9A9A9A]">Backend Status</span>
              <span className="flex items-center gap-1.5 text-emerald-400 font-mono font-medium">
                <CheckCircleIcon className="w-3.5 h-3.5" /> Online (v0.1.0)
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-[#9A9A9A]">Active AI Engine</span>
              <span className="font-mono text-[#F5F2EA] capitalize">
                {aiConfig?.provider || "Ollama (Local)"}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-[#9A9A9A]">Configured Model</span>
              <span className="font-mono text-[#FF5A1F]">
                {aiConfig?.model || "qwen2.5:7b"}
              </span>
            </div>
          </div>

          <div className="text-[11px] text-[#666666] leading-relaxed">
            AI providers are configured via <code className="text-[#9A9A9A]">backend/.env</code>. To use OpenAI instead of Ollama, set <code className="text-[#9A9A9A]">AI_PROVIDER=openai</code> and your API key.
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-white/5 flex justify-end bg-[#070707]">
          <button onClick={onClose} className="btn-secondary text-xs py-1.5 px-4">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

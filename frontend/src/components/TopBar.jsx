import React from "react";
import {
  LogoIcon,
  SaveIcon,
  PreviewIcon,
  ExportIcon,
  SettingsIcon,
  GithubIcon,
  CheckCircleIcon,
  AlertCircleIcon,
} from "./Icons";

export function TopBar({
  currentProject,
  draftPlan,
  timelineErrors,
  hasUnsavedChanges,
  activeTab,
  setActiveTab,
  onSaveProject,
  projectLoading,
  onOpenProjectsModal,
  onOpenSettingsModal,
  aiConfig,
}) {
  return (
    <header className="top-bar">
      {/* Left: Brand & Project Name */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => setActiveTab("story")}>
          <div className="w-8 h-8 rounded-lg bg-[#FF5A1F]/10 border border-[#FF5A1F]/30 flex items-center justify-center text-[#FF5A1F]">
            <LogoIcon className="w-4 h-4" />
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="font-serif text-lg font-bold tracking-tight text-[#F5F2EA]">EraForge</span>
            <span className="text-[10px] uppercase font-mono tracking-widest text-[#9A9A9A] border border-white/10 px-1.5 py-0.2 rounded">
              v0.1.0
            </span>
          </div>
        </div>

        <div className="h-4 w-px bg-white/10 hidden sm:block" />

        {/* Project Selector Pill */}
        <button
          onClick={onOpenProjectsModal}
          className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.04] border border-white/10 hover:border-white/20 transition-all text-xs text-[#F5F2EA] max-w-[200px] truncate"
          title="Switch or manage projects"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-[#FF5A1F]" />
          <span className="truncate font-medium">{currentProject?.name || "Untitled Project"}</span>
        </button>
      </div>

      {/* Center: Workflow / Status Indicator */}
      <div className="hidden md:flex items-center gap-2">
        {draftPlan ? (
          <div className="flex items-center gap-3 px-3 py-1 rounded-full bg-[#111111] border border-white/10 text-xs">
            <span className="text-[#9A9A9A]">
              {draftPlan.scenes.length} Scenes · {draftPlan.total_duration.toFixed(1)}s ({draftPlan.aspect_ratio || "9:16"})
            </span>
            <span className="w-px h-3 bg-white/10" />
            {timelineErrors.length === 0 ? (
              <span className="flex items-center gap-1.5 text-emerald-400 font-medium text-[11px]">
                <CheckCircleIcon className="w-3.5 h-3.5" /> Timeline Valid
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-amber-400 font-medium text-[11px]">
                <AlertCircleIcon className="w-3.5 h-3.5" /> {timelineErrors.length} Issue{timelineErrors.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>
        ) : (
          <div className="text-xs text-[#9A9A9A] font-mono tracking-wider uppercase">
            Story Studio · Standby
          </div>
        )}
      </div>

      {/* Right: Quick Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={onSaveProject}
          disabled={projectLoading || !currentProject || !draftPlan}
          className={`btn-secondary text-xs py-1.5 px-3 ${
            hasUnsavedChanges ? "border-[#FF5A1F]/50 text-[#FF5A1F] shadow-[0_0_12px_rgba(255,90,31,0.2)]" : ""
          }`}
          title="Save project (persists to local disk)"
        >
          <SaveIcon className="w-3.5 h-3.5" />
          <span>Save{hasUnsavedChanges ? " *" : ""}</span>
        </button>

        <button
          onClick={() => setActiveTab("preview")}
          className={`btn-secondary text-xs py-1.5 px-3 ${activeTab === "preview" ? "border-white/40 text-white" : ""}`}
          title="Open Video Preview"
        >
          <PreviewIcon className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Preview</span>
        </button>

        <button
          onClick={() => setActiveTab("export")}
          className="btn-primary text-xs py-1.5 px-3.5"
          title="Export MP4 Video"
        >
          <ExportIcon className="w-3.5 h-3.5" />
          <span>Export</span>
        </button>

        <div className="h-4 w-px bg-white/10 mx-1 hidden sm:block" />

        <button
          onClick={onOpenSettingsModal}
          className="btn-icon"
          title={`Settings · AI Provider: ${aiConfig?.provider || "Ollama"} (${aiConfig?.model || "qwen2.5:7b"})`}
        >
          <SettingsIcon className="w-4 h-4" />
        </button>

        <a
          href="https://github.com/chotarahat/EraForge"
          target="_blank"
          rel="noreferrer"
          className="btn-icon"
          title="GitHub Repository"
        >
          <GithubIcon className="w-4 h-4" />
        </a>
      </div>
    </header>
  );
}

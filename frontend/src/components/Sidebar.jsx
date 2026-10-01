import React from "react";
import {
  PlusIcon,
  ProjectIcon,
  ScriptIcon,
  ScenesIcon,
  PreviewIcon,
  AssetsIcon,
  MapIcon,
  AudioIcon,
  SubtitleIcon,
  ExportIcon,
  SettingsIcon,
  GithubIcon,
  InfoIcon,
} from "./Icons";

export function Sidebar({
  activeTab,
  setActiveTab,
  currentProject,
  projects,
  onNewProject,
  onOpenProjectsModal,
  onOpenSettingsModal,
  aiConfig,
  draftPlan,
}) {
  const workflowTabs = [
    { id: "story", label: "Story", icon: ScriptIcon, badge: null },
    { id: "scenes", label: "Scenes", icon: ScenesIcon, badge: draftPlan ? draftPlan.scenes.length : null },
    { id: "preview", label: "Preview", icon: PreviewIcon, badge: null },
    { id: "assets", label: "Assets", icon: AssetsIcon, badge: null },
    { id: "geography", label: "Geography", icon: MapIcon, badge: null },
    { id: "narration", label: "Narration", icon: AudioIcon, badge: null },
    { id: "subtitles", label: "Subtitles", icon: SubtitleIcon, badge: null },
    { id: "export", label: "Export", icon: ExportIcon, badge: null },
  ];

  return (
    <aside className="project-sidebar py-4 px-3 flex flex-col justify-between">
      <div className="flex flex-col gap-6">
        {/* PROJECT SECTION */}
        <div>
          <div className="text-[10px] font-mono uppercase tracking-widest text-[#9A9A9A] px-2 mb-2">
            Project
          </div>

          <div className="space-y-1">
            <button
              onClick={onNewProject}
              className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-xs font-medium text-[#F5F2EA] bg-white/[0.03] hover:bg-white/[0.08] border border-white/5 hover:border-white/15 transition-all group"
            >
              <PlusIcon className="w-3.5 h-3.5 text-[#FF5A1F] group-hover:scale-110 transition-transform" />
              <span>New Project</span>
            </button>

            <button
              onClick={onOpenProjectsModal}
              className="w-full flex items-center justify-between px-2.5 py-2 rounded-lg text-xs text-[#9A9A9A] hover:text-[#F5F2EA] hover:bg-white/[0.03] transition-all"
            >
              <div className="flex items-center gap-2.5">
                <ProjectIcon className="w-3.5 h-3.5 text-[#9A9A9A]" />
                <span>Archive</span>
              </div>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 border border-white/5 text-[#9A9A9A]">
                {projects.length}
              </span>
            </button>
          </div>
        </div>

        {/* WORKFLOW SECTION */}
        <div>
          <div className="text-[10px] font-mono uppercase tracking-widest text-[#9A9A9A] px-2 mb-2">
            Workflow
          </div>

          <nav className="space-y-0.5">
            {workflowTabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center justify-between px-2.5 py-2 rounded-lg text-xs transition-all relative ${
                    isActive
                      ? "bg-[#161616] text-[#F5F2EA] font-medium border border-white/10 shadow-[0_2px_12px_rgba(0,0,0,0.5)]"
                      : "text-[#9A9A9A] hover:text-[#F5F2EA] hover:bg-white/[0.03]"
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    {isActive && (
                      <span className="absolute left-0 top-1.5 bottom-1.5 w-[3px] bg-[#FF5A1F] rounded-r shadow-[0_0_8px_var(--accent-glow)]" />
                    )}
                    <Icon className={`w-3.5 h-3.5 ${isActive ? "text-[#FF5A1F]" : "text-[#9A9A9A]"}`} />
                    <span>{tab.label}</span>
                  </div>

                  {tab.badge !== null && (
                    <span
                      className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                        isActive
                          ? "bg-[#FF5A1F]/20 text-[#FF5A1F] border border-[#FF5A1F]/30"
                          : "bg-white/5 text-[#9A9A9A]"
                      }`}
                    >
                      {tab.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* SYSTEM & UTILITY SECTION */}
      <div className="pt-4 border-t border-white/5 space-y-2">
        {/* Local AI status card */}
        <div
          onClick={onOpenSettingsModal}
          className="p-2.5 rounded-xl bg-[#070707] border border-white/5 hover:border-white/15 transition-all cursor-pointer group"
          title="Click to configure AI settings"
        >
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] uppercase font-mono tracking-wider text-[#9A9A9A]">AI Engine</span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.7)]" />
          </div>
          <div className="text-xs font-medium text-[#F5F2EA] truncate">
            {aiConfig?.provider === "openai" ? "OpenAI" : "Ollama (Local)"}
          </div>
          <div className="text-[10px] font-mono text-[#666666] truncate">
            {aiConfig?.model || "qwen2.5:7b"}
          </div>
        </div>

        {/* Footer links */}
        <div className="flex items-center justify-between px-2 pt-1 text-[11px] text-[#666666]">
          <button onClick={onOpenSettingsModal} className="hover:text-[#F5F2EA] transition-colors">
            Settings
          </button>
          <span>·</span>
          <a
            href="https://github.com/chotarahat/EraForge#readme"
            target="_blank"
            rel="noreferrer"
            className="hover:text-[#F5F2EA] transition-colors"
          >
            Docs
          </a>
          <span>·</span>
          <a
            href="https://github.com/chotarahat/EraForge"
            target="_blank"
            rel="noreferrer"
            className="hover:text-[#F5F2EA] transition-colors"
          >
            v0.1
          </a>
        </div>
      </div>
    </aside>
  );
}

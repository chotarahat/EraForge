import React, { useState } from "react";
import { ProjectIcon, PlusIcon, TrashIcon, CloseIcon } from "./Icons";

export function ProjectModal({
  isOpen,
  onClose,
  projects,
  currentProject,
  onOpenProject,
  onCreateProject,
  onRemoveProject,
  projectLoading,
  projectError,
}) {
  const [newProjectName, setNewProjectName] = useState("");

  if (!isOpen) return null;

  const handleCreate = (e) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    onCreateProject(newProjectName.trim());
    setNewProjectName("");
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="p-6 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#FF5A1F]/10 border border-[#FF5A1F]/30 flex items-center justify-center text-[#FF5A1F]">
              <ProjectIcon className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-serif text-xl font-medium text-[#F5F2EA]">Project Archive</h2>
              <p className="text-xs text-[#9A9A9A]">Local persistent history projects on this machine</p>
            </div>
          </div>

          <button onClick={onClose} className="btn-icon">
            <CloseIcon className="w-4 h-4" />
          </button>
        </div>

        {/* Create Project Form */}
        <form onSubmit={handleCreate} className="p-6 border-b border-white/5 bg-[#070707] flex gap-3">
          <input
            type="text"
            value={newProjectName}
            onChange={(e) => setNewProjectName(e.target.value)}
            placeholder="Enter new project title..."
            className="cinematic-input text-xs"
          />
          <button
            type="submit"
            disabled={!newProjectName.trim() || projectLoading}
            className="btn-primary text-xs py-2 px-4 whitespace-nowrap"
          >
            <PlusIcon className="w-3.5 h-3.5" />
            <span>Create</span>
          </button>
        </form>

        {projectError && (
          <div className="mx-6 mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-xs">
            {projectError}
          </div>
        )}

        {/* Project List */}
        <div className="p-6 overflow-y-auto max-h-[420px] space-y-3">
          {projects?.length > 0 ? (
            projects.map((project) => {
              const isActive = currentProject?.id === project.id;
              const dateStr = new Date(project.updated_at).toLocaleString();

              return (
                <div
                  key={project.id}
                  className={`p-4 rounded-xl border transition-all flex items-center justify-between gap-4 ${
                    isActive
                      ? "bg-[#141414] border-[#FF5A1F]/60 shadow-[0_2px_16px_var(--accent-glow)]"
                      : "bg-[#090909] border-white/5 hover:border-white/15"
                  }`}
                >
                  <div className="space-y-1 truncate">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-[#F5F2EA] truncate">
                        {project.name}
                      </span>
                      {isActive && (
                        <span className="badge badge-accent text-[9px]">Active</span>
                      )}
                    </div>
                    <div className="text-[11px] font-mono text-[#666666]">
                      Last updated {dateStr}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        onOpenProject(project.id);
                        onClose();
                      }}
                      disabled={projectLoading}
                      className="btn-secondary text-xs py-1.5 px-3"
                    >
                      {isActive ? "Reload" : "Open"}
                    </button>
                    <button
                      onClick={() => onRemoveProject(project.id)}
                      disabled={projectLoading}
                      className="btn-icon text-[#9A9A9A] hover:text-red-400 hover:bg-red-500/10"
                      title="Delete project"
                    >
                      <TrashIcon className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="text-center py-12 text-[#666666] text-xs">
              No saved projects yet. Create one above to begin.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

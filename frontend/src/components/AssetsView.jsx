import React, { useState } from "react";
import { AssetsIcon, AlertCircleIcon, CheckCircleIcon } from "./Icons";

export function AssetsView({
  assetPlan,
  assetResolution,
  assetLoading,
  assetResolving,
  assetError,
  onRefreshAssetPlan,
  onResolveAssets,
  draftPlan,
}) {
  const [selectedCategory, setSelectedCategory] = useState("all");

  const categories = [
    { id: "all", label: "All Assets" },
    { id: "character", label: "Characters" },
    { id: "landmark", label: "Landmarks" },
    { id: "location", label: "Locations" },
    { id: "illustration", label: "Illustrations" },
    { id: "map", label: "Maps" },
    { id: "background", label: "Backgrounds" },
  ];

  const assetsToDisplay = assetPlan.filter((asset) => {
    if (selectedCategory === "all") return true;
    return asset.type?.toLowerCase() === selectedCategory;
  });

  const resolvedCount = assetResolution?.resolved?.length || 0;
  const missingCount = assetResolution?.missing?.length || 0;
  const placeholderCount = assetResolution?.placeholders?.length || 0;

  return (
    <div className="flex-1 p-6 sm:p-10 max-w-6xl mx-auto w-full flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-6 border-b border-white/5">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-[#FF5A1F] mb-1.5">
              <AssetsIcon className="w-3.5 h-3.5" />
              <span>Asset Manifest & Library</span>
            </div>
            <h1 className="font-serif text-3xl font-medium tracking-tight text-[#F5F2EA]">
              Visual Assets
            </h1>
            <p className="text-xs text-[#9A9A9A] mt-1">
              Extract visual requirements from scene hints and resolve against local media files in <code className="text-[#F5F2EA]">backend/assets/</code>.
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={() => onRefreshAssetPlan(draftPlan)}
              disabled={assetLoading || !draftPlan}
              className="btn-secondary text-xs"
            >
              {assetLoading ? "Planning…" : "Re-Plan Assets"}
            </button>
            <button
              onClick={() => onResolveAssets(draftPlan)}
              disabled={assetResolving || !draftPlan}
              className="btn-primary text-xs"
            >
              {assetResolving ? "Resolving…" : "Resolve Local Library"}
            </button>
          </div>
        </div>

        {/* Error Alert */}
        {assetError && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-3 mb-6">
            <AlertCircleIcon className="w-4 h-4 flex-shrink-0 text-red-400" />
            <span>{assetError}</span>
          </div>
        )}

        {/* Resolution Status Summary Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
          <div className="p-3.5 rounded-xl bg-[#090909] border border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircleIcon className="w-4 h-4 text-emerald-400" />
              <span className="text-xs text-[#9A9A9A]">Resolved Locally</span>
            </div>
            <span className="text-sm font-mono font-bold text-emerald-400">{resolvedCount}</span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#090909] border border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircleIcon className="w-4 h-4 text-amber-400" />
              <span className="text-xs text-[#9A9A9A]">Missing Media</span>
            </div>
            <span className="text-sm font-mono font-bold text-amber-400">{missingCount}</span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#090909] border border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-400" />
              <span className="text-xs text-[#9A9A9A]">Active Placeholders</span>
            </div>
            <span className="text-sm font-mono font-bold text-blue-400">{placeholderCount}</span>
          </div>
        </div>

        {/* Category Filter Pills */}
        <div className="flex items-center gap-2 pb-4 overflow-x-auto mb-6 border-b border-white/5">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                selectedCategory === cat.id
                  ? "bg-[#FF5A1F] text-white shadow-[0_0_12px_rgba(255,90,31,0.3)]"
                  : "bg-white/5 text-[#9A9A9A] hover:text-[#F5F2EA] hover:bg-white/10"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Asset Cards Grid */}
        {assetsToDisplay.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {assetsToDisplay.map((asset) => {
              const isResolved = assetResolution?.resolved?.some(
                (r) => r.id === asset.id || r.name.toLowerCase() === asset.name.toLowerCase()
              );
              const isMissing = assetResolution?.missing?.some(
                (m) => m.name.toLowerCase() === asset.name.toLowerCase()
              );

              return (
                <div
                  key={asset.id}
                  className="cinematic-card p-4 bg-[#090909] border-white/5 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span className="badge badge-muted text-[10px]">{asset.type}</span>
                      {isResolved ? (
                        <span className="badge badge-success text-[10px]">Resolved</span>
                      ) : isMissing ? (
                        <span className="badge badge-warning text-[10px]">Placeholder</span>
                      ) : (
                        <span className="badge bg-white/5 text-[#666666] text-[10px]">Required</span>
                      )}
                    </div>

                    <h3 className="text-sm font-medium text-[#F5F2EA] truncate mb-1" title={asset.name}>
                      {asset.name}
                    </h3>
                    <div className="text-[10px] font-mono text-[#666666] truncate">{asset.id}</div>
                  </div>

                  <div className="pt-3 mt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-[#9A9A9A]">
                    <span>Used in:</span>
                    <div className="flex flex-wrap gap-1">
                      {asset.metadata?.scene_ids?.map((id) => (
                        <span key={id} className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-[#F5F2EA]">
                          {id}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="cinematic-card p-12 text-center max-w-md mx-auto my-8 bg-[#090909] border-white/5">
            <p className="text-xs text-[#9A9A9A] mb-4">
              {draftPlan
                ? "No assets match the selected filter category."
                : "Generate a scene plan to detect asset requirements."}
            </p>
            {draftPlan && (
              <button
                onClick={() => onRefreshAssetPlan(draftPlan)}
                className="btn-secondary text-xs"
              >
                Scan Assets Now
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

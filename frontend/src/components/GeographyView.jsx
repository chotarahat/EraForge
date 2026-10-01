import React from "react";
import { MapIcon, AlertCircleIcon } from "./Icons";

export function GeographyView({
  geographyPlan,
  geographyLoading,
  geographyError,
  onPlanGeography,
  draftPlan,
}) {
  const scenesWithGeo = draftPlan?.scenes?.filter(
    (scene) => geographyPlan[scene.id]?.enabled
  ) || [];

  return (
    <div className="flex-1 p-6 sm:p-10 max-w-6xl mx-auto w-full flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-6 border-b border-white/5">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-[#FF5A1F] mb-1.5">
              <MapIcon className="w-3.5 h-3.5" />
              <span>Historical Geography & Cartography</span>
            </div>
            <h1 className="font-serif text-3xl font-medium tracking-tight text-[#F5F2EA]">
              Geographic Operations
            </h1>
            <p className="text-xs text-[#9A9A9A] mt-1">
              Automatic territory extraction, geospatial centering, and dynamic camera pan/zoom sequences.
            </p>
          </div>

          <button
            onClick={() => onPlanGeography(draftPlan)}
            disabled={geographyLoading || !draftPlan}
            className="btn-primary text-xs"
          >
            {geographyLoading ? "Detecting Coordinates…" : "Plan Geography"}
          </button>
        </div>

        {/* Error Alert */}
        {geographyError && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-3 mb-6">
            <AlertCircleIcon className="w-4 h-4 flex-shrink-0 text-red-400" />
            <span>{geographyError}</span>
          </div>
        )}

        {scenesWithGeo.length > 0 ? (
          <div className="space-y-6">
            {/* Visual Cartographic Radar Canvas */}
            <div className="cinematic-card p-6 bg-[#070707] border-white/10 rounded-2xl relative overflow-hidden flex flex-col items-center justify-center min-h-[220px]">
              {/* Decorative Geospatial Lat/Long Grid Lines */}
              <div
                className="absolute inset-0 opacity-10 pointer-events-none"
                style={{
                  backgroundImage:
                    "radial-gradient(circle, #FF5A1F 1px, transparent 1px), linear-gradient(to right, #333 1px, transparent 1px), linear-gradient(to bottom, #333 1px, transparent 1px)",
                  backgroundSize: "24px 24px, 48px 48px, 48px 48px",
                }}
              />

              <div className="relative z-10 text-center">
                <div className="w-10 h-10 rounded-full bg-[#FF5A1F]/10 border border-[#FF5A1F]/30 flex items-center justify-center text-[#FF5A1F] mx-auto mb-3 shadow-[0_0_20px_var(--accent-glow)]">
                  <MapIcon className="w-5 h-5" />
                </div>
                <div className="text-sm font-medium text-[#F5F2EA] mb-1">
                  Active Geospatial Matrix
                </div>
                <div className="text-xs text-[#9A9A9A] font-mono">
                  {scenesWithGeo.length} scene{scenesWithGeo.length !== 1 ? "s" : ""} configured with geographical camera movements
                </div>
              </div>
            </div>

            {/* Per-Scene Geographic Specifications */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {scenesWithGeo.map((scene) => {
                const geo = geographyPlan[scene.id];

                return (
                  <div
                    key={scene.id}
                    className="cinematic-card p-5 bg-[#090909] border-white/5 space-y-4"
                  >
                    <div className="flex items-center justify-between pb-3 border-b border-white/5">
                      <div>
                        <span className="text-[10px] font-mono text-[#FF5A1F] uppercase tracking-wider">
                          {scene.id}
                        </span>
                        <h3 className="text-sm font-medium text-[#F5F2EA] truncate max-w-[200px]">
                          {scene.title}
                        </h3>
                      </div>
                      <span className="badge badge-accent text-[10px]">
                        Zoom {geo.zoom_level}x
                      </span>
                    </div>

                    {/* Coordinates & Center */}
                    {geo.center && (
                      <div className="flex items-center justify-between text-xs bg-white/[0.02] p-2.5 rounded-lg border border-white/5 font-mono">
                        <span className="text-[#9A9A9A]">Centroid:</span>
                        <span className="text-[#F5F2EA]">
                          {geo.center.latitude.toFixed(3)}°N, {geo.center.longitude.toFixed(3)}°E
                        </span>
                      </div>
                    )}

                    {/* Regions */}
                    {geo.regions?.length > 0 && (
                      <div>
                        <span className="text-[10px] font-mono uppercase text-[#666666] block mb-1.5">
                          Active Regions
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {geo.regions.map((reg) => (
                            <span key={reg.id} className="badge badge-muted text-[11px]">
                              {reg.name}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Scheduled Camera / Map Operations */}
                    {geo.operations?.length > 0 && (
                      <div>
                        <span className="text-[10px] font-mono uppercase text-[#666666] block mb-1.5">
                          Operations Sequence
                        </span>
                        <div className="space-y-1.5">
                          {geo.operations.map((op, i) => (
                            <div
                              key={i}
                              className="text-xs p-2 rounded bg-white/[0.03] border border-white/5 flex items-center justify-between"
                            >
                              <span className="text-[#F5F2EA] font-mono capitalize">
                                {op.type.replace(/_/g, " ")}
                              </span>
                              <span className="text-[10px] font-mono text-[#9A9A9A]">
                                {op.duration}s
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="cinematic-card p-12 text-center max-w-md mx-auto my-8 bg-[#090909] border-white/5">
            <div className="w-10 h-10 rounded-full bg-[#FF5A1F]/10 border border-[#FF5A1F]/30 flex items-center justify-center text-[#FF5A1F] mx-auto mb-3">
              <MapIcon className="w-5 h-5" />
            </div>
            <p className="text-xs text-[#9A9A9A] mb-4">
              No historical geographic coordinates detected yet. Click "Plan Geography" to scan scenes for territories, cities, and landmarks.
            </p>
            {draftPlan && (
              <button
                onClick={() => onPlanGeography(draftPlan)}
                disabled={geographyLoading}
                className="btn-primary text-xs"
              >
                Scan Historical Geography
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

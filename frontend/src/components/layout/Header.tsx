import React from 'react';
import { Activity, LayoutGrid, Monitor, Settings } from 'lucide-react';

interface HeaderProps {
  viewMode: 'single' | 'composite';
  setViewMode: (mode: 'single' | 'composite') => void;
  currentLap?: number;
  totalLaps?: number;
  backendOnline: boolean;
  onOpenSettings: () => void;
  glassEffects: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  viewMode,
  setViewMode,
  currentLap = 24,
  totalLaps = 78,
  backendOnline,
  onOpenSettings,
  glassEffects,
}) => {
  return (
    <header className="h-14 border-b border-[#28313D] bg-[#0D1219] flex items-center justify-between px-4 lg:px-6 sticky top-0 z-50">
      <div className="flex items-center space-x-3">
        {/* F1 Style Geometric Emblem */}
        <div className="flex items-center gap-1.5 font-black italic tracking-tighter text-xl text-[#F20D2F]">
          <svg className="w-8 h-5 fill-current" viewBox="0 0 54 24">
            <path d="M0 24L18 0H42L36 8H20L14 16H34L28 24H0Z" fill="#F20D2F" />
            <path d="M46 0H54L36 24H28L46 0Z" fill="#FFFFFF" opacity="0.9" />
          </svg>
        </div>
        <span className="text-sm font-semibold tracking-wide text-white uppercase sm:inline-block font-display">
          Motorsport Strategy Optimizer
        </span>
      </div>

      {/* Center/Right Controls */}
      <div className="flex items-center space-x-3">
        {/* View Mode Selector: Single Focus vs 6-Panel Composite Overview Grid */}
        <div className="bg-[#111821] border border-[#28313D] rounded p-0.5 flex text-xs font-medium">
          <button
            onClick={() => setViewMode('composite')}
            className={`px-2.5 py-1 rounded transition-colors flex items-center gap-1.5 ${
              viewMode === 'composite'
                ? 'bg-[#F20D2F] text-white shadow-md shadow-[#F20D2F]/20'
                : 'text-slate-400 hover:text-white'
            }`}
            title="View 6-Screen Composite Grid"
          >
            <LayoutGrid className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Overview Grid</span>
          </button>
          <button
            onClick={() => setViewMode('single')}
            className={`px-2.5 py-1 rounded transition-colors flex items-center gap-1.5 ${
              viewMode === 'single'
                ? 'bg-[#F20D2F] text-white shadow-md shadow-[#F20D2F]/20'
                : 'text-slate-400 hover:text-white'
            }`}
            title="Focus Single Full Screen"
          >
            <Monitor className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Single Focus</span>
          </button>
        </div>

        {/* Telemetry Status Badge */}
        <div className="hidden md:flex items-center gap-2 px-2.5 py-1 bg-[#111821] border border-[#28313D] rounded text-xs text-slate-300">
          <span
            className={`w-2 h-2 rounded-full ${
              backendOnline ? 'bg-[#16B86A] animate-pulse' : 'bg-amber-400'
            }`}
          />
          <span className="font-mono text-[11px] tabular-nums">
            {backendOnline ? 'LIVE TELEMETRY:' : 'LOCAL MODE:'} {currentLap}/{totalLaps}
          </span>
        </div>

        {/* System Settings Icon */}
        <button
          onClick={onOpenSettings}
          className="p-1.5 hover:bg-[#151D27] rounded text-slate-400 hover:text-white border border-transparent hover:border-[#28313D] transition-colors relative"
          title="Pit-Wall Command Settings"
        >
          <Settings className="w-4 h-4" />
          {glassEffects && (
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 absolute top-1 right-1" title="Glass Effects Active" />
          )}
        </button>
      </div>
    </header>
  );
};


import React from 'react';
import { CircuitConfig, OptimizationResponse, SingleSimulationResult, TireSetInventoryItem } from '../types';
import { TabId } from '../components/layout/Sidebar';
import { Flag, Activity, Disc, Zap, CloudRain, Clock, ExternalLink } from 'lucide-react';

interface OverviewGridProps {
  setActiveTab: (tab: TabId) => void;
  setViewMode: (mode: 'single' | 'composite') => void;
  circuitId: string;
  circuits: Record<string, CircuitConfig>;
  optimizationData: OptimizationResponse | null;
  simulationResult: SingleSimulationResult | null;
}

export const OverviewGrid: React.FC<OverviewGridProps> = ({
  setActiveTab,
  setViewMode,
  circuitId,
  circuits,
  optimizationData,
  simulationResult,
}) => {
  const currentCircuit = circuits[circuitId] || circuits.monaco;

  const navigateTo = (tab: TabId) => {
    setActiveTab(tab);
    setViewMode('single');
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between pb-1 border-b border-[#28313D]">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#F20D2F]" />
          <h2 className="text-base font-bold text-white uppercase tracking-wider font-mono">
            6-Panel Live Command Overview
          </h2>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          Click any panel to enter Single Focus mode
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Panel 1: Race Overview */}
        <div
          onClick={() => navigateTo('overview')}
          className="bg-[#111821] border border-[#28313D] hover:border-[#F20D2F] rounded p-3.5 cursor-pointer transition-all hover:shadow-lg hover:shadow-[#F20D2F]/10 flex flex-col justify-between group h-64"
        >
          <div className="flex items-center justify-between border-b border-[#28313D] pb-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono px-1 rounded bg-[#F20D2F]/20 text-[#F20D2F] font-bold">1</span>
              <span className="text-xs font-bold text-white font-mono uppercase">Race Overview</span>
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-[#F20D2F] transition-colors" />
          </div>

          <div className="py-2 flex items-center justify-between">
            <div>
              <span className="text-[10px] text-slate-400 block font-mono">CIRCUIT</span>
              <span className="text-sm font-bold text-white">{currentCircuit.name}</span>
              <span className="text-[10px] text-slate-400 block mt-1 font-mono">LAP 24 / {currentCircuit.total_laps}</span>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-slate-400 block font-mono">EST. TIME</span>
              <span className="text-base font-bold font-mono text-emerald-400">1:32:15.4</span>
              <span className="text-[10px] text-slate-400 block font-mono mt-1">WEATHER: DRY (32°C)</span>
            </div>
          </div>

          <div className="bg-[#151D27] p-2 rounded border border-[#28313D] flex items-center justify-between text-xs font-mono">
            <span className="text-amber-400 font-bold">MEDIUM C3 (12 LAPS)</span>
            <span className="text-emerald-400">STATUS: GREEN</span>
          </div>
        </div>

        {/* Panel 2: Simulation */}
        <div
          onClick={() => navigateTo('simulation')}
          className="bg-[#111821] border border-[#28313D] hover:border-[#F20D2F] rounded p-3.5 cursor-pointer transition-all hover:shadow-lg hover:shadow-[#F20D2F]/10 flex flex-col justify-between group h-64"
        >
          <div className="flex items-center justify-between border-b border-[#28313D] pb-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono px-1 rounded bg-[#F20D2F]/20 text-[#F20D2F] font-bold">2</span>
              <span className="text-xs font-bold text-white font-mono uppercase">Race Simulation</span>
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-[#F20D2F] transition-colors" />
          </div>

          <div className="py-1">
            <span className="text-[10px] text-slate-400 font-mono block mb-1">STOCHASTIC PACE TRAJECTORY</span>
            <div className="h-28 w-full bg-[#0D1219] rounded p-2 border border-[#28313D] flex items-center justify-center">
              <svg className="w-full h-full" viewBox="0 0 100 40">
                <path d="M 0,25 Q 25,20 50,30 T 100,22" fill="none" stroke="#1677E8" strokeWidth="2" />
                <path d="M 0,24 L 15,22 L 30,28 L 45,35 L 60,20 L 75,22 L 90,26 L 100,24" fill="none" stroke="#F20D2F" strokeWidth="2" />
              </svg>
            </div>
          </div>

          <div className="flex justify-between text-[11px] text-slate-400 font-mono">
            <span>Runs: 1000 CRN</span>
            <span className="text-white font-bold">Pace Var: σ = 0.3s</span>
          </div>
        </div>

        {/* Panel 3: Tire Sets */}
        <div
          onClick={() => navigateTo('tire-sets')}
          className="bg-[#111821] border border-[#28313D] hover:border-[#F20D2F] rounded p-3.5 cursor-pointer transition-all hover:shadow-lg hover:shadow-[#F20D2F]/10 flex flex-col justify-between group h-64"
        >
          <div className="flex items-center justify-between border-b border-[#28313D] pb-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono px-1 rounded bg-[#F20D2F]/20 text-[#F20D2F] font-bold">3</span>
              <span className="text-xs font-bold text-white font-mono uppercase">Tire Sets Inventory</span>
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-[#F20D2F] transition-colors" />
          </div>

          <div className="space-y-1.5 font-mono text-xs py-1">
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-red-400 font-bold">SOFT (C4/C5)</span>
              <span>2 Sets &bull; 0-48% Wear</span>
            </div>
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-amber-400 font-bold">MEDIUM (C3)</span>
              <span className="text-emerald-400 font-bold">FITTED &bull; 35% Wear</span>
            </div>
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-slate-200 font-bold">HARD (C2)</span>
              <span>2 Sets &bull; Fresh (0%)</span>
            </div>
            <div className="flex justify-between items-center text-slate-300">
              <span className="text-emerald-400 font-bold">INTERMEDIATE</span>
              <span>1 Set Available</span>
            </div>
          </div>

          <div className="bg-[#151D27] p-2 rounded border border-[#28313D] text-[10px] text-slate-400 font-mono flex justify-between">
            <span>ALLOCATION STATUS</span>
            <span className="text-emerald-400 font-bold">Pirelli Compliant</span>
          </div>
        </div>

        {/* Panel 4: Strategy Optimization */}
        <div
          onClick={() => navigateTo('strategy')}
          className="bg-[#111821] border border-emerald-500/40 hover:border-emerald-400 rounded p-3.5 cursor-pointer transition-all hover:shadow-lg hover:shadow-emerald-500/10 flex flex-col justify-between group h-64 relative overflow-hidden"
        >
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 via-[#1677E8] to-[#F20D2F]" />
          <div className="flex items-center justify-between border-b border-[#28313D] pb-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono px-1 rounded bg-emerald-500/20 text-emerald-400 font-bold">4</span>
              <span className="text-xs font-bold text-white font-mono uppercase">Optimal Strategy</span>
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-emerald-400 transition-colors" />
          </div>

          <div className="py-1">
            <span className="text-xs font-bold text-white block mb-1">1-Stop (M-H @ Lap 34)</span>
            <div className="h-6 w-full rounded flex overflow-hidden border border-[#28313D] font-mono text-[9px] font-bold text-center leading-6 text-black">
              <div className="bg-amber-400 h-full w-[44%]">M (L1-34)</div>
              <div className="bg-slate-200 h-full w-[56%]">H (L35-78)</div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            <div className="bg-[#151D27] p-1.5 rounded border border-[#28313D]">
              <span className="text-[9px] text-slate-400 block">EXPECTED TIME</span>
              <span className="text-white font-bold">1:31:42</span>
            </div>
            <div className="bg-[#151D27] p-1.5 rounded border border-[#28313D]">
              <span className="text-[9px] text-slate-400 block">STD DEV</span>
              <span className="text-emerald-400 font-bold">±12.6s</span>
            </div>
          </div>
        </div>

        {/* Panel 5: Weather & Risk */}
        <div
          onClick={() => navigateTo('weather')}
          className="bg-[#111821] border border-[#28313D] hover:border-[#F20D2F] rounded p-3.5 cursor-pointer transition-all hover:shadow-lg hover:shadow-[#F20D2F]/10 flex flex-col justify-between group h-64"
        >
          <div className="flex items-center justify-between border-b border-[#28313D] pb-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono px-1 rounded bg-[#F20D2F]/20 text-[#F20D2F] font-bold">5</span>
              <span className="text-xs font-bold text-white font-mono uppercase">Weather &amp; Risk</span>
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-[#F20D2F] transition-colors" />
          </div>

          <div className="py-1">
            <span className="text-[10px] text-slate-400 font-mono block mb-1">RAIN PROBABILITY CURVE</span>
            <div className="h-28 w-full bg-[#0D1219] rounded p-2 border border-[#28313D] flex items-center justify-center">
              <svg className="w-full h-full" viewBox="0 0 100 40">
                <path d="M 0,35 L 20,35 L 35,10 L 45,15 L 60,35 L 80,35 L 90,20 L 100,35" fill="none" stroke="#1677E8" strokeWidth="2" />
              </svg>
            </div>
          </div>

          <div className="flex justify-between text-[11px] text-slate-400 font-mono">
            <span>Peak Risk: Laps 20-28</span>
            <span className="text-cyan-400 font-bold">Markov Model Active</span>
          </div>
        </div>

        {/* Panel 6: Results & History */}
        <div
          onClick={() => navigateTo('results')}
          className="bg-[#111821] border border-[#28313D] hover:border-[#F20D2F] rounded p-3.5 cursor-pointer transition-all hover:shadow-lg hover:shadow-[#F20D2F]/10 flex flex-col justify-between group h-64"
        >
          <div className="flex items-center justify-between border-b border-[#28313D] pb-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono px-1 rounded bg-[#F20D2F]/20 text-[#F20D2F] font-bold">6</span>
              <span className="text-xs font-bold text-white font-mono uppercase">Simulation History</span>
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-[#F20D2F] transition-colors" />
          </div>

          <div className="space-y-2 font-mono text-xs py-1">
            <div className="flex justify-between text-slate-300 border-b border-[#28313D]/50 pb-1">
              <span className="font-bold text-white">RUN-001 (Monaco)</span>
              <span className="text-emerald-400 font-bold">1:31:42</span>
            </div>
            <div className="flex justify-between text-slate-300 border-b border-[#28313D]/50 pb-1">
              <span className="font-bold text-white">RUN-002 (Silverstone)</span>
              <span className="text-white">1:28:15</span>
            </div>
            <div className="flex justify-between text-slate-300">
              <span className="font-bold text-white">RUN-003 (Spa)</span>
              <span className="text-amber-400 font-bold">1:44:22</span>
            </div>
          </div>

          <div className="bg-[#151D27] p-2 rounded border border-[#28313D] text-[10px] text-slate-400 font-mono flex justify-between">
            <span>TOTAL SAVED TRIALS</span>
            <span className="text-white font-bold">5 Experiments</span>
          </div>
        </div>
      </div>
    </div>
  );
};


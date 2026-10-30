import React, { useState } from 'react';
import { CircuitConfig, TireCompound } from '../types';
import { Play, Activity, Sun, CloudRain, AlertTriangle, ShieldCheck, Gauge } from 'lucide-react';

interface RaceOverviewProps {
  circuitId: string;
  setCircuitId: (id: string) => void;
  circuits: Record<string, CircuitConfig>;
  onStartSimulation: () => void;
  isSimulating: boolean;
  backendOnline: boolean;
}

export const RaceOverview: React.FC<RaceOverviewProps> = ({
  circuitId,
  setCircuitId,
  circuits,
  onStartSimulation,
  isSimulating,
  backendOnline,
}) => {
  const currentCircuit = circuits[circuitId] || circuits.monaco || {
    circuit_id: 'monaco',
    name: 'Circuit de Monaco',
    total_laps: 78,
    baseline_lap_time: 73.8,
    circuit_wear_factor: 0.65,
    is_street_circuit: true,
    pit_loss: 21.5,
  };

  const [currentLap, setCurrentLap] = useState<number>(24);
  const totalLaps = currentCircuit.total_laps || 78;
  const progressPercent = Math.min(100, Math.round((currentLap / totalLaps) * 1000) / 10);
  const remainingLaps = totalLaps - currentLap;

  // Track vector configurations
  const renderCircuitSVG = () => {
    switch (circuitId) {
      case 'silverstone':
        return (
          <path
            className="opacity-90 transition-all duration-300"
            d="M 30,50 L 60,30 L 100,35 L 140,20 L 175,45 L 165,75 L 120,85 L 90,65 L 50,85 Z"
          />
        );
      case 'spa':
        return (
          <path
            className="opacity-90 transition-all duration-300"
            d="M 25,35 L 50,25 L 80,45 L 120,40 L 170,20 L 180,60 L 140,85 L 90,80 L 40,75 Z"
          />
        );
      case 'monza':
        return (
          <path
            className="opacity-90 transition-all duration-300"
            d="M 30,70 L 60,30 L 130,25 L 175,40 L 170,75 L 110,75 L 45,75 Z"
          />
        );
      default: // Monaco
        return (
          <path
            className="opacity-90 transition-all duration-300"
            d="M 25,65 L 45,70 L 70,68 C 90,67 105,75 115,70 C 130,62 145,30 160,35 C 172,39 180,50 175,65 C 170,80 150,88 135,85 C 120,83 115,92 100,92 C 85,92 70,80 50,82 C 35,84 20,80 25,65 Z"
          />
        );
    }
  };

  return (
    <section className="view-panel space-y-5" data-purpose="race-overview-screen">
      {/* Subheader Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-[#28313D]">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono px-1.5 py-0.5 rounded bg-[#F20D2F]/20 text-[#F20D2F] font-bold">
              1
            </span>
            <h1 className="text-xl font-bold tracking-tight text-white font-display">Race Overview</h1>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">Live simulation status and key race telemetry</p>
        </div>

        <div className="flex items-center space-x-2.5 text-xs">
          <div className="relative">
            <select
              aria-label="Select Telemetry Stream"
              className="bg-[#111821] text-xs text-slate-200 border border-[#28313D] rounded px-3 py-1.5 focus:outline-none focus:border-[#F20D2F]"
            >
              <option>Live Pit-Wall Stream</option>
              <option>Telemetry Feed (Raw)</option>
              <option>MCTS Stochastic Model</option>
            </select>
          </div>

          <span className="flex items-center gap-1.5 px-2.5 py-1 bg-[#16B86A]/10 text-[#16B86A] border border-[#16B86A]/30 rounded font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-[#16B86A] animate-ping" />
            {backendOnline ? 'Engine Connected' : 'Local Offline Mode'}
          </span>

          <button
            onClick={onStartSimulation}
            disabled={isSimulating}
            className="bg-[#F20D2F] hover:bg-[#d00926] disabled:opacity-50 text-white px-3.5 py-1.5 rounded font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-lg shadow-[#F20D2F]/20"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            {isSimulating ? 'Simulating...' : 'Start Simulation'}
          </button>
        </div>
      </div>

      {/* Upper 3 Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Card A: Circuit */}
        <div className="bg-[#111821] border border-[#28313D] rounded p-4 flex flex-col justify-between hover:border-[#F20D2F]/50 transition-colors">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Circuit</span>
            <select
              aria-label="Select Circuit"
              value={circuitId}
              onChange={(e) => setCircuitId(e.target.value)}
              className="bg-[#151D27] text-xs text-slate-200 border border-[#28313D] rounded px-2.5 py-1 focus:outline-none focus:border-[#F20D2F]"
            >
              {Object.keys(circuits).length > 0 ? (
                Object.values(circuits).map((c) => (
                  <option key={c.circuit_id} value={c.circuit_id}>
                    {c.name}
                  </option>
                ))
              ) : (
                <>
                  <option value="monaco">Circuit de Monaco</option>
                  <option value="silverstone">Silverstone Circuit</option>
                  <option value="spa">Spa-Francorchamps</option>
                  <option value="monza">Monza Autodromo</option>
                </>
              )}
            </select>
          </div>

          {/* Circuit Vector Map */}
          <div className="py-2 flex items-center justify-center">
            <svg
              className="w-48 h-24 stroke-[#F20D2F] fill-none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2.5"
              viewBox="0 0 200 110"
            >
              {renderCircuitSVG()}
              {/* Sector markings / Start line */}
              <line stroke="#FFFFFF" strokeWidth="3" x1="28" x2="28" y1="62" y2="70" />
              <circle cx="160" cy="35" fill="#16B86A" r="3" />
              <circle cx="115" cy="70" fill="#F5C928" r="3" />
            </svg>
          </div>

          {/* Circuit Details */}
          <div className="flex justify-between text-xs pt-2 border-t border-[#28313D]/60 text-slate-400">
            <div>
              <span className="block text-[10px] uppercase font-mono">Lap Distance</span>
              <span className="font-mono text-slate-200 font-semibold text-sm">
                {circuitId === 'spa' ? '7.004 km' : circuitId === 'silverstone' ? '5.891 km' : '3.337 km'}
              </span>
            </div>
            <div className="text-right">
              <span className="block text-[10px] uppercase font-mono">Pit Lane Loss</span>
              <span className="font-mono text-slate-200 font-semibold text-sm">
                ~{currentCircuit.pit_loss.toFixed(1)} s
              </span>
            </div>
          </div>
        </div>

        {/* Card B: Weather */}
        <div className="bg-[#111821] border border-[#28313D] rounded p-4 flex flex-col justify-between hover:border-[#F20D2F]/50 transition-colors">
          <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Weather Condition</span>
          <div className="flex items-center gap-3 py-2">
            <div className="text-yellow-400">
              <Sun className="w-10 h-10 stroke-[1.8]" />
            </div>
            <div>
              <span className="text-base font-semibold text-white">Partly Cloudy</span>
              <span className="block text-xs text-slate-400 font-mono">Track dry with humidity 54%</span>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 pt-2 border-t border-[#28313D]/60 text-xs">
            <div>
              <span className="block text-[10px] text-slate-400 uppercase font-mono">Track Temp</span>
              <span className="font-mono text-slate-100 font-semibold text-sm">32°C</span>
            </div>
            <div>
              <span className="block text-[10px] text-slate-400 uppercase font-mono">Air Temp</span>
              <span className="font-mono text-slate-100 font-semibold text-sm">28°C</span>
            </div>
            <div>
              <span className="block text-[10px] text-slate-400 uppercase font-mono">Rain Prob</span>
              <span className="font-mono text-[#1677E8] font-bold text-sm">15%</span>
            </div>
          </div>
        </div>

        {/* Card C: Current Lap */}
        <div className="bg-[#111821] border border-[#28313D] rounded p-4 flex flex-col justify-between hover:border-[#F20D2F]/50 transition-colors">
          <div className="flex justify-between items-center">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Current Lap</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#151D27] text-slate-300 font-bold border border-[#28313D]">
              STINT 1
            </span>
          </div>

          <div className="py-1">
            <div className="text-3xl font-black font-mono tracking-tight text-white tabular-nums">
              {currentLap} <span className="text-lg text-slate-500 font-normal">/ {totalLaps}</span>
            </div>
            {/* Red filled progress bar */}
            <div className="w-full bg-[#151D27] h-2.5 rounded-full overflow-hidden mt-3 border border-[#28313D]">
              <div
                className="bg-[#F20D2F] h-full rounded-full transition-all duration-500 shadow-sm shadow-[#F20D2F]/50"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>

          <div className="flex justify-between text-[11px] text-slate-400 pt-2 border-t border-[#28313D]/60 font-mono">
            <span>Remaining: {remainingLaps} Laps</span>
            <span className="text-emerald-400 font-medium">On Target ({progressPercent}%)</span>
          </div>
        </div>
      </div>

      {/* Lower 4 KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Current Tire */}
        <div className="bg-[#111821] border border-[#28313D] rounded p-4 flex items-center gap-3 hover:border-slate-600 transition-colors">
          {/* Tire Circular SVG Graphic */}
          <div className="relative w-14 h-14 shrink-0 flex items-center justify-center">
            <svg className="w-14 h-14 transform -rotate-90" viewBox="0 0 36 36">
              <circle cx="18" cy="18" fill="#0D1219" r="14" stroke="#28313D" strokeWidth="4" />
              <circle
                cx="18"
                cy="18"
                fill="none"
                r="14"
                stroke="#F5C928"
                strokeDasharray="88"
                strokeDashoffset="35"
                strokeLinecap="round"
                strokeWidth="4"
              />
            </svg>
            <span className="absolute font-black text-xs font-mono text-[#F5C928]">M</span>
          </div>
          <div className="flex-1 min-w-0">
            <span className="text-xs font-bold text-[#F5C928] uppercase tracking-wide">MEDIUM C3</span>
            <div className="text-[11px] text-slate-400 font-mono mt-0.5">
              <div>Age: <span className="text-slate-200 font-semibold">12 laps</span></div>
              <div>Estimated Life: <span className="text-slate-200 font-semibold">18 laps</span></div>
            </div>
          </div>
        </div>

        {/* KPI 2: Safety Car */}
        <div className="bg-[#111821] border border-[#28313D] rounded p-4 flex items-center gap-3 hover:border-slate-600 transition-colors">
          <div className="w-12 h-12 rounded bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center shrink-0">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
          </div>
          <div>
            <span className="block text-xs font-medium text-slate-400 uppercase font-mono">Safety Car</span>
            <span className="text-sm font-bold text-white">Track Clear</span>
            <span className="block text-[11px] text-emerald-400 font-mono mt-0.5">Status: Green Flag</span>
          </div>
        </div>

        {/* KPI 3: Estimated Race Time */}
        <div className="bg-[#111821] border border-[#28313D] rounded p-4 hover:border-slate-600 transition-colors">
          <span className="block text-xs font-medium text-slate-400 uppercase font-mono">Estimated Race Time</span>
          <div className="text-2xl font-black font-mono text-white tracking-tight mt-1 tabular-nums">
            1:32:15.4
          </div>
          <div className="mt-1">
            <span className="inline-block text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              -2.3s vs baseline
            </span>
          </div>
        </div>

        {/* KPI 4: Pit Stops */}
        <div className="bg-[#111821] border border-[#28313D] rounded p-4 hover:border-slate-600 transition-colors">
          <span className="block text-xs font-medium text-slate-400 uppercase font-mono">Pit Stops</span>
          <div className="text-2xl font-black font-mono text-white tracking-tight mt-1">
            1 Stop
          </div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">
            Optimal Pit Window: <span className="text-slate-200 font-bold">Laps 32 - 36</span>
          </div>
        </div>
      </div>
    </section>
  );
};


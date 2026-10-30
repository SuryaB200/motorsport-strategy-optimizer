import React, { useState } from 'react';
import { HistoricalRunItem } from '../types';
import { Clock, Eye, Download, Search, CheckCircle2, X } from 'lucide-react';

const INITIAL_RUNS: HistoricalRunItem[] = [
  {
    id: '1',
    run_id: 'RUN-001',
    created_at: '2026-10-30 14:23',
    circuit_name: 'Monaco',
    circuit_id: 'monaco',
    total_laps: 78,
    algorithm: 'MCTS',
    simulations_count: 500,
    best_strategy: '1 Stop (M-H @ Lap 34)',
    best_time_formatted: '1:31:42.0',
    best_time_seconds: 5502.0,
    risk_lambda: 0.0,
    status: 'COMPLETED',
  },
  {
    id: '2',
    run_id: 'RUN-002',
    created_at: '2026-10-30 12:11',
    circuit_name: 'Silverstone',
    circuit_id: 'silverstone',
    total_laps: 52,
    algorithm: 'Monte Carlo (CRN)',
    simulations_count: 1000,
    best_strategy: '2 Stop (S-M-M @ 18, 36)',
    best_time_formatted: '1:28:15.2',
    best_time_seconds: 5295.2,
    risk_lambda: 0.5,
    status: 'COMPLETED',
  },
  {
    id: '3',
    run_id: 'RUN-003',
    created_at: '2026-10-29 18:45',
    circuit_name: 'Spa-Francorchamps',
    circuit_id: 'spa',
    total_laps: 44,
    algorithm: 'MCTS',
    simulations_count: 400,
    best_strategy: '1 Stop (M-H @ Lap 22)',
    best_time_formatted: '1:44:22.8',
    best_time_seconds: 6262.8,
    risk_lambda: 1.0,
    status: 'COMPLETED',
  },
  {
    id: '4',
    run_id: 'RUN-004',
    created_at: '2026-10-29 16:02',
    circuit_name: 'Monza',
    circuit_id: 'monza',
    total_laps: 53,
    algorithm: 'Monte Carlo (CRN)',
    simulations_count: 800,
    best_strategy: '1 Stop (S-H @ Lap 24)',
    best_time_formatted: '1:20:11.4',
    best_time_seconds: 4811.4,
    risk_lambda: 0.0,
    status: 'COMPLETED',
  },
  {
    id: '5',
    run_id: 'RUN-005',
    created_at: '2026-10-28 21:37',
    circuit_name: 'Albert Park',
    circuit_id: 'albert_park',
    total_laps: 58,
    algorithm: 'MCTS',
    simulations_count: 600,
    best_strategy: '2 Stop (S-M-H @ 16, 38)',
    best_time_formatted: '1:34:18.9',
    best_time_seconds: 5658.9,
    risk_lambda: 0.2,
    status: 'COMPLETED',
  },
];

export const ResultsHistory: React.FC = () => {
  const [runs, setRuns] = useState<HistoricalRunItem[]>(INITIAL_RUNS);
  const [selectedCircuit, setSelectedCircuit] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [viewedRun, setViewedRun] = useState<HistoricalRunItem | null>(null);

  const filteredRuns = runs.filter((r) => {
    const matchesCircuit = selectedCircuit === 'ALL' || r.circuit_id === selectedCircuit;
    const matchesQuery =
      r.run_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.circuit_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.algorithm.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCircuit && matchesQuery;
  });

  return (
    <section className="view-panel space-y-4" data-purpose="results-and-history-screen">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-[#28313D]">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono px-1.5 py-0.5 rounded bg-[#F20D2F]/20 text-[#F20D2F] font-bold">
              6
            </span>
            <h1 className="text-xl font-bold tracking-tight text-white font-display">Simulation Results</h1>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">Historical catalog of optimization trials and stochastic evaluations</p>
        </div>

        <div className="flex items-center space-x-2">
          <select
            value={selectedCircuit}
            onChange={(e) => setSelectedCircuit(e.target.value)}
            className="bg-[#111821] text-xs text-slate-200 border border-[#28313D] rounded px-3 py-1.5 focus:outline-none focus:border-[#F20D2F]"
          >
            <option value="ALL">All Circuits</option>
            <option value="monaco">Monaco</option>
            <option value="silverstone">Silverstone</option>
            <option value="spa">Spa</option>
            <option value="monza">Monza</option>
            <option value="albert_park">Albert Park</option>
          </select>
        </div>
      </div>

      {/* Search Bar */}
      <div className="flex items-center justify-between bg-[#111821] p-2.5 rounded border border-[#28313D]">
        <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
          <Search className="w-3.5 h-3.5" />
          <span>FILTER HISTORICAL RUNS:</span>
        </div>
        <input
          type="text"
          placeholder="Filter by Run ID or Algorithm..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="bg-[#151D27] border border-[#28313D] rounded px-3 py-1 text-xs text-slate-200 focus:outline-none focus:border-[#F20D2F] w-64 font-mono"
        />
      </div>

      {/* History Table */}
      <div className="bg-[#111821] border border-[#28313D] rounded overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-[#151D27] text-slate-400 uppercase text-[10px] font-mono tracking-wider border-b border-[#28313D]">
            <tr>
              <th className="px-4 py-3">Run ID</th>
              <th className="px-4 py-3">Date &amp; Time</th>
              <th className="px-4 py-3">Circuit</th>
              <th className="px-4 py-3">Algorithm</th>
              <th className="px-4 py-3">Best Strategy</th>
              <th className="px-4 py-3">Expected Time</th>
              <th className="px-4 py-3">Simulations</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#28313D]/70 font-mono">
            {filteredRuns.map((r) => (
              <tr key={r.id} className="hover:bg-[#151D27]/60 transition-colors">
                <td className="px-4 py-3 font-bold text-white flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  {r.run_id}
                </td>
                <td className="px-4 py-3 text-slate-400">{r.created_at}</td>
                <td className="px-4 py-3 text-slate-200 font-semibold">{r.circuit_name}</td>
                <td className="px-4 py-3 text-slate-300">
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 text-[10px] border border-slate-700">
                    {r.algorithm}
                  </span>
                </td>
                <td className="px-4 py-3 font-semibold text-white">{r.best_strategy}</td>
                <td className="px-4 py-3 font-bold text-emerald-400">{r.best_time_formatted}</td>
                <td className="px-4 py-3 text-slate-400">{r.simulations_count} runs</td>
                <td className="px-4 py-3 text-right space-x-2">
                  <button
                    onClick={() => setViewedRun(r)}
                    className="bg-[#F20D2F] hover:bg-[#d00926] text-white px-3 py-1 rounded text-[11px] font-semibold transition-colors"
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Detail Modal */}
      {viewedRun && (
        <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4">
          <div className="bg-[#111821] border border-[#28313D] rounded-lg max-w-lg w-full p-5 space-y-4 shadow-2xl relative">
            <div className="flex justify-between items-center border-b border-[#28313D] pb-3">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-[#16B86A]" />
                <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                  {viewedRun.run_id} &bull; Detailed Telemetry Report
                </h3>
              </div>
              <button
                onClick={() => setViewedRun(null)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="bg-[#151D27] p-2.5 rounded border border-[#28313D]">
                <span className="text-[10px] text-slate-400 block">CIRCUIT</span>
                <span className="text-white font-bold text-sm">{viewedRun.circuit_name}</span>
              </div>
              <div className="bg-[#151D27] p-2.5 rounded border border-[#28313D]">
                <span className="text-[10px] text-slate-400 block">ALGORITHM</span>
                <span className="text-white font-bold text-sm">{viewedRun.algorithm}</span>
              </div>
              <div className="bg-[#151D27] p-2.5 rounded border border-[#28313D]">
                <span className="text-[10px] text-slate-400 block">TOTAL LAPS</span>
                <span className="text-white font-bold text-sm">{viewedRun.total_laps} Laps</span>
              </div>
              <div className="bg-[#151D27] p-2.5 rounded border border-[#28313D]">
                <span className="text-[10px] text-slate-400 block">EXPECTED TIME</span>
                <span className="text-emerald-400 font-bold text-sm">{viewedRun.best_time_formatted}</span>
              </div>
            </div>

            <div className="bg-[#0D1219] p-3 rounded border border-[#28313D] text-xs font-mono text-slate-300 space-y-1">
              <p className="text-slate-400 text-[10px] uppercase">OPTIMAL STRATEGY SPECIFICATION</p>
              <p className="text-white font-bold">{viewedRun.best_strategy}</p>
              <p className="text-slate-400 text-[11px] pt-1">
                Converged in {viewedRun.simulations_count} stochastic iterations under Common Random Numbers.
              </p>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setViewedRun(null)}
                className="bg-[#28313D] hover:bg-slate-700 text-white px-4 py-1.5 rounded text-xs font-medium transition-colors"
              >
                Close Report
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};


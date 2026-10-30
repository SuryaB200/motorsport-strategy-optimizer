import React, { useState } from 'react';
import { TireCompound, TireSetInventoryItem } from '../types';
import { INITIAL_TIRE_SETS } from '../services/api';
import { Disc, Plus, Check, Filter } from 'lucide-react';

export const TireSets: React.FC = () => {
  const [tireSets, setTireSets] = useState<TireSetInventoryItem[]>(INITIAL_TIRE_SETS);
  const [filterCompound, setFilterCompound] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const handleFit = (id: string) => {
    setTireSets((prev) =>
      prev.map((ts) => ({
        ...ts,
        status: ts.id === id ? 'FITTED' : ts.status === 'FITTED' ? 'USED' : ts.status,
      }))
    );
  };

  const handleAddSet = () => {
    const nextIdx = tireSets.length + 1;
    const newSet: TireSetInventoryItem = {
      id: `ts-${Date.now()}`,
      set_number: `SET-0${nextIdx}`,
      compound: 'MEDIUM',
      status: 'NEW',
      laps_run: 0,
      wear_percent: 0,
      allocation_session: 'Pit-Wall Reserve',
      allocated_date: 'Oct 30 15:00',
    };
    setTireSets([newSet, ...tireSets]);
  };

  const filteredSets = tireSets.filter((ts) => {
    const matchesComp = filterCompound === 'ALL' || ts.compound === filterCompound;
    const matchesQuery =
      ts.set_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ts.compound.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ts.allocation_session.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesComp && matchesQuery;
  });

  const getCompoundBadge = (compound: TireCompound) => {
    switch (compound) {
      case 'SOFT':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-600/30 text-red-400 border border-red-500/40">
            SOFT
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40">
            MEDIUM
          </span>
        );
      case 'HARD':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-200/20 text-slate-200 border border-slate-300/40">
            HARD
          </span>
        );
      case 'INTERMEDIATE':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
            INTERMEDIATE
          </span>
        );
      case 'WET':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-400 border border-blue-500/40">
            WET
          </span>
        );
    }
  };

  return (
    <section className="view-panel space-y-4" data-purpose="tire-set-management-screen">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-[#28313D]">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono px-1.5 py-0.5 rounded bg-[#F20D2F]/20 text-[#F20D2F] font-bold">
              3
            </span>
            <h1 className="text-xl font-bold tracking-tight text-white font-display">Tire Sets</h1>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">Manage available tire sets and track degradation status</p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleAddSet}
            className="bg-[#F20D2F] hover:bg-[#d00926] text-white px-3 py-1.5 rounded font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-md shadow-[#F20D2F]/20"
          >
            <Plus className="w-3.5 h-3.5" />
            Add Tire Set
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-[#111821] p-2.5 rounded border border-[#28313D]">
        <div className="flex items-center gap-1.5 text-xs font-medium overflow-x-auto pb-1 sm:pb-0">
          <span className="text-slate-400 mr-1 flex items-center gap-1 text-[11px] font-mono">
            <Filter className="w-3 h-3" /> COMPOUND:
          </span>
          {['ALL', 'SOFT', 'MEDIUM', 'HARD', 'INTERMEDIATE', 'WET'].map((comp) => (
            <button
              key={comp}
              onClick={() => setFilterCompound(comp)}
              className={`px-2.5 py-1 rounded text-xs transition-colors font-mono ${
                filterCompound === comp
                  ? 'bg-[#F20D2F] text-white font-bold'
                  : 'bg-[#151D27] text-slate-400 hover:text-white border border-[#28313D]'
              }`}
            >
              {comp}
            </button>
          ))}
        </div>

        <input
          type="text"
          placeholder="Search set ID or session..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="bg-[#151D27] border border-[#28313D] rounded px-3 py-1 text-xs text-slate-200 focus:outline-none focus:border-[#F20D2F] w-48 font-mono"
        />
      </div>

      {/* Inventory Table Container */}
      <div className="bg-[#111821] border border-[#28313D] rounded overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-[#151D27] text-slate-400 uppercase text-[10px] tracking-wider font-mono border-b border-[#28313D]">
            <tr>
              <th className="px-3.5 py-3">Set ID</th>
              <th className="px-3 py-3">Compound</th>
              <th className="px-3 py-3">Age (laps)</th>
              <th className="px-4 py-3">Estimated Wear</th>
              <th className="px-3 py-3">Remaining Life</th>
              <th className="px-3 py-3">Availability</th>
              <th className="px-3 py-3">Fitted</th>
              <th className="px-3 py-3">Est. Pace Δ (s)</th>
              <th className="px-3 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#28313D]/70 font-mono">
            {filteredSets.map((ts) => {
              const isFitted = ts.status === 'FITTED';
              const paceDelta =
                ts.compound === 'SOFT' ? -0.8 : ts.compound === 'MEDIUM' ? 0.0 : ts.compound === 'HARD' ? +0.6 : +1.4;

              return (
                <tr
                  key={ts.id}
                  className={`transition-colors ${
                    isFitted
                      ? 'bg-[#151D27]/80 hover:bg-[#151D27] border-l-2 border-l-[#F20D2F]'
                      : 'hover:bg-[#151D27]/50'
                  }`}
                >
                  <td className="px-3.5 py-2.5 font-bold text-white flex items-center gap-1.5">
                    {ts.set_number}
                    {isFitted && (
                      <span className="w-1.5 h-1.5 rounded-full bg-[#F20D2F] animate-pulse" title="Active on Car" />
                    )}
                  </td>
                  <td className="px-3 py-2.5">{getCompoundBadge(ts.compound)}</td>
                  <td className="px-3 py-2.5">{ts.laps_run}</td>
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-[#151D27] h-1.5 rounded-full overflow-hidden border border-slate-700">
                        <div
                          className={`h-full rounded-full ${
                            ts.wear_percent > 60
                              ? 'bg-red-500'
                              : ts.wear_percent > 30
                              ? 'bg-amber-400'
                              : 'bg-emerald-500'
                          }`}
                          style={{ width: `${ts.wear_percent}%` }}
                        />
                      </div>
                      <span className="text-[10px] text-slate-400">{ts.wear_percent}%</span>
                    </div>
                  </td>
                  <td className="px-3 py-2.5">
                    {Math.max(0, (ts.compound === 'HARD' ? 45 : ts.compound === 'MEDIUM' ? 32 : 20) - ts.laps_run)} laps
                  </td>
                  <td className="px-3 py-2.5">
                    {ts.status === 'NEW' ? (
                      <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        New
                      </span>
                    ) : isFitted ? (
                      <span className="px-2 py-0.5 rounded text-[10px] bg-[#F20D2F]/20 text-[#F20D2F] border border-[#F20D2F]/40 font-bold">
                        Fitted
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] bg-slate-700/50 text-slate-400">
                        Used
                      </span>
                    )}
                  </td>
                  <td className="px-3 py-2.5 font-bold">
                    {isFitted ? <span className="text-[#F20D2F]">Yes</span> : <span className="text-slate-500">-</span>}
                  </td>
                  <td className="px-3 py-2.5">
                    <span className={paceDelta <= 0 ? 'text-emerald-400' : 'text-slate-300'}>
                      {paceDelta > 0 ? `+${paceDelta.toFixed(1)}` : paceDelta.toFixed(1)}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 text-right">
                    {isFitted ? (
                      <button className="bg-slate-700 text-slate-300 px-2.5 py-1 rounded text-[11px] cursor-default font-semibold">
                        Current
                      </button>
                    ) : (
                      <button
                        onClick={() => handleFit(ts.id)}
                        className="bg-[#F20D2F] hover:bg-[#d00926] text-white px-2.5 py-1 rounded text-[11px] font-semibold transition-colors"
                      >
                        Fit
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Tire Allocation Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
        <div className="bg-[#111821] border border-[#28313D] rounded p-3 font-mono">
          <div className="flex items-center justify-between text-xs text-red-400 font-bold">
            <span>SOFT (C4/C5)</span>
            <span className="text-white text-base">2 Sets</span>
          </div>
          <span className="text-[10px] text-slate-400 mt-0.5 block">1 Scrubbed, 1 Fresh</span>
        </div>
        <div className="bg-[#111821] border border-[#28313D] rounded p-3 font-mono">
          <div className="flex items-center justify-between text-xs text-amber-400 font-bold">
            <span>MEDIUM (C3)</span>
            <span className="text-white text-base">3 Sets</span>
          </div>
          <span className="text-[10px] text-slate-400 mt-0.5 block">1 Fitted, 2 Fresh</span>
        </div>
        <div className="bg-[#111821] border border-[#28313D] rounded p-3 font-mono">
          <div className="flex items-center justify-between text-xs text-slate-200 font-bold">
            <span>HARD (C2)</span>
            <span className="text-white text-base">2 Sets</span>
          </div>
          <span className="text-[10px] text-slate-400 mt-0.5 block">2 Fresh Available</span>
        </div>
        <div className="bg-[#111821] border border-[#28313D] rounded p-3 font-mono">
          <div className="flex items-center justify-between text-xs text-blue-400 font-bold">
            <span>WET PROTOCOL</span>
            <span className="text-white text-base">2 Sets</span>
          </div>
          <span className="text-[10px] text-slate-400 mt-0.5 block">1 Inter, 1 Extreme Wet</span>
        </div>
      </div>
    </section>
  );
};


import React from 'react';
import { CircuitConfig } from '../types';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar, LineChart, Line, Legend } from 'recharts';
import { CloudRain, ShieldAlert, BarChart3, Wind } from 'lucide-react';

interface WeatherRiskProps {
  circuitId: string;
  circuits: Record<string, CircuitConfig>;
}

export const WeatherRisk: React.FC<WeatherRiskProps> = ({ circuitId, circuits }) => {
  const currentCircuit = circuits[circuitId] || circuits.monaco;
  const totalLaps = currentCircuit?.total_laps || 70;

  // 1. Rain probability curve data
  const rainCurveData = Array.from({ length: 15 }, (_, i) => {
    const lap = Math.round((i * totalLaps) / 14);
    // Create spike around lap 20-30 and 45-55
    let prob = 0.05;
    if (lap >= 18 && lap <= 28) prob = 0.65 - Math.abs(lap - 23) * 0.08;
    else if (lap >= 45 && lap <= 55) prob = 0.45 - Math.abs(lap - 50) * 0.07;
    return {
      lap,
      rainProb: +Math.max(0.02, prob).toFixed(2),
    };
  });

  // 2. Safety car probability histogram data by 5-lap windows
  const scHistoData = [
    { window: 'L1-5', scProb: 0.28 },
    { window: 'L6-10', scProb: 0.12 },
    { window: 'L11-15', scProb: 0.08 },
    { window: 'L16-20', scProb: 0.22 },
    { window: 'L21-25', scProb: 0.35 },
    { window: 'L26-30', scProb: 0.15 },
    { window: 'L31-35', scProb: 0.18 },
    { window: 'L36-40', scProb: 0.10 },
    { window: 'L41-45', scProb: 0.14 },
    { window: 'L46-50', scProb: 0.25 },
    { window: 'L51-55', scProb: 0.18 },
    { window: 'L56-60', scProb: 0.08 },
  ];

  // 3. Race time distribution bell curve data
  const bellCurveData = [
    { timeSec: 5480, count: 2 },
    { timeSec: 5490, count: 8 },
    { timeSec: 5500, count: 24 },
    { timeSec: 5510, count: 58 },
    { timeSec: 5520, count: 84 },
    { timeSec: 5530, count: 68 },
    { timeSec: 5540, count: 32 },
    { timeSec: 5550, count: 12 },
    { timeSec: 5560, count: 4 },
  ];

  // 4. Strategy Sensitivity to Rain Probability
  const sensitivityData = [
    { rainProb: '0.0', conservative: 5540, balanced: 5502, aggressive: 5480 },
    { rainProb: '0.1', conservative: 5545, balanced: 5515, aggressive: 5510 },
    { rainProb: '0.2', conservative: 5550, balanced: 5532, aggressive: 5550 },
    { rainProb: '0.3', conservative: 5555, balanced: 5560, aggressive: 5610 },
    { rainProb: '0.4', conservative: 5565, balanced: 5595, aggressive: 5690 },
    { rainProb: '0.5', conservative: 5580, balanced: 5640, aggressive: 5780 },
  ];

  return (
    <section className="view-panel space-y-4" data-purpose="weather-and-risk-analysis-screen">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-[#28313D]">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono px-1.5 py-0.5 rounded bg-[#F20D2F]/20 text-[#F20D2F] font-bold">
              5
            </span>
            <h1 className="text-xl font-bold tracking-tight text-white font-display">Weather and Risk Analysis</h1>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">Quantify how stochastic weather and Safety Car events affect strategy</p>
        </div>
      </div>

      {/* Upper 3 Analytics Panels */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* 1. Rain Probability by Lap */}
        <div className="bg-[#111821] border border-[#28313D] rounded p-3.5 flex flex-col justify-between">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
              Rain Probability by Lap
            </span>
            <span className="text-[10px] text-cyan-400 font-mono">Peak: 65% @ L23</span>
          </div>

          <div className="h-40 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={rainCurveData} margin={{ top: 5, right: 10, left: -25, bottom: 0 }}>
                <defs>
                  <linearGradient id="rainGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1677E8" stopOpacity={0.6} />
                    <stop offset="95%" stopColor="#1677E8" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#1f2937" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="lap" stroke="#6B7280" tick={{ fontSize: 9, fill: '#6B7280', fontFamily: 'monospace' }} />
                <YAxis domain={[0, 1]} stroke="#6B7280" tick={{ fontSize: 9, fill: '#6B7280', fontFamily: 'monospace' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#111821',
                    border: '1px solid #28313D',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontFamily: 'monospace',
                  }}
                />
                <Area type="monotone" dataKey="rainProb" stroke="#1677E8" strokeWidth={2} fillOpacity={1} fill="url(#rainGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="text-[10px] text-center text-slate-500 font-mono pt-1">Lap Number</div>
        </div>

        {/* 2. Weather Transition Matrix (3x3 Heatmap) */}
        <div className="bg-[#111821] border border-[#28313D] rounded p-3.5 flex flex-col justify-between">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
              Transition Matrix
            </span>
            <span className="text-[10px] text-slate-500 font-mono">MARKOV CHAIN</span>
          </div>

          <div className="py-2">
            <table className="w-full text-center text-[11px] font-mono">
              <thead>
                <tr className="text-slate-400 text-[10px]">
                  <th className="text-left font-normal pb-1">From \ To</th>
                  <th className="pb-1 font-semibold text-amber-400">Dry</th>
                  <th className="pb-1 font-semibold text-emerald-400">Int.</th>
                  <th className="pb-1 font-semibold text-[#1677E8]">Wet</th>
                </tr>
              </thead>
              <tbody className="space-y-1">
                <tr>
                  <td className="text-left text-slate-400 py-1 font-semibold">Dry</td>
                  <td className="p-1">
                    <span className="block bg-red-600/80 text-white font-bold rounded py-1">0.85</span>
                  </td>
                  <td className="p-1">
                    <span className="block bg-red-950/80 text-slate-200 rounded py-1">0.10</span>
                  </td>
                  <td className="p-1">
                    <span className="block bg-[#151D27] text-slate-400 rounded py-1 border border-[#28313D]">0.05</span>
                  </td>
                </tr>
                <tr>
                  <td className="text-left text-slate-400 py-1 font-semibold">Int. Wet</td>
                  <td className="p-1">
                    <span className="block bg-red-900/60 text-slate-100 rounded py-1">0.30</span>
                  </td>
                  <td className="p-1">
                    <span className="block bg-red-700/80 text-white font-bold rounded py-1">0.50</span>
                  </td>
                  <td className="p-1">
                    <span className="block bg-red-950/70 text-slate-300 rounded py-1">0.20</span>
                  </td>
                </tr>
                <tr>
                  <td className="text-left text-slate-400 py-1 font-semibold">Wet</td>
                  <td className="p-1">
                    <span className="block bg-[#151D27] text-slate-400 rounded py-1 border border-[#28313D]">0.15</span>
                  </td>
                  <td className="p-1">
                    <span className="block bg-red-900/70 text-slate-200 rounded py-1">0.35</span>
                  </td>
                  <td className="p-1">
                    <span className="block bg-red-700/80 text-white font-bold rounded py-1">0.50</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div className="text-[10px] text-center text-slate-500 font-mono">Calibrated Markov Probabilities</div>
        </div>

        {/* 3. Safety Car Probability Histogram */}
        <div className="bg-[#111821] border border-[#28313D] rounded p-3.5 flex flex-col justify-between">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
              Safety Car Likelihood
            </span>
            <span className="text-[10px] text-amber-400 font-mono">P(Start): 28%</span>
          </div>

          <div className="h-40 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={scHistoData} margin={{ top: 5, right: 10, left: -25, bottom: 0 }}>
                <CartesianGrid stroke="#1f2937" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="window" stroke="#6B7280" tick={{ fontSize: 8, fill: '#6B7280', fontFamily: 'monospace' }} />
                <YAxis stroke="#6B7280" tick={{ fontSize: 9, fill: '#6B7280', fontFamily: 'monospace' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#111821',
                    border: '1px solid #28313D',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontFamily: 'monospace',
                  }}
                />
                <Bar dataKey="scProb" fill="#1677E8" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="text-[10px] text-center text-slate-500 font-mono pt-1">5-Lap Window Bin</div>
        </div>
      </div>

      {/* Lower 2 Analytical Panels */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 4. Race Time Distribution (Bell Curve) */}
        <div className="bg-[#111821] border border-[#28313D] rounded p-3.5">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
              Monte Carlo Finish Time Distribution
            </span>
            <span className="text-[10px] text-emerald-400 font-mono">μ = 5520s, σ = 12.6s</span>
          </div>

          <div className="h-44 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={bellCurveData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid stroke="#1f2937" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="timeSec" stroke="#6B7280" tick={{ fontSize: 9, fill: '#6B7280', fontFamily: 'monospace' }} />
                <YAxis stroke="#6B7280" tick={{ fontSize: 9, fill: '#6B7280', fontFamily: 'monospace' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#111821',
                    border: '1px solid #28313D',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontFamily: 'monospace',
                  }}
                />
                <Bar dataKey="count" fill="#F20D2F" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="text-[10px] text-center text-slate-500 font-mono pt-1">Total Race Time (seconds)</div>
        </div>

        {/* 5. Strategy Sensitivity to Rain Probability */}
        <div className="bg-[#111821] border border-[#28313D] rounded p-3.5 flex flex-col justify-between">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
              Strategy Sensitivity to Rain Prob
            </span>
            <div className="flex items-center gap-2 text-[10px] font-mono">
              <span className="flex items-center gap-1 text-emerald-400">
                <span className="w-2 h-0.5 bg-emerald-400" /> Conservative
              </span>
              <span className="flex items-center gap-1 text-cyan-400">
                <span className="w-2 h-0.5 bg-cyan-400" /> Balanced
              </span>
              <span className="flex items-center gap-1 text-[#F20D2F]">
                <span className="w-2 h-0.5 bg-[#F20D2F]" /> Aggressive
              </span>
            </div>
          </div>

          <div className="h-44 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sensitivityData} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid stroke="#1f2937" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="rainProb" stroke="#6B7280" tick={{ fontSize: 9, fill: '#6B7280', fontFamily: 'monospace' }} />
                <YAxis domain={['auto', 'auto']} stroke="#6B7280" tick={{ fontSize: 9, fill: '#6B7280', fontFamily: 'monospace' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#111821',
                    border: '1px solid #28313D',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontFamily: 'monospace',
                  }}
                />
                <Line type="monotone" dataKey="conservative" stroke="#10B981" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="balanced" stroke="#06B6D4" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="aggressive" stroke="#F20D2F" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="text-[10px] text-center text-slate-500 font-mono pt-1">Rain Probability Scale (0.0 - 0.5)</div>
        </div>
      </div>
    </section>
  );
};


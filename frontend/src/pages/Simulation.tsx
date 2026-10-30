import React, { useState } from 'react';
import { CircuitConfig, SingleSimulationResult, Strategy } from '../types';
import { runSimulation } from '../services/api';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ReferenceArea } from 'recharts';
import { Activity, Play, CheckCircle2, Cloud, ShieldAlert } from 'lucide-react';

interface SimulationProps {
  circuitId: string;
  circuits: Record<string, CircuitConfig>;
  simulationResult: SingleSimulationResult | null;
  setSimulationResult: (res: SingleSimulationResult) => void;
}

export const Simulation: React.FC<SimulationProps> = ({
  circuitId,
  circuits,
  simulationResult,
  setSimulationResult,
}) => {
  const currentCircuit = circuits[circuitId] || circuits.monaco;
  const [totalLaps, setTotalLaps] = useState<number>(currentCircuit?.total_laps || 70);
  const [initialWeather, setInitialWeather] = useState<string>('Dry');
  const [rainProb, setRainProb] = useState<number>(0.05);
  const [weatherModel, setWeatherModel] = useState<string>('Markov Chain');
  const [safetyCarProb, setSafetyCarProb] = useState<number>(0.15);
  const [scDuration, setScDuration] = useState<number>(3);
  const [lapTimeSigma, setLapTimeSigma] = useState<number>(0.3);
  const [seed, setSeed] = useState<number>(42);
  const [mcRuns, setMcRuns] = useState<number>(1000);
  const [activeTab, setActiveTab] = useState<'chart' | 'events' | 'summary'>('chart');
  const [loading, setLoading] = useState<boolean>(false);

  const handleRun = async () => {
    setLoading(true);
    try {
      const defaultStrategy: Strategy = {
        strategy_id: 'strat-active',
        name: `Optimal 1-Stop (${circuitId.toUpperCase()})`,
        stints: [
          { compound: 'MEDIUM', start_lap: 1, end_lap: Math.floor(totalLaps * 0.45), planned_laps: Math.floor(totalLaps * 0.45) },
          { compound: 'HARD', start_lap: Math.floor(totalLaps * 0.45) + 1, end_lap: totalLaps, planned_laps: totalLaps - Math.floor(totalLaps * 0.45) },
        ],
        pit_laps: [Math.floor(totalLaps * 0.45)],
        compounds: ['MEDIUM', 'HARD'],
      };
      const res = await runSimulation(circuitId, defaultStrategy);
      setSimulationResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // Generate chart data from simulation result or default curve
  const chartData = (simulationResult?.laps && simulationResult.laps.length > 0)
    ? simulationResult.laps.map((lap) => ({
        lap: lap.lap_number,
        driverPace: lap.lap_time,
        optimalPace: +(lap.lap_time - (lap.is_pit_lap ? 0 : 0.4)).toFixed(2),
        isSC: lap.safety_car !== 'NONE',
        isPit: lap.is_pit_lap,
        wear: lap.tire_wear,
      }))
    : Array.from({ length: totalLaps }, (_, i) => {
        const lap = i + 1;
        const isSC = lap >= 20 && lap <= 23;
        const isPit = lap === 32;
        const base = currentCircuit?.baseline_lap_time || 74.0;
        const deg = (lap % 32) * 0.12;
        const driverPace = +(base + deg + (isSC ? 25 : 0) + (isPit ? (currentCircuit?.pit_loss || 22) : 0)).toFixed(2);
        const optimalPace = +(base + (lap % 34) * 0.08 + (isSC ? 25 : 0) + (lap === 34 ? (currentCircuit?.pit_loss || 22) : 0)).toFixed(2);
        return {
          lap,
          driverPace,
          optimalPace,
          isSC,
          isPit,
          wear: Math.min(100, Math.round(((lap % 35) + 1) * 2.8)),
        };
      });

  return (
    <section className="view-panel space-y-5" data-purpose="race-simulation-screen">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-[#28313D]">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono px-1.5 py-0.5 rounded bg-[#F20D2F]/20 text-[#F20D2F] font-bold">
              2
            </span>
            <h1 className="text-xl font-bold tracking-tight text-white font-display">Race Simulation</h1>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">Configure and run stochastic race simulations</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left Column: Simulation Parameters (4 Cols) */}
        <div className="lg:col-span-4 bg-[#111821] border border-[#28313D] rounded p-4 space-y-3.5">
          <h2 className="text-xs font-bold text-white uppercase tracking-wider border-b border-[#28313D] pb-2 font-mono flex items-center justify-between">
            <span>Simulation Parameters</span>
            <span className="text-[10px] text-slate-500 font-normal">STOCHASTIC SEED</span>
          </h2>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Total Laps</label>
              <input
                type="number"
                value={totalLaps}
                onChange={(e) => setTotalLaps(Number(e.target.value))}
                className="w-full bg-[#151D27] border border-[#28313D] rounded px-2.5 py-1.5 text-slate-100 font-mono focus:border-[#F20D2F] focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Initial Weather</label>
              <select
                value={initialWeather}
                onChange={(e) => setInitialWeather(e.target.value)}
                className="w-full bg-[#151D27] border border-[#28313D] rounded px-2.5 py-1.5 text-slate-100 text-xs focus:border-[#F20D2F] focus:outline-none"
              >
                <option>Dry</option>
                <option>Light Rain</option>
                <option>Wet</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Rain Prob (per lap)</label>
              <input
                type="text"
                value={rainProb}
                onChange={(e) => setRainProb(Number(e.target.value))}
                className="w-full bg-[#151D27] border border-[#28313D] rounded px-2.5 py-1.5 text-slate-100 font-mono focus:border-[#F20D2F] focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Weather Model</label>
              <select
                value={weatherModel}
                onChange={(e) => setWeatherModel(e.target.value)}
                className="w-full bg-[#151D27] border border-[#28313D] rounded px-2.5 py-1.5 text-slate-100 text-xs focus:border-[#F20D2F] focus:outline-none"
              >
                <option>Markov Chain</option>
                <option>Static Distribution</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Safety Car Prob</label>
              <input
                type="text"
                value={safetyCarProb}
                onChange={(e) => setSafetyCarProb(Number(e.target.value))}
                className="w-full bg-[#151D27] border border-[#28313D] rounded px-2.5 py-1.5 text-slate-100 font-mono focus:border-[#F20D2F] focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Avg SC Duration (laps)</label>
              <input
                type="number"
                value={scDuration}
                onChange={(e) => setScDuration(Number(e.target.value))}
                className="w-full bg-[#151D27] border border-[#28313D] rounded px-2.5 py-1.5 text-slate-100 font-mono focus:border-[#F20D2F] focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Lap Time Var (σ)</label>
              <input
                type="text"
                value={lapTimeSigma}
                onChange={(e) => setLapTimeSigma(Number(e.target.value))}
                className="w-full bg-[#151D27] border border-[#28313D] rounded px-2.5 py-1.5 text-slate-100 font-mono focus:border-[#F20D2F] focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Random Seed</label>
              <input
                type="number"
                value={seed}
                onChange={(e) => setSeed(Number(e.target.value))}
                className="w-full bg-[#151D27] border border-[#28313D] rounded px-2.5 py-1.5 text-slate-100 font-mono focus:border-[#F20D2F] focus:outline-none"
              />
            </div>
          </div>

          <div className="text-xs pt-1">
            <label className="block text-[11px] text-slate-400 mb-1">Monte Carlo Runs</label>
            <select
              value={mcRuns}
              onChange={(e) => setMcRuns(Number(e.target.value))}
              className="w-full bg-[#151D27] border border-[#28313D] rounded px-2.5 py-1.5 text-slate-100 text-xs focus:border-[#F20D2F] focus:outline-none font-mono"
            >
              <option value={500}>500 Iterations</option>
              <option value={1000}>1000 Iterations (Standard)</option>
              <option value={5000}>5000 Iterations (High Precision)</option>
            </select>
          </div>

          <button
            onClick={handleRun}
            disabled={loading}
            className="w-full bg-[#F20D2F] hover:bg-[#d00926] disabled:opacity-50 text-white py-2 rounded font-bold text-xs transition-colors mt-2 tracking-wide uppercase flex items-center justify-center gap-2 shadow-lg shadow-[#F20D2F]/20"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            {loading ? 'Simulating...' : 'Run Simulation'}
          </button>
        </div>

        {/* Right Column: Simulation Results (8 Cols) */}
        <div className="lg:col-span-8 bg-[#111821] border border-[#28313D] rounded p-4 flex flex-col justify-between space-y-4">
          {/* Tab Controls & Legend */}
          <div className="flex flex-wrap items-center justify-between border-b border-[#28313D] pb-3 gap-2">
            <div className="flex space-x-1.5 bg-[#151D27] p-1 rounded border border-[#28313D] text-xs font-medium">
              <button
                onClick={() => setActiveTab('chart')}
                className={`px-3 py-1 rounded transition-colors ${
                  activeTab === 'chart' ? 'bg-[#28313D] text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                Lap Chart
              </button>
              <button
                onClick={() => setActiveTab('events')}
                className={`px-3 py-1 rounded transition-colors ${
                  activeTab === 'events' ? 'bg-[#28313D] text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                Event Telemetry
              </button>
              <button
                onClick={() => setActiveTab('summary')}
                className={`px-3 py-1 rounded transition-colors ${
                  activeTab === 'summary' ? 'bg-[#28313D] text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                Summary Metrics
              </button>
            </div>

            {/* Legend */}
            <div className="flex items-center space-x-3 text-[11px] text-slate-300 font-mono">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-0.5 bg-[#F20D2F] inline-block" /> Driver
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-0.5 bg-[#1677E8] inline-block" /> Optimal Strategy
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 bg-slate-700/60 inline-block border border-slate-500" /> Safety Car Period
              </span>
            </div>
          </div>

          {/* Tab View 1: Lap Chart */}
          {activeTab === 'chart' && (
            <div className="space-y-3">
              <div className="relative w-full h-64 bg-[#0D1219] rounded p-2 border border-[#28313D]">
                <div className="text-[10px] text-slate-400 font-mono uppercase tracking-wider mb-1 px-2 pt-1 flex justify-between">
                  <span>Simulated Lap Times (seconds)</span>
                  <span className="text-slate-500 font-normal">Common Random Numbers Active</span>
                </div>
                <ResponsiveContainer width="100%" height="88%">
                  <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid stroke="#1f2937" strokeDasharray="3 3" vertical={false} />
                    <XAxis
                      dataKey="lap"
                      stroke="#6B7280"
                      tick={{ fontSize: 10, fill: '#6B7280', fontFamily: 'monospace' }}
                    />
                    <YAxis
                      domain={['auto', 'auto']}
                      stroke="#6B7280"
                      tick={{ fontSize: 10, fill: '#6B7280', fontFamily: 'monospace' }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#111821',
                        border: '1px solid #28313D',
                        borderRadius: '4px',
                        fontSize: '11px',
                        color: '#F4F6F8',
                        fontFamily: 'monospace',
                      }}
                    />
                    {/* SC shaded areas if active */}
                    <ReferenceArea x1={19} x2={23} fill="#374151" fillOpacity={0.4} label={{ value: 'SC', fill: '#9CA3AF', fontSize: 10 }} />
                    <Line
                      type="monotone"
                      dataKey="optimalPace"
                      stroke="#1677E8"
                      strokeWidth={2}
                      dot={false}
                      name="Optimal Reference"
                    />
                    <Line
                      type="monotone"
                      dataKey="driverPace"
                      stroke="#F20D2F"
                      strokeWidth={2}
                      dot={false}
                      name="Simulated Lap Time"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Weather Condition Multi-color Bar Strip */}
              <div className="space-y-1">
                <div className="flex justify-between text-[11px] text-slate-400">
                  <span className="font-medium font-mono">Weather Condition Along Laps</span>
                  <span className="font-mono">Lap 0 to {totalLaps}</span>
                </div>
                <div className="h-3.5 w-full rounded flex overflow-hidden border border-[#28313D]">
                  <div className="bg-amber-400 h-full" style={{ width: '28%' }} title="Dry (Laps 0-20)" />
                  <div className="bg-slate-600 h-full" style={{ width: '12%' }} title="Safety Car (Laps 20-25)" />
                  <div className="bg-emerald-500 h-full" style={{ width: '22%' }} title="Intermediate Wet (Laps 25-38)" />
                  <div className="bg-[#1677E8] h-full" style={{ width: '14%' }} title="Wet (Laps 38-46)" />
                  <div className="bg-amber-400 h-full" style={{ width: '24%' }} title="Dry (Laps 46-70)" />
                </div>
                <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono pt-1">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-1"><span className="w-2 h-2 bg-amber-400 inline-block" /> Dry</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 bg-emerald-500 inline-block" /> Int. Wet</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 bg-[#1677E8] inline-block" /> Wet</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 bg-slate-600 inline-block" /> Safety Car</span>
                  </div>
                  <span>Lap Progress Timeline</span>
                </div>
              </div>
            </div>
          )}

          {/* Tab View 2: Event Telemetry */}
          {activeTab === 'events' && (
            <div className="bg-[#0D1219] border border-[#28313D] rounded p-3 h-72 overflow-y-auto font-mono text-xs space-y-2">
              <div className="flex items-center justify-between text-slate-500 text-[10px] pb-1 border-b border-[#28313D]">
                <span>LAP / EVENT</span>
                <span>TELEMETRY DETAILS</span>
                <span>TIME DELTA</span>
              </div>
              <div className="flex items-center justify-between text-emerald-400 py-1">
                <span>LAP 01: Race Start</span>
                <span className="text-slate-300">Clean getaway, Medium C3 fitted</span>
                <span>+0.000s</span>
              </div>
              <div className="flex items-center justify-between text-slate-300 py-1">
                <span>LAP 12: Degradation Inflection</span>
                <span className="text-slate-400">Front left wear crosses 28%</span>
                <span>+0.420s</span>
              </div>
              <div className="flex items-center justify-between text-amber-400 py-1 bg-amber-500/5 px-1.5 rounded">
                <span>LAP 20: Safety Car Deployed</span>
                <span className="text-amber-300">Incident Turn 4; Pace limited to delta</span>
                <span>+25.000s</span>
              </div>
              <div className="flex items-center justify-between text-cyan-400 py-1">
                <span>LAP 24: Green Flag Restart</span>
                <span className="text-slate-300">Racing resumes; Track Temp 31°C</span>
                <span>-0.850s</span>
              </div>
              <div className="flex items-center justify-between text-[#F20D2F] py-1 bg-[#F20D2F]/10 px-1.5 rounded">
                <span>LAP 32: Box This Lap (Pit Stop 1)</span>
                <span className="text-white">Medium -&gt; Hard C2; Stationary: 2.4s</span>
                <span>+21.500s</span>
              </div>
              <div className="flex items-center justify-between text-emerald-400 py-1">
                <span>LAP 52: Finish Line</span>
                <span className="text-slate-300">Race simulation concluded</span>
                <span className="font-bold text-white">1:32:15.4</span>
              </div>
            </div>
          )}

          {/* Tab View 3: Summary Metrics */}
          {activeTab === 'summary' && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="bg-[#151D27] p-3 rounded border border-[#28313D]">
                <span className="block text-[10px] text-slate-400 font-mono uppercase">Total Race Time</span>
                <span className="text-lg font-black font-mono text-white">1:32:15.4</span>
                <span className="block text-[10px] text-emerald-400 font-mono mt-1">-2.3s vs expected</span>
              </div>
              <div className="bg-[#151D27] p-3 rounded border border-[#28313D]">
                <span className="block text-[10px] text-slate-400 font-mono uppercase">Pit Stops</span>
                <span className="text-lg font-bold font-mono text-white">1 Stop</span>
                <span className="block text-[10px] text-slate-400 font-mono mt-1">Lap 32 (M-&gt;H)</span>
              </div>
              <div className="bg-[#151D27] p-3 rounded border border-[#28313D]">
                <span className="block text-[10px] text-slate-400 font-mono uppercase">SC Laps</span>
                <span className="text-lg font-bold font-mono text-amber-400">4 Laps</span>
                <span className="block text-[10px] text-slate-400 font-mono mt-1">Laps 20 - 23</span>
              </div>
              <div className="bg-[#151D27] p-3 rounded border border-[#28313D]">
                <span className="block text-[10px] text-slate-400 font-mono uppercase">Tire Efficiency</span>
                <span className="text-lg font-bold font-mono text-emerald-400">94.2%</span>
                <span className="block text-[10px] text-slate-400 font-mono mt-1">Linear cliff avoided</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};


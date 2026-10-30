import React, { useState, useEffect } from 'react';
import { Header } from './components/layout/Header';
import { Sidebar, TabId } from './components/layout/Sidebar';
import { RaceOverview } from './pages/RaceOverview';
import { Simulation } from './pages/Simulation';
import { TireSets } from './pages/TireSets';
import { StrategyOptimization } from './pages/StrategyOptimization';
import { WeatherRisk } from './pages/WeatherRisk';
import { ResultsHistory } from './pages/ResultsHistory';
import { OverviewGrid } from './pages/OverviewGrid';
import { SettingsModal } from './components/layout/SettingsModal';
import {
  checkBackendHealth,
  fetchCircuits,
  DEFAULT_CIRCUITS,
  runSimulation,
  runOptimization,
} from './services/api';
import { CircuitConfig, OptimizationResponse, SingleSimulationResult, Strategy } from './types';

class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }
  componentDidCatch(error: Error, info: any) {
    console.error('ErrorBoundary caught:', error, info);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-[#111821] border border-amber-500/40 rounded p-6 text-center space-y-3 font-mono">
          <span className="text-[#F20D2F] font-bold text-sm block">TELEMETRY VIEW RECOVERY</span>
          <p className="text-slate-300 text-xs">
            {this.state.error?.message || 'An unexpected telemetry state occurred.'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="bg-[#F20D2F] hover:bg-[#d00926] text-white px-4 py-1.5 rounded text-xs font-bold transition-colors"
          >
            Reset Telemetry View
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [viewMode, setViewMode] = useState<'single' | 'composite'>('single');
  const [circuitId, setCircuitId] = useState<string>('monaco');
  const [circuits, setCircuits] = useState<Record<string, CircuitConfig>>(DEFAULT_CIRCUITS);
  const [backendOnline, setBackendOnline] = useState<boolean>(true);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [simulationResult, setSimulationResult] = useState<SingleSimulationResult | null>(null);
  const [optimizationData, setOptimizationData] = useState<OptimizationResponse | null>(null);

  // Settings State: Glassmorphism, Glow accents, Auto Refresh
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);
  const [glassEffects, setGlassEffects] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('f1_glass_effects');
      return saved !== null ? saved === 'true' : true;
    } catch {
      return true;
    }
  });
  const [glowEffects, setGlowEffects] = useState<boolean>(true);
  const [autoRefresh, setAutoRefresh] = useState<boolean>(false);

  useEffect(() => {
    try {
      localStorage.setItem('f1_glass_effects', String(glassEffects));
    } catch {
      // ignore
    }
  }, [glassEffects]);

  // Initial health check and circuit data retrieval
  useEffect(() => {
    let mounted = true;
    async function init() {
      try {
        const health = await checkBackendHealth();
        if (mounted) setBackendOnline(health.status === 'healthy');

        const fetchedCircuits = await fetchCircuits();
        if (mounted && fetchedCircuits && Object.keys(fetchedCircuits).length > 0) {
          setCircuits(fetchedCircuits);
        }
      } catch (err) {
        if (mounted) setBackendOnline(false);
      }
    }
    init();
    return () => {
      mounted = false;
    };
  }, []);

  const handleStartSimulation = async () => {
    setIsSimulating(true);
    try {
      const cur = circuits[circuitId] || circuits.monaco;
      const defaultStrategy: Strategy = {
        strategy_id: 'strat-active',
        name: `Optimal 1-Stop (${circuitId.toUpperCase()})`,
        stints: [
          { compound: 'MEDIUM', start_lap: 1, end_lap: Math.floor(cur.total_laps * 0.45), planned_laps: Math.floor(cur.total_laps * 0.45) },
          { compound: 'HARD', start_lap: Math.floor(cur.total_laps * 0.45) + 1, end_lap: cur.total_laps, planned_laps: cur.total_laps - Math.floor(cur.total_laps * 0.45) },
        ],
        pit_laps: [Math.floor(cur.total_laps * 0.45)],
        compounds: ['MEDIUM', 'HARD'],
      };
      const res = await runSimulation(circuitId, defaultStrategy);
      setSimulationResult(res);
      setActiveTab('simulation');
      setViewMode('single');
    } catch (e) {
      console.error(e);
    } finally {
      setIsSimulating(false);
    }
  };

  const currentCircuit = circuits[circuitId] || circuits.monaco;

  return (
    <div
      className={`text-slate-100 font-sans min-h-screen antialiased flex flex-col selection:bg-[#F20D2F] selection:text-white transition-all duration-300 ${
        glassEffects ? 'glass-active' : 'bg-[#090D12]'
      } ${glowEffects ? 'glow-active' : ''}`}
    >
      {/* Global Header */}
      <Header
        viewMode={viewMode}
        setViewMode={setViewMode}
        currentLap={24}
        totalLaps={currentCircuit.total_laps}
        backendOnline={backendOnline}
        onOpenSettings={() => setIsSettingsOpen(true)}
        glassEffects={glassEffects}
      />

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        glassEffects={glassEffects}
        setGlassEffects={setGlassEffects}
        glowEffects={glowEffects}
        setGlowEffects={setGlowEffects}
        autoRefresh={autoRefresh}
        setAutoRefresh={setAutoRefresh}
        backendOnline={backendOnline}
      />

      {/* Main Shell */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Left Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={(tab) => {
            setActiveTab(tab);
            setViewMode('single');
          }}
          backendOnline={backendOnline}
        />

        {/* Viewport Content Area */}
        <main className="flex-1 overflow-y-auto p-3 lg:p-6 bg-[#090D12]" id="main-content-scroll">
          <ErrorBoundary>
            {viewMode === 'composite' ? (
              <OverviewGrid
                setActiveTab={setActiveTab}
                setViewMode={setViewMode}
                circuitId={circuitId}
                circuits={circuits}
                optimizationData={optimizationData}
                simulationResult={simulationResult}
              />
            ) : (
              <>
                {activeTab === 'overview' && (
                  <RaceOverview
                    circuitId={circuitId}
                    setCircuitId={setCircuitId}
                    circuits={circuits}
                    onStartSimulation={handleStartSimulation}
                    isSimulating={isSimulating}
                    backendOnline={backendOnline}
                  />
                )}
                {activeTab === 'simulation' && (
                  <Simulation
                    circuitId={circuitId}
                    circuits={circuits}
                    simulationResult={simulationResult}
                    setSimulationResult={setSimulationResult}
                  />
                )}
                {activeTab === 'tire-sets' && <TireSets />}
                {activeTab === 'strategy' && (
                  <StrategyOptimization
                    circuitId={circuitId}
                    setCircuitId={setCircuitId}
                    circuits={circuits}
                    optimizationData={optimizationData}
                    setOptimizationData={setOptimizationData}
                  />
                )}
                {activeTab === 'weather' && (
                  <WeatherRisk circuitId={circuitId} circuits={circuits} />
                )}
                {activeTab === 'results' && <ResultsHistory />}
              </>
            )}
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
};
export default App;


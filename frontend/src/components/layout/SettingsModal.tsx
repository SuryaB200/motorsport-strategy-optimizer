import React, { useState } from 'react';
import { X, Sparkles, Sliders, CheckCircle2, ShieldAlert, Cpu, Eye, Radio } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  glassEffects: boolean;
  setGlassEffects: (val: boolean) => void;
  glowEffects: boolean;
  setGlowEffects: (val: boolean) => void;
  autoRefresh: boolean;
  setAutoRefresh: (val: boolean) => void;
  backendOnline: boolean;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  glassEffects,
  setGlassEffects,
  glowEffects,
  setGlowEffects,
  autoRefresh,
  setAutoRefresh,
  backendOnline,
}) => {
  const [testStatus, setTestStatus] = useState<string | null>(null);
  const [testing, setTesting] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleTestConnection = async () => {
    setTesting(true);
    setTestStatus('Pinging API endpoint...');
    const startTime = performance.now();
    try {
      const res = await fetch('/health');
      const duration = Math.round(performance.now() - startTime);
      if (res.ok) {
        setTestStatus(`SUCCESS: Connected in ${duration}ms (HTTP 200 OK)`);
      } else {
        setTestStatus(`ERROR: Received status ${res.status}`);
      }
    } catch (e: any) {
      setTestStatus(`OFFLINE: Could not reach backend: ${e.message}`);
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-[#111821] border border-[#28313D] rounded-xl max-w-lg w-full p-5 space-y-5 shadow-2xl relative font-sans text-slate-100">
        {/* Modal Top */}
        <div className="flex items-center justify-between border-b border-[#28313D] pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded bg-[#F20D2F]/20 text-[#F20D2F]">
              <Sliders className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold uppercase tracking-wider font-display text-white">
                Pit-Wall Command Settings
              </h2>
              <p className="text-[11px] text-slate-400">Configure visual effects &amp; telemetry engine parameters</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded text-slate-400 hover:text-white hover:bg-[#151D27] transition-colors"
            title="Close Settings"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Setting Groups */}
        <div className="space-y-4 text-xs">
          {/* 1. Visual Glassmorphism Effects */}
          <div className="bg-[#151D27] p-3.5 rounded-lg border border-[#28313D] flex items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                <span className="font-bold text-white font-mono uppercase text-[11px]">
                  Glassmorphism &amp; Frosted Glass
                </span>
                {glassEffects && (
                  <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                    ACTIVE
                  </span>
                )}
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Applies frosted glass backdrop-blur, translucent telemetry card surfaces, ambient mesh lighting, and luminous depth.
              </p>
            </div>

            {/* Custom Switch Toggle */}
            <button
              onClick={() => setGlassEffects(!glassEffects)}
              role="switch"
              aria-checked={glassEffects}
              className={`w-12 h-6 flex items-center rounded-full p-1 transition-colors shrink-0 ${
                glassEffects ? 'bg-[#F20D2F]' : 'bg-[#28313D]'
              }`}
            >
              <div
                className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                  glassEffects ? 'translate-x-6' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {/* 2. Neon Red Glow Effects */}
          <div className="bg-[#151D27] p-3.5 rounded-lg border border-[#28313D] flex items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Eye className="w-3.5 h-3.5 text-[#F20D2F]" />
                <span className="font-bold text-white font-mono uppercase text-[11px]">
                  F1 Neon Glow &amp; Shadows
                </span>
              </div>
              <p className="text-slate-400 text-[11px]">
                Enables high-intensity telemetry glows on pit-stop indicators, optimal badges, and buttons.
              </p>
            </div>

            <button
              onClick={() => setGlowEffects(!glowEffects)}
              role="switch"
              aria-checked={glowEffects}
              className={`w-12 h-6 flex items-center rounded-full p-1 transition-colors shrink-0 ${
                glowEffects ? 'bg-[#F20D2F]' : 'bg-[#28313D]'
              }`}
            >
              <div
                className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                  glowEffects ? 'translate-x-6' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {/* 3. Live Telemetry Stream */}
          <div className="bg-[#151D27] p-3.5 rounded-lg border border-[#28313D] flex items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Radio className="w-3.5 h-3.5 text-emerald-400" />
                <span className="font-bold text-white font-mono uppercase text-[11px]">
                  Live Stream Polling
                </span>
              </div>
              <p className="text-slate-400 text-[11px]">
                Periodically synchronizes lap times and stochastic simulation state with the backend.
              </p>
            </div>

            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              role="switch"
              aria-checked={autoRefresh}
              className={`w-12 h-6 flex items-center rounded-full p-1 transition-colors shrink-0 ${
                autoRefresh ? 'bg-[#16B86A]' : 'bg-[#28313D]'
              }`}
            >
              <div
                className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                  autoRefresh ? 'translate-x-6' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {/* 4. Backend Connection Diagnostics */}
          <div className="bg-[#0D1219] p-3.5 rounded-lg border border-[#28313D] space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Cpu className="w-3.5 h-3.5 text-slate-400" />
                <span className="font-bold text-white font-mono uppercase text-[11px]">
                  FastAPI Engine Endpoint
                </span>
              </div>
              <span
                className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                  backendOnline
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                    : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                }`}
              >
                {backendOnline ? 'ONLINE' : 'STANDALONE / DISCONNECTED'}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="text"
                readOnly
                value="http://127.0.0.1:8000"
                className="bg-[#151D27] border border-[#28313D] rounded px-2.5 py-1 text-xs text-slate-300 font-mono flex-1 focus:outline-none"
              />
              <button
                onClick={handleTestConnection}
                disabled={testing}
                className="bg-[#28313D] hover:bg-slate-700 text-white px-3 py-1 rounded text-xs font-mono font-bold transition-colors disabled:opacity-50"
              >
                {testing ? 'Testing...' : 'Test Connection'}
              </button>
            </div>

            {testStatus && (
              <p className="text-[11px] font-mono text-slate-300 pt-1 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#1677E8]" />
                {testStatus}
              </p>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between border-t border-[#28313D] pt-3 text-xs font-mono text-slate-400">
          <span>Preferences saved automatically</span>
          <button
            onClick={onClose}
            className="bg-[#F20D2F] hover:bg-[#d00926] text-white px-4 py-1.5 rounded font-bold text-xs transition-colors shadow-md shadow-[#F20D2F]/20"
          >
            Apply &amp; Close
          </button>
        </div>
      </div>
    </div>
  );
};


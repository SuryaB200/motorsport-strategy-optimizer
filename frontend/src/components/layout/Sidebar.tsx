import React from 'react';
import {
  Flag,
  Activity,
  Disc,
  Zap,
  CloudRain,
  Clock,
} from 'lucide-react';

export type TabId = 'overview' | 'simulation' | 'tire-sets' | 'strategy' | 'weather' | 'results';

interface SidebarProps {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
  backendOnline: boolean;
}

interface NavItem {
  id: TabId;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'overview', label: 'Race Overview', icon: Flag },
  { id: 'simulation', label: 'Simulation', icon: Activity },
  { id: 'tire-sets', label: 'Tire Sets', icon: Disc },
  { id: 'strategy', label: 'Strategy Optimization', icon: Zap },
  { id: 'weather', label: 'Weather & Risk', icon: CloudRain },
  { id: 'results', label: 'Results & History', icon: Clock },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, backendOnline }) => {
  return (
    <aside className="w-16 md:w-52 bg-[#0D1219] border-r border-[#28313D] flex flex-col justify-between shrink-0 select-none py-3 z-40">
      {/* Navigation items */}
      <nav className="space-y-1.5 px-2">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded text-xs font-medium transition-all ${
                isActive
                  ? 'text-white bg-[#F20D2F] shadow-lg shadow-[#F20D2F]/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#151D27]'
              }`}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="hidden md:inline truncate">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* System Status info */}
      <div className="px-3 text-[10px] text-slate-500 font-mono hidden md:block">
        <div className="border-t border-[#28313D] pt-3 space-y-1">
          <p className="font-semibold text-slate-400 tracking-wider">STRAT-ENGINE v4.2</p>
          <div className="flex items-center gap-1.5 text-slate-400">
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                backendOnline ? 'bg-[#16B86A]' : 'bg-amber-400'
              }`}
            />
            <span>{backendOnline ? 'API FASTAPI: ONLINE' : 'STANDALONE MODE'}</span>
          </div>
          <p className="text-[9px] text-slate-600">STOCHASTIC SIMULATION</p>
        </div>
      </div>
    </aside>
  );
};


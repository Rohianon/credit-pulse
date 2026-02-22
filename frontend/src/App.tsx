import { useState } from 'react';
import { LayoutDashboard, Target, Database, Moon, Sun, Activity } from 'lucide-react';
import Dashboard from './components/Dashboard';
import RiskScorer from './components/RiskScorer';
import SQLAnalysis from './components/SQLAnalysis';

type Page = 'dashboard' | 'scorer' | 'sql';

const NAV: { id: Page; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'scorer', label: 'Risk Scorer', icon: Target },
  { id: 'sql', label: 'SQL Analysis', icon: Database },
];

export default function App() {
  const [page, setPage] = useState<Page>('dashboard');
  const [light, setLight] = useState(false);

  return (
    <div className={light ? 'light' : ''}>
      <div className="min-h-screen bg-surface transition-colors duration-300">
        {/* Ambient glow */}
        <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-pz-green/5 rounded-full blur-[120px] pointer-events-none" />

        {/* Header */}
        <header className="sticky top-0 z-50 bg-surface-glass backdrop-blur-2xl border-b border-border-subtle">
          <div className="max-w-[1400px] mx-auto px-6 h-14 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative flex items-center gap-2">
                <div className="w-7 h-7 rounded-md bg-pz-green flex items-center justify-center">
                  <Activity className="w-4 h-4 text-white" strokeWidth={2.5} />
                </div>
                <span className="text-[15px] font-semibold tracking-tight text-text-primary">
                  Credit<span className="text-pz-green">Pulse</span>
                </span>
              </div>
              <span className="hidden sm:block text-[10px] font-medium uppercase tracking-[0.15em] text-text-muted ml-3 pl-3 border-l border-border-subtle">
                Pezesha
              </span>
            </div>

            <div className="flex items-center">
              <nav className="flex items-center bg-surface-overlay rounded-lg p-0.5 mr-3">
                {NAV.map(({ id, label, icon: Icon }) => (
                  <button
                    key={id}
                    onClick={() => setPage(id)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${
                      page === id
                        ? 'bg-pz-green text-white shadow-sm shadow-pz-green/25'
                        : 'text-text-secondary hover:text-text-primary'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">{label}</span>
                  </button>
                ))}
              </nav>
              <button
                onClick={() => setLight(!light)}
                className="p-1.5 rounded-md text-text-muted hover:text-text-secondary hover:bg-surface-overlay transition-colors"
              >
                {light ? <Moon className="w-3.5 h-3.5" /> : <Sun className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="max-w-[1400px] mx-auto px-6 py-6">
          <div key={page} className="animate-fade-up">
            {page === 'dashboard' && <Dashboard />}
            {page === 'scorer' && <RiskScorer />}
            {page === 'sql' && <SQLAnalysis />}
          </div>
        </main>

        {/* Footer */}
        <footer className="border-t border-border-subtle py-4 mt-8">
          <div className="max-w-[1400px] mx-auto px-6 flex items-center justify-between">
            <p className="text-[11px] text-text-muted">
              CreditPulse &middot; Pezesha Africa Limited
            </p>
            <p className="text-[11px] text-text-muted">
              Data Engineering Assessment &middot; 2026
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}

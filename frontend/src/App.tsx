import { useState } from 'react';
import { LayoutDashboard, Target, Database, Moon, Sun } from 'lucide-react';
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
  const [dark, setDark] = useState(false);

  return (
    <div className={dark ? 'dark' : ''}>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors">
        {/* Header */}
        <header className="sticky top-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200 dark:border-gray-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">CP</span>
              </div>
              <h1 className="text-lg font-bold text-gray-900 dark:text-white">Credit Pulse</h1>
            </div>

            <nav className="flex items-center gap-1">
              {NAV.map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setPage(id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    page === id
                      ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{label}</span>
                </button>
              ))}
              <button
                onClick={() => setDark(!dark)}
                className="ml-2 p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              </button>
            </nav>
          </div>
        </header>

        {/* Main content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {page === 'dashboard' && <Dashboard />}
          {page === 'scorer' && <RiskScorer />}
          {page === 'sql' && <SQLAnalysis />}
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-200 dark:border-gray-800 py-4">
          <p className="text-center text-xs text-gray-400 dark:text-gray-600">
            Credit Pulse — Pezesha Data Engineering Assessment
          </p>
        </footer>
      </div>
    </div>
  );
}

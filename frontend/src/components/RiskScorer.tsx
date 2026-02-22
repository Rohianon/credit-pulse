import { useState } from 'react';
import { api } from '../lib/api';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts';
import { Zap, Shield, AlertTriangle, Target } from 'lucide-react';

const FIELDS = [
  { key: 'transaction_count', label: 'Transaction Count', default: 1500 },
  { key: 'active_days', label: 'Active Days', default: 200 },
  { key: 'total_inflows', label: 'Total Inflows (KES)', default: 500000 },
  { key: 'total_outflows', label: 'Total Outflows (KES)', default: 450000 },
  { key: 'avg_balance', label: 'Average Balance (KES)', default: 5000 },
  { key: 'balance_volatility', label: 'Balance Volatility', default: 3000 },
  { key: 'betting_spend_ratio', label: 'Betting Spend Ratio', default: 0.02 },
  { key: 'utility_payment_ratio', label: 'Utility Payment Ratio', default: 0.05 },
  { key: 'cash_withdrawal_ratio', label: 'Cash Withdrawal Ratio', default: 0.15 },
  { key: 'p2p_transfer_ratio', label: 'P2P Transfer Ratio', default: 0.3 },
  { key: 'loan_product_count', label: 'Loan Products Used', default: 1 },
  { key: 'inflow_outflow_ratio', label: 'Inflow/Outflow Ratio', default: 1.1 },
];

type Result = {
  risk_score: number;
  risk_label: string;
  default_probability: number;
  model_used: string;
  top_factors: { feature: string; value: number; importance: number }[];
};

const riskConfig = (label: string) => ({
  high: { color: '#E85D5D', bg: 'bg-danger/10 border-danger/20', text: 'text-danger', icon: AlertTriangle },
  medium: { color: '#E8A84C', bg: 'bg-warning/10 border-warning/20', text: 'text-warning', icon: Shield },
  low: { color: '#4CB050', bg: 'bg-pz-green/10 border-pz-green/20', text: 'text-pz-green', icon: Shield },
}[label] ?? { color: '#4CB050', bg: 'bg-pz-green/10 border-pz-green/20', text: 'text-pz-green', icon: Shield });

export default function RiskScorer() {
  const [values, setValues] = useState<Record<string, number>>(
    Object.fromEntries(FIELDS.map((f) => [f.key, f.default]))
  );
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.scoreRisk(values);
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to score');
    } finally {
      setLoading(false);
    }
  };

  const config = result ? riskConfig(result.risk_label) : null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
      {/* Input form — 3 cols */}
      <div className="lg:col-span-3 bg-surface-raised rounded-xl p-6 border border-border-subtle noise relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-pz-green" />
        <div className="flex items-center gap-2 mb-6">
          <Zap className="w-4 h-4 text-pz-green" />
          <h3 className="text-sm font-semibold text-text-primary">Borrower Profile</h3>
        </div>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {FIELDS.map((f) => (
              <div key={f.key} className="group">
                <label className="block text-[10px] font-medium uppercase tracking-[0.1em] text-text-muted mb-1.5 group-focus-within:text-pz-green transition-colors">
                  {f.label}
                </label>
                <input
                  type="number"
                  step="any"
                  value={values[f.key]}
                  onChange={(e) => setValues({ ...values, [f.key]: Number(e.target.value) })}
                  className="w-full px-3 py-2 rounded-lg bg-surface-overlay border border-border-subtle text-text-primary text-sm font-mono
                    focus:border-pz-green/50 focus:ring-1 focus:ring-pz-green/20 focus:bg-surface-raised outline-none transition-all"
                />
              </div>
            ))}
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-pz-green hover:bg-pz-green-dark text-white text-sm font-semibold rounded-lg
              transition-all duration-200 disabled:opacity-40 hover:shadow-lg hover:shadow-pz-green/20
              active:scale-[0.98]"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Analyzing...
              </span>
            ) : (
              'Calculate Risk Score'
            )}
          </button>
          {error && (
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-danger-muted border border-danger/20">
              <AlertTriangle className="w-3.5 h-3.5 text-danger" />
              <p className="text-xs text-danger">{error}</p>
            </div>
          )}
        </form>
      </div>

      {/* Result — 2 cols */}
      <div className="lg:col-span-2 space-y-4">
        {result && config ? (
          <>
            {/* Score display */}
            <div className="bg-surface-raised rounded-xl p-6 border border-border-subtle noise relative overflow-hidden animate-fade-up">
              <div className={`absolute top-0 left-0 right-0 h-[2px]`} style={{ background: config.color }} />
              <div className="text-center">
                <p className="text-[10px] font-medium uppercase tracking-[0.15em] text-text-muted mb-4">Risk Assessment</p>

                {/* Score gauge */}
                <div className="relative w-36 h-36 mx-auto mb-4">
                  <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                    <circle cx="50" cy="50" r="42" fill="none" stroke="var(--color-border-subtle)" strokeWidth="6" />
                    <circle
                      cx="50" cy="50" r="42" fill="none"
                      stroke={config.color}
                      strokeWidth="6" strokeLinecap="round"
                      strokeDasharray={`${result.risk_score * 264} 264`}
                      style={{ transition: 'stroke-dasharray 0.8s ease-out' }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-3xl font-bold font-mono text-text-primary">{(result.risk_score * 100).toFixed(0)}</span>
                    <span className="text-[10px] text-text-muted font-mono">/ 100</span>
                  </div>
                </div>

                {/* Risk badge */}
                <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border ${config.bg}`}>
                  <config.icon className={`w-3 h-3 ${config.text}`} />
                  <span className={`text-xs font-bold uppercase tracking-wider ${config.text}`}>
                    {result.risk_label} Risk
                  </span>
                </div>

                <div className="mt-4 space-y-1">
                  <p className="text-xs text-text-secondary">
                    Default probability: <span className="font-mono font-medium text-text-primary">{(result.default_probability * 100).toFixed(1)}%</span>
                  </p>
                  <p className="text-[11px] text-text-muted">
                    Model: {result.model_used.replace(/_/g, ' ')}
                  </p>
                </div>
              </div>
            </div>

            {/* Top factors */}
            <div className="bg-surface-raised rounded-xl p-5 border border-border-subtle noise relative overflow-hidden animate-fade-up" style={{ animationDelay: '100ms' }}>
              <div className="absolute top-0 left-0 right-0 h-[2px] bg-border-accent" />
              <p className="text-[10px] font-medium uppercase tracking-[0.15em] text-text-muted mb-3">Contributing Factors</p>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart
                  data={result.top_factors.slice(0, 8).map((f) => ({
                    name: f.feature.replace(/_/g, ' '),
                    importance: Number(f.importance.toFixed(4)),
                  })).reverse()}
                  layout="vertical"
                  margin={{ left: 100, right: 8 }}
                >
                  <XAxis type="number" tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: 'var(--color-text-secondary)' }} width={95} axisLine={false} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      background: 'var(--color-surface-raised)',
                      border: '1px solid var(--color-border-subtle)',
                      borderRadius: '8px',
                      fontSize: '11px',
                      color: 'var(--color-text-primary)',
                    }}
                  />
                  <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
                    {result.top_factors.slice(0, 8).reverse().map((_, i) => (
                      <Cell key={i} fill={`rgba(76, 176, 80, ${0.4 + (i / 8) * 0.6})`} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : (
          <div className="bg-surface-raised rounded-xl p-10 border border-border-subtle border-dashed text-center noise relative overflow-hidden h-full flex flex-col items-center justify-center">
            <div className="w-14 h-14 rounded-2xl bg-pz-green/10 flex items-center justify-center mb-4">
              <Target className="w-7 h-7 text-pz-green" />
            </div>
            <h3 className="text-sm font-semibold text-text-primary mb-2">Score a Borrower</h3>
            <p className="text-xs text-text-muted max-w-[240px] leading-relaxed">
              Fill in the M-Pesa transaction features and click calculate to get a real-time credit risk assessment.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

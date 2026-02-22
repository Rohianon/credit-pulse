import { useState } from 'react';
import { api } from '../lib/api';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';

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

  const riskColor = (label: string) =>
    label === 'high' ? 'text-red-500' : label === 'medium' ? 'text-amber-500' : 'text-emerald-500';
  const riskBg = (label: string) =>
    label === 'high' ? 'bg-red-500' : label === 'medium' ? 'bg-amber-500' : 'bg-emerald-500';

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Input form */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-800">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6">Borrower Features</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {FIELDS.map((f) => (
              <div key={f.key}>
                <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{f.label}</label>
                <input
                  type="number"
                  step="any"
                  value={values[f.key]}
                  onChange={(e) => setValues({ ...values, [f.key]: Number(e.target.value) })}
                  className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                />
              </div>
            ))}
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-xl transition-colors disabled:opacity-50"
          >
            {loading ? 'Scoring...' : 'Calculate Risk Score'}
          </button>
          {error && <p className="text-sm text-red-500">{error}</p>}
        </form>
      </div>

      {/* Result */}
      <div className="space-y-6">
        {result ? (
          <>
            {/* Score gauge */}
            <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-800 text-center">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Risk Assessment</h3>
              <div className="relative w-40 h-40 mx-auto mb-4">
                <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                  <circle cx="50" cy="50" r="42" fill="none" stroke="#e5e7eb" strokeWidth="8" />
                  <circle
                    cx="50" cy="50" r="42" fill="none"
                    stroke={result.risk_label === 'high' ? '#ef4444' : result.risk_label === 'medium' ? '#f59e0b' : '#22c55e'}
                    strokeWidth="8" strokeLinecap="round"
                    strokeDasharray={`${result.risk_score * 264} 264`}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-bold text-gray-900 dark:text-white">{(result.risk_score * 100).toFixed(0)}</span>
                  <span className="text-xs text-gray-500">/ 100</span>
                </div>
              </div>
              <span className={`inline-block px-4 py-1.5 rounded-full text-sm font-semibold text-white ${riskBg(result.risk_label)}`}>
                {result.risk_label.toUpperCase()} RISK
              </span>
              <p className="text-sm text-gray-500 mt-2">Default probability: {(result.default_probability * 100).toFixed(1)}%</p>
              <p className="text-xs text-gray-400 mt-1">Model: {result.model_used.replace(/_/g, ' ')}</p>
            </div>

            {/* Top factors */}
            <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Top Risk Factors</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart
                  data={result.top_factors.slice(0, 8).map((f) => ({ name: f.feature.replace(/_/g, ' '), importance: Number(f.importance.toFixed(4)) })).reverse()}
                  layout="vertical"
                  margin={{ left: 120 }}
                >
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={110} />
                  <Tooltip contentStyle={{ borderRadius: '12px', border: 'none' }} />
                  <Bar dataKey="importance" fill="#6366f1" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : (
          <div className="bg-white dark:bg-gray-900 rounded-2xl p-12 shadow-sm border border-gray-100 dark:border-gray-800 text-center">
            <div className="text-6xl mb-4">🎯</div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Score a Borrower</h3>
            <p className="text-sm text-gray-500">Fill in the borrower's transaction features on the left and click "Calculate Risk Score" to get a real-time credit risk assessment.</p>
          </div>
        )}
      </div>
    </div>
  );
}

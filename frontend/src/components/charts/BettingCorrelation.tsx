import { ScatterChart, Scatter, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts';
import { useApi } from '../../hooks/useApi';
import { api } from '../../lib/api';

export default function BettingCorrelation() {
  const { data, loading } = useApi(api.getBetting);
  if (loading || !data) return <div className="animate-pulse h-64 bg-gray-100 dark:bg-gray-800 rounded-xl" />;

  const chartData = data.map((d) => ({
    betting: Number((d.betting_spend_ratio * 100).toFixed(1)),
    loan: d.loan_amount,
    defaulted: d.is_defaulted,
  }));

  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-800">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Betting Spend vs Default</h3>
      <ResponsiveContainer width="100%" height={280}>
        <ScatterChart margin={{ bottom: 10 }}>
          <XAxis dataKey="betting" name="Betting %" unit="%" tick={{ fontSize: 11 }} />
          <YAxis dataKey="loan" name="Loan" tick={{ fontSize: 11 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}K`} />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,.08)' }} />
          <Scatter data={chartData}>
            {chartData.map((d, i) => (
              <Cell key={i} fill={d.defaulted ? '#ef4444' : '#22c55e'} opacity={0.7} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      <div className="flex gap-4 justify-center mt-2 text-xs text-gray-500">
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-green-500" /> Repaid</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-red-500" /> Defaulted</span>
      </div>
    </div>
  );
}

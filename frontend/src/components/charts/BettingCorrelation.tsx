import { ScatterChart, Scatter, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts';
import { useApi } from '../../hooks/useApi';
import { api } from '../../lib/api';

export default function BettingCorrelation() {
  const { data, loading } = useApi(api.getBetting);
  if (loading || !data) return <div className="h-72 rounded-xl animate-shimmer" />;

  const chartData = data.map((d) => ({
    betting: Number((d.betting_spend_ratio * 100).toFixed(1)),
    loan: d.loan_amount,
    defaulted: d.is_defaulted,
  }));

  return (
    <div className="bg-surface-raised rounded-xl p-5 border border-border-subtle noise relative overflow-hidden card-hover">
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-danger" />
      <div className="flex items-center justify-between mb-4">
        <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-text-muted">Betting Spend vs Default</p>
        <div className="flex gap-3">
          <span className="flex items-center gap-1.5 text-[10px] text-text-muted">
            <span className="w-2 h-2 rounded-full bg-pz-green" /> Repaid
          </span>
          <span className="flex items-center gap-1.5 text-[10px] text-text-muted">
            <span className="w-2 h-2 rounded-full bg-danger" /> Defaulted
          </span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <ScatterChart margin={{ bottom: 10, left: 0 }}>
          <XAxis dataKey="betting" name="Betting %" unit="%" tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }} axisLine={false} tickLine={false} />
          <YAxis dataKey="loan" name="Loan" tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}K`} axisLine={false} tickLine={false} />
          <Tooltip
            cursor={{ strokeDasharray: '3 3', stroke: 'var(--color-border-accent)' }}
            contentStyle={{
              background: 'var(--color-surface-raised)',
              border: '1px solid var(--color-border-subtle)',
              borderRadius: '8px',
              fontSize: '11px',
              color: 'var(--color-text-primary)',
            }}
          />
          <Scatter data={chartData}>
            {chartData.map((d, i) => (
              <Cell key={i} fill={d.defaulted ? '#E85D5D' : '#4CB050'} opacity={0.65} r={5} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { useApi } from '../../hooks/useApi';
import { api } from '../../lib/api';

const COLORS = ['#4CB050', '#E85D5D'];

export default function RepaymentDistribution() {
  const { data, loading } = useApi(api.getRepayment);
  if (loading || !data) return <div className="h-72 rounded-xl animate-shimmer" />;

  const total = data.reduce((s, d) => s + d.count, 0);

  return (
    <div className="bg-surface-raised rounded-xl p-5 border border-border-subtle noise relative overflow-hidden card-hover">
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-pz-green" />
      <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-text-muted mb-4">Repayment Distribution</p>
      <div className="flex items-center">
        <ResponsiveContainer width="55%" height={220}>
          <PieChart>
            <Pie data={data} dataKey="count" nameKey="status" cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={3} strokeWidth={0}>
              {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
            </Pie>
            <Tooltip
              formatter={(value) => Number(value).toLocaleString()}
              contentStyle={{
                background: 'var(--color-surface-raised)',
                border: '1px solid var(--color-border-subtle)',
                borderRadius: '8px',
                fontSize: '11px',
                color: 'var(--color-text-primary)',
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="flex-1 space-y-3 pl-2">
          {data.map((d, i) => (
            <div key={d.status} className="flex items-center gap-3">
              <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: COLORS[i] }} />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-text-primary">{d.status}</p>
                <p className="text-[11px] text-text-muted font-mono">
                  {d.count} ({((d.count / total) * 100).toFixed(0)}%)
                </p>
              </div>
            </div>
          ))}
          <div className="pt-2 border-t border-border-subtle">
            <p className="text-[10px] text-text-muted">Avg defaulted loan</p>
            <p className="text-xs font-mono font-medium text-danger">
              KES {data.find(d => d.status === 'Defaulted')?.avg_loan_amount?.toLocaleString(undefined, { maximumFractionDigits: 0 }) ?? '—'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

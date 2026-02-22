import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { useApi } from '../../hooks/useApi';
import { api } from '../../lib/api';

export default function TransactionFlows() {
  const { data, loading } = useApi(api.getTransactions);
  if (loading || !data) return <div className="h-72 rounded-xl animate-shimmer" />;

  const chartData = data.monthly_flows.map((d) => ({
    month: d.month,
    inflows: Math.round(d.total_inflows),
    outflows: Math.round(d.total_outflows),
  }));

  return (
    <div className="bg-surface-raised rounded-xl p-5 border border-border-subtle noise relative overflow-hidden card-hover">
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-pz-green" />
      <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-text-muted mb-4">Monthly Transaction Flows</p>
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="inflowGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#4CB050" stopOpacity={0.25} />
              <stop offset="100%" stopColor="#4CB050" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="outflowGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#E85D5D" stopOpacity={0.2} />
              <stop offset="100%" stopColor="#E85D5D" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="month" tick={{ fontSize: 9, fill: 'var(--color-text-muted)' }} interval="preserveStartEnd" axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }} tickFormatter={(v) => `${(v / 1e6).toFixed(1)}M`} axisLine={false} tickLine={false} />
          <Tooltip
            formatter={(v) => `KES ${Number(v).toLocaleString()}`}
            contentStyle={{
              background: 'var(--color-surface-raised)',
              border: '1px solid var(--color-border-subtle)',
              borderRadius: '8px',
              fontSize: '11px',
              color: 'var(--color-text-primary)',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '11px', color: 'var(--color-text-muted)' }} />
          <Area type="monotone" dataKey="inflows" stroke="#4CB050" fill="url(#inflowGrad)" strokeWidth={2} name="Inflows" />
          <Area type="monotone" dataKey="outflows" stroke="#E85D5D" fill="url(#outflowGrad)" strokeWidth={1.5} name="Outflows" strokeDasharray="4 2" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

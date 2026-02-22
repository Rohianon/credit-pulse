import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { useApi } from '../../hooks/useApi';
import { api } from '../../lib/api';

export default function RiskSegments() {
  const { data, loading } = useApi(api.getSegments);
  if (loading || !data) return <div className="h-72 rounded-xl animate-shimmer" />;

  const chartData = data.map((d) => ({
    segment: d.risk_segment.replace('_', ' '),
    count: d.count,
    default_rate: Number((d.default_rate * 100).toFixed(1)),
  }));

  return (
    <div className="bg-surface-raised rounded-xl p-5 border border-border-subtle noise relative overflow-hidden card-hover">
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-danger" />
      <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-text-muted mb-4">Risk Segments</p>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={chartData} barGap={6}>
          <XAxis dataKey="segment" tick={{ fontSize: 11, fill: 'var(--color-text-secondary)' }} axisLine={false} tickLine={false} />
          <YAxis yAxisId="left" tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }} axisLine={false} tickLine={false} />
          <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }} unit="%" axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{
              background: 'var(--color-surface-raised)',
              border: '1px solid var(--color-border-subtle)',
              borderRadius: '8px',
              fontSize: '11px',
              color: 'var(--color-text-primary)',
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: '11px', color: 'var(--color-text-muted)' }}
          />
          <Bar yAxisId="left" dataKey="count" fill="#4CB050" radius={[4, 4, 0, 0]} name="Borrowers" opacity={0.85} />
          <Bar yAxisId="right" dataKey="default_rate" fill="#E85D5D" radius={[4, 4, 0, 0]} name="Default Rate %" opacity={0.85} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts';
import { useApi } from '../../hooks/useApi';
import { api } from '../../lib/api';

export default function FeatureImportance() {
  const { data, loading } = useApi(api.getFeatures);
  if (loading || !data) return <div className="h-72 rounded-xl animate-shimmer" />;

  const chartData = data.feature_importance.slice(0, 10).map(([name, value]) => ({
    name: name.replace(/_/g, ' '),
    importance: Number(value.toFixed(4)),
  })).reverse();

  const maxVal = Math.max(...chartData.map(d => d.importance));

  return (
    <div className="bg-surface-raised rounded-xl p-5 border border-border-subtle noise relative overflow-hidden card-hover">
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-pz-green" />
      <div className="flex items-center justify-between mb-4">
        <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-text-muted">Feature Importance</p>
        <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-md bg-pz-green/10 text-pz-green border border-pz-green/20">
          AUC {data.auc.toFixed(3)}
        </span>
      </div>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 110, right: 8 }}>
          <XAxis type="number" tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: 'var(--color-text-secondary)' }} width={105} axisLine={false} tickLine={false} />
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
            {chartData.map((entry, i) => (
              <Cell key={i} fill={`rgba(76, 176, 80, ${0.3 + (entry.importance / maxVal) * 0.7})`} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

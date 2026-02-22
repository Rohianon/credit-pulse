import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts';
import { useApi } from '../../hooks/useApi';
import { api } from '../../lib/api';

const CATEGORY_COLORS: Record<string, string> = {
  'p2p sent': '#4CB050',
  'p2p received': '#6ECF72',
  'cash withdrawal': '#E8A84C',
  'merchant': '#4C9BE8',
  'betting': '#E85D5D',
  'airtime': '#A78BFA',
  'utility': '#2DD4BF',
  'mshwari': '#F472B6',
  'kcb mpesa': '#FB923C',
  'fuliza': '#94A3B8',
  'other': '#6D6E71',
};

export default function CategoryBreakdown() {
  const { data, loading } = useApi(api.getTransactions);
  if (loading || !data) return <div className="h-72 rounded-xl animate-shimmer" />;

  const chartData = data.categories
    .filter((c) => c.total_amount > 0)
    .slice(0, 10)
    .map((d) => ({
      category: d.tx_category.replace(/_/g, ' '),
      amount: Math.round(d.total_amount),
      count: d.count,
    }));

  return (
    <div className="bg-surface-raised rounded-xl p-5 border border-border-subtle noise relative overflow-hidden card-hover">
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-warning" />
      <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-text-muted mb-4">Transaction Categories</p>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={chartData}>
          <XAxis dataKey="category" tick={{ fontSize: 9, fill: 'var(--color-text-muted)' }} angle={-35} textAnchor="end" height={60} axisLine={false} tickLine={false} />
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
          <Bar dataKey="amount" radius={[4, 4, 0, 0]} name="Total Amount (KES)">
            {chartData.map((entry, i) => (
              <Cell key={i} fill={CATEGORY_COLORS[entry.category] ?? '#6D6E71'} opacity={0.85} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

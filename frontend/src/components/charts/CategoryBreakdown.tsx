import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { useApi } from '../../hooks/useApi';
import { api } from '../../lib/api';

export default function CategoryBreakdown() {
  const { data, loading } = useApi(api.getTransactions);
  if (loading || !data) return <div className="animate-pulse h-64 bg-gray-100 dark:bg-gray-800 rounded-xl" />;

  const chartData = data.categories
    .filter((c) => c.total_amount > 0)
    .slice(0, 10)
    .map((d) => ({
      category: d.tx_category.replace(/_/g, ' '),
      amount: Math.round(d.total_amount),
      count: d.count,
    }));

  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-800">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Transaction Categories</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData}>
          <XAxis dataKey="category" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" height={60} />
          <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${(v / 1e6).toFixed(1)}M`} />
          <Tooltip formatter={(v: number) => `KES ${v.toLocaleString()}`} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,.08)' }} />
          <Bar dataKey="amount" fill="#f59e0b" radius={[6, 6, 0, 0]} name="Total Amount (KES)" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

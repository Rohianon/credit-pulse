import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { useApi } from '../../hooks/useApi';
import { api } from '../../lib/api';

const COLORS = ['#22c55e', '#ef4444'];

export default function RepaymentDistribution() {
  const { data, loading } = useApi(api.getRepayment);
  if (loading || !data) return <div className="animate-pulse h-64 bg-gray-100 dark:bg-gray-800 rounded-xl" />;

  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-800">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Repayment Distribution</h3>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie data={data} dataKey="count" nameKey="status" cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={4} strokeWidth={0}>
            {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Pie>
          <Tooltip formatter={(value) => Number(value).toLocaleString()} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,.08)' }} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
